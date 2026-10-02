# ADR 0003: Experimental Local Shot-Boundary Analysis

**Status:** Accepted for a reversible Python research prototype only; not selected for mobile production.  
**Date:** 3 October 2026  
**Related requirements:** ANA-001, ANA-002, IMP-002, SREV-001; open decisions DEC-002 and DEC-003.

## Context

The Expo app has manual section splitting but no analysis adapter. The existing Python package probes, decodes, and measures technical quality; `videotemplate.analysis` was a placeholder. The product needs candidate visual cut points while preserving the rule that cuts are not creative/story sections and never make user decisions automatically.

Production analysis location remains open. Sending an imported clip to a server requires a disclosed transfer, retention/deletion controls, service security, and cost evidence. On-device mobile analysis requires native decoder/model work and iOS/Android parity evidence. Neither path is selected by this prototype.

## Decision

- Add a local CLI-only cut-proposal experiment using PySceneDetect `AdaptiveDetector` with the PyAV input backend.
- Convert detected shot boundaries into ordered, half-open millisecond ranges in a versioned `AnalysisProposal` contract.
- Label every boundary and span as unreviewed, keep uncertainty unknown, and include warnings that these are cuts rather than story sections. Do not emit a confidence percentage.
- Keep this detector outside the mobile app and do not upload media. This experiment does not physically cut or alter the source file.
- Pin PySceneDetect below 0.8 because its official API documentation advises that compatibility bound while the API is under development. The headless package is BSD-3-Clause; its OpenCV, PyAV, and codec dependency inventory still needs release review.
- Revisit the detector and processing location after running the permissioned annotated corpus and comparing correction burden, latency, resource use, privacy, and platform feasibility.

## Consequences

- Developers can inspect candidate shot segmentation on a local file before choosing a mobile/server adapter.
- A video with no candidate cuts still produces one full-duration proposed span for manual review.
- Thresholds are experimental and not calibrated to the product's short-form corpus. No user-facing mobile claim or accuracy promise is allowed.
- The Python CLI does not yet satisfy mobile analysis progress/cancel/retry or iOS/Android acceptance requirements.

## Sources

- [PySceneDetect AdaptiveDetector](https://www.scenedetect.com/docs/latest/api/detectors.html)
- [PySceneDetect SceneManager and PyAV backend documentation](https://www.scenedetect.com/docs/latest/api/scene_manager.html)
- [PySceneDetect package and API version guidance](https://www.scenedetect.com/docs/latest/api.html)
- [PySceneDetect BSD-3-Clause license](https://github.com/Breakthrough/PySceneDetect/blob/main/LICENSE)
