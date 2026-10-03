# MVP Product Blueprint: Viral Video to Reusable Template

**Status:** Product direction agreed; detailed requirements remain subject to user and technical validation  
**Related research:** [Product strategy and competitive research](../research/product_strategy_and_competitive_research.md), [technology and design research](../research/mvp_technology_and_design_research.md), [mobile frontend design specification](../design/mobile_frontend_design_spec.md), [account/security/monetization/editor scope research](../research/account_security_monetization_and_editor_scope.md), [software evolution and AI change-safety plan](../research/software_evolution_and_ai_change_safety.md)  
**Detailed workflow:** [Video-to-template workflow specification](video_template_workflow_spec.md)
**Coverage and implementation tracking:** [MVP coverage and traceability map](mvp_coverage_and_traceability.md)
**Expected-functionality baseline:** [Product-owner requirements and research crosswalk](expected_functionality_and_research_map.md)
**Product:** Mobile-first app that analyzes short reference videos, turns them into editable reusable templates, and exports template-based videos for users to download and finish in their preferred editor.

## 1. Product definition

### Agreed product decisions

- The MVP focuses on analyzing a short reference video, shaping it into an editable reusable template, filling its slots, previewing, and exporting a standard video file.
- Keep creation local and accountless where feasible; ask for sign-in only for account-based capabilities such as cloud sync or backup.
- Do not launch with a subscription paywall. Revisit monetization after repeat use and ongoing costs are measured.
- Do not build a professional multitrack editor into the MVP. Consider a bounded finishing editor only if creator research shows that MP4 handoff is a meaningful obstacle.
- iOS and Android are the intended mobile platforms. The app framework, renderer, backend, and authentication provider remain unselected until the comparative technical and market research gates are complete.
- Build for safe, isolated upgrades: named feature boundaries, small public contracts, versioned saved templates, explicit migrations, and scoped AI/developer changes with impact verification and rollback.

### Vision

Help people turn a short video they admire into an editable reusable template, use it to create videos from their own replacement media, and download the results. A template defines selected sections, timing, text, sound, transitions, effects, overlays, and optional visual transformations. In the first release, the user edits within that template and downloads the rendered video file; adding arbitrary extra clips before or after it in a full timeline editor is a later capability.

### Primary outcome

A user can import a complete or partial reference video, review its detected sections, choose for each section to edit, keep, or exclude it, adapt the text/audio/visual treatment, preview the composition, and confirm it as a reusable template. They can save and reopen the editable template in the app, use it with their own replacement media to create a video, then download the rendered video file.

### Product principles

1. **Explain the method.** Every template communicates the purpose of its sections and what kind of footage belongs in each.
2. **Keep creators in control.** AI proposes structure; users can inspect and correct it.
3. **Make reuse create variety.** Reuse applies an editable composition to new footage and supports changes to story, pacing, message, people or characters, objects, backgrounds, text, and sound.
4. **Make rights and provenance visible.** The reference is an inspiration and analysis input; it is not automatically reusable source content.
5. **Make the first success fast.** Beginners should be able to make a useful first export without understanding a professional editing timeline.
6. **Measure creation value.** Success is a completed, reusable output—not just a template view or AI analysis result.

## 2. Target users for the first release

### Primary: emerging creator

Posts short videos but does not know how to plan scenes, hooks, timing, or text. Wants to recreate a format using their own footage without learning a complex editor.

### Secondary: solo business creator

Needs repeatable product, service, or behind-the-scenes videos. Wants saved brand information and multiple versions without rebuilding each post.

### Later: template creator and curator

Packages useful creative structures for the community or publishes a reviewed collection. This role needs moderation, rights, attribution, and analytics and should follow proof of the private creation loop.

## 3. Primary journey

```text
Home
  -> Create from a video / Browse inspiration
  -> Import reference (<= 30 seconds)
  -> Confirm use rights and analysis consent
  -> Analyze video
  -> Review proposed sections and correct them
  -> For each section: edit / keep / exclude
  -> Get replacement ideas for sections marked Edit
  -> Choose new text, voice, music, and sound effects
  -> Choose own media, record a suggested shot, use a licensed asset, or generate an eligible replacement
  -> Edit text, audio, tone, timing, and effects
  -> Preview the proposed template edit
  -> Confirm and save editable private template
  -> Reopen template and add/replace media in its defined sections
  -> Preview the template-based video and fix issues
  -> Render and download video file
  -> Continue editing in another video editor if desired
  -> Save as a new version or reusable section
```

