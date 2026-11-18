from __future__ import annotations

import json

from conftest import ROOT, load_script

lint_mod = load_script("skills/paper-section-writing/scripts/lint_latex.py")
TEMPLATE = ROOT / "examples/paper-project/latex_template/template.tex"


def test_clean_template_passes():
    errors, _ = lint_mod.lint(TEMPLATE, None)
    assert not errors


def test_mismatched_environment_fails(tmp_path):
    path = tmp_path / "paper.tex"
    path.write_text(
        "\\documentclass{article}\n\\begin{document}\n"
        "\\begin{figure*}\n\\end{figure}\n\\end{document}\n"
    )
    errors, _ = lint_mod.lint(path, None)
    assert any("closes" in error or "never closed" in error for error in errors)


def test_unknown_citation_fails(tmp_path):
    path = tmp_path / "paper.tex"
    path.write_text(
        "\\documentclass{article}\n\\begin{document}\n"
        "\\cite{missing}\n\\end{document}\n"
    )
    citation_map = tmp_path / "citation_map.json"
    citation_map.write_text(json.dumps({"known": {"title": "Known"}}))
    errors, _ = lint_mod.lint(path, citation_map)
    assert any("not in citation map" in error for error in errors)
