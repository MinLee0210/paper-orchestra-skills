#!/usr/bin/env bash
# Install PaperOrchestra Skills into an agent's skills directory.
#
#   macOS / Linux / WSL       each skill is symlinked.
#   Windows (Git Bash, MSYS2, Cygwin)
#                             native symlinks are used when Windows allows them
#                             (Developer Mode or an elevated shell). Otherwise each skill is
#                             copied and marked, so it can be refreshed or removed safely.
#
# The script only ever deletes symlinks and copies that it created itself.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$ROOT/skills"
MARKER=".research-orchestra-installed"
UNINSTALL=0
FORCE=0
LINK_MODE="auto"   # auto = symlink (Windows: symlink, else copy); copy = always copy
TARGETS=()

usage() {
  cat <<'EOF'
Usage: ./install.sh [options]

Options:
  --target DIR   Install into DIR (repeatable). Defaults to:
                 ~/.claude/skills and ~/.config/opencode/skills
                 (on Windows, ~ is %USERPROFILE%)
  --copy         Copy skills instead of symlinking. Re-run after updating the
                 repository to refresh the copies. Default on Windows when
                 symlinks are not permitted.
  --uninstall    Remove the links and copies created by this script
  --force        Replace existing files, directories, or links that this script did not create
  -h, --help     Show this help

Windows: run this from Git Bash, MSYS2, Cygwin, or WSL. To get real symlinks
instead of copies, turn on Developer Mode (Settings > System > For developers)
or run the shell as Administrator.
EOF
}

# --- platform ------------------------------------------------------------------------------------

# INSTALL_SH_PLATFORM=windows|unix overrides detection (used by the tests).
detect_platform() {
  if [[ -n "${INSTALL_SH_PLATFORM:-}" ]]; then
    echo "$INSTALL_SH_PLATFORM"
    return
  fi
  case "$(uname -s 2>/dev/null || echo unknown)" in
    MINGW*|MSYS*|CYGWIN*) echo windows ;;
    *) echo unix ;;
  esac
}

PLATFORM="$(detect_platform)"

# Claude Code and opencode resolve ~ to %USERPROFILE% on Windows, which can differ from Git
# Bash's $HOME. Prefer USERPROFILE when cygpath can translate it.
user_home() {
  if [[ "$PLATFORM" == "windows" && -n "${USERPROFILE:-}" ]] && command -v cygpath >/dev/null 2>&1; then
    cygpath -u "$USERPROFILE"
  else
    echo "$HOME"
  fi
}

# --- arguments -----------------------------------------------------------------------------------

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      [[ $# -ge 2 ]] || { echo "error: --target needs a directory" >&2; exit 2; }
      TARGETS+=("$2")
      shift 2
      ;;
    --copy)
      LINK_MODE="copy"
      shift
      ;;
    --uninstall)
      UNINSTALL=1
      shift
      ;;
    --force)
      FORCE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! -d "$SOURCE" ]]; then
  echo "error: $SOURCE does not exist" >&2
  exit 1
fi

if [[ ${#TARGETS[@]} -eq 0 ]]; then
  HOME_DIR="$(user_home)"
  TARGETS=("$HOME_DIR/.claude/skills" "$HOME_DIR/.config/opencode/skills")
fi

# --- helpers -------------------------------------------------------------------------------------

# A directory this script created by copying. Only these are ever removed with rm -rf.
is_our_copy() {
  [[ -d "$1" && ! -L "$1" && -f "$1/$MARKER" ]]
}

copy_skill() {
  local skill="$1" link="$2"
  mkdir -p "$link"
  # Marker first: if the copy is interrupted, a re-run recognises and refreshes it.
  printf '%s\n' "$skill" > "$link/$MARKER"
  cp -R "$skill/." "$link/"
  LAST_ACTION="copied "
}

# Sets LAST_ACTION to "linked " or "copied ".
install_one() {
  local skill="$1" link="$2"

  if [[ "$LINK_MODE" == "copy" ]]; then
    copy_skill "$skill" "$link"
    return
  fi

  if [[ "$PLATFORM" != "windows" ]]; then
    ln -s "$skill" "$link"
    LAST_ACTION="linked "
    return
  fi

  # Windows: without these variables, MSYS and Cygwin make `ln -s` silently create a copy.
  # "nativestrict" requests a real symlink and fails loudly if Windows does not allow one.
  if MSYS=winsymlinks:nativestrict CYGWIN=winsymlinks:nativestrict ln -s "$skill" "$link" 2>/dev/null; then
    if [[ -L "$link" ]]; then
      LAST_ACTION="linked "
      return
    fi
    rm -rf "$link"   # ln produced a plain copy, which this call just created
  fi
  copy_skill "$skill" "$link"
  FELL_BACK=1
}

# --- main ----------------------------------------------------------------------------------------

installed=0
skipped=0
FELL_BACK=0
COPIES=0

for target in "${TARGETS[@]}"; do
  mkdir -p "$target"
  echo "Installing into $target"
  for skill in "$SOURCE"/*/; do
    [[ -f "$skill/SKILL.md" ]] || continue
    name="$(basename "$skill")"
    link="$target/$name"
    skill="${skill%/}"

    if [[ "$UNINSTALL" -eq 1 ]]; then
      if [[ -L "$link" ]]; then
        rm "$link"
        echo "  removed $name"
        installed=$((installed + 1))
      elif is_our_copy "$link"; then
        rm -rf "$link"
        echo "  removed $name (copy)"
        installed=$((installed + 1))
      fi
      continue
    fi

    if [[ -L "$link" ]]; then
      same=0
      [[ "$(readlink -f "$link")" == "$(readlink -f "$skill")" ]] && same=1
      if [[ "$same" -eq 1 && "$LINK_MODE" != "copy" ]]; then
        echo "  ok      $name"
        continue
      fi
      if [[ "$same" -eq 1 || "$FORCE" -eq 1 ]]; then
        rm "$link"
      else
        echo "  skip    $name (points elsewhere; use --force)" >&2
        skipped=$((skipped + 1))
        continue
      fi
    elif is_our_copy "$link"; then
      rm -rf "$link"   # refresh our own copy
    elif [[ -e "$link" ]]; then
      if [[ "$FORCE" -eq 1 ]]; then
        rm -rf "$link"
      else
        echo "  skip    $name (exists; use --force)" >&2
        skipped=$((skipped + 1))
        continue
      fi
    fi

    install_one "$skill" "$link"
    echo "  $LAST_ACTION $name"
    [[ "$LAST_ACTION" == "copied " ]] && COPIES=$((COPIES + 1))
    installed=$((installed + 1))
  done
done

if [[ "$UNINSTALL" -eq 1 ]]; then
  echo "Removed $installed links or copies."
else
  echo "Installed $installed skills."
  [[ "$skipped" -eq 0 ]] || echo "Skipped $skipped; rerun with --force to replace."
  if [[ "$COPIES" -gt 0 ]]; then
    echo "Note: $COPIES skills were copied, not linked, so they do not follow the repository."
    echo "      Re-run ./install.sh after pulling updates."
    if [[ "$FELL_BACK" -eq 1 ]]; then
      echo "      Windows refused symlinks. Turn on Developer Mode or use an Administrator shell to link instead."
    fi
  fi
fi