The user can skip importing a reference by starting with a curated app template. Both entry points lead to the same recipe and editing model.

## 4. MVP scope

### Must have

- Mobile onboarding with a clear explanation of reference-video use and a no-virality-guarantee promise.
- A small, app-owner-curated inspiration hub organized by the target video categories, with a working **Use this template** path. Keep the first catalog intentionally small; grow it after the create/reuse workflow works.
- Accountless local creation where feasible; explain and request sign-in only when an account-bound feature such as cloud sync is needed. Provide secure recovery, sign-out, and account deletion if authentication is included.
- Essential settings for creator defaults, privacy/media retention, accessibility, notification preferences, and help. Request protected-resource and notification permission only in context.
- Import a local reference video up to 30 seconds; validate duration, format, size, and decodeability before analysis.
- Analyze the complete time-aligned component inventory: media integrity, shot boundaries, people/objects/actions/background/layout, visible text/marks, speech, music/sound/beat cues, and creative-beat role hypotheses. Show per-signal coverage and uncertainty before the user edits sections; incomplete analysis remains clearly partial with a manual path.
- Classify the template's creative format and editing intent, allowing multiple tags such as song/beat edit, cinematic/film, action, comedy/funny, storytime, tutorial, and product showcase.
- Show a reviewable section timeline with uncertain findings clearly marked.
- Present the analyzed video as an ordered component map and proposed section list with thumbnails/evidence, timestamps, duration, short descriptions, signal coverage, and uncertainty. Keep shot boundaries distinct from creative sections.
- For every section, let the user choose **Edit this section**, **Keep this section as-is**, or **Do not include this section**. Make the selected action visible in the section list.
- Allow users to rename, split, merge, reorder, trim, or mark sections optional before deciding their action.
- Allow users to remove attached intros/outros, unwanted overlays or segments, repeated footage, blank portions, and unusable partial sections from the template structure.
- Suggest replacement ideas for sections marked Edit, based on section role, visible content, template goal, and optional user brief. Suggestions can be shot prompts, user-library matches, licensed assets, or generated concepts where supported.
- Keep suggestions optional. Never silently replace a section or treat a suggested/generated asset as user-approved.
- Let users edit or replace on-screen text, captions, narration/voiceover, music, and sound effects; let them mute or remove source audio and adjust levels/mix.
- Offer original text rewrites and alternative audio moods (for example, calm, playful, dramatic, or energetic) as optional ideas. Suggestions must be editable, labeled, and never applied without user approval.
- Show audio asset source, license/usage scope, and supported platforms. Do not imply that changing audio, text, or other elements automatically makes a video copyright-safe.
- Save the confirmed template as an editable in-app project that users can reopen, revise, duplicate, and reuse.
- Let users add or replace media in the template's defined sections, then align, trim, crop, or retime it according to the recipe, with user review.
- Support music/beat-driven templates with editable beat markers and timing alignment; support dialogue, action, comedy, story, and tutorial formats with pacing that is not forced onto a beat grid.
- Preview the proposed edits and assembled result using included sections only; confirm before saving the reusable template. Excluded sections must not appear in that template or its generated outputs.
- Generate a structured template recipe with editable text, media slots, durations, transition guidance, and aspect ratio.
- Explain each slot with a prompt and an example (e.g. “show the result first; use a close-up”).
- Select, trim, and crop personal replacement clips; provide framing and duration fit guidance.
- Basic editor controls for text, section order, timing, crop, volume, and approved transitions.
- A visual-layer editor for supported footage, limited to transformations that pass the cross-platform quality spike. Whole-section replacement with user-selected media is the baseline; tracked background replacement is conditional. Generative person/character replacement is a research item and must not be promised as a general MVP feature.
- Text/audio controls for changing captions and titles, replacing or muting source audio, adding voiceover, selecting licensed music/effects, and previewing the mix.
- For any supported AI-assisted visual edit, preserve section timing and show before/after with undo/restore. Make limitations visible for motion, lighting, and occlusion; do not describe segmentation as person/character replacement.
- Make background edits separate from person/character edits. Label generated or materially altered visuals clearly.
- Preview the full video and identify unresolved issues before export.
- Export a vertical short video up to 30 seconds, with resolution and audio behavior shown before rendering.
- Preview the template-based video with selected replacement clips before export; warn about duration, missing sections, audio mismatch, and unsupported effects.
- Render and download the result as a standard video file (MP4 as the initial target); retain the editable template separately in the app.
- Save projects and private templates; duplicate a template to create another version.
- Create a saved custom section from a user’s own project.
- Include template source/provenance fields and a clear confirmation that users have rights to upload and publish their inputs.
- Enforce 30-second policy in both user interface and backend processing gate.

