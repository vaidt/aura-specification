#!/usr/bin/env bash
# Run parser/test commands inside an immutable-image Docker container with no network.
set -euo pipefail

readonly PINNED_IMAGE="ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55"

: "${GITHUB_WORKSPACE:?GITHUB_WORKSPACE is required}"
: "${pythonLocation:?setup-python must run before the offline runner}"

workspace="$(realpath "$GITHUB_WORKSPACE")"
python_home="$(realpath "$pythonLocation")"
[[ -x "$python_home/bin/python" ]] || { echo "C6_OFFLINE_RUNNER=FAIL: pinned Python path unavailable" >&2; exit 1; }
[[ -d "$HOME/.cargo" && -d "$HOME/.rustup" ]] || { echo "C6_OFFLINE_RUNNER=FAIL: Cargo/Rustup cache missing" >&2; exit 1; }
docker image inspect "$PINNED_IMAGE" >/dev/null 2>&1 || {
  echo "C6_OFFLINE_RUNNER=FAIL: pinned container image has not been prefetched" >&2
  exit 1
}

cwd="$(realpath "$PWD")"
case "$cwd" in
  "$workspace") relative_cwd="" ;;
  "$workspace"/*) relative_cwd="${cwd#"$workspace"/}" ;;
  *) echo "C6_OFFLINE_RUNNER=FAIL: current directory is outside GITHUB_WORKSPACE" >&2; exit 1 ;;
esac
container_cwd="/workspace"
[[ -n "$relative_cwd" ]] && container_cwd="/workspace/$relative_cwd"

args=(
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
  "$PINNED_IMAGE"
  /bin/bash -euo pipefail -c '
    "$AURA_C6_PYTHON" /workspace/scripts/stage_c/verify_c6_network_isolation.py
    exec "$@"
  ' c6-offline-command
)

# Forward only the allowlisted variables needed by the pinned corpus/parser harness.
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
  args=("${args[@]:0:${#args[@]}-2}" --env "$name=$value" "${args[@]: -2}")
done

# setup-python exports LD_LIBRARY_PATH to the selected interpreter's lib directory.
if [[ -n "${LD_LIBRARY_PATH:-}" ]]; then
  args=("${args[@]:0:${#args[@]}-2}" --env "LD_LIBRARY_PATH=$LD_LIBRARY_PATH" "${args[@]: -2}")
fi

printf 'C6_OFFLINE_IMAGE=%s\n' "$PINNED_IMAGE"
printf 'C6_OFFLINE_WORKDIR=%s\n' "$container_cwd"
printf 'C6_OFFLINE_POLICY=network-none,read-only-rootfs,drop-all-capabilities,no-new-privileges\n'
exec docker "${args[@]}" "$@"
