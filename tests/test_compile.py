from __future__ import annotations

import shutil

import pytest

from conftest import ROOT, run_script
pdflatex = shutil.which("pdflatex")


@pytest.mark.skipif(pdflatex is None, reason="pdflatex not installed")
def test_example_template_compiles(tmp_path):
    source = ROOT / "examples/paper-project/latex_template"
    target = tmp_path / "latex_template"
    shutil.copytree(source, target)
    completed = run_script(
        "skills/research-content-refinement/scripts/compile_latex.py",
        str(target),
        "--name", "template",
        "--no-bib",
        "--timeout", "60",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert (target / "template.pdf").exists()


@pytest.mark.skipif(pdflatex is None, reason="pdflatex not installed")
def test_compile_resolves_citations(tmp_path):
    (tmp_path / "paper.tex").write_text(
        "\\documentclass{article}\n"
        "\\begin{document}\n"
        "Attention~\\cite{vaswani2017}.\n"
        "\\bibliographystyle{plain}\n"
        "\\bibliography{references}\n"
        "\\end{document}\n"
    )
    (tmp_path / "references.bib").write_text(
        "@inproceedings{vaswani2017,\n"
        "  title={Attention Is All You Need},\n"
        "  author={Vaswani, Ashish},\n"
        "  booktitle={NeurIPS},\n"
        "  year={2017}\n"
        "}\n"
    )
    completed = run_script(
        "skills/research-content-refinement/scripts/compile_latex.py",
        str(tmp_path),
        "--name", "paper",
        "--timeout", "60",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Undefined citations" not in completed.stdout
