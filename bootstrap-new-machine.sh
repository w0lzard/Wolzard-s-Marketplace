#!/usr/bin/env bash
# ==============================================================================
# bootstrap-new-machine.sh
#
# Run this on a fresh machine to restore your full Claude Code setup:
#   - your personal marketplace (skills + obsidian MCP + hooks)
#   - all 6 third-party marketplaces you already track
#   - all plugins you had enabled
#   - the two skydoves skill repos, re-cloned and re-symlinked
#
# EDIT the placeholders marked <<< before running.
# ==============================================================================
set -euo pipefail

# <<< set this to wherever you pushed build-marketplace.sh's output
YOUR_MARKETPLACE="your-github-username/yash-personal-marketplace"

echo "==> Adding marketplaces"
claude plugin marketplace add "$YOUR_MARKETPLACE"
claude plugin marketplace add chrisbanes/skills
claude plugin marketplace add JuliusBrussee/caveman
claude plugin marketplace add thedotmack/claude-mem
claude plugin marketplace add jarrodwatts/claude-hud
claude plugin marketplace add firebase/agent-skills
claude plugin marketplace add dietrichgebert/ponytail
# claude-plugins-official is built in, no need to add it

echo "==> Installing your personal plugins"
claude plugin install personal-skills@yash-personal
claude plugin install personal-tools@yash-personal

echo "==> Installing everything you had enabled before"
for entry in \
  kotlin-lsp@claude-plugins-official \
  caveman@caveman \
  claude-mem@thedotmack \
  figma@claude-plugins-official \
  superpowers@claude-plugins-official \
  frontend-design@claude-plugins-official \
  skill-creator@claude-plugins-official \
  feature-dev@claude-plugins-official \
  claude-code-setup@claude-plugins-official \
  coderabbit@claude-plugins-official \
  session-report@claude-plugins-official \
  claude-md-management@claude-plugins-official \
  github@claude-plugins-official \
  claude-hud@claude-hud \
  firebase@firebase \
  ponytail@ponytail; do
  echo "   installing $entry"
  claude plugin install "$entry" || echo "   !! failed: $entry (check name/marketplace)"
done

echo "==> Re-cloning external skill sources (skydoves repos)"
mkdir -p ~/.claude/skills-sources
[ -d ~/.claude/skills-sources/android-testing-skills ] || \
  git clone https://github.com/skydoves/android-testing-skills.git ~/.claude/skills-sources/android-testing-skills
[ -d ~/.claude/skills-sources/compose-performance-skills ] || \
  git clone https://github.com/skydoves/compose-performance-skills.git ~/.claude/skills-sources/compose-performance-skills

echo ""
echo "==> Manual steps still required:"
echo "  1. Set secrets in your shell profile (~/.zshrc, ~/.bashrc, etc.):"
echo "       export OBSIDIAN_API_KEY='your-real-key-here'"
echo "       export OBSIDIAN_BASE_URL='http://127.0.0.1:27123'"
echo "  2. Merge settings-snippet.json's contents (statusLine, permissions,"
echo "     model, effortLevel, theme) into this machine's ~/.claude/settings.json"
echo "     by hand — these are preferences, not plugin-managed."
echo "  3. Re-create the individual skill symlinks in ~/.claude/skills/ that"
echo "     pointed into skills-sources/, if you rely on them outside of"
echo "     the android-testing-skills / compose-performance-skills repos'"
echo "     own plugin registration (check if those repos ship a marketplace.json"
echo "     of their own — if so, 'claude plugin marketplace add skydoves/...'"
echo "     may replace this manual symlink step entirely)."
echo "  4. Run /reload-plugins inside Claude Code."
