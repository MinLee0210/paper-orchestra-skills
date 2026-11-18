from __future__ import annotations

import shutil

from conftest import ROOT, run_script

EXAMPLE = ROOT / "examples/paper-project"
ARTIFACTS = [
    "outline.json",
    "literature_agent_output",
    "figures",
    "plotting_results.json",
    "latex_writeup",
    "content_refinement_workdir",
    "final_paper.tex",
    "final_paper.pdf",
    "metrics",
    "run_report.json",
]


def clean_project(tmp_path):
    project = tmp_path / "project"
    shutil.copytree(EXAMPLE, project)
    for name in ARTIFACTS:
        target = project / name
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    return project


def test_fresh_project_starts_at_outline(tmp_path):
    project = clean_project(tmp_path)
    completed = run_script("skills/paper-orchestra/scripts/pipeline_status.py", str(project))
    assert completed.returncode == 2
    assert "Stage 1" in completed.stdout


def test_outline_advances_to_literature(tmp_path):
    project = clean_project(tmp_path)
    shutil.copy(ROOT / "tests/fixtures/outline.json", project / "outline.json")
    completed = run_script("skills/paper-orchestra/scripts/pipeline_status.py", str(project))
    assert completed.returncode == 2
    assert "Stage 2a" in completed.stdout


def test_complete_example_reaches_final_pdf():
    completed = run_script("skills/paper-orchestra/scripts/pipeline_status.py", str(EXAMPLE))
    assert completed.returncode == 0
    assert "Pipeline complete" in completed.stdout
