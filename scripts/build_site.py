#!/usr/bin/env python3
"""Render the landing page for the published F-Droid repo.

Takes the repo URL and the index signing fingerprint, reads whatever apps
actually landed in the signed index, and fills in the template. Kept out of the
workflow so it can be run and eyeballed on its own.
"""
import html
import json
import pathlib
import sys

TEMPLATE = pathlib.Path(".github/pages/index.html")
INDEX = pathlib.Path("fdroid/repo/index-v1.json")
OUT = pathlib.Path("site/index.html")


def rows() -> str:
    if not INDEX.exists():
        return '<tr><td colspan="3">No apps in the index yet.</td></tr>'
    data = json.loads(INDEX.read_text())
    packages = data.get("packages", {})
    out = []
    for app in sorted(data.get("apps", []), key=lambda a: (a.get("name") or "").lower()):
        pkg = app.get("packageName", "")
        versions = packages.get(pkg, [])
        newest = versions[0].get("versionName", "") if versions else ""
        out.append(
            "<tr>"
            f'<td><strong>{html.escape(app.get("name") or pkg)}</strong><br>'
            f'<span class="mono dim">{html.escape(pkg)}</span></td>'
            f'<td>{html.escape(app.get("summary") or "")}</td>'
            f'<td class="mono">{html.escape(str(newest))}</td>'
            "</tr>"
        )
    return "\n".join(out) or '<tr><td colspan="3">No apps in the index yet.</td></tr>'


def main() -> int:
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <repo-url> <fingerprint>", file=sys.stderr)
        return 2
    url, fingerprint = sys.argv[1], sys.argv[2]
    page = (
        TEMPLATE.read_text()
        .replace("@REPO_URL@", html.escape(url))
        .replace("@FINGERPRINT@", html.escape(fingerprint))
        .replace("@APP_ROWS@", rows())
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
