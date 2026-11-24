"""Guards against cross-skill contradictions that were found and fixed once."""
from __future__ import annotations

from conftest import ROOT


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_reviewer_caps_defined_in_one_place():
    refinement = read("skills/paper-content-refinement/references/reviewer-rubric.md")
    evaluation = read("skills/paper-evaluation/references/agentreview.md")
    assert "cap Presentation at 2" in refinement and "caps Soundness at 2" in refinement
    for phrase in ("Presentation at 2", "Soundness at 2"):
        assert phrase not in evaluation
    assert "reviewer-rubric.md" in evaluation


def test_tie_handling_is_consistent():
    text = read("skills/paper-content-refinement/SKILL.md")
    assert "gains >= drops → accept and continue" not in text
    assert "gains >= drops → accept the revision, then stop" in text
    assert "a tie counts as a stall" in text


def test_tabularx_exception_is_declared_where_packages_are_restricted():
    assert "tabularx" in read("skills/paper-section-writing/SKILL.md")
    assert "tabularx" in read("skills/paper-template/SKILL.md")
    assert "tabularx" in read("skills/paper-content-refinement/SKILL.md")


def test_autoresearch_does_not_override_integrity_gates():
    text = read("skills/research-autoresearch/SKILL.md")
    assert "Autonomy boundary" in text
    assert "**Never stop.**" not in text
    assert "adapt and keep going — produce the best draft" not in text


def test_user_bib_is_reverified_not_merged():
    assert "never copied into the paper" in read("skills/paper-orchestra/SKILL.md")
    assert (ROOT / "skills/paper-literature-review/scripts/bib_to_candidates.py").exists()
    assert "bib_to_candidates.py" in read("skills/paper-literature-review/SKILL.md")


def test_trigger_descriptions_do_not_claim_everything():
    assert "for all systems conference paper writing" not in read("skills/research-systems-paper-writing/SKILL.md")
    assert "produces research presentations and papers" not in read("skills/research-autoresearch/SKILL.md")
