# Repository Change-Safety Rules

These rules apply to AI agents and developers making changes in this repository.

## Before changing code

- Read the applicable product, architecture, feature, and contract documents first.
- Identify the feature or contract being changed, its callers, persisted data, and platform adapters.
- Check the current workspace state and avoid overwriting existing user changes.
- Keep changes narrowly scoped. Do not perform broad rewrites, unrelated cleanup, mass formatting, or dependency upgrades as incidental work.
- Do not change the selected product scope or architecture decisions silently. Record material decisions and update the relevant docs.

## Data and public contract safety

- Treat saved `TemplateRecipe` data, analysis payloads, output profiles, and render jobs as versioned contracts.
- For a persisted/API schema change, document compatibility and migration before implementation. Preserve user data and provenance; unknown newer formats must fail safely without overwrite.
- Keep analysis suggestions distinct from user-approved decisions.
- Keep platform and vendor implementations behind narrow interfaces. Do not expose renderer/database/provider internals to unrelated features.
- Update the feature map/registry, migration notes, and changelog whenever those artifacts are introduced and affected.

## AI-assisted change protocol

- State the feature IDs and files expected to change before a nontrivial code change.
- Make the smallest coherent patch and inspect the complete diff for unintended edits.
- Report exactly what verification was run and its result. Never claim tests, builds, or device behavior that were not verified.
- Do not remove or rewrite unrelated work to make a change fit.
- If impact or migration safety is unclear, stop before broad edits and describe the uncertainty and a narrower option.
- Maintain a recoverable source-control checkpoint before production implementation. Do not use destructive reset/clean operations as a rollback substitute.

The full principles are in [software evolution and AI change-safety plan](docs/research/software_evolution_and_ai_change_safety.md); current feature IDs are in [feature map](docs/architecture/feature-map.md).
