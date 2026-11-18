from __future__ import annotations

import base64
import json

from conftest import load_script

figures_mod = load_script("skills/paper-plotting/scripts/validate_figures.py")
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Z1ZkAAAAASUVORK5CYII="
)


def make_project(tmp_path):
    root = tmp_path / "project"
    figures = root / "figures"
    figures.mkdir(parents=True)
    (figures / "fig.png").write_bytes(PNG)
    (figures / "info.json").write_text(json.dumps([{"name": "fig.png", "caption": "A figure."}]))
    return root, figures


def test_valid_manifest(tmp_path):
    root, figures = make_project(tmp_path)
    errors, warnings = figures_mod.check(root, figures)
    assert not errors
    assert not warnings


def test_missing_figure_fails(tmp_path):
    root, figures = make_project(tmp_path)
    (figures / "fig.png").unlink()
    errors, _ = figures_mod.check(root, figures)
    assert any("missing figure file" in error for error in errors)


def test_missing_caption_warns(tmp_path):
    root, figures = make_project(tmp_path)
    (figures / "info.json").write_text(json.dumps([{"name": "fig.png"}]))
    errors, warnings = figures_mod.check(root, figures)
    assert not errors
    assert any("no caption" in warning for warning in warnings)
