from __future__ import annotations

from conftest import ROOT, load_script

aggregate_mod = load_script("skills/paper-content-refinement/scripts/aggregate_reviews.py")
decide_mod = load_script("skills/paper-content-refinement/scripts/decide_revision.py")
REVIEWS = ROOT / "tests/fixtures/reviews"


def load_reviews():
    return [aggregate_mod.load(path) for path in sorted(REVIEWS.glob("*.json"))]


def test_aggregate_mean_and_majority():
    result = aggregate_mod.aggregate(load_reviews(), stat="mean")
    assert result["Overall"] == 6.33
    assert result["Decision"] == "Accept"
    assert result["ensemble"]["count"] == 3
    assert result["ensemble"]["axes"]["Overall"]["median"] == 6.0
    assert result["Strengths"] == ["clear method", "solid evaluation"]
    assert result["Weaknesses"] == ["weak baseline", "missing ablation"]
    assert result["Questions"] == ["what is the latency?"]


def test_aggregate_median():
    result = aggregate_mod.aggregate(load_reviews(), stat="median")
    assert result["Overall"] == 6.0


def test_decide_revision_rules():
    assert decide_mod.decide({"Overall": 6}, {"Overall": 7})["decision"] == "ACCEPT"
    assert decide_mod.decide({"Overall": 6}, {"Overall": 5})["decision"] == "REJECT"

    tie_gain = decide_mod.decide({"Overall": 6, "Quality": 2}, {"Overall": 6, "Quality": 3})
    assert tie_gain["decision"] == "ACCEPT"

    tie_drop = decide_mod.decide({"Overall": 6, "Quality": 3}, {"Overall": 6, "Quality": 2})
    assert tie_drop["decision"] == "REJECT"
