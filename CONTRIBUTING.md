# Contributing

Corrections to crawler data, platform rules and forum notes are especially useful, since they change often. Please link to the source of any rule you add.

## Repository layout

```text
.claude-plugin/     Plugin and marketplace manifests
.mcp.json           LinkGecko connector, idle until the user signs in
skills/             One folder per skill, each able to work as its own upload
shared/             Source files copied into the skills' references folders
scripts/            Sync, validation and packaging tools
tests/              Unit tests, standard library only
```

## Editing shared files

Edit files in `shared/`, never the copies in `skills/*/references/`. Then copy them across:

```bash
python3 scripts/sync_shared.py
```

## Checks to run

```bash
python3 scripts/validate_repo.py
```

```bash
python3 -m unittest discover -s tests
```

```bash
claude plugin validate . --strict
```

## Writing rules for skills

- Keep descriptions to 200 characters, the limit for claude.ai uploads, and include the words people use when asking for the task.
- Keep each `SKILL.md` under 500 lines and move detail into `references/`.
- Scripts use the Python standard library only.
- Use no em dashes or en dashes.
- Claim only what can be checked, and use placeholders in drafts where real facts belong.
- Skills may prepare outreach and replies, and they must never send or post them.

## Releases

Raise `version` in `.claude-plugin/plugin.json`, add a `CHANGELOG.md` entry, then push a tag such as `v1.1.0`. The release workflow publishes a zip for each skill.
