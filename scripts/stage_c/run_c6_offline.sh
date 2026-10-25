#!/usr/bin/env bash
# Run parser/test commands inside an immutable toolchain image derived from a
# digest-pinned Ubuntu base, with the actual parser/test execution network-isolated.
set -euo pipefail

readonly PINNED_BASE_IMAGE="ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55"

: "${GITHUB_WORKSPACE:?GITHUB_WORKSPACE is required}"
: "${pythonLocation:?setup-python must run before the offline runner}"

workspace="$(realpath "$GITHUB_WORKSPACE")"
python_home="$(realpath "$pythonLocation")"
[[ -x "$python_home/bin/python" ]] || { echo "C6_OFFLINE_RUNNER=FAIL: pinned Python path unavailable" >&2; exit 1; }
[[ -d "$HOME/.cargo" && -d "$HOME/.rustup" ]] || { echo "C6_OFFLINE_RUNNER=FAIL: Cargo/Rustup cache missing" >&2; exit 1; }
docker image inspect "$PINNED_BASE_IMAGE" >/dev/null 2>&1 || {
  echo "C6_OFFLINE_RUNNER=FAIL: pinned base container image has not been prefetched" >&2
  exit 1
}

# The base image is digest-pinned. Build a local derived image before test
# execution so the network-none container has the tools required by the
# validators and Rust build scripts. Capture the derived image's content ID
# and installed package versions in the workflow logs as execution evidence.
readonly IMAGE_TAG_SUFFIX="${GITHUB_RUN_ID:-local}-${GITHUB_RUN_ATTEMPT:-1}-$(uname -m)"
readonly TOOLCHAIN_IMAGE_TAG="aura-c6-offline-toolchain:$IMAGE_TAG_SUFFIX"

if ! docker image inspect "$TOOLCHAIN_IMAGE_TAG" >/dev/null 2>&1; then
  build_context="$(mktemp -d)"
  cat > "$build_context/Dockerfile" <<EOF
FROM $PINNED_BASE_IMAGE
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      ca-certificates git build-essential \
 && rm -rf /var/lib/apt/lists/*
EOF
  docker build --pull=false --file "$build_context/Dockerfile" --tag "$TOOLCHAIN_IMAGE_TAG" "$build_context"
  rm -rf "$build_context"
fi

PINNED_IMAGE="$(docker image inspect --format '{{.Id}}' "$TOOLCHAIN_IMAGE_TAG")"
[[ "$PINNED_IMAGE" =~ ^sha256:[a-f0-9]{64}$ ]] || {
  echo "C6_OFFLINE_RUNNER=FAIL: derived toolchain image ID is missing or malformed" >&2
  exit 1
}
toolchain_info="$(docker run --rm --network none "$PINNED_IMAGE" /bin/bash -euo pipefail -c '
  command -v git >/dev/null
  command -v cc >/dev/null
  printf "C6_OFFLINE_TOOLCHAIN_GIT=%s\n" "$(git --version)"
  printf "C6_OFFLINE_TOOLCHAIN_CC=%s\n" "$(cc --version | sed -n "1p")"
  dpkg-query -W ca-certificates git build-essential
')"
printf 'C6_OFFLINE_BASE_IMAGE=%s\n' "$PINNED_BASE_IMAGE"
printf 'C6_OFFLINE_TOOLCHAIN_IMAGE_TAG=%s\n' "$TOOLCHAIN_IMAGE_TAG"
printf 'C6_OFFLINE_TOOLCHAIN_IMAGE_ID=%s\n' "$PINNED_IMAGE"
printf '%s\n' "$toolchain_info"

cwd="$(realpath "$PWD")"
case "$cwd" in
  "$workspace") relative_cwd="" ;;
  "$workspace"/*) relative_cwd="${cwd#"$workspace"/}" ;;
  *) echo "C6_OFFLINE_RUNNER=FAIL: current directory is outside GITHUB_WORKSPACE" >&2; exit 1 ;;
esac
container_cwd="/workspace"
[[ -n "$relative_cwd" ]] && container_cwd="/workspace/$relative_cwd"

docker_opts=(
  run --rm
  --network none
  --read-only
  --cap-drop ALL
  --security-opt no-new-privileges
  --pids-limit 256
  --memory 4g
  --cpus 2
  --tmpfs /tmp:rw,nosuid,nodev,size=512m
  --mount "type=bind,src=$workspace,dst=/workspace"
  --mount "type=bind,src=$python_home,dst=$python_home,readonly"
  --mount "type=bind,src=$HOME/.cargo,dst=$HOME/.cargo"
  --mount "type=bind,src=$HOME/.rustup,dst=$HOME/.rustup,readonly"
  --workdir "$container_cwd"
  --user "$(id -u):$(id -g)"
  --env "HOME=$HOME"
  --env "GITHUB_WORKSPACE=/workspace"
  --env "AURA_C6_PYTHON=$python_home/bin/python"
  --env "PATH=$HOME/.cargo/bin:$python_home/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
  --env "CARGO_HOME=$HOME/.cargo"
  --env "RUSTUP_HOME=$HOME/.rustup"
  --env "RUSTUP_TOOLCHAIN=1.87.0"
  --env "CARGO_NET_OFFLINE=true"
  --env "PIP_NO_INDEX=1"
  --env "PYTHONDONTWRITEBYTECODE=1"
  --env "PYTHONNOUSERSITE=1"
  --env "AURA_C6_OFFLINE_EXECUTION=1"
)

# Forward only the allowlisted environment required by the pinned corpus/parsers.
for name in \
  ARCHITECTURE \
  AURA_C6_WIRE_CORPUS_DIR AURA_C6_WIRE_RESULTS_DIR \
  AURA_RI_RS_COMMIT AURA_RI_RS_SOURCE_BLOB AURA_RI_RS_LIB_BLOB AURA_RI_RS_CARGO_BLOB AURA_RI_RS_TEST_BLOB \
  C6_BASELINE_DIR CORPUS_DIR C6_LAB_DIR C6_PILOT_DIR
do
  value="${!name:-}"
  [[ -n "$value" ]] || continue
  case "$value" in
    "$workspace"*) value="/workspace${value#"$workspace"}" ;;
  esac
  docker_opts+=(--env "$name=$value")
done

# setup-python may require this variable for its shared libraries.
if [[ -n "${LD_LIBRARY_PATH:-}" ]]; then
  docker_opts+=(--env "LD_LIBRARY_PATH=$LD_LIBRARY_PATH")
fi

printf 'C6_OFFLINE_IMAGE_ID=%s\n' "$PINNED_IMAGE"
printf 'C6_OFFLINE_WORKDIR=%s\n' "$container_cwd"
printf 'C6_OFFLINE_POLICY=network-none,read-only-rootfs,drop-all-capabilities,no-new-privileges\n'
exec docker "${docker_opts[@]}" "$PINNED_IMAGE" /bin/bash -euo pipefail -c '
  "$AURA_C6_PYTHON" "$GITHUB_WORKSPACE/scripts/stage_c/verify_c6_network_isolation.py"
  exec "$@"
' c6-offline-command "$@"
