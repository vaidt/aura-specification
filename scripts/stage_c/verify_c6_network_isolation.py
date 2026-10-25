#!/usr/bin/env python3
"""Fail-closed assertion that parser execution is inside a Docker network-none namespace."""
from __future__ import annotations

import os
import socket
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"C6_NETWORK_ISOLATION=FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


if os.environ.get("AURA_C6_OFFLINE_EXECUTION") != "1":
    fail("offline execution marker is missing")
if os.environ.get("CARGO_NET_OFFLINE", "").lower() != "true":
    fail("Cargo offline mode is not enabled")
if os.environ.get("PIP_NO_INDEX") != "1":
    fail("pip index access is not disabled")

interfaces = {name for _, name in socket.if_nameindex()}
if interfaces != {"lo"}:
    fail(f"expected only loopback interface; got {sorted(interfaces)}")

route_file = Path("/proc/net/route")
if not route_file.is_file():
    fail("/proc/net/route is unavailable; isolation cannot be verified")
default_routes: list[str] = []
for line in route_file.read_text(encoding="ascii").splitlines()[1:]:
    fields = line.split()
    if len(fields) >= 4 and fields[1] == "00000000" and fields[0] != "lo":
        default_routes.append(fields[0])
if default_routes:
    fail(f"external/default route found on: {default_routes}")

print("C6_NETWORK_ISOLATION=PASS")
print("C6_NETWORK_MODE=DOCKER_NETWORK_NONE")
print(f"C6_NETWORK_INTERFACES={','.join(sorted(interfaces))}")
print("C6_NETWORK_DEFAULT_ROUTE=NONE")
print("C6_CARGO_NET_OFFLINE=true")
print("C6_PIP_NO_INDEX=1")
