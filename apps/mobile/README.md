# Remix Mobile App

This iOS/Android app is an early Expo + React Native + TypeScript MVP candidate, not a finished video editor. Automatic video analysis, replacement-media editing, and rendering are not connected. Expo remains a reversible interface choice, not a final renderer decision. See the [implementation cross-check](../../docs/product/mobile_mvp_implementation_audit.md) for feature-by-feature status and next steps.

## Run locally

```powershell
npm install
npm start
```

Use the Expo development build or Android Studio emulator to open the project. Native iOS compilation requires macOS/Xcode or a configured cloud build. The dependency packages were installed when this scaffold was created.

## Feature layout

- `src/features/discover` — entry screen and starter recipe cards.
- `src/features/import` — device video picker, duration gate, local preview.
- `src/features/section-review` — manual section splitting and Edit/Keep/Exclude decisions.
- `src/features/project-drafts` — local recoverable manual project draft.
- `src/features/recipe-editor` — sample replacement idea and structure-only recipe preview.
- `src/features/template-library` — SQLite-backed local recipe metadata.
- `src/features/settings` — account/settings information architecture; services are pending.
- `src/shared` — design tokens, shared UI, navigation, and sample data.

Feature screens own their behavior and UI. Keep shared components generic; use narrow props for navigation and cross-feature events. When service contracts are ready, add feature-owned adapters rather than importing Python internals into the React Native UI.

## Current capability and limits

- Connected: native video-library picker, selected-video preview, 30-second duration gate, manual time-based section splitting, explicit Edit/Keep/Exclude choices, local recipe save/list/reopen/rename/duplicate/delete, and one recoverable local project draft through versioned SQLite repositories.
- Sample only: automatic section boundaries/roles, replacement suggestions, source-video rendering, fill-with-new-footage, and MP4 output.
- Not connected: the experimental Python shot-analysis CLI is not wired to the mobile app; mobile automatic scene detection, analysis progress/cancel/retry, durable source-media persistence (draft resume asks the user to reselect the source), audio editing, visual transformations, export/rendering, authentication, push notifications, and billing remain unimplemented.

Saved recipes and project drafts store timing and user decisions, not the source video or picker URI. Drafts currently keep only source technical facts; resume asks the user to reselect the clip and confirms if those facts differ. Do not represent manual sections as analysis results. Keep generated and user-approved decisions distinct when the real analysis contract is introduced.
