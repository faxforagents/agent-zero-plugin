# Index submission

This folder contains an unpublished index entry and thumbnail.
The repository URL is `https://github.com/faxforagents/agent-zero-plugin`.
The plugin identity is `fax_for_agents`.

The [index rules](https://github.com/agent0ai/a0-plugins/blob/main/README.md) require one plugin folder per PR.
Only `index.yaml` and an optional thumbnail belong in that folder.
Do not copy this README into the index PR.

## Before the PR

1. Review the source and local validation record.
2. Install into Agent Zero and verify the setup screen on desktop and mobile.
3. Run the [sandbox check](../docs/sandbox-check.md) separately for hosted and stdio.
4. Publish the reviewed source repository with root `plugin.yaml` and `LICENSE`.

The public repository must exist before the index's remote checks can pass.
Its root manifest must contain `name: fax_for_agents`.
The runtime currently ignores the requested `author` manifest field.
It obtains displayed author information from the source repository.

## Prepare the index PR

1. Fork `agent0ai/a0-plugins` and create a branch for this plugin.
2. Add `plugins/fax_for_agents/index.yaml` from this folder.
3. Add `plugins/fax_for_agents/thumbnail.png` from this folder.
4. Confirm the PR changes only those two files.
5. Run the current index validator against the committed PR range.
6. Open one PR and address automated validation and maintainer review.

The index accepts only `title`, `description`, `github`, `tags`, and `screenshots` fields.
This draft uses the first four fields.
Its thumbnail must be square and at most 20,480 bytes.
The rules specify no pixel dimension limit.
The [build record](../.coding-agent/summary.md) records this thumbnail's dimensions and byte count.

Run the validator from the index checkout after an authorized submission commit exists.
Set `BASE_SHA` and `HEAD_SHA` to the actual PR range.
The workflow also uses GitHub authentication and PR author context.

```bash
python scripts/validate_plugin_submission.py
```

## Steps Ben must do

Ben supplies his sandbox credential and checks authenticated installation in his Agent Zero instance.
Ben authorizes publication after reviewing the package and test evidence.
Ben creates or authorizes the public repository under `faxforagents`.
Ben uses his GitHub identity for the fork, push, and PR.
Ben handles any account consent or human review requested by maintainers.

No npm or PyPI publication is needed for this index entry.