### Should have if validation supports it

- Search and filters for goal, category, required footage, duration, and aspect ratio.
- Creator profile settings for logo, colors, preferred tone, and default call to action.
- A/B preview of two hook or ending alternatives.
- Export presets for selected social platforms, without claiming privileged platform access.

### Not in MVP

- Public user-generated template marketplace.
- Monetization, creator payouts, follows, comments, and social graph.
- Full professional multi-track editing suite.
- Arbitrary extra clip insertion before or after a template in a general-purpose timeline editor (future release).
- Unlimited, frame-perfect generative replacement for arbitrary subjects or footage in the first release.
- Automated scraping or downloading of videos from social platforms.
- Guaranteed virality scoring or audience-performance predictions.
- Automated publishing to third-party accounts.
- Unreviewed AI publishing of public templates.
- A general professional multitrack editing suite. The MVP exports a template-based MP4 for further editing elsewhere; a bounded Finishing Studio may be assessed after the core workflow is validated.
- Subscription paywalls at launch unless user research and variable-cost analysis validate a recurring paid offer. Keep plan/billing UX out of the first-use flow.

## 5. Screen and interaction requirements

### Home

Primary actions: **Create from a video**, **Use an app template**, **My templates**. Inspiration should be secondary until its catalog is useful. A card must disclose duration, required clip count, output format, creative format (such as music edit, cinematic, action, comedy/funny, story, or tutorial), and template purpose.

### Import and permission

Show the reference duration and source before analysis. Explain that the app analyzes the video to infer structure. Ask for the minimum permissions needed, in context. Do not imply that uploading grants rights to publish or reuse the reference content.

### Analysis progress

Use honest stage-based progress (uploading, inspecting, detecting sections, preparing preview). Do not display a fabricated percentage. If a step fails, preserve the uploaded project and give a clear retry or manual-template option.

### Recipe review

Show a vertical preview plus an ordered section list. Every detected section has a thumbnail, timestamp range, duration, label, purpose, and confidence state. The user can correct boundaries and labels before accepting the analysis. Distinguish “app suggestion” from source fact.

Each section has three clear decisions: **Edit**, **Keep**, or **Exclude**. “Edit” makes the section a user-editable part of the future template; “Keep” retains it unchanged as part of the template; “Exclude” removes it from the assembled template. Explain the difference between keeping reference content and using the user's replacement media. Users can also trim/split/merge sections when the automated boundaries are not right. Partial clips are valid inputs: the app should describe only what is present, mark uncertain section roles, and let the user exclude fragments that do not make sense in the final sequence.

The preview must update as sections are excluded, reordered, or trimmed. Before template creation, show the included sequence, its total duration, and any gaps or transition changes caused by exclusions. Require a clear confirmation action to create/save the template.

For sections marked Edit, show a few relevant replacement ideas before template confirmation. Each idea should explain what to capture or insert and why it fits the section (for example, “replace the opening close-up with your product in use to keep the visual hook”). Let the user accept, edit, skip, or request alternatives. Support user-owned media, an in-app shot prompt/capture flow, licensed assets, or generated replacements where available. Label the origin of every suggestion and asset. Do not imply that an idea will improve virality.

Also allow users to revise text and audio before confirmation. Text suggestions can preserve the section's role (such as a hook or call to action) while using new wording suited to the user's topic. Audio options can include muting source audio, using the user's own audio, selecting a licensed track/effect, adding narration, or generating an eligible sound bed. Let users preview timing, voice/tone, and mix in context. Track the source and applicable usage permission of every audio/text asset where relevant.

Before final template creation, offer a draft preview. If the user has not supplied replacement media, use a clearly labeled placeholder preview or let them privately preview the reference section; do not present it as the finished reusable output. When replacements are supplied, preview those in the selected sequence. The confirmation step summarizes included/excluded sections, replacement sources, total duration, and unresolved placeholders. Saving preserves editable slots and user-approved defaults.

### Template editor

Use approachable section cards first; expose a detailed timeline as an optional advanced view. The recipe is an editable composition of media slots and audio, text, and effect layers. Later, when the user applies it to new video clips, each slot shows:

- What to capture or select.
- Suggested duration and framing.
- Whether the slot is required or optional.
- Accepted media type and crop behavior.
- Any text/audio/effect that will remain fixed or can be edited.

