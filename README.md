# Video Template Builder

An early-stage project for analyzing short videos and turning their structure into reusable, editable templates.

## Project areas

- `apps/mobile/` — Expo and React Native iOS/Android interface prototype. Import and preview flows are present; analysis, persistence, and rendering are not connected yet. See its [README](apps/mobile/README.md) for setup and current limits.
- `src/videotemplate/` — Python video ingestion, decoding, source description, and template-recipe foundations.
- `docs/` — product research, design prototype, architecture, and technical contracts.
- [`docs/product/video_template_workflow_spec.md`](docs/product/video_template_workflow_spec.md) — detailed import, section review, replacement, preview, save, reuse, export, and validation workflow.
- [`docs/product/mvp_coverage_and_traceability.md`](docs/product/mvp_coverage_and_traceability.md) — requirement coverage, release scenarios, open decisions, and implementation traceability.
- [`docs/product/video_analysis_signal_strategy.md`](docs/product/video_analysis_signal_strategy.md) — OCR, speech, beat, visual cues, and replacement-suggestion research for video analysis.
- `_s23_*` and `_s23_fixtures/` — reproducibility scripts, recorded evidence, and small media fixtures cited by the technical specifications and checks.

## Mobile app

```powershell
cd apps/mobile
npm install
npm start
```

## Python project

Requires Python 3.11 or newer. Install the project and development dependencies with `pip install -e ".[dev]"`. See `pyproject.toml` for dependencies and package details.

## Status

The mobile app is a UI spike, not a production video editor. Automatic video analysis, replacement generation, durable template storage, audio editing, export/rendering, accounts, notifications, and billing remain future implementation work.
