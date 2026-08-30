# lbellows F-Droid repository

A self-hosted [F-Droid](https://f-droid.org) repository, published to GitHub Pages:

    https://lbellows.github.io/fdroid/repo?fingerprint=<index fingerprint>

Add that under *Settings → Repositories* in the F-Droid client. Including
`?fingerprint=` pins the repository to the signing key, so the client verifies it
instead of the user eyeballing a hex string; the plain URL works too. The landing
page at <https://lbellows.github.io/fdroid/> always shows the current
copy-pasteable form and lists what is published.

## How it works

`.github/workflows/publish.yml` collects the APKs attached to each app's GitHub
releases, copies each app's fastlane store listing into the layout `fdroid update`
expects, builds and signs the index, and deploys the result to Pages. It runs on
push, nightly, on demand, and on a `repository_dispatch` of type `app-released`
so an app repo can refresh the index as soon as it publishes.

## Adding an app

One entry in `apps.json`:

```json
{ "repo": "lbellows/some-app", "appid": "com.example.someapp" }
```

The app needs APKs attached to its GitHub releases and, for a decent listing,
`fastlane/metadata/android/<locale>/` in its source tree. Multiple per-ABI APKs
per release are fine — F-Droid indexes them by versionCode and serves each client
the one matching its architecture.

To have an app refresh this repo the moment it publishes a release, add a step to
its release workflow:

```yaml
- name: Refresh the F-Droid repo
  run: gh api repos/lbellows/fdroid/dispatches -f event_type=app-released
  env:
    GH_TOKEN: ${{ secrets.FDROID_DISPATCH_TOKEN }}
```

That needs a token with `contents: write` on this repository; without it the
nightly run picks the release up within a day anyway.

## Signing

The index is signed with a dedicated key — deliberately not any app's release
key — held in the `FDROID_KEYSTORE_BASE64` and `FDROID_KEYSTORE_PASSWORD` secrets.

**The fingerprint of that key is the repository's identity.** If it is lost or
changed, every user has to remove and re-add the repository by hand. Back up the
keystore and its password off-machine.
