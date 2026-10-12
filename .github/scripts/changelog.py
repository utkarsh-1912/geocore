"""
GeoCore changelog tool. website/_content/geocore/changelog.md is the single source of release history: the docs
page (/docs/changelog), the GitHub release notes and the download page's "Release notes" all come from it.

    python .github/scripts/changelog.py draft [--since v1.0.0] [--to HEAD] [--write]
        Describe what changed since the last release tag: calculators, catalogue calculations and methods, GeoAI
        tools, local API routes, docs pages, dependencies and the groundhog version, plus files changed per area.
        Compares against the working tree unless --to is given. --write puts the result in the Unreleased section
        between the auto markers (re-running replaces it); edit it into the hand-written lists before releasing.

    python .github/scripts/changelog.py release v1.1.0 [--date 2026-10-20] [--build]
        Turn "## Unreleased" into "## v1.1.0 — <date>" and start a new empty Unreleased section. Refuses an empty
        section or one that still holds an unreviewed auto-draft. --build regenerates the website afterwards.

    python .github/scripts/changelog.py notes v1.1.0
        Print that version's section as GitHub release notes (used by .github/workflows/release.yml).

    python .github/scripts/changelog.py sync
        Refresh the generated docs page (website/_content/pages/changelog.md) after editing the changelog by hand.

    python .github/scripts/changelog.py check v1.1.0
        Fail unless the changelog has a non-empty, reviewed section for the version (release workflow gate).

Commit messages are not used: they do not describe the changes, so the draft is built from the code itself.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parents[2]
CHANGELOG = ROOT / "website" / "_content" / "geocore" / "changelog.md"
REPO_URL = "https://github.com/utkarsh-1912/geocore"

UNRELEASED = "## Unreleased"
AUTO_START = "<!-- changelog:auto:start -->"
AUTO_END = "<!-- changelog:auto:end -->"
VERSION_RE = re.compile(r"^v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
SECTION_RE = re.compile(r"^## (Unreleased|v\d+\.\d+\.\d+\S*)(?:\s+[—-]\s+(\d{4}-\d{2}-\d{2}))?\s*$", re.M)

# Files changed are grouped under these areas, first match wins.
AREAS: List[Tuple[str, str]] = [
    ("python-backend/core/geoai/", "GeoAI"),
    ("python-backend/core/standards/", "Indian Standard (BIS) calculations"),
    ("python-backend/core/catalogue/", "Calculation catalogue"),
    ("python-backend/core/project/", "Project model and reports"),
    ("python-backend/tests/", "Backend tests"),
    ("python-backend/", "Backend and calculations"),
    ("electron-app/src/features/copilot/", "GeoAI chat (app)"),
    ("electron-app/src/features/calculations/", "Calculator forms and guides (app)"),
    ("electron-app/electron/", "Desktop shell (Electron)"),
    ("electron-app/", "Desktop app (other)"),
    ("website/_content/geocore/", "Documentation (GeoCore pages)"),
    ("website/_build/", "Documentation build"),
    ("website/_templates/", "Website pages"),
    ("website/assets/", "Website pages"),
    ("website/", "Website pages"),
    (".github/", "Release and CI"),
    ("stage/", "Planning notes"),
]
GENERATED = ("website/docs/", "website/_content/groundhog/", "website/_content/pages/")


# --------------------------------------------------------------------------- git / file access

def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True,
                          encoding="utf-8").stdout


def last_tag() -> Optional[str]:
    tags = [t for t in _git("tag", "--list", "v*", "--sort=-v:refname").split() if VERSION_RE.match(t)]
    return tags[0] if tags else None


def _read(path: str, ref: Optional[str]) -> Optional[str]:
    """File text at a git ref, or in the working tree when ref is None; None if it does not exist."""
    if ref is None:
        p = ROOT / path
        return p.read_text(encoding="utf-8") if p.is_file() else None
    try:
        return _git("show", f"{ref}:{path}")
    except subprocess.CalledProcessError:
        return None


def _list(pattern: str, ref: Optional[str]) -> List[str]:
    """Repo paths matching a glob (working tree) or a git pathspec (at ref)."""
    if ref is None:
        return sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in ROOT.glob(pattern))
    return sorted(_git("ls-tree", "-r", "--name-only", ref, "--", pattern.split("*")[0]).split())


def changed_files(since: str, to: Optional[str]) -> List[Tuple[str, str]]:
    """(status, path) between two refs, or between a ref and the working tree (including new files)."""
    out = _git("diff", "--name-status", since, *([to] if to else []))
    rows = [(ln.split("\t")[0][0], ln.split("\t")[-1]) for ln in out.splitlines() if ln.strip()]
    if to is None:
        rows += [("A", p) for p in _git("ls-files", "--others", "--exclude-standard").splitlines() if p]
    return rows


# --------------------------------------------------------------------------- what the code contains

def calculators(ref: Optional[str]) -> Dict[str, str]:
    """App calculators (id -> title) from the classic navigation list."""
    text = _read("electron-app/src/config/geotechnicalModules.js", ref) or ""
    return {m.group(1): re.sub(r"\\(.)", r"\1", m.group(2))
            for m in re.finditer(r"\{\s*id:\s*'([^']+)',\s*title:\s*'((?:[^'\\]|\\.)+)'\s*\}", text)}


def catalogue(ref: Optional[str]) -> Tuple[Dict[str, str], Set[Tuple[str, str]]]:
    """Catalogue calculations (id -> title) and (calculation, method label) pairs."""
    calcs: Dict[str, str] = {}
    methods: Set[Tuple[str, str]] = set()
    for path in _list("python-backend/core/catalogue/data/*.json", ref):
        if not path.endswith(".json") or path.endswith("_internal.json"):
            continue
        data = json.loads(_read(path, ref) or "{}")
        for c in data.get("calculations", []):
            calcs[c["id"]] = c.get("title", c["id"])
            for m in c.get("methods", []):
                methods.add((c.get("title", c["id"]), m.get("label", m.get("id", ""))))
    return calcs, methods


def geoai_tools(ref: Optional[str]) -> Set[str]:
    names: Set[str] = set()
    for path in _list("python-backend/core/geoai/*.py", ref):
        if path.endswith(".py"):
            names |= set(re.findall(r"geoai_tool\(\s*name=\"(\w+)\"", _read(path, ref) or ""))
    return names


def api_routes(ref: Optional[str]) -> Set[str]:
    routes: Set[str] = set()
    for path in _list("python-backend/*.py", ref) + _list("python-backend/core/*.py", ref) + \
            _list("python-backend/core/*/api.py", ref):
        if not path.endswith(".py"):
            continue
        text = _read(path, ref) or ""
        prefix = re.search(r"APIRouter\([^)]*prefix=\"([^\"]*)\"", text)
        for verb, route in re.findall(r"@\w+\.(get|post|put|delete|patch)\(\s*\"([^\"]+)\"", text):
            routes.add(f"{verb.upper()} {(prefix.group(1) if prefix else '')}{route}")
    return routes


def doc_pages(ref: Optional[str]) -> Dict[str, str]:
    pages: Dict[str, str] = {}
    for path in _list("website/_content/geocore/*.md", ref):
        if path.endswith(".md"):
            m = re.search(r"^title:\s*(.+)$", _read(path, ref) or "", re.M)
            pages[path] = m.group(1).strip() if m else Path(path).stem
    return pages


def requirements(ref: Optional[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for ln in (_read("python-backend/requirements.txt", ref) or "").splitlines():
        ln = ln.split("#")[0].strip()
        if ln:
            name = re.split(r"[<>=!~ @\[;]", ln, maxsplit=1)[0].lower()
            out[name] = ln
    pkg = json.loads(_read("electron-app/package.json", ref) or "{}")
    for section in ("dependencies", "devDependencies"):
        for name, ver in pkg.get(section, {}).items():
            out[f"npm:{name}"] = f"{name} {ver}"
    return out


def groundhog_version(ref: Optional[str]) -> Optional[str]:
    data = json.loads(_read("python-backend/core/function_manifest.json", ref) or "{}")
    return (data.get("meta") or data).get("groundhog_version")


def app_version(ref: Optional[str]) -> Optional[str]:
    return json.loads(_read("electron-app/package.json", ref) or "{}").get("version")


# --------------------------------------------------------------------------- draft

def _diff_dict(old: Dict[str, str], new: Dict[str, str]) -> Tuple[List[str], List[str]]:
    return ([new[k] for k in sorted(new) if k not in old], [old[k] for k in sorted(old) if k not in new])


def draft(since: str, to: Optional[str]) -> str:
    lines: List[str] = []

    def bullets(title: str, items: List[str], limit: int = 40) -> None:
        if not items:
            return
        lines.append(f"- {title}:")
        lines.extend(f"  - {i}" for i in items[:limit])
        if len(items) > limit:
            lines.append(f"  - … and {len(items) - limit} more")

    added, removed = _diff_dict(calculators(since), calculators(to))
    bullets(f"New calculators ({len(added)})", added)
    bullets(f"Removed calculators ({len(removed)})", removed)

    (old_calcs, old_methods), (new_calcs, new_methods) = catalogue(since), catalogue(to)
    added, removed = _diff_dict(old_calcs, new_calcs)
    if not old_calcs and new_calcs:  # the catalogue itself is new: one line, not every calculation
        lines.append(f"- Calculation catalogue introduced: {len(new_calcs)} calculations, {len(new_methods)} methods")
        added = []
    bullets(f"New catalogue calculations ({len(added)})", added)
    bullets(f"Removed catalogue calculations ({len(removed)})", removed)
    bullets("New methods", sorted(f"{c}: {m}" for c, m in new_methods - old_methods if c in old_calcs.values()))

    old_tools, new_tools = geoai_tools(since), geoai_tools(to)
    bullets("New GeoAI tools", [f"`{t}`" for t in sorted(new_tools - old_tools)])
    bullets("Removed GeoAI tools", [f"`{t}`" for t in sorted(old_tools - new_tools)])

    old_routes, new_routes = api_routes(since), api_routes(to)
    bullets("New local API routes", [f"`{r}`" for r in sorted(new_routes - old_routes)])
    bullets("Removed local API routes", [f"`{r}`" for r in sorted(old_routes - new_routes)])

    added, removed = _diff_dict(doc_pages(since), doc_pages(to))
    bullets("New documentation pages", added)

    old_req, new_req = requirements(since), requirements(to)
    dep = [f"added {new_req[k]}" for k in sorted(new_req) if k not in old_req]
    dep += [f"removed {old_req[k]}" for k in sorted(old_req) if k not in new_req]
    dep += [f"{old_req[k]} → {new_req[k]}" for k in sorted(new_req) if k in old_req and old_req[k] != new_req[k]]
    bullets("Dependencies", dep)

    gh_old, gh_new = groundhog_version(since), groundhog_version(to)
    if gh_old != gh_new:
        lines.append(f"- groundhog {gh_old} → {gh_new}")
    v_old, v_new = app_version(since), app_version(to)
    if v_old != v_new:
        lines.append(f"- App version {v_old} → {v_new}")

    areas: Counter = Counter()
    for _, path in changed_files(since, to):
        if path.startswith(GENERATED) or path == CHANGELOG.relative_to(ROOT).as_posix():
            continue
        areas[next((label for prefix, label in AREAS if path.startswith(prefix)), "Other")] += 1
    if areas:
        lines.append("- Files changed by area: " + ", ".join(f"{a} ({n})" for a, n in areas.most_common()))

    target = to or "working tree"
    head = (f"Auto-draft: changes from {since} to {target}, detected from the code (not commit messages). "
            "Review, rewrite as user-facing notes under Added / Changed / Fixed, then delete this block.")
    return "\n".join([AUTO_START, f"*{head}*", "", *(lines or ["- No changes detected."]), AUTO_END])


# --------------------------------------------------------------------------- changelog file

def _sections(text: str) -> List[Tuple[str, Optional[str], int, int]]:
    """(name, date, start, end) of each '## ' release section; end is the start of the next section."""
    marks = list(SECTION_RE.finditer(text))
    return [(m.group(1), m.group(2), m.start(), marks[i + 1].start() if i + 1 < len(marks) else len(text))
            for i, m in enumerate(marks)]


def section_body(text: str, name: str) -> Optional[str]:
    for sec, _, start, end in _sections(text):
        if sec == name:
            return text[start:end].split("\n", 1)[1].strip() if "\n" in text[start:end] else ""
    return None


def _has_entries(body: str) -> bool:
    return bool(re.search(r"^\s*[-*] \S", re.sub(re.escape(AUTO_START) + r".*?" + re.escape(AUTO_END), "", body,
                                                    flags=re.S), re.M))


def write_draft(block: str) -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    if UNRELEASED not in text:
        first = SECTION_RE.search(text)
        text = text[:first.start()] + f"{UNRELEASED}\n\n" + text[first.start():] if first else text + f"\n{UNRELEASED}\n"
    if AUTO_START in text:
        text = re.sub(re.escape(AUTO_START) + r".*?" + re.escape(AUTO_END), lambda _m: block, text, flags=re.S)
    else:
        text = text.replace(UNRELEASED + "\n", f"{UNRELEASED}\n\n{block}\n", 1)
    CHANGELOG.write_text(text, encoding="utf-8")


def release(version: str, date: str) -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    if section_body(text, version) is not None:
        raise SystemExit(f"FAIL: the changelog already has a {version} section.")
    body = section_body(text, "Unreleased")
    if body is None or not _has_entries(body):
        raise SystemExit("FAIL: the Unreleased section is empty. Run 'draft --write', turn the draft into notes, "
                         "and try again.")
    if AUTO_START in body:
        raise SystemExit("FAIL: the Unreleased section still holds the auto-draft block. Rewrite it as notes "
                         "under Added / Changed / Fixed and delete the block first.")
    text = text.replace(f"{UNRELEASED}\n", f"{UNRELEASED}\n\n## {version} — {date}\n", 1)
    CHANGELOG.write_text(text, encoding="utf-8")


def _split_front_matter(text: str) -> Tuple[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    return (m.group(1), text[m.end():]) if m else ("", text)


def sync_docs_page() -> Optional[Path]:
    """
    Refresh the generated docs page (website/_content/pages/changelog.md) from the changelog source, as
    website/_content/extract_docs.py would: same generated front matter, the source's `sources:` list and body.
    Running the whole extractor is not needed (and without a groundhog clone it drops the guides and tutorials).
    """
    page = CHANGELOG.parent.parent / "pages" / "changelog.md"
    if not page.is_file():
        return None
    src_fm, src_body = _split_front_matter(CHANGELOG.read_text(encoding="utf-8"))
    gen_fm, _ = _split_front_matter(page.read_text(encoding="utf-8"))
    sources = re.search(r"^sources:\n(?:- .*\n?)+", src_fm + "\n", re.M)
    gen_fm = re.sub(r"^sources:\n(?:- .*(?:\n|$))+", "", gen_fm + "\n", flags=re.M).rstrip("\n")
    if sources:
        gen_fm += "\n" + sources.group(0).rstrip("\n")
    page.write_text(f"---\n{gen_fm}\n---\n\n{src_body.strip()}\n", encoding="utf-8")
    return page


def release_notes(version: str) -> str:
    body = section_body(CHANGELOG.read_text(encoding="utf-8"), version)
    if body is None:
        raise SystemExit(f"FAIL: no '## {version}' section in {CHANGELOG.relative_to(ROOT)}.")
    body = re.sub(r"\[([^\]]+)\]\((/docs/[^)]*)\)", r"\1", body)  # site-relative links do not resolve on GitHub
    previous = next((s for s, _, _, _ in _sections(CHANGELOG.read_text(encoding="utf-8"))
                     if s not in ("Unreleased", version) and _version_key(s) < _version_key(version)), None)
    footer = f"\n\n---\n\nFull history: [CHANGELOG]({REPO_URL}/blob/main/{CHANGELOG.relative_to(ROOT).as_posix()})"
    if previous:
        footer += f" · Code changes: [{previous}...{version}]({REPO_URL}/compare/{previous}...{version})"
    return body + footer + "\n"


def _version_key(v: str) -> Tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v.split("-")[0].split("+")[0])[:3])


def check(version: str) -> int:
    body = section_body(CHANGELOG.read_text(encoding="utf-8"), version)
    if body is None:
        print(f"FAIL: no '## {version}' section in the changelog. Run: python .github/scripts/changelog.py release {version}")
        return 1
    if not _has_entries(body) or AUTO_START in body:
        print(f"FAIL: the {version} changelog section is empty or still an unreviewed auto-draft.")
        return 1
    print(f"ok: changelog has notes for {version}")
    return 0


# --------------------------------------------------------------------------- CLI

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("draft")
    p.add_argument("--since", help="git ref to compare from (default: latest vX.Y.Z tag)")
    p.add_argument("--to", help="git ref to compare to (default: the working tree)")
    p.add_argument("--write", action="store_true", help="put the draft in the Unreleased section")
    p = sub.add_parser("release")
    p.add_argument("version")
    p.add_argument("--date", default=dt.date.today().isoformat())
    p.add_argument("--build", action="store_true", help="rebuild the website afterwards")
    for name in ("notes", "check"):
        sub.add_parser(name).add_argument("version")
    sub.add_parser("sync", help="refresh the generated docs page after editing the changelog by hand")
    args = parser.parse_args(argv)

    if getattr(args, "version", None) and not VERSION_RE.match(args.version):
        raise SystemExit(f"FAIL: {args.version!r} is not of the form vMAJOR.MINOR.PATCH")
    if args.cmd == "draft":
        since = args.since or last_tag()
        if not since:
            raise SystemExit("FAIL: no vX.Y.Z tag found; pass --since.")
        block = draft(since, args.to)
        if args.write:
            write_draft(block)
            sync_docs_page()
            print(f"wrote the draft to {CHANGELOG.relative_to(ROOT)} (Unreleased)")
        else:
            print(block)
        return 0
    if args.cmd == "release":
        release(args.version, args.date)
        print(f"{CHANGELOG.relative_to(ROOT)}: Unreleased is now {args.version} — {args.date}")
        sync_docs_page()
        if args.build:
            subprocess.run([sys.executable, str(ROOT / "website" / "_build" / "build.py")], cwd=ROOT, check=True)
        else:
            print("Rebuild the site so the docs page shows it: python website/_build/build.py")
        return 0
    if args.cmd == "sync":
        page = sync_docs_page()
        print(f"refreshed {page.relative_to(ROOT)}; rebuild with: python website/_build/build.py" if page
              else "no generated changelog page found")
        return 0
    if args.cmd == "notes":
        sys.stdout.write(release_notes(args.version))
        return 0
    return check(args.version)


if __name__ == "__main__":
    sys.exit(main())
