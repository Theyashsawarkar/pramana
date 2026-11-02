# 3. A tool of its own, not part of dvarapala

**Status:** Accepted  
**Date:** 2026-10-24

## Context

The polkit agent was first written inside dvarapala, which already had the right window and the root-owned install. But dvarapala has one job: letting AI agents ask for root commands that the user approves one by one. A polkit agent serves every app on the desktop and is needed by people who never use an AI agent.

## Decision

pramana is its own repo and package, with its own install, service and app id (`io.github.theyashsawarkar.Pramana`). It shares only the theme module with dvarapala, by copy.

## Consequences

- Either can be installed without the other; dvarapala's scope stays small and easy to review.
- The theme module exists twice; changes to it are made in both (noted in both CLAUDE.md files).
