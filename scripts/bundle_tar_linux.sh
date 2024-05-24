#!/bin/bash
set -e
ARCH="${ARCH:-x86_64}"
export PLATFORM="linux-${ARCH}"

APP="CGAspects"
TAR_PATH="CGAspects-${PLATFORM}.tar.gz"

tar -czf "${TAR_PATH}" -C dist "${APP}"
