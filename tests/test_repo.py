from __future__ import annotations

import re

from conftest import ROOT


def test_skill_frontmatter_and_links():
    errors = []
    for skill in sorted((ROOT / "skills").iterdir()):
        path = skill / "SKILL.md"
        if not path.exists():
            errors.append(f"missing {path}")
            continue
        text = path.read_text()
        parts = text.split("---", 2)
        if len(parts) < 3:
            errors.append(f"bad frontmatter {path}")
            continue
        frontmatter, body = parts[1], parts[2]
        name = re.search(r"^name:\s*(.+)$", frontmatter, re.M)
        desc = re.search(r"^description:\s*(.+)$", frontmatter, re.M)
        if not name or name.group(1).strip() != skill.name:
            errors.append(f"name mismatch {path}")
        if not desc or len(desc.group(1).strip()) < 80:
            errors.append(f"description too short {path}")
        for match in re.finditer(r"`((?:scripts|references|assets)/[^`\s]+)`", body):
            target = skill / match.group(1).rstrip(".,)")
            if not target.exists():
                errors.append(f"missing referenced path {target}")

    for path in [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md")), *sorted((ROOT / "skills").glob("*/SKILL.md"))]:
        for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
            target = match.group(1).split("#")[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (path.parent / target).resolve().exists():
                errors.append(f"broken link {path}: {target}")

    assert not errors, "\n".join(errors)


def test_markdown_fences_balanced():
    bad = []
    for path in list(ROOT.rglob("*.md")) + [ROOT / "llms.txt"]:
        if ".git" in path.parts:
            continue
        fences = sum(1 for line in path.read_text().splitlines() if line.strip().startswith("```"))
        if fences % 2:
            bad.append(str(path))
    assert not bad, bad


def test_readme_covers_all_skills_and_templates():
    readme = (ROOT / "README.md").read_text()
    for skill in (ROOT / "skills").iterdir():
        assert f"skills/{skill.name}/SKILL.md" in readme
    for venue in ("cvpr2025", "iclr2025", "ieeeconf", "arxiv",
                  "osdi2026", "sosp2026", "asplos2027", "nsdi2027"):
        assert venue in (ROOT / "skills/research-template/SKILL.md").read_text()


def test_every_skill_uses_the_research_prefix():
    names = sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir())
    assert names, "no skills found"
    wrong = [n for n in names if not n.startswith("research-")]
    assert not wrong, f"skills missing the research- prefix: {wrong}"
