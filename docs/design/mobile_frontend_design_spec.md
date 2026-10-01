# Mobile Frontend and Interface Design Specification

**Status:** Research-informed UI direction for creator validation; visual styling and screen density are not yet final.  
**Platforms:** iOS and Android phones first.  
**Product boundary:** Create and save reusable section-based templates from reference videos, fill their slots with new media, preview, and export a short MP4. Full multitrack editing and posting are later work.
**Related:** [Account, security, monetization, and editor scope research](../research/account_security_monetization_and_editor_scope.md)
**Mobile UI spike:** [Expo app notes](../../apps/mobile/README.md)
**Clickable concept:** [Open the standalone workflow prototype](prototype/index.html) · [prototype notes](prototype/README.md)

## 1. Design objective

Make the app feel like a creative template workshop, not a professional editing suite. A new creator should be able to understand a reference video as a sequence of editable moments, decide what to keep or change, and produce a reusable recipe without learning a timeline editor. Experienced creators can open precise timing controls when needed.

The distinguishing interface idea is the **Remix Map**: a compact, ordered set of scene cards that describes each moment's job (hook, setup, reveal, payoff, CTA, or a user-defined role), its timing, what can be changed, and why the next replacement suggestion fits. It connects inspiration to an actionable reusable structure instead of presenting a wall of effects or undifferentiated templates.

## 2. Competitive interface observations

