#!/usr/bin/env bash
# Nijer Khata — Ubuntu toolchain setup
# Installs: git, build tools, Python 3 + pip + venv + pipx, Node.js LTS (nvm), .NET SDK (default 8.0)
# Safe to run more than once.
#   bash setup/setup-ubuntu.sh               install everything
#   bash setup/setup-ubuntu.sh --no-node     skip Node.js
#   bash setup/setup-ubuntu.sh --no-dotnet   skip .NET
#   DOTNET_CHANNEL=9.0 bash setup/setup-ubuntu.sh   pick another .NET channel
set -euo pipefail

WANT_NODE=1
WANT_DOTNET=1
DOTNET_CHANNEL="${DOTNET_CHANNEL:-8.0}"

for arg in "$@"; do
  case "$arg" in
    --no-node)   WANT_NODE=0 ;;
    --no-dotnet) WANT_DOTNET=0 ;;
    -h|--help)   sed -n '2,8p' "$0"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

if [[ -t 1 ]]; then
  BOLD=$'\033[1m'; GRN=$'\033[32m'; YLW=$'\033[33m'; RED=$'\033[31m'; RST=$'\033[0m'
else
  BOLD=""; GRN=""; YLW=""; RED=""; RST=""
fi
step() { printf '\n%s== %s ==%s\n' "$BOLD" "$*" "$RST"; }
ok()   { printf '%s✔%s %s\n' "$GRN" "$RST" "$*"; }
warn() { printf '%s!%s %s\n' "$YLW" "$RST" "$*"; }
die()  { printf '%s✘%s %s\n' "$RED" "$RST" "$*" >&2; exit 1; }

[[ "$(uname -s)" == "Linux" ]] || die "This script is for Linux/Ubuntu. On Windows install WSL first: wsl --install -d Ubuntu"

if [[ -r /etc/os-release ]]; then . /etc/os-release; fi
case "${ID:-unknown}" in
  ubuntu|debian) ;;
  *) warn "Tested on Ubuntu. Detected '${ID:-unknown}', continuing anyway." ;;
esac

SUDO=""
if [[ $EUID -ne 0 ]]; then
  command -v sudo >/dev/null 2>&1 || die "sudo not found. Run as root, or install sudo first."
  SUDO="sudo"
fi

# ---------------------------------------------------------------- apt packages
step "System packages (apt)"
$SUDO apt-get update -y
$SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  ca-certificates curl wget gnupg unzip zip jq git build-essential \
  python3 python3-pip python3-venv pipx libicu-dev
ok "git $(git --version | awk '{print $3}')"
ok "$(python3 --version) · pip $(python3 -m pip --version | awk '{print $2}')"
pipx ensurepath >/dev/null 2>&1 || true

# ---------------------------------------------------------------- Node.js (nvm)
if [[ $WANT_NODE -eq 1 ]]; then
  step "Node.js LTS (nvm)"
  export NVM_DIR="$HOME/.nvm"
  if [[ ! -s "$NVM_DIR/nvm.sh" ]]; then
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
  fi
  set +u            # nvm.sh is not safe under 'set -u'
  # shellcheck disable=SC1091
  . "$NVM_DIR/nvm.sh"
  nvm install --lts >/dev/null
  nvm alias default 'lts/*' >/dev/null
  set -u
  ok "node $(node -v) · npm $(npm -v)"
fi

# ---------------------------------------------------------------- .NET SDK
if [[ $WANT_DOTNET -eq 1 ]]; then
  step ".NET SDK ${DOTNET_CHANNEL}"
  export DOTNET_ROOT="$HOME/.dotnet"
  export PATH="$DOTNET_ROOT:$PATH"
  if command -v dotnet >/dev/null 2>&1 && dotnet --list-sdks | grep -q "^${DOTNET_CHANNEL%%.*}\."; then
    ok ".NET SDK ${DOTNET_CHANNEL%%.*} already installed"
  else
    tmp="$(mktemp)"
    curl -fsSL https://dot.net/v1/dotnet-install.sh -o "$tmp"
    bash "$tmp" --channel "$DOTNET_CHANNEL" --install-dir "$DOTNET_ROOT"
    rm -f "$tmp"
  fi
  ok "dotnet $(dotnet --version)"
fi

# ---------------------------------------------------------------- ~/.bashrc
MARK="# >>> nijer-khata toolchain >>>"
RC="$HOME/.bashrc"
if grep -qF "$MARK" "$RC" 2>/dev/null; then
  ok "~/.bashrc already configured"
else
  cat >> "$RC" <<'BLOCK'

# >>> nijer-khata toolchain >>>
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
export DOTNET_ROOT="$HOME/.dotnet"
export PATH="$DOTNET_ROOT:$HOME/.local/bin:$PATH"
# <<< nijer-khata toolchain <<<
BLOCK
  ok "PATH, nvm and .NET added to ~/.bashrc"
fi

step "Done"
echo "Open a new terminal, or run:  source ~/.bashrc"
echo "Then check:  git --version · python3 --version · pip3 --version · node -v · dotnet --version"
