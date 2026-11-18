#!/usr/bin/env bash
# Install PaperOrchestra Skills by symlinking each skill into an agent's skills directory.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$ROOT/skills"
UNINSTALL=0
FORCE=0
TARGETS=()

usage() {
  cat <<'EOF'
Usage: ./install.sh [options]

Options:
  --target DIR   Install into DIR (repeatable). Defaults to:
                 ~/.claude/skills and ~/.config/opencode/skills
  --uninstall    Remove links created by this script
  --force        Replace existing files or links
  -h, --help     Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      [[ $# -ge 2 ]] || { echo "error: --target needs a directory" >&2; exit 2; }
      TARGETS+=("$2")
      shift 2
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
  TARGETS=("$HOME/.claude/skills" "$HOME/.config/opencode/skills")
fi

installed=0
skipped=0

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
      fi
      continue
    fi

    if [[ -L "$link" ]]; then
      if [[ "$(readlink -f "$link")" == "$(readlink -f "$skill")" ]]; then
        echo "  ok      $name"
        continue
      fi
      if [[ "$FORCE" -eq 1 ]]; then
        rm "$link"
      else
        echo "  skip    $name (points elsewhere; use --force)" >&2
        skipped=$((skipped + 1))
        continue
      fi
    elif [[ -e "$link" ]]; then
      if [[ "$FORCE" -eq 1 ]]; then
        rm -rf "$link"
      else
        echo "  skip    $name (exists; use --force)" >&2
        skipped=$((skipped + 1))
        continue
      fi
    fi

    ln -s "$skill" "$link"
    echo "  linked  $name"
    installed=$((installed + 1))
  done
done

if [[ "$UNINSTALL" -eq 1 ]]; then
  echo "Removed $installed links."
else
  echo "Installed $installed skills."
  [[ "$skipped" -eq 0 ]] || echo "Skipped $skipped; rerun with --force to replace."
fi
