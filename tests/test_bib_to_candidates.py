from __future__ import annotations

import json

from conftest import run_script

SCRIPT = "skills/paper-literature-review/scripts/bib_to_candidates.py"

BIB = """@inproceedings{vaswani2017,
  title = {Attention Is All You Need},
  author = {Vaswani, Ashish and Shazeer, Noam},
  year = {2017}
}
@article{adamw,
  title = "Decoupled Weight Decay {Regularization}",
  author = "Ilya Loshchilov and Frank Hutter",
  year = 2019,
}
@misc{noidentity, title = {Mystery},}
@string{foo = "bar"}
"""


def test_bib_entries_become_targeted_candidates(tmp_path):
    bib = tmp_path / "references.bib"
    bib.write_text(BIB)
    out = tmp_path / "candidates.json"
    completed = run_script(SCRIPT, str(bib), "--out", str(out))
    assert completed.returncode == 0, completed.stderr

    candidates = json.loads(out.read_text())
    assert [c["title"] for c in candidates] == [
        "Attention Is All You Need",
        "Decoupled Weight Decay Regularization",
    ]
    assert all(c["targeted"] for c in candidates)
    assert candidates[0]["author"] == "Vaswani" and candidates[0]["year"] == 2017
    assert candidates[1]["author"] == "Loshchilov" and candidates[1]["year"] == 2019
    # An entry with neither year nor author cannot satisfy a targeted lookup.
    assert "noidentity" in completed.stderr


def test_empty_bib_fails(tmp_path):
    bib = tmp_path / "empty.bib"
    bib.write_text("@comment{nothing here}\n")
    assert run_script(SCRIPT, str(bib)).returncode == 1
