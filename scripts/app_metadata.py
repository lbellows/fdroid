#!/usr/bin/env python3
"""Derive an app's repo metadata from its in-tree fdroiddata recipe.

`fdroid update` takes descriptions, icons and screenshots from
metadata/<appid>/<locale>/ -- which is what fastlane already provides -- but it
reads License, Categories, SourceCode and friends from metadata/<appid>.yml.
Without that file every app is published as licence "Unknown" in the catch-all
"fdroid" category with no link back to its source.

Each app already states all of it in the recipe it submits to fdroiddata, so
lift the app-level fields from there and drop everything that only describes how
to build from source. One source of truth, and it cannot drift from the
fdroiddata submission.

AllowedAPKSigningKeys is deliberately NOT taken from the recipe. Here it is a
useful guard -- fdroid update drops any APK whose signer is not on the list. In
fdroiddata it would be actively harmful: F-Droid builds from source and signs
with its own key, so pinning our release cert there would silently exclude
F-Droid's own build and the app would vanish from the main index with no error.
It comes from apps.json, which never reaches the upstream submission.

    app_metadata.py <recipe.yml> <appid> <out-dir> [signing-key-sha256]
"""
import re
import sys

import yaml

# Everything F-Droid shows about an app, as opposed to how it is built.
KEEP = (
    "AntiFeatures", "AuthorEmail", "AuthorName", "AuthorWebSite",
    "AutoName", "Categories", "Changelog",
    "CurrentVersion", "CurrentVersionCode", "Description", "Donate",
    "IssueTracker", "License", "Liberapay", "Name", "OpenCollective",
    "SourceCode", "Summary", "Translation", "WebSite",
)


def main() -> int:
    if len(sys.argv) not in (4, 5):
        print(f"usage: {sys.argv[0]} <recipe.yml> <appid> <out-dir> [signing-key]",
              file=sys.stderr)
        return 2
    recipe, appid, outdir = sys.argv[1:4]
    signing_key = sys.argv[4] if len(sys.argv) == 5 else ""

    with open(recipe) as fh:
        src = yaml.safe_load(fh) or {}

    out = {k: src[k] for k in KEEP if k in src}
    # AutoName is what fdroiddata's updater fills in from the APK; fdroid update
    # ignores it and reads Name, so an app with only AutoName publishes nameless.
    if "Name" not in out and "AutoName" in src:
        out["Name"] = src["AutoName"]
    if not out.get("SourceCode"):
        print(f"warning: {appid} recipe has no SourceCode", file=sys.stderr)
    if not out.get("License"):
        print(f"warning: {appid} recipe has no License", file=sys.stderr)

    out.pop("AllowedAPKSigningKeys", None)
    if signing_key:
        if not re.fullmatch(r"[0-9a-f]{64}", signing_key):
            print(f"error: {appid} signing_key must be lowercase hex SHA-256",
                  file=sys.stderr)
            return 1
        out["AllowedAPKSigningKeys"] = [signing_key]

    path = f"{outdir}/{appid}.yml"
    with open(path, "w") as fh:
        yaml.safe_dump(out, fh, default_flow_style=False, sort_keys=True,
                       allow_unicode=True)
    print(f"{path}: " + ", ".join(f"{k}={out[k]!r}" for k in
                                  ("License", "Categories", "SourceCode") if k in out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
