from __future__ import annotations

import json

from conftest import ROOT

EXAMPLE = ROOT / "examples/paper-project"


def test_demo_outputs_exist():
    assert (EXAMPLE / "final_paper.pdf").stat().st_size > 10_000
    assert (EXAMPLE / "final_paper.tex").exists()
    assert (EXAMPLE / "figures/info.json").exists()
    assert (EXAMPLE / "content_refinement_workdir/peer_reviews/review_v0.json").exists()
    assert (EXAMPLE / "content_refinement_workdir/peer_reviews/review_v1.json").exists()
    assert (EXAMPLE / "content_refinement_workdir/peer_reviews/decision_v1.json").exists()


def test_run_report_records_all_stages():
    report = json.loads((EXAMPLE / "run_report.json").read_text())
    stages = report["stages"]
    for stage in ("inputs", "outline", "literature", "plotting", "section_writing", "refinement"):
        assert stages[stage]["status"] == "complete"
    assert stages["evaluation"]["status"] == "skipped"
    assert any("cached" in warning for warning in report["warnings"])


def test_final_tex_cites_verified_keys():
    import re

    tex = (EXAMPLE / "final_paper.tex").read_text()
    citation_map = json.loads((EXAMPLE / "literature_agent_output/citation_map.json").read_text())
    cited = set()
    for group in re.findall(r"\\cite\{([^}]*)\}", tex):
        cited.update(key.strip() for key in group.split(",") if key.strip())
    assert cited
    assert cited <= set(citation_map)
    assert len(cited) >= 10
