# Video Template Builder

An early-stage project for analyzing short videos and turning their structure into reusable, editable templates.

## Project areas

- [`docs/product/expected_functionality_and_research_map.md`](docs/product/expected_functionality_and_research_map.md) - consolidated functionality baseline, MVP/future scope, open decisions, and research links.

- `apps/mobile/` — Expo and React Native iOS/Android MVP candidate. Manual video import/review, recoverable section drafts, and local template recipe storage work; automatic analysis and rendering remain disconnected. See its [README](apps/mobile/README.md) for setup and current limits.
- `src/videotemplate/` — Python video ingestion, decoding, source description, and template-recipe foundations.
- `docs/` — product research, design prototype, architecture, and technical contracts.
- [`docs/product/video_template_workflow_spec.md`](docs/product/video_template_workflow_spec.md) — detailed import, section review, replacement, preview, save, reuse, export, and validation workflow.
- [`docs/product/mvp_coverage_and_traceability.md`](docs/product/mvp_coverage_and_traceability.md) — requirement coverage, release scenarios, open decisions, and implementation traceability.
- [`docs/product/video_analysis_signal_strategy.md`](docs/product/video_analysis_signal_strategy.md) — OCR, speech, beat, visual cues, and replacement-suggestion research for video analysis.
- [`docs/product/rendering_capability_and_quality_gate.md`](docs/product/rendering_capability_and_quality_gate.md) — iOS/Android rendering options, export behavior, and the parity spike required before locking a renderer.
- `_s23_*` and `_s23_fixtures/` — reproducibility scripts, recorded evidence, and small media fixtures cited by the technical specifications and checks.

- [`docs/product/media_privacy_security_and_data_lifecycle.md`](docs/product/media_privacy_security_and_data_lifecycle.md) - media data inventory, threat model, local/cloud storage, backup, deletion, and security release gates.

- [`docs/product/copyright_rights_and_asset_provenance.md`](docs/product/copyright_rights_and_asset_provenance.md) - rights declarations, music and source provenance, replacement-first exports, and legal review gates.

## Mobile app

```powershell
cd apps/mobile
npm install
npm start
```

## Python project

Requires Python 3.11 or newer. Install the project and development dependencies with `pip install -e ".[dev]"`. See `pyproject.toml` for dependencies and package details.

The experimental local shot-boundary proposal command is `python -m videotemplate.cli analyze <video-path>`. It emits candidate time ranges only; it does not physically split the video and is not connected to the mobile app.

## Status

The mobile app is an early MVP, not a production video editor. It supports manual section review, on-device recovery of one unfinished project, and local storage of reusable template recipes. Automatic video analysis, media replacement and rendering, audio editing, export, accounts, notifications, and billing remain future work.
