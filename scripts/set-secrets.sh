#!/usr/bin/env bash
# Upload the index signing key to this repository's Actions secrets.
#
# Run it after generating or rotating the key. The keystore never leaves the
# machine except as a GitHub secret, which is write-only -- so if the local
# copies are lost, the key is lost with them and every user has to remove and
# re-add the repository.
#
#   bash scripts/set-secrets.sh
set -euo pipefail

REPO=lbellows/fdroid
KS="${KS:-$HOME/.android-signing/lbellows-fdroid-repo.keystore}"
PW="${PW:-$HOME/.android-signing/lbellows-fdroid-repo.password}"

for f in "$KS" "$PW"; do
  [ -r "$f" ] || { echo "missing: $f" >&2; exit 1; }
done

base64 -w0 "$KS" | gh secret set FDROID_KEYSTORE_BASE64 --repo "$REPO"
gh secret set FDROID_KEYSTORE_PASSWORD --repo "$REPO" < "$PW"

echo
gh secret list --repo "$REPO"
echo
echo "Now publish:  gh workflow run 'Publish F-Droid repo' --repo $REPO"
