# Changelog

## Unreleased

### Mobile video moment review

- Add local video playback and a touch timeline scrubber to the section-review screen.
- Let users split a moment at the current playhead or enter an exact time, then decide Edit / Keep / Exclude for each resulting span.
- Keep section changes in the existing local draft flow; seeking and splitting do not alter the imported media file.

### Video analysis prototype

- Add an experimental local Python command that proposes adaptive visual cuts and ordered shot spans for clips up to 30 seconds.
- Record detector/source versions and local processing in a versioned proposal; mark boundaries unreviewed with unknown uncertainty and warn that shot cuts are not story sections.
- Keep the mobile app disconnected until analysis location and cross-platform integration decisions have evidence.
- Add `python -m videotemplate.cli analyze <video-path>` for local developer evaluation; it outputs proposed time ranges and does not rewrite source media.

### Mobile project recovery

- Persist the active manual-review draft locally, including source technical facts, section ranges, user decisions, and workflow stage.
- Resume an unfinished draft after restart; reselect the source video to preview it and confirm if its technical facts differ.
- Discard the unfinished draft from the import flow or when starting another project.
- Add SQLite schema migration v1 to v2 for the `project_drafts` table. Existing saved recipe rows are preserved.
- Draft records exclude the source media bytes and temporary picker URI.
