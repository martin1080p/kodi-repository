# Centralized old-zip pruning in deploy.yml

## Problem

When an add-on is updated, its old versioned zip should be removed from this
repository so `zips/<id>/` holds only the newest version. Today pruning is done
by each add-on's own publish workflow (the `git rm` loop in
`docs/addon-publish-workflow.yml`). We want the guarantee to live centrally in
`kodi-repository` instead of depending on each add-on repo's CI, so an add-on
repo can just drop its new zip and trust this repo to prune.

## Goal

On every push to `main`, `kodi-repository` deletes all but the newest version of
each add-on under `zips/`, commits that deletion back to git, and deploys the
pruned tree to GitHub Pages — in a single workflow run.

## Approach

Add a prune step to the existing `.github/workflows/deploy.yml`, before the
build/generate/deploy steps.

Rationale for reusing `deploy.yml` rather than a separate workflow: the deploy
workflow already fires on exactly the right trigger (push to `main`, which is
when an add-on drops a new zip via its PAT push). Keeping prune → regenerate →
deploy in one run avoids ordering problems and a second workflow needing a PAT.

### Loop safety

The prune step commits and pushes with the built-in `GITHUB_TOKEN`. GitHub does
**not** re-trigger workflow runs for pushes made with `GITHUB_TOKEN`, so this
cannot cause an infinite prune→push→prune loop. No `[skip ci]` marker is needed.

## Changes

### `.github/workflows/deploy.yml`

1. Change `permissions.contents` from `read` to `write` (needed to push the
   pruning commit; `pages: write` and `id-token: write` stay).
2. Add a **Prune old add-on versions** step immediately after `Checkout`,
   before `Build repository add-on zip`:
   - For each directory `zips/*/`, collect its `<id>-*.zip` files.
   - Determine the newest by `sort -V` (GNU version sort — orders
     `1.0.10 > 1.0.9` correctly, unlike lexicographic sort).
   - `git rm -q` every zip except the newest.
   - If anything was removed, configure the `github-actions[bot]` identity,
     commit as `Prune old add-on versions`, and `git push`.
   - If nothing was removed, make no commit.

No other files change. `docs/addon-publish-workflow.yml` keeps its own prune
loop (harmlessly redundant) and `README.md` is left as-is, per decision.

## Behavior notes / edge cases

- **Retention:** exactly one (the newest) zip per add-on is kept.
- **`repository.martin1080p`:** its zip is not committed to git (it is rebuilt
  each run into the working tree), so the prune step finds nothing to remove for
  it; the existing build step continues to own it.
- **Newest = highest version, not most recently pushed.** If an older version is
  ever pushed while a higher one exists, the higher one is kept. This is the
  correct behavior for a Kodi repo (serve the highest version).
- **First push of a brand-new add-on:** only one zip exists, nothing is pruned,
  no commit is made.

## Verification

- Trigger: with two versions of an add-on present under `zips/<id>/`, a push to
  `main` results in a `Prune old add-on versions` commit that removes the older
  zip, and the deployed Pages tree contains only the newest zip.
- No-op: with a single version present, the run makes no prune commit.
