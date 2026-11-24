from __future__ import annotations

import shutil
from pathlib import Path

from conftest import ROOT, load_script, run_script

validator = load_script("skills/research-inputs/scripts/validate_inputs.py")
EXAMPLE = ROOT / "examples/paper-project"


def test_clean_example_passes():
    result = validator.validate(EXAMPLE)
    assert result["ok"], result["errors"]


def test_leakage_is_blocking(tmp_path):
    project = tmp_path / "project"
    shutil.copytree(EXAMPLE, project)
    idea = project / "raw_materials/idea.md"
    idea.write_text(
        idea.read_text()
        + "\nSmith et al. (2023) \\cite{foo}; by John Doe achieves 95.2% on the benchmark.\n"
    )
    result = validator.validate(project)
    assert not result["ok"]
    messages = " ".join(item["message"] for item in result["errors"])
    assert "LaTeX citation" in messages
    assert "et al." in messages
    assert "named author" in messages
    assert "percentage result" in messages
    assert "result claim" in messages


def test_source_title_is_blocking(tmp_path):
    project = tmp_path / "project"
    shutil.copytree(EXAMPLE, project)
    idea = project / "raw_materials/idea.md"
    idea.write_text(idea.read_text() + "\nConfidence-Aware Token Routing\n")
    result = validator.validate(project, source_title="Confidence-Aware Token Routing")
    assert not result["ok"]
    assert any("source paper title" in item["message"] for item in result["errors"])


def test_warn_only_cli(tmp_path):
    project = tmp_path / "project"
    shutil.copytree(EXAMPLE, project)
    idea = project / "raw_materials/idea.md"
    idea.write_text(idea.read_text() + "\nSmith et al. (2023) achieves 95.2%.\n")
    completed = run_script("skills/research-inputs/scripts/validate_inputs.py", str(project), "--warn-only")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "WARNING" in completed.stdout


def test_benign_number_phrases_are_not_blocked(tmp_path):
    project = tmp_path / "project"
    shutil.copytree(EXAMPLE, project)
    idea = project / "raw_materials/idea.md"
    idea.write_text(idea.read_text() + "\nThe model has 6 layers and maps 128 tokens to a summary.\n")
    result = validator.validate(project)
    assert result["ok"], result["errors"]


def test_improvement_without_percent_is_blocked(tmp_path):
    project = tmp_path / "project"
    shutil.copytree(EXAMPLE, project)
    idea = project / "raw_materials/idea.md"
    idea.write_text(idea.read_text() + "\nThe method improves by 3.1 over the baseline.\n")
    result = validator.validate(project)
    assert not result["ok"]
    assert any("result claim" in item["message"] for item in result["errors"])
