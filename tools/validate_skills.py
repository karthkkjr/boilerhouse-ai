#!/usr/bin/env python3
"""Validate every skills/<name>/SKILL.md against the agentskills.io rules.

Stdlib only. Logs -> stderr, JSON report -> stdout. Exit 1 if any skill fails.
Usage: python3 tools/validate_skills.py [skills_dir]
"""
import json
import os
import re
import sys

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")  # no leading/trailing/double hyphens


def parse_frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fm = {}
    for line in text[3:end].splitlines():
        if line and not line.startswith((" ", "\t")) and ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


def check_skill(path):
    errs, name = [], os.path.basename(path)
    if not NAME_RE.match(name) or len(name) > 64:
        errs.append(f"folder '{name}' must be 1-64 chars, lowercase alphanumeric + single hyphens")
    md = os.path.join(path, "SKILL.md")
    if not os.path.isfile(md):
        return name, ["missing SKILL.md"]
    fm = parse_frontmatter(open(md, encoding="utf-8").read())
    if fm is None:
        return name, ["SKILL.md missing YAML frontmatter (--- ... ---)"]
    if fm.get("name") != name:
        errs.append(f"frontmatter name '{fm.get('name')}' != folder '{name}'")
    desc = fm.get("description", "")
    if not 1 <= len(desc) <= 1024:
        errs.append(f"description length {len(desc)} not in 1-1024")
    if "compatibility" in fm and not 1 <= len(fm["compatibility"]) <= 500:
        errs.append("compatibility must be 1-500 chars")
    sdir = os.path.join(path, "scripts")
    if os.path.isdir(sdir):
        for f in sorted(os.listdir(sdir)):
            fp = os.path.join(sdir, f)
            if not f.endswith(".py"):
                continue
            first = open(fp, encoding="utf-8").readline().rstrip()
            if first != "#!/usr/bin/env python3":
                errs.append(f"scripts/{f}: bad shebang '{first}'")
            if not os.access(fp, os.X_OK):
                errs.append(f"scripts/{f}: not executable (chmod +x)")
    return name, errs


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills")
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        print(f"skills dir not found: {root}", file=sys.stderr)
        print(json.dumps({"status": "error", "error": f"not found: {root}"}))
        sys.exit(1)
    report = {}
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d)
        if os.path.isdir(p) and not d.startswith((".", "_")):
            name, errs = check_skill(p)
            report[name] = errs
            print(f"{'PASS' if not errs else 'FAIL'} {name}" + "".join(f"\n  - {e}" for e in errs), file=sys.stderr)
    ok = bool(report) and all(not e for e in report.values())
    print(json.dumps({"status": "ok" if ok else "error", "skills": report}, indent=2))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
