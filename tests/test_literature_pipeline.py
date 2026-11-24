from __future__ import annotations

import json

from conftest import ROOT, run_script

REGISTRY = ROOT / "tests/fixtures/registry.json"
OUTLINE = ROOT / "tests/fixtures/outline.json"


def test_build_inject_and_validate(tmp_path):
    out = tmp_path / "literature_agent_output"
    built = run_script(
        "skills/research-literature-review/scripts/build_bib.py",
        "--registry", str(REGISTRY),
        "--out", str(out),
    )
    assert built.returncode == 0, built.stderr

    injected = run_script(
        "skills/research-literature-review/scripts/inject_citations.py",
        "--outline", str(OUTLINE),
        "--registry", str(REGISTRY),
        "--out", str(out / "outline_v1.json"),
    )
    assert injected.returncode == 0, injected.stderr

    validated = run_script(
        "skills/research-literature-review/scripts/validate_literature.py",
        "--dir", str(out),
        "--outline", str(out / "outline_v1.json"),
        "--registry", str(REGISTRY),
        "--min-papers", "3",
    )
    assert validated.returncode == 0, validated.stdout + validated.stderr
    assert "Checked 3 papers" in validated.stdout

    bib = (out / "references.bib").read_text()
    for key in ("Vaswani2017Attention", "Child2019Generating", "Jang2017Categorical"):
        assert key in bib

    outline = json.loads((out / "outline_v1.json").read_text())
    intro = outline["intro_related_work_plan"]["introduction_strategy"]
    cluster = outline["intro_related_work_plan"]["related_work_strategy"]["subsections"][0]
    method = outline["section_plan"][1]["subsections"][0]
    assert intro["citation_candidates"] == ["Vaswani2017Attention"]
    assert cluster["citation_candidates"] == ["Child2019Generating"]
    assert method["citation_candidates"] == ["Jang2017Categorical"]
    assert "citation_hints" not in method


def test_missing_cluster_is_reported(tmp_path):
    registry = json.loads(REGISTRY.read_text())
    registry = [paper for paper in registry if paper["found_in_section"] != "Related Work: 2.1 Fixed Sparse Patterns"]
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(registry))
    out = tmp_path / "out"
    completed = run_script(
        "skills/research-literature-review/scripts/inject_citations.py",
        "--outline", str(OUTLINE),
        "--registry", str(path),
        "--out", str(out / "outline_v1.json"),
    )
    assert completed.returncode == 0
    assert "Related Work: 2.1 Fixed Sparse Patterns" in completed.stdout