When duration changes, ask how to adapt timing: preserve beats, preserve total duration, or preserve the selected clip length. Show resulting changes in preview.

### Visual transformation

Treat visual changes as explicit, reviewable operations on a section rather than silently changing the entire video. The baseline is **Replace this section with my image/video**. Offer **Change background** only for supported shots after segmentation and render-quality validation. Person/character generation, object removal, and inpainting are later research capabilities unless their quality, consent, and safety pass separate gates. If subject isolation is unreliable, allow manual region selection or explain that the edit is unsupported.

Before applying an edit, let the user choose the replacement asset: their own upload, a licensed library asset, or a generated description where available. Preserve the original as a reversible version. Show a side-by-side or wipe preview; let users refine the selection, retry, undo, or restore. Apply changes to one section by default, with an explicit option to apply them to matching sections.

The app should aim to preserve movement and scene continuity, while explaining limits. Fast motion, hair, transparent objects, shadows, reflections, occlusion, camera cuts, and low-resolution footage can cause artifacts. Run an artifact check before export and do not present generated replacement imagery as authentic footage.

### Export

Run checks for missing media, text overflow, invalid duration, crop/framing problems, unsupported assets, and audio. Clearly show quality and export settings. Save the rendered result to the device as a standard video file. In the first release, users can take that file to another video editor to add other clips or make further edits; direct posting and an in-app full timeline are later options.

## 6. Template recipe: minimum conceptual schema

The recipe must remain independent of a single video-rendering engine. One possible shape:

```json
{
  "id": "template-id",
  "schema_version": 1,
  "title": "Before to after reveal",
  "purpose": "Show a visible transformation quickly",
  "audience": ["small_business", "creator"],
  "source_provenance": {
    "source_type": "user_upload",
    "creator_id": "user-id",
    "rights_declaration": "confirmed",
    "analysis_version": "versioned-tool-chain"
  },
  "output_profiles": [{"aspect_ratio": "9:16", "max_duration_seconds": 30}],
  "sections": [
    {
      "id": "hook",
      "role": "hook",
      "purpose": "Show the outcome before explaining it",
      "required": true,
      "duration_seconds": {"target": 2.0, "min": 1.0, "max": 4.0},
      "media_slot": {
        "prompt": "Show the finished result clearly",
        "framing": "close_up",
        "accepted_types": ["video", "image"]
      },
      "layers": [],
      "adaptation_rules": {"timing_mode": "flexible", "can_reorder": false},
      "analysis": {"confidence": 0.82, "review_state": "user_confirmed"}
    }
  ]
}
```

This is a discussion shape, not a final API schema. The model should also define captions, soundtrack references, transitions, effects, overlays, color treatment, safe areas, localization, and render compatibility before public templates are introduced.

The final schema should make the template reusable across source videos: encode edit instructions and placeholders independently from the reference video's actual media. It should support synchronized music/beat edits as well as non-music-led timing for film/cinematic, action, comedy/funny, dialogue/story, and tutorial formats. The initial renderer creates the video defined by the template and its selected replacement media. A later full editor can support arbitrary extra clips, longer compositions, and direct sharing.

## 7. Acceptance criteria for the first end-to-end prototype

The prototype is ready for creator testing when:

1. A reference video longer than 30 seconds is rejected before full decode, with a clear user message.
2. A valid reference can be analyzed and shown as an editable sequence of sections.
3. Each section can be assigned Edit, Keep, or Exclude; an excluded section is absent from the assembled preview and saved recipe.
4. A user can correct section boundaries and analysis mistakes without restarting the project.
5. Every section marked Edit receives at least one relevant, clearly labeled replacement idea; the user can skip or reject it.
6. The preview updates correctly after trimming, reordering, excluding a section, or accepting a replacement and shows the resulting duration.
7. The user can preview a draft before confirming and saving a reusable template; unresolved placeholders are clearly labeled.
8. The confirmation summarizes included/excluded sections and replacement asset origins.
9. Each editable section communicates what replacement media is needed and why it exists.
10. A user can replace media, revise text, replace or mute source audio, add voiceover/music/effects, change selected timings, and preview the result.
11. A user can change the background or replace a supported person/character/object, preview the change, undo it, and export; unsupported or low-confidence selections are clearly surfaced.
12. The resulting export contains only selected/confirmed sections and user-approved media and follows duration/aspect constraints.
13. The user can save and reopen an editable recipe privately, fill its defined media sections, and create a second output from the same template.
14. The rendered video downloads as a playable standard video file, while the editable template remains saved separately in the app.
15. Source media is not silently included in a public template or export when the user has selected replacement-only behavior.
16. Failures preserve enough job state to retry without losing the reviewed recipe.
17. Users can explain in their own words what the template preserved and what they changed.

