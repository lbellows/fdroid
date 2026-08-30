#!/usr/bin/env python3
"""Fail the build if an app did not make it into the signed index.

`fdroid update` drops APKs silently in more than one situation -- the one that
prompted this is AllowedAPKSigningKeys, where a signer that is not on the list
is excluded with no error, so a wrong pin looks exactly like a successful
publish until someone opens the repo in a client and the app is not there.
"""
import json
import pathlib
import sys

APPS = pathlib.Path("apps.json")
INDEX = pathlib.Path("fdroid/repo/index-v1.json")


def main() -> int:
    if not INDEX.exists():
        print(f"error: {INDEX} was not produced", file=sys.stderr)
        return 1
    index = json.loads(INDEX.read_text())
    packages = index.get("packages", {})
    indexed = {a["packageName"] for a in index.get("apps", [])}

    failed = False
    for app in json.loads(APPS.read_text()):
        appid = app["appid"]
        count = len(packages.get(appid, []))
        if appid not in indexed or count == 0:
            print(f"error: {appid} is missing from the index "
                  f"(in apps: {appid in indexed}, APKs: {count})", file=sys.stderr)
            failed = True
        else:
            codes = sorted(p["versionCode"] for p in packages[appid])
            print(f"ok: {appid} -- {count} APKs, versionCodes {codes}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
