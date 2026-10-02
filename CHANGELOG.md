# Changelog

## Unreleased

### Mobile project recovery

- Persist the active manual-review draft locally, including source technical facts, section ranges, user decisions, and workflow stage.
- Resume an unfinished draft after restart; reselect the source video to preview it and confirm if its technical facts differ.
- Discard the unfinished draft from the import flow or when starting another project.
- Add SQLite schema migration v1 to v2 for the `project_drafts` table. Existing saved recipe rows are preserved.
- Draft records exclude the source media bytes and temporary picker URI.
