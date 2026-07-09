# Personal Kodi Repository — Design

## Goal

A static Kodi add-on repository hosted on GitHub Pages that serves my own
add-ons to Kodi over HTTP. The first hosted add-on is `plugin.video.prehrajto`,
whose source lives in a separate repo and whose built zip is pushed here by CI.

## Facts

- GitHub user: `martin1080p`
- Repo name: `kodi-repository`
- Pages URL / Kodi `<datadir>`: `https://martin1080p.github.io/kodi-repository/`
- Repository add-on id: `repository.martin1080p`
- First hosted add-on: `plugin.video.prehrajto`

## Hosting

GitHub Pages, deployed via **GitHub Actions** (`upload-pages-artifact` +
`deploy-pages`). Pages "source" is set to *GitHub Actions* in repo settings.
The published artifact is the `zips/` folder, so its root maps to the datadir
URL. This keeps repo source separate from the generated/published tree.

## Layout

```
kodi-repository/
├── .github/workflows/deploy.yml     # regenerate manifest + build repo zip + deploy Pages
├── repository.martin1080p/          # SOURCE of the repository add-on
│   ├── addon.xml
│   └── icon.png
├── zips/                            # published tree → uploaded as Pages artifact
│   ├── addons.xml                   # generated
│   ├── addons.xml.md5               # generated
│   ├── repository.martin1080p/
│   │   └── repository.martin1080p-1.0.0.zip   # built from source by CI
│   └── plugin.video.prehrajto/
│       └── plugin.video.prehrajto-X.Y.Z.zip   # pushed here by the add-on's CI
├── _generate.py                     # scans zips/, reads each zip's addon.xml, writes manifest
└── README.md
```

## Components

### `repository.martin1080p/addon.xml`

A `xbmc.addon.repository` add-on. Declares one `<dir>` info block pointing at
the datadir:

- `<info compressed="false">…/addons.xml</info>`
- `<checksum>…/addons.xml.md5</checksum>`
- `<datadir zip="true">…/</datadir>`

Version `1.0.0`, author `martin1080p`, English + Czech summary.

### `_generate.py`

Pure Python 3, standard library only. Steps:

1. Walk `zips/` for `<addon.id>/<addon.id>-<version>.zip` files.
2. For each zip, open it and read the embedded `addon.xml`; take the `<addon>`
   element verbatim (this is how per-add-on metadata reaches the manifest
   without this repo knowing the add-on's internals).
3. Concatenate all `<addon>` elements into a single `<addons>` document →
   `zips/addons.xml` (UTF-8, no BOM).
4. Write MD5 of the exact bytes of `addons.xml` → `zips/addons.xml.md5`.
5. If a zip is missing or has no `addon.xml`, skip it with a warning; never
   crash. A repo with only the repository add-on is valid output.

### `.github/workflows/deploy.yml`

Triggers: push to default branch (covers the CI zip commit) and manual
`workflow_dispatch`. Steps:

1. Checkout.
2. Build `repository.martin1080p` source into
   `zips/repository.martin1080p/repository.martin1080p-<version>.zip`, reading
   the version from its `addon.xml`.
3. Run `python _generate.py`.
4. `upload-pages-artifact` with `path: zips/`.
5. `deploy-pages`.

Permissions: `pages: write`, `id-token: write`, `contents: read`.
Concurrency group so overlapping pushes don't race the deploy.

### `README.md`

Explains: what the repo is, the install URL for Kodi (add file source
`https://martin1080p.github.io/kodi-repository/`, install
`repository.martin1080p-1.0.0.zip`), the expected drop path for the add-on
CI (`zips/plugin.video.prehrajto/plugin.video.prehrajto-<ver>.zip`), and a
one-time note to set Pages source to "GitHub Actions".

## Contract with the add-on's CI (other repo)

The add-on repo's CI must commit/push its built zip to
`zips/plugin.video.prehrajto/plugin.video.prehrajto-<version>.zip` on this
repo's default branch. Nothing else is required — the manifest regenerates
and Pages redeploys automatically. (Implementing that CI is out of scope for
this repo.)

## Non-goals

- No add-on source for `plugin.video.prehrajto` in this repo.
- No manual manifest editing.
- No support for non-GitHub-Pages hosts.
```

## Testing / verification

- `_generate.py` runs against a seeded fixture (the repo add-on zip only) and
  produces a well-formed `addons.xml` + matching `.md5`.
- `addons.xml` parses as valid XML and the md5 matches the file bytes.
