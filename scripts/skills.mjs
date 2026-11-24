#!/usr/bin/env node
// Zero-dependency tooling for this repo.
//   node scripts/skills.mjs sync        regenerate every harness manifest
//   node scripts/skills.mjs check       validate skills and fail if manifests are stale (CI)
//   node scripts/skills.mjs new <name>  scaffold skills/<name>/SKILL.md
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const cfg = JSON.parse(fs.readFileSync(path.join(root, "plugin.config.json"), "utf8"));
const NAME_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;

function frontmatter(text) {
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) return null;
  const out = {};
  const lines = m[1].split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const kv = lines[i].match(/^([A-Za-z_-]+):\s*(.*)$/);
    if (!kv) continue;
    let v = kv[2].trim();
    if (/^[>|][-+]?$/.test(v)) {
      const parts = [];
      while (i + 1 < lines.length && /^\s+\S/.test(lines[i + 1])) parts.push(lines[++i].trim());
      v = parts.join(" ");
    }
    if (/^[^"'>|]/.test(v) && /:\s|\s#/.test(v)) out.__yamlError = kv[1];
    out[kv[1]] = v.replace(/^(["'])([\s\S]*)\1$/, "$2");
  }
  return out;
}

function loadSkills() {
  const dir = path.join(root, "skills");
  const skills = [], errors = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (!e.isDirectory()) continue;
    const file = path.join(dir, e.name, "SKILL.md");
    if (!fs.existsSync(file)) { errors.push(`skills/${e.name}: missing SKILL.md`); continue; }
    const fm = frontmatter(fs.readFileSync(file, "utf8"));
    if (!fm) { errors.push(`skills/${e.name}: SKILL.md has no frontmatter`); continue; }
    if (fm.__yamlError) errors.push(`skills/${e.name}: unquoted "${fm.__yamlError}" contains ": " or " #" (invalid YAML; strict parsers drop the skill). Wrap it in double quotes`);
    if (fm.name !== e.name) errors.push(`skills/${e.name}: frontmatter name "${fm.name}" must equal the directory name`);
    if (!NAME_RE.test(e.name) || e.name.length > 64) errors.push(`skills/${e.name}: name must be lowercase-hyphenated, <= 64 chars`);
    if (!fm.description) errors.push(`skills/${e.name}: description is required`);
    else if (fm.description.length > 1024) errors.push(`skills/${e.name}: description exceeds 1024 chars`);
    const lines = fs.readFileSync(file, "utf8").split("\n").length;
    if (lines > 500) errors.push(`skills/${e.name}: SKILL.md is ${lines} lines (max 500); move detail to references/`);
    skills.push({ name: e.name, description: fm.description || "" });
  }
  return { skills: skills.sort((a, b) => a.name.localeCompare(b.name)), errors };
}

function manifests(skills) {
  const base = { name: cfg.name, version: cfg.version, description: cfg.description,
    author: cfg.author, repository: cfg.repository, license: cfg.license };
  const bundle = { name: cfg.name, source: "./", description: cfg.description, version: cfg.version };
  const owner = cfg.author;
  return {
    // Claude Code: plugin + marketplace (bundle, then one entry per skill so users can pick one)
    ".claude-plugin/plugin.json": { ...base, keywords: cfg.keywords, skills: "./skills/" },
    ".claude-plugin/marketplace.json": {
      name: cfg.name, description: cfg.description, owner,
      plugins: [bundle, ...skills.map((s) => ({
        name: s.name, source: "./", strict: false, description: s.description,
        version: cfg.version, skills: [`./skills/${s.name}`] }))],
    },
    // Codex: plugin manifest + marketplace catalog
    ".codex-plugin/plugin.json": { ...base, keywords: cfg.keywords, skills: "./skills/",
      interface: { displayName: cfg.displayName, shortDescription: cfg.description, category: cfg.category } },
    ".agents/plugins/marketplace.json": {
      name: cfg.name, interface: { displayName: cfg.displayName },
      plugins: [{ name: cfg.name, source: { source: "local", path: "./" },
        policy: { installation: "AVAILABLE", authentication: "ON_INSTALL" }, category: cfg.category }],
    },
    // Agent Plugins 1.0 package (read by GitHub Copilot and others) + Copilot marketplace
    "plugin.json": { $schema: "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
      ...base, keywords: cfg.keywords },
    "marketplace.json": {
      name: cfg.name, owner, metadata: { description: cfg.description },
      plugins: [bundle, ...skills.map((s) => ({
        name: s.name, source: `./skills/${s.name}`, description: s.description, version: cfg.version }))],
    },
  };
}

const render = (o) => JSON.stringify(o, null, 2) + "\n";
const [cmd, arg] = process.argv.slice(2);

if (cmd === "sync" || cmd === "check") {
  const { skills, errors } = loadSkills();
  if (!skills.length) errors.push("no skills found under skills/");
  const out = manifests(skills);
  const stale = [];
  for (const [rel, obj] of Object.entries(out)) {
    const file = path.join(root, rel), next = render(obj);
    if (cmd === "sync") { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, next); }
    else if (!fs.existsSync(file) || fs.readFileSync(file, "utf8") !== next) stale.push(rel);
  }
  stale.forEach((f) => errors.push(`${f} is stale: run "node scripts/skills.mjs sync"`));
  if (errors.length) { console.error(errors.map((e) => "✗ " + e).join("\n")); process.exit(1); }
  console.log(`✓ ${skills.length} skill(s): ${skills.map((s) => s.name).join(", ")}`);
  console.log(cmd === "sync" ? `✓ wrote ${Object.keys(out).length} manifests` : "✓ manifests up to date");
} else if (cmd === "new") {
  if (!arg || !NAME_RE.test(arg)) { console.error("usage: skills.mjs new <lowercase-hyphen-name>"); process.exit(1); }
  const dest = path.join(root, "skills", arg);
  if (fs.existsSync(dest)) { console.error(`skills/${arg} already exists`); process.exit(1); }
  fs.mkdirSync(dest, { recursive: true });
  fs.writeFileSync(path.join(dest, "SKILL.md"),
    fs.readFileSync(path.join(root, "templates/skill/SKILL.md"), "utf8").replaceAll("__NAME__", arg));
  console.log(`✓ created skills/${arg}/SKILL.md. Edit it, then run: node scripts/skills.mjs sync`);
} else {
  console.error("usage: skills.mjs <sync|check|new <name>>"); process.exit(1);
}
