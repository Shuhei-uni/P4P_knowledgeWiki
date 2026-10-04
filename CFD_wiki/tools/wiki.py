"""Read-only search and structural checks for the maintained CFD wiki."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ALIASES = {
    "ewf": "wall film",
    "dpm": "discrete phase particle droplet",
    "psd": "droplet size distribution",
    "vv": "verification validation",
    "carryover": "entrainment purity",
}


def pages():
    return sorted(p for folder in ("wiki", "paper_lookup")
                  for p in (ROOT / folder).rglob("*.md")
                  if "archive" not in p.parts and p.name != "log.md")


def relative(path):
    return path.relative_to(ROOT).as_posix()


def tokens(value):
    return re.findall(r"[a-z0-9]+", value.lower())


def search(query, limit):
    original = set(tokens(query)) - {"a", "an", "the", "is", "of", "to", "in",
        "and", "or", "how", "what", "why", "can", "i", "do", "for", "with"}
    expanded = set(original)
    for term in original:
        expanded.update(tokens(ALIASES.get(term, "")))
    results = []
    for path in pages():
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        title = next((line.lstrip("# ") for line in lines if line.startswith("# ")),
                     path.stem)
        body = Counter(tokens("\n".join(lines)))
        found = original & body.keys()
        if original and not (expanded & body.keys()):
            continue
        if not original:
            continue
        header = set(tokens(title + " " + path.stem))
        score = sum(8 if term in original else 2 for term in expanded & header)
        score += sum(min(body[term], 4) * (2 if term in original else 0.5)
                     for term in expanded)
        score += 10 * len(found) / len(original)
        if "synthesis" in path.parts or "physics-basis" in path.parts:
            score += 4
        if path.name == "index.md":
            score *= 0.4
        # Prefer compiled explanations to lookup dictionaries for broad questions.
        if "paper_lookup" in path.parts:
            score *= 0.7
        snippets = []
        section = title
        for number, line in enumerate(lines, 1):
            if line.startswith("#"):
                section = line.lstrip("# ")
            line_terms = set(tokens(line))
            matches = expanded & line_terms
            if matches and line.strip() and not line.startswith("#"):
                weight = len(original & line_terms) * 3 + len(matches)
                snippets.append((weight, number, section, line.strip()))
        best = sorted(snippets, key=lambda item: (-item[0], item[1]))[:2]
        results.append({"path": relative(path), "title": title,
                        "score": round(score, 2), "matched_terms": sorted(found),
                        "snippets": [{"line": n, "section": s, "text": t[:320]}
                                     for _, n, s, t in best]})
    return sorted(results, key=lambda item: (-item["score"], item["path"]))[:limit]


def links(text):
    # Inline Markdown links, including angle-wrapped targets. Ignore fenced code.
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in re.finditer(r"!?\[[^\]]*\]\((<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\)", line):
            yield number, match.group(1).strip("<>")


def health():
    documents = pages()
    content = [p for p in documents if "wiki" in p.relative_to(ROOT).parts
               and p.name != "index.md"]
    inbound = Counter()
    catalogued = set()
    broken = []
    unavailable = []
    for path in documents:
        text = path.read_text(encoding="utf-8-sig")
        for number, target in links(text):
            url = urlsplit(target)
            if url.scheme or target.startswith("//") or not url.path:
                continue
            dest = (path.parent / unquote(url.path)).resolve()
            if not dest.exists():
                broken.append({"path": relative(path), "line": number, "target": target})
            elif path != dest:
                if path == ROOT / "wiki/index.md":
                    catalogued.add(dest)
                if path.name != "index.md":
                    inbound[dest] += 1
        # Source records use paths relative to CFD_wiki in inline code.
        for match in re.finditer(r"`((?:raw|guide)/[^`]+)`", text):
            target = match.group(1)
            if not (ROOT / target).exists():
                unavailable.append({"path": relative(path), "target": target})
    return {"pages": len(documents), "compiled_pages": len(content),
            "broken_file_links": broken,
            "not_in_catalog": [relative(p) for p in content if p.resolve() not in catalogued],
            "no_content_backlinks": [relative(p) for p in content if not inbound[p.resolve()]],
            "unavailable_source_references": unavailable,
            "source_folders": {name: (ROOT / name).is_dir() for name in ("raw", "guide")},
            "limits": "Checks inline Markdown file targets, not anchors, reference-style links, "
                      "Obsidian wikilinks, external URLs, scientific claims, citations or units. "
                      "Backlinks count content pages only; catalog links are excluded."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    find = commands.add_parser("search", help="Rank local pages with section and line snippets")
    find.add_argument("query")
    find.add_argument("--limit", type=int, default=5)
    find.add_argument("--json", action="store_true")
    check = commands.add_parser("health", help="Check links, catalog coverage and source availability")
    check.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.command == "search":
        result = search(args.query, max(1, args.limit))
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            for item in result:
                print(f"{item['path']} [{item['score']}] — {item['title']}")
                for snippet in item["snippets"]:
                    print(f"  L{snippet['line']} ({snippet['section']}): {snippet['text']}")
            if not result:
                print("No matches. Try a model name, mechanism, author or alternate term.")
    else:
        result = health()
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"{result['pages']} pages; {result['compiled_pages']} compiled content pages")
            for key in ("broken_file_links", "not_in_catalog", "no_content_backlinks",
                        "unavailable_source_references"):
                print(f"{key}: {len(result[key])}")
                for item in result[key]:
                    print("  " + (json.dumps(item, ensure_ascii=False) if isinstance(item, dict) else item))
            print("Source folders: " + json.dumps(result["source_folders"]))
            print(result["limits"])
        return 1 if result["broken_file_links"] or result["not_in_catalog"] else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
