from __future__ import annotations

import copy
import json

from conftest import ROOT, load_script

validator = load_script("skills/paper-outline/scripts/validate_outline.py")
OUTLINE = json.loads((ROOT / "tests/fixtures/outline.json").read_text())


def test_valid_outline():
    errors, warnings = validator.validate(copy.deepcopy(OUTLINE))
    assert not errors
    assert any("citation hints" in warning for warning in warnings)


def test_missing_keys_fail():
    errors, _ = validator.validate({"plotting_plan": []})
    assert any("intro_related_work_plan" in error for error in errors)
    assert any("section_plan" in error for error in errors)


def test_bad_aspect_ratio_fails():
    data = copy.deepcopy(OUTLINE)
    data["plotting_plan"][0]["aspect_ratio"] = "17:9"
    errors, _ = validator.validate(data)
    assert any("aspect_ratio" in error for error in errors)


def test_missing_cluster_fails():
    data = copy.deepcopy(OUTLINE)
    data["intro_related_work_plan"]["related_work_strategy"]["subsections"] = []
    errors, _ = validator.validate(data)
    assert any("subsections" in error for error in errors)