Suggested usability target for early testing: at least 8 of 10 first-time participants complete a usable export with no facilitator intervention after onboarding. Treat this as a prototype target, not a claim about expected production performance.

## 8. Outcome metrics

### North-star candidate

**Weekly creators who export two or more meaningfully distinct videos from a saved recipe.**

### Supporting measures

- Import-to-reviewed-recipe completion.
- Median time from import to first export.
- Analysis correction minutes and correction types.
- Export completion and render failure rates by device class.
- Second-version creation within 7 days.
- Percentage of outputs where a user changes story, hook, order, or pacing (not only source footage).
- Template save/reuse rate.
- Rights/report issue rate and moderation response time once publishing exists.
- User-rated confidence that the recipe is understandable and adaptable.

Segment all results by novice/experienced creator and personal/business use. Do not optimize template plays as a proxy for useful creation.

## 9. Phased roadmap

### Phase 0 — Validate the need

Interview creators, observe current recreation workflows, test a clickable prototype, and manually produce recipes from example videos. Validate which formats users repeatedly need and what “different enough” means to them.

**Exit:** users value the analysis explanation and reuse loop over a simple template swap; a few high-value formats are clear.

### Phase 1 — Private creation loop

Build import, full component-analysis review, recipe editing, replacement media, basic rendering, private save, and reuse. Ship the small app-owned, category-based starter catalog in this phase; expand it after the core workflow works. Start with a small set of formats and device targets.

**Exit:** users reliably finish and reuse templates; analysis and export errors are measurable and fixable.

### Phase 2 — Expand curated inspiration

Grow the initial app-owned starter catalog with transparent quality, format, footage requirements, freshness, and rights information. Improve editorial tooling, search, and catalog updates. Add creator profiles and brand presets if testing shows repeated demand.

**Exit:** hub discovery leads to successful first exports and repeat usage.

### Phase 3 — Creator publishing and community

Add submission review, moderation, attribution, takedown/reporting, versioning, creator analytics, and optional monetization only after rights and operational controls are ready.

**Exit:** template supply is high quality, support load is manageable, and creators understand ownership and remix rules.

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Analysis mislabels narrative intent | User-confirmed labels, confidence, easy correction, and keep the recipe useful even with manual labels. |
| Generated work looks like a copy | Encourage replacement footage; offer meaningful structural variants; record derivation; establish reporting and removal controls. |
| Copyright or privacy issues | Default to private projects, require rights acknowledgment, avoid republishing reference media by default, define retention/deletion policy, and obtain legal review for public remix. |
| Users assume changing music or wording guarantees copyright clearance | Explain that edits do not automatically remove rights obligations; label asset rights and usage scope, default to user-owned or licensed replacements, and provide a pre-export rights checklist. |
| Users cannot capture suitable clips | Provide prompts, example framing, camera capture checklist, and fit diagnostics. |
| Editor scope grows to match incumbents | Keep advanced timeline features behind validated user needs; focus on template transformation and reuse. |
| “Viral” positioning overpromises | Describe the app as a creation and inspiration tool, not a reach predictor. |
| Catalog becomes stale or noisy | Start curated, show freshness, support expiry and quality standards, and rank by successful adaptation rather than views alone. |

## 11. Decisions needed before implementation expands

Resolve these through prototype testing and technical spikes:

1. First launch market, languages, and target creator segment.
2. iOS/Android launch order and minimum supported devices.
3. Whether analysis runs on-device, server-side, or in a hybrid flow.
4. Supported source media sizes, codecs, and retention/deletion policy.
5. Initial rendering engine and offline/online export requirements.
6. Whether the initial hub is curated editorial content, private user templates, or both.
7. How soundtrack selection and licensing will work by region and export destination.
8. What can be shared publicly and what attribution/remix permissions are required.
9. Which visual transformation operations can meet acceptable quality, latency, and cost on target devices and supported footage.

## 12. Recommended immediate work

1. Conduct creator interviews and concept/usability tests before building a public hub.
2. Select three to five repeatable video formats for a manually assisted prototype.
3. Define the versioned `TemplateRecipe` contract and example recipes.
4. Test analysis and editing using real user-provided videos, measuring correction burden.
5. Prototype the phone flow end to end and validate time to first export and second reuse.
6. Only then decide mobile stack, rendering architecture, and which parts of the existing Python pipeline should become services or be replaced.
