# Copyright, Rights, and Asset Provenance

**Prepared:** 3 October 2026  
**Status:** Product safeguards and legal-review checklist. This is not legal advice or a conclusion that any specific import, analysis, transformation, or export is lawful. Launch markets and counsel review are still open.  
**Related:** [MVP coverage and traceability](mvp_coverage_and_traceability.md), [video workflow](video_template_workflow_spec.md), [privacy and data lifecycle](media_privacy_security_and_data_lifecycle.md), [account/security research](../research/account_security_monetization_and_editor_scope.md).

## 1. Product rule: editing does not clear rights

Changing a soundtrack, pitch, tone, caption, crop, color, or a few frames does not automatically make a copied video, film scene, performance, song, lyrics, photograph, or other protected material safe to use. The U.S. Copyright Office explains that there is no fixed safe number of words, notes, or percentage for fair use, that fair use depends on the facts, and that only the rights holder may authorize a derivative version absent an applicable exception. Copyright rules and exceptions vary by country. [U.S. Copyright Office fair-use FAQ](https://www.copyright.gov/help/faq/faq-fairuse.html), [Copyright in Derivative Works](https://www.copyright.gov/eco/help/limitation.html)

Product consequences:

- Never label an edit as "copyright-free", "copyright-safe", or "cleared" merely because audio/text was replaced or the video was transformed.
- The user's permission to process an upload and the user's right to publish/export it are different questions. A confirmation checkbox is evidence of a user statement, not a license, legal determination, or protection for the app.
- Treat social-media availability or the ability to save a file as neither proof of ownership nor permission to download, adapt, reuse, or publish it. The MVP should not scrape social platforms, bypass download controls, or provide downloader instructions/integrations.
- Support an educational, private structure-extraction workflow while making retained reference footage opt-in and defaulting new outputs to user-selected replacement media. Private/local handling reduces distribution by the app but is not represented as a universal legal exemption.
- If the user cannot confirm a suitable right, offer a structure-only recipe with reference pixels/audio omitted from saved template and export; allow them to stop. This is a product choice, not a guarantee that analysis itself is lawful in every jurisdiction.

## 2. Rights attach to more than the music track

One short clip can include several independently controlled or regulated elements. Capture enough provenance to identify what an asset is and how the user says it may be used; do not infer permission from its file source.

| Element | Examples | Product handling |
|---|---|---|
| Audiovisual work | Film/TV scene, creator video, sports footage, animation, transition or edit | Record as a distinct source asset; preserve original-source status; default to replace/exclude in outputs. |
| Music composition | Melody, arrangement, lyrics | Separate from the sound recording; replacing the recording does not remove composition/lyric rights. |
| Sound recording / master | A particular studio track, live recording, sampled audio | Separate from composition; do not assume a platform music-library license applies to an exported MP4 or another platform. |
| Spoken performance | Dialogue, voiceover, podcast, recorded conversation | Track whether it is user-created, licensed, or third-party; protect private speech data; avoid promises that pitch or tone changes solve rights concerns. |
| Text and lyrics | Captions, quoted lines, subtitles, song lyrics, screenplay/dialogue | Keep source text distinct from user-authored replacement text; paraphrasing is not automatic clearance. |
| Image, art, logo, trademark | Brand marks, artwork, product packaging, photographs | Track asset provenance and display risk; do not imply endorsement or affiliation. |
| Person and performance | Face, likeness, voice, dancer/actor performance, bystanders | Rights and privacy/publicity/consent rules are market-specific; keep identity-changing or synthetic person edits outside the base MVP absent separate safety and legal review. |
| App/editorial template media | Sample clips, posters, tutorial audio, curated reference examples | App owner must obtain rights for the exact uses, markets, term, marketing, in-app display, modification, and export. Use synthetic or licensed assets in the shipped app and design prototype. |

For music, the composition (including lyrics) and a particular sound recording are separate works and commonly have different owners. U.S. Copyright Office materials further explain that synchronizing music with video can require rights for both the composition and the recording; a license to use a track in one platform's library must not be represented as automatically covering export or reuse elsewhere. Verify the actual license scope with counsel/provider. [Copyright Office: musical works and sound recordings](https://www.copyright.gov/engage/docs/recording.pdf), [Copyright Office: music and audiovisual licensing discussion](https://www.copyright.gov/music-modernization/educational-materials/musicians-income.pdf)

## 3. User experience and rights checkpoints

### Import / before analysis

Use a short, plain-language acknowledgment at the point it matters:

> I have the right or permission needed for this app to analyze this clip for my private template project. I understand this does not grant me permission to publish or reuse the original clip, music, dialogue, or other material.

This text needs review for the selected market and feature. Do not make the statement a warranty that the user's intended use is lawful or imply the app can verify ownership. Show the processing-location and retention disclosure separately; rights consent must not substitute for privacy/processing consent.

Allow a project to record the user's declared basis:

- I created/own the relevant material.
- I have permission or a license for this operation.
- I am using material under an exception or other legal basis (do not tell the user this applies automatically).
- I am unsure; continue only with the clearly described structure-only path or cancel.

The first three choices do not automatically authorize the final export, commercial use, or social platform use. Do not demand proof documents for ordinary local MVP use unless a specific hosted/public feature and counsel-reviewed policy require them.

### Section review / recipe creation

- Keep **Edit / Keep / Exclude** semantics explicit: **Edit** means a replaceable slot; **Keep** retains source material and requires an explicit confirmation; **Exclude** removes it from all later recipe/render inputs.
- Report the number and type of retained source assets, including original video and audio, before saving.
- Default to replacement-only output. Offer **Replace all reference media** and an audio removal/mute path.
- Show where a template stores a reference asset versus a reusable instruction. Do not package reference pixels, audio, recognizable frames, or extracted source text in a shareable recipe unless an independently approved rights path exists.
- A timing/shot-structure recipe may still recreate a distinctive protected arrangement. Do not describe a recipe as non-infringing solely because the media bytes were removed.

### Audio and text editing

- Present separate controls for source audio, replacement music, voice, effects, captions, and title text; label what remains in the output.
- A sound tone or pitch control changes a technical parameter, not rights clearance. Muting source music protects only against carrying that music forward; source footage, dialogue, lyrics, composition, performance, and other rights remain separate.
- If a licensed catalog is added, filter choices by actual destination, territory, commercial/personal use, edit/remix, synchronization, duration, expiry, attribution, and export terms. The UI must not show a track for a use its license does not cover.
- Keep stock/generation prompts separate from provided assets. A prompt has no asset license. Generated outputs require provider terms, provenance, likeness/voice safeguards, and a separate legal/policy gate.

### Preview / export

Before final render, summarize:

- Which source-video spans, source audio, text/lyrics, and third-party assets remain.
- The declared provenance/license status and any missing, expired, destination-limited, or attribution-required rights information.
- Destination is a local MP4 / system share handoff; do not say the app has cleared a downstream social platform's rights checks.
- A clear stop/replace/mute option. Do not use an alarming false legal warning for ordinary user-owned content, but do not silently label unknown rights as approved.

Use statuses like **User says owned**, **License details recorded**, **Permission not confirmed**, **Expired**, or **Destination not covered**. Avoid a universal green "copyright cleared" badge. The app cannot adjudicate fair use or another country's exception.

## 4. Rights and provenance data contract

Each asset and render layer should carry a versioned provenance record. Store user declarations and license metadata separately from verified facts; mark the provenance source and last review time.

Suggested fields:

```json
{
  "asset_id": "stable-id",
  "asset_kind": "source_video | composition | sound_recording | text | image | voice | generated",
  "origin": "user_import | app_catalog | generated | app_authored",
  "rights_status": "unknown | user_declared_owned | permission_declared | license_recorded | expired | restricted",
  "declared_basis": "user_selected_value",
  "rights_holder_or_provider": null,
  "license_reference": null,
  "allowed_actions": ["private_analysis", "edit", "export"],
  "allowed_destinations": [],
  "territories": [],
  "commercial_use": "unknown | allowed | prohibited",
  "derivatives_allowed": "unknown | allowed | prohibited",
  "attribution_text": null,
  "valid_from": null,
  "expires_at": null,
  "declaration_timestamp": null,
  "provenance_confidence": "user_declared | provider_verified | app_owned"
}
```

The schema must support distinct rights for the composition, recording, underlying audiovisual source, and user replacement. `allowed_actions` and destination checks are product bookkeeping, not a machine legal opinion. Retain a rights snapshot with each immutable render snapshot so project changes cannot silently drop provenance.

## 5. MVP scope and operational boundaries

### Include

- Local import of user-selected media; rights/processing notices at separate decision points.
- User-declared provenance, visible source-retention state, and a pre-export rights summary.
- Structure-only recipe path; replacement-only outputs by default; explicit retained-source confirmation.
- App-authored instructions and synthetic demonstration media, or third-party content with a documented license for exact use.
- Help explaining that changing music/text does not clear other rights and that platform music licenses may have scope limits.
- Internal contact route for rights reports about app-owned curated content, even while the product has no public template marketplace.

### Defer until a separate launch gate

- Public template publishing, user-uploaded template catalog, searchable public profiles, remix feed, hosted video, or in-app public sharing. These require documented terms, IP complaint/takedown process, moderation/reporting, repeat-infringer/abuse handling as legally applicable, staffing, response targets, and region-specific legal review.
- Social-platform scraping/download integrations, automated reuse of platform content, or promises of monetization eligibility.
- Licensed music/video catalog until provider rights explicitly cover synchronization, edits, exports, destinations, regions, term, attribution, and commercial scope.
- Automated fair-use decisions or a badge that declares an upload safe to publish.

Apple's current review guidance requires authorization for third-party content used by the app and has dedicated expectations for user-generated-content services. Google Play likewise defines UGC based on content accessible to some subset of users and requires terms/moderation/report/block controls for apps hosting UGC. The MVP's private local projects and MP4 exports are not the same as a public UGC marketplace; if public hosting is later introduced, re-review the then-current policies and implement the applicable safeguards before launch. [Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), [Google Play UGC policy](https://support.google.com/googleplay/android-developer/answer/9876937)

## 6. Acceptance requirements

| ID | Acceptance check |
|---|---|
| RGT-001 | Replacing, muting, pitching, or changing text never produces UI copy claiming the retained video or new output is copyright-safe. |
| RGT-002 | Import notice distinguishes authority to analyze from permission to publish; processing-location/retention consent remains separate. |
| RGT-003 | A project with unknown rights can take the structure-only path; unknown rights never appear as verified/cleared. |
| RGT-004 | Any retained reference video, audio, text, or other asset is listed before recipe save and render, with replace/mute/exclude actions where technically applicable. |
| RGT-005 | Excluded source spans and removed source audio do not enter render inputs; retained source is included only after explicit confirmation and is visible in the output summary. |
| RGT-006 | Music provenance can represent composition and sound recording separately, plus destination/territory/term/attribution constraints. |
| RGT-007 | App-owned inspiration examples have an auditable source and permission/license record for shipped display and any downstream export. |
| RGT-008 | Project deletion removes app-owned local source/derivatives as described in the [data lifecycle plan](media_privacy_security_and_data_lifecycle.md); external downloads remain outside app control. |
| RGT-009 | No public UGC/marketplace feature ships without terms, reporting/takedown, moderation operations, and store/legal re-review. |

## 7. Open legal/product decisions

| Decision | Open question | Why still open |
|---|---|---|
| DEC-001 | Target jurisdictions, age policy, and privacy/copyright laws? | Product/launch market has not been selected; rights exceptions and publicity/privacy rules differ. |
| DEC-007 | Licensed asset provider and exact license scope? | Provider, destinations, territory, cost, rights metadata, and export permissions are unknown. |
| DEC-017 | What retained-source use will the product permit in MVP? | Needs market-specific legal analysis of import, local analysis, private storage, transformation, and export; default proposed is replacement-only outputs. |
| DEC-018 | What is the rights complaint/takedown path for app-owned/editorial content? | Even without public UGC, app owner needs a route for its own catalog, and future hosting would add operational obligations. |
| DEC-019 | What rights metadata and review evidence are required for curated examples? | Catalog format, source owners, licenses, territories, term, marketing/display and reuse permissions must be chosen. |

## 8. Primary sources and limits

- U.S. Copyright Office, [Fair Use FAQ](https://www.copyright.gov/help/faq/faq-fairuse.html), [Fair Use Index](https://www.copyright.gov/fair-use/), and [Derivative Works](https://www.copyright.gov/eco/help/limitation.html).
- U.S. Copyright Office, [Musical Works, Sound Recordings & Copyright](https://www.copyright.gov/engage/docs/recording.pdf) and [music licensing educational material](https://www.copyright.gov/music-modernization/educational-materials/musicians-income.pdf).
- Apple, [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/).
- Google Play, [User-generated content policy](https://support.google.com/googleplay/android-developer/answer/9876937).

These sources give a U.S. copyright baseline and current storefront policy examples, not a complete global legal survey. Recheck all policies and obtain qualified counsel for selected markets before release, especially if the product moves from private local editing to cloud processing, public sharing, licensing, or monetization.
