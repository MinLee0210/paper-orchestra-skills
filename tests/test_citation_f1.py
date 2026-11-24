from __future__ import annotations

import json

from conftest import load_script

f1_mod = load_script("skills/research-evaluation/scripts/citation_f1.py")


def write(path, data):
    path.write_text(json.dumps(data))
    return path


def test_overall_and_p0_p1(tmp_path):
    gt = write(
        tmp_path / "gt.json",
        [
            {"title": "Attention Is All You Need", "paper_id": "p1", "priority": "P0"},
            {"title": "Longformer", "paper_id": "p2", "priority": "P1"},
            {"title": "Big Bird", "paper_id": "p3", "priority": "P1"},
        ],
    )
    gen = write(
        tmp_path / "gen.json",
        [
            {"title": "Attention Is All You Need", "paper_id": "p1"},
            {"title": "An Invented Paper", "paper_id": "px"},
        ],
    )
    gt_records, _ = f1_mod.load_records(gt)
    gen_records, _ = f1_mod.load_records(gen)
    pairs = f1_mod.match(gt_records, gen_records)
    metrics = f1_mod.prf(len(pairs), len(gen_records), len(gt_records))
    assert len(pairs) == 1
    assert metrics["precision"] == 0.5
    assert round(metrics["recall"], 4) == round(1 / 3, 4)
    assert round(metrics["f1"], 4) == 0.4
