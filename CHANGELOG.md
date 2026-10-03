# Changelog

## Unreleased

### Component analysis contract

- Define analysis as a time-aligned component inventory with separately reported coverage for people/subjects, objects/actions, setting/background, camera/layout, on-screen text, speech, music/sounds, creative beats, and source integrity.
- Version the local Python proposal as schema v2; distinguish shot spans from creative sections and keep shot-only results explicitly partial.
- Add per-finding provenance, uncertainty, anonymous clip-local entity references, normalized visual regions, and optional segmentation-mask references.
- Update the end-to-end workflow, mobile screen design, feature map, research, and traceability requirements to show the component map before section decisions.

### Mobile video moment review

- Add local video playback and a touch timeline scrubber to the section-review screen.
- Let users split a moment at the current playhead or enter an exact time, then decide Edit / Keep / Exclude for each resulting span.
- Generate local native frame previews for up to 16 moments so users can visually inspect each section.
- Let users select a moment from its frame preview; playback seeks to its start and pauses at its end.
- Keep section changes in the existing local draft flow; seeking and splitting do not alter the imported media file.
- Add SDK-compatible `expo-image` to render generated thumbnails on iOS and Android.

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
