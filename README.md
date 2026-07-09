# Martin's Kodi Repository

A personal [Kodi](https://kodi.tv) add-on repository, hosted on GitHub Pages.

**Repository URL:** <https://martin1080p.github.io/kodi-repository/>

## Install in Kodi

1. In Kodi, go to **Settings → System → Add-ons** and enable **Unknown sources**.
2. **Settings → File manager → Add source**, and add:
   `https://martin1080p.github.io/kodi-repository/`
   Give it a name, e.g. `Martin`.
3. **Add-ons → Install from zip file** → pick the source →
   `repository.martin1080p/repository.martin1080p-1.0.0.zip`.
4. **Add-ons → Install from repository → Martin's Kodi Repository** → install
   any add-on (e.g. `plugin.video.prehrajto`).

Once the repository add-on is installed, Kodi checks it for updates
automatically.

## How it works

- `repository.martin1080p/` — source of the repository add-on. Its zip is
  built automatically by CI.
- `zips/` — the published tree that GitHub Pages serves. Contains one folder
  per add-on with versioned zips, plus the generated `addons.xml` and
  `addons.xml.md5`.
- `_generate.py` — scans `zips/`, reads the `addon.xml` embedded in each zip,
  and regenerates `addons.xml` + `addons.xml.md5`.
- `.github/workflows/deploy.yml` — on every push to `main` (and on manual
  dispatch): builds the repository add-on zip, runs `_generate.py`, and
  deploys `zips/` to GitHub Pages.

## Adding / updating an add-on

An add-on's own CI (in its own repo) only needs to commit its built zip to:

```
zips/<addon.id>/<addon.id>-<version>.zip
```

For example:

```
zips/plugin.video.prehrajto/plugin.video.prehrajto-1.2.3.zip
```

Pushing that to `main` triggers this repo's workflow, which regenerates the
manifest and redeploys Pages. No manual edits to `addons.xml` are needed.

## One-time setup

In this repo's **Settings → Pages**, set **Source** to **GitHub Actions**.
