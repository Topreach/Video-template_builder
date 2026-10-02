# Remix Mobile App Spike

This iOS/Android app is an isolated Expo + React Native + TypeScript user-interface spike. Expo is a candidate implementation, not a final renderer or architecture decision. The video analysis and render pipeline are not connected yet.

## Run locally

```powershell
npm install
npm start
```

Use the Expo development build or Android Studio emulator to open the project. Native iOS compilation requires macOS/Xcode or a configured cloud build. The dependency packages were installed when this scaffold was created.

## Feature layout

- `src/features/discover` — entry screen and starter recipe cards.
- `src/features/import` — device video picker, duration gate, local preview.
- `src/features/section-review` — section decision interface; currently clearly marked sample data.
- `src/features/recipe-editor` — replacement idea and template preview screens.
- `src/features/template-library` — in-memory preview of saved recipes; durable storage is pending.
- `src/features/settings` — account/settings information architecture; services are pending.
- `src/shared` — design tokens, shared UI, navigation, and sample data.

Feature screens own their behavior and UI. Keep shared components generic; use narrow props for navigation and cross-feature events. When service contracts are ready, add feature-owned adapters rather than importing Python internals into the React Native UI.

## Current capability and limits

- Connected: native video-library picker, selected-video preview, 30-second duration gate, manual time-based section splitting, explicit Edit/Keep/Exclude choices, local recipe save/list/reopen/rename/duplicate/delete through a versioned SQLite repository.
- Sample only: automatic section boundaries/roles, replacement suggestions, source-video rendering, fill-with-new-footage, and MP4 output.
- Not connected: automatic scene detection, analysis API, source-media persistence, audio editing, visual transformations, export/rendering, authentication, push notifications, and billing.

Saved recipes store timing and user decisions, not the source video or picker URI. Do not represent manual sections as analysis results. Keep generated and user-approved decisions distinct when the real analysis contract is introduced.
