from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_script(relative_path: str):
    """Load a skill script by path, avoiding name collisions between scripts."""
    path = ROOT / relative_path
    module_name = "skill_" + relative_path.replace("/", "_").replace(".py", "").replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def run_script(relative_path: str, *args: str, cwd: Path | None = None):
    return subprocess.run(
        [sys.executable, str(ROOT / relative_path), *args],
        cwd=str(cwd or ROOT),
        capture_output=True,
        text=True,
    )
