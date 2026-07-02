# Wolzard's Marketplace

A private Claude Code plugin marketplace for syncing my personal setup — skills, MCP servers, and hooks — across machines.

## What's in here

| Plugin | Contains |
|---|---|
| `personal-skills` | Android / KMP / Compose Multiplatform skills, design-taste skills, and misc utility skills (originally under `~/.agents/skills`) |
| `personal-tools` | Obsidian MCP server config + `PostToolUse`/`Stop` hooks that log sessions to Obsidian |

This marketplace does **not** vendor third-party skill packs. `android-testing-skills` and `compose-performance-skills` (both by [skydoves](https://github.com/skydoves)) are cloned directly from their own repos on each machine instead of being copied in here — see [Setup on a new machine](#setup-on-a-new-machine).

## Install

```
/plugin marketplace add <your-username>/Wolzard-s-Marketplace
/plugin install personal-skills@Wolzard-s-Marketplace
/plugin install personal-tools@Wolzard-s-Marketplace
```

Then `/reload-plugins`.

## Required environment variables

`personal-tools` expects these to be set in your shell profile *before* starting Claude Code — they are intentionally **not** stored in this repo:

```bash
export OBSIDIAN_API_KEY="your-real-key"
export OBSIDIAN_BASE_URL="http://127.0.0.1:27123"   # optional, defaults to this
```

The `obsidian-mcp-server` binary path is currently hardcoded to `/home/wolzard/.local/bin/obsidian-mcp-server` in `plugins/personal-tools/.mcp.json`. If installing on a machine where that binary lives elsewhere (or isn't on that exact path), update the `command` field accordingly, or put the binary on `PATH` and simplify it to `"command": "obsidian-mcp-server"`.

## Setup on a new machine

Full bootstrap (marketplaces, plugins, external skill repos) is handled by `bootstrap-new-machine.sh` in this repo — see that file for details. Summary:

1. Add this marketplace + the other marketplaces already in use (`chrisbanes/skills`, `JuliusBrussee/caveman`, `thedotmack/claude-mem`, `jarrodwatts/claude-hud`, `firebase/agent-skills`, `dietrichgebert/ponytail`).
2. Install `personal-skills` and `personal-tools` from here.
3. Reinstall previously-enabled plugins from those marketplaces.
4. Clone the external skill sources:
   ```bash
   git clone https://github.com/skydoves/android-testing-skills.git ~/.claude/skills-sources/android-testing-skills
   git clone https://github.com/skydoves/compose-performance-skills.git ~/.claude/skills-sources/compose-performance-skills
   ```
5. Set the environment variables above.
6. Merge personal preferences (status line, permissions, model, theme) from `settings-snippet.json` into `~/.claude/settings.json` by hand — these are machine-level preferences, not plugin-managed.

## Updating

When skills or hooks change locally:

```bash
# re-run the scaffold script to pull in changes from ~/.agents/skills
./build-marketplace.sh   # if kept in this repo, otherwise re-copy manually

cd ~/claude-personal-marketplace
git add .
git commit -m "Update skills"
git push
```

Bump the `version` field in the relevant `plugin.json` so installed copies pick up the change on next `/plugin marketplace update`.

## ⚠️ Before making this repo public

- Confirm no API keys, tokens, or absolute paths containing usernames/secrets are committed.
- `plugins/personal-tools/.mcp.json` should only ever contain `${ENV_VAR}` references, never literal secrets.
- Review `plugins/personal-skills/skills/` for anything project-specific that shouldn't be shared (e.g. Housizy/Sanvyara-specific business logic, if any skill leaked internal details).