- CapCut's official help describes a template flow centered on browsing, choosing media, previewing, editing individual segments, and exporting. This is efficient for rapid remakes; our workflow must add explicit source review, section exclusion, and a reusable editable recipe because the imported video may be partial or contain unwanted attached material. [CapCut template workflow](https://www.capcut.com/help/use-and-export-templates-in-capcut)
- Canva emphasizes replacing template media, including replacing multiple media items together. We should make slot replacement similarly low effort, with a clear mapping of selected source clips to template slots and a batch replacement option. [Canva mobile video editor](https://www.canva.com/video-editor/mobile-app/)
- The product's edge should come from understanding the *structure* of a clip and giving users a guided way to transform it, not from matching a competitor's template gallery or exposing every editing control at once. These are product hypotheses and require creator usability tests.

## 3. Navigation and app shell

Use a persistent four-destination bottom navigation on primary browsing screens:

1. **Discover** — curated examples, categories, search, and featured remix recipes.
2. **Create** — primary action to import a reference or start from an app recipe.
3. **My Templates** — private saved recipes, drafts, versions, and recent exports.
4. **Profile** — creator defaults, language, accessibility, privacy, storage, and help.

During creation, switch to a focused full-screen workflow with a clear back action, step label, save-draft behavior, and one primary action per screen. Do not keep the bottom navigation visible over the editor; preserve the user's place if they leave to choose media or inspect a template.

## 4. Screen-by-screen specification

| Screen | Primary layout and controls | Key states and behavior |
|---|---|---|
| Welcome | One short value statement; primary **Create from a video**; secondary **Explore examples**; concise explanation of reference analysis and rights. | Guest exploration where possible; request account only when sync or publishing features require it. |
| Discover | Search; horizontal category chips; featured cards; recent/popular curated recipes; each card shows format, runtime, number of slots, needed media, and supported output profiles. | Loading skeletons; useful empty/search state; unavailable/offline state; avoid fake trending labels without measured data. |
| Recipe detail | Large playable example; purpose and format; section count/runtime; required footage; editable fields; rights/asset notices; **Use this recipe** and **Save**. | Do not autoplay sound. Clearly mark reference/demo media and any locked or unsupported effects. |
| Import reference | Local picker/camera-roll entry; selected clip preview; duration, resolution, orientation, audio presence, file size; explain processing and deletion. | Validate duration and supported file before analysis; show actionable errors and alternate start-from-recipe path. |
| Analyze | Video preview thumbnail; named progress stages (checking clip, finding cuts, reading text/audio, preparing sections); cancel and keep-draft controls. | No fabricated percentage. On failure, retain the project and offer retry or manual section creation. |
| Review / Remix Map | Top preview; total included duration; section cards with timecode, thumbnail, role, confidence cue, Edit / Keep / Exclude; add/split/merge and optional compact timeline. | Preview updates after decisions. Undo snackbar; excluded cards remain visible as excluded until confirmation. Low-confidence boundaries request correction, not blind trust. |
| Section edit | Large section preview; start/end handles; role and suggested replacement; **Why this fits**; choose own media, capture prompt, licensed asset, or supported generated concept; text/audio controls as contextual tools. | Keep/replace/remove source audio separately. Save/cancel section changes; all suggestions optional. Unsupported AI actions explain why and offer whole-section replacement. |
| Sound and text | Track/list view with distinct lanes for source audio, music, voice, effects, captions/title; simple controls first (mute, replace, volume, timing, style), advanced timing on demand. | Show asset origin, license scope, and destination limits; preview mix; no default claim that a replacement makes source footage copyright-safe. |
| Visual treatment | Section-scoped choices: replace whole section, change background when supported, crop/reframe, text/effects; before/after wipe; undo/restore. | Make AI-generated/altered imagery explicit. Explain mask uncertainty; do not offer person generation as a universal one-tap tool. |
| Template preview | Vertical player; toggle **Reference**, **Template structure**, and **Your version**; included/excluded summary; placeholder list; output profile selector and interface safe-zone preview. | Confirm only when the user can see which original sections remain, what is a replaceable slot, and what still needs media. |
| Fill template | Remix Map with slot cards; add/select multiple clips; suggested slot-to-clip mapping; adjust crop, trim, and timing; batch replace. | Missing slot indicators and mismatched-duration guidance; preserve the original recipe; save this result as a new version. |
| Export | Output preview; profile, aspect ratio, resolution and audio summary; estimated file size only when calculable; **Export video**. | Progress, cancel, retry, low-storage and unsupported-effect errors; completion with save location and system share sheet. Do not promise direct social posting. |
| My Templates | Draft / Ready / Recently exported filters; thumbnail cards; search/sort; duplicate, rename, archive/delete, edit. | Explain draft vs confirmed recipe vs rendered MP4; confirm destructive deletion and support recovery where possible. |
| Sign-in / sign-up | Email entry, password or supported passwordless flow, verification/recovery links; **Continue without account** where core local workflow permits. | State why an account is needed before requesting it; preserve local drafts through sign-up; show neutral recovery errors and rate-limit feedback. |
| Creator profile | Optional display name/avatar and creator preferences, separate from login identity. | Skip profile setup; do not gate editing on avatar, bio, or social connections. |
| Settings | Grouped rows for Creator profile, Account & security, Creation defaults, Notifications, Privacy & media, Plan & billing, Accessibility, Help & legal. | Show current values and OS permission status; label cloud vs device behavior plainly. |
| Notification preferences | In-app categories for render status and optional updates; explain system permission only when relevant. | Core app works when denied; never repeatedly prompt; foreground render state updates in-app. |
| Account & privacy | Linked sign-in methods, session/sign-out controls where supported, media retention, data export/delete, account deletion. | Explain which local/cloud media will be deleted and when; require clear confirmation for account deletion. |
| Plan & billing (later) | Current plan, included usage, renewal date, restore purchase, manage subscription. | Keep hidden until a paid product exists; show exact terms before purchase and preserve access/exports according to published plan rules. |

## 5. Core layout patterns

### Remix Map section card

Each card should answer, without opening a detailed editor:

- What moment is this and when does it occur?
- Is it included, editable, or excluded?
- What is the user's next action?
- How certain is the app about this boundary or role?
- What source media will be retained or replaced?

Use a thumbnail, role label, time range and duration, visible decision state, and direct controls. Avoid color-only states. Put secondary operations (split, merge, reorder, rename) in a clearly labeled overflow/action menu. Make drag-to-reorder optional; provide accessible move-up/down actions.

### Progressive timeline

Default to cards and a compact scrubber. Tapping **Fine-tune timing** expands the timeline with section boundaries and playback cursor. Keep touch targets large; use a magnified time readout and frame-step controls for trim handles. A precision timeline must never be the only way to complete the workflow.

### Preview controls

Place the preview where it remains the dominant visual anchor. Keep play/pause, mute, scrub, and fit/crop controls predictable. Editing panels may use a bottom sheet, but the sheet must not cover the selected section's essential content; allow a full-screen preview and always provide a visible close/back route.

## 6. Visual direction (starting hypothesis)

- **Overall character:** editorial and creator-focused; vivid media thumbnails carry the energy, while the interface chrome remains quiet and readable.
- **Color:** neutral canvas and surfaces, one high-contrast brand accent for primary actions, plus semantic success/warning/error colors. Validate contrast in light and dark appearance before choosing final values.
- **Preview workspace:** test a darker preview surface against a light browsing surface; this can distinguish media from controls, but should follow platform appearance settings and user preference.
- **Typography:** system-friendly sans serif, clear role hierarchy, tabular numerals for timecodes, and Dynamic Type/font scaling support.
- **Shape and motion:** consistent card/control radii; subtle transitions; no decorative animation over moving video. Respect Reduce Motion and flashing-light settings.
- **Media-first cards:** use real stills from the recipe preview rather than abstract category icons alone; do not place important metadata over busy imagery without a scrim or solid surface.

These are hypotheses for prototype comparison, not a finalized brand system. The design should be tested in real clips with varied skin tones, dark/bright scenes, captions, RTL language, and large text.

## 7. Interaction and state requirements

- Provide explicit Save draft, Undo, and Restore original affordances. Confirm irreversible deletion.
- Preserve work through app backgrounding, picker handoff, low-memory termination where feasible, and recoverable render failure.
- Distinguish **Detected**, **Suggested**, **User selected**, and **Applied** states in text and accessibility labels.
- Show why a suggestion was made and let users accept, edit, skip, or request another idea.
- Keep creation progress step-based and honest. Never make an AI operation look complete while it is still processing.
- Use plain language for Edit / Keep / Exclude and explain whether source pixels/audio will remain in the resulting template.
- Warn before leaving a dirty edit; autosave a recoverable draft when possible.
- Use haptics only as optional confirmation, never as the sole state signal.

## 8. Responsive behavior and social-output previews

The app's **interface layout** and a video's **output profile** are separate systems. The editor UI adapts to device size, font scale, safe insets, and orientation; the output profile controls aspect ratio, crop, safe areas, duration guidance, frame rate, and export format.

- Phone portrait is the primary authoring layout. On compact phones, stack preview and controls; allow preview collapse to reclaim room.
- On larger phones and tablets, use a preview plus side-by-side section inspector where width permits. Do not stretch controls across a tablet-sized canvas.
- Respect system safe insets and keyboard appearance; ensure bottom actions remain reachable above the keyboard/home indicator.
- Keep the canvas aspect ratio fixed to the selected output profile while surrounding controls adapt. Never distort footage to fill the preview.
- Provide neutral vertical preview and destination-profile overlays for TikTok, Instagram/Facebook Reels, and YouTube Shorts. Treat platform chrome/safe zones as dated guidance and clearly separate ad specifications from organic-use assumptions.
- When changing profiles, show crop and text/subject collisions before applying; retain independent per-profile framing adjustments in the edit session rather than changing the reusable recipe silently.
- Support RTL layout and localized text expansion. Preview captions and titles in the selected language before export.

## 9. Accessibility and inclusive use

- Use native screen-reader semantics and name controls by purpose, including playhead, section boundary, crop, and audio level values.
- Aim for comfortable platform-sized targets: Apple recommends 44×44 pt defaults; Android's Compose guidance uses a 48dp minimum target. Provide spacing and larger hit regions for timeline handles. [Apple accessibility guidance](https://developer.apple.com/design/human-interface-guidelines/accessibility), [Android touch-target guidance](https://developer.android.com/develop/ui/compose/accessibility/api-defaults)
- Maintain text/background contrast, visible focus, and state labels that do not rely on color alone.
- Support captions, mute, and visual equivalents of audio cues; do not autoplay sound.
- Respect font scaling, screen readers, Reduce Motion, and flashing-light protections. Avoid time-limited prompts and gesture-only actions.
- Test with VoiceOver and TalkBack on actual devices, including the section decision flow and timeline alternative controls.

## 10. Account and lifecycle UX

- A person can try the local creation flow before registration wherever processing allows. If cloud analysis or sync requires identity, explain that dependency at the point it matters and offer a local/manual path when feasible.
- Separate account identity (email/provider) from the optional public-facing creator profile. Do not ask for birthdate, contacts, or social credentials without a validated requirement.
- The Settings screen is grouped by task, with account/security and privacy/media controls easy to find. Include sign out, account deletion, source deletion, and cloud retention status.
- Do not request camera-roll, microphone, notification, or tracking permissions at launch. Ask in context and state the feature benefit before the operating-system permission request.
- Notifications are off until permission is granted and category preferences are chosen. A render-complete notification is relevant only for an opted-in remote/long render; local render completion belongs in the app.
- If paid plans are introduced later, subscription selection is a distinct, dismissible screen that spells out recurring price, period, included limits, renewal, trial, cancellation, and restore. Do not interrupt the first-use template workflow with an unvalidated paywall.
- Provide clear loading, offline, expired-session, verification-pending, payment-pending, and account-deletion states. Avoid displaying sensitive media titles or thumbnails in notifications and lock-screen content.

## 11. Prototype and validation plan

Create clickable prototypes for three competing authoring patterns:

1. Section cards only.
2. Section cards plus compact timeline (recommended starting hypothesis).
3. Timeline-first editor.

Test with novice creators and experienced short-video editors using partial references, attached intros/outros, mixed aspect ratios, beat edits, spoken jokes, and tutorials. Observe whether people can remove unwanted source material, understand replacement slots, and complete a saved recipe without help. Compare task success, time, boundary-correction burden, accidental inclusion, confidence, and perceived complexity. Test color/typography and preview panel placement separately from workflow to avoid conflating visual preference with usability.

Do not produce a high-fidelity final UI kit or lock a visual identity until the workflow prototype has passed these tests. Record unresolved questions and revise the screen model before production frontend implementation.

## 12. Evidence and limitations

Competitor sources here describe current documented workflows, not a complete independent usability audit. Feature access and interface details can vary by version, account, and region. We have not yet run creator interviews or hands-on app testing; all proposed differentiators and UI patterns remain hypotheses. Official platform accessibility guidance supports the interaction constraints cited above.
