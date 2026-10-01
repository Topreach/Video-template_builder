# Product and Competitive Research: Video-to-Template Creator

**Prepared:** 1 October 2026  
**Purpose:** Align product direction before expanding implementation. This is desk research and product analysis, not user research or legal advice. Competitor features can vary by region, account, platform, and release.

## 1. Product vision

Build a mobile-first creator app that turns a short reference video (maximum 30 seconds) into an understandable, editable reusable template. The app splits complete or partial source videos into reviewable sections; users choose which sections to edit, keep, or exclude, adapt sound/text/effects, preview, and save the template in the app. They use its defined replacement slots to create a template-based video and download the rendered video file. In the first release, users can take that file to another editor to add extra footage or make further edits. A full in-app editor for arbitrary additional clips and direct publishing is a later phase. Support different creative formats—song/beat edits, film/cinematic, action, comedy/funny, story, tutorial, and more—without forcing every template into one editing pattern. The app also offers curated inspiration and lets users build and save their own reusable sections and templates.

The product is not simply “another editor with templates.” Its distinctive job is to help a creator understand *why a short video works*, translate that structure into editable parts, and make a set of new videos without requiring professional editing skills.

### Product promise to test

> Show us a short video you like. We’ll turn its structure into a reusable plan, help you make it yours, and let you create the next version quickly.

Avoid promises that a template will make a video go viral. Virality depends on creative quality, audience, distribution, timing, and platform systems; the app can improve the creation workflow but cannot guarantee reach.

## 2. Users and jobs to be done

| User | Need | Product opportunity |
|---|---|---|
| New creator | “I know what I like, but don’t know how to make it.” | Explain a reference as a simple sequence of shots, text, pacing, and actions. |
| Frequent creator | “I need to make more than one post without repeating myself.” | Generate meaningful variations and preserve a personal style. |
| Small business / solo marketer | “I need repeatable content that looks like my brand.” | Save brand voice, colors, logo, product facts, and recurring sections. |
| Template maker | “I want to package my creative method so others can use it.” | Build reusable sections, add clear prompts, test the template, and publish it. |
| App curator | “I need useful, safe, timely inspiration.” | Curate categories, review quality and rights, and retire stale trends. |

## 3. Competitive landscape

### CapCut

CapCut already has community templates, clip replacement, text editing, and template publishing for eligible creators. Its help material describes replaceable clips, including media-type and maximum-duration options in some workflows. The same material says defining replaceable clips is supported on mobile and web, but not desktop. Its documentation also advises template creators to limit replaceable clips and clearly cue users.

**Implication:** Clip swapping and a large template feed are table stakes. A possible opening is to make the template’s structure and intent editable: explain each section, allow changes to timing and order, recommend suitable footage, and make it easy to derive variations. Cross-device consistency is a potential differentiator, but should be validated rather than assumed to be a widespread pain point.

Sources: [CapCut replaceable material clips](https://www.capcut.com/help/how-to-set-replaceable-material-clips), [CapCut template creation](https://www.capcut.com/help/how-to-create-templates-in-capcut), [CapCut template use and export](https://www.capcut.com/help/use-and-export-templates-in-capcut).

### Canva

Canva emphasizes a large searchable template catalog, branded assets, and reusing a design across formats. It offers Brand Kits for logos, colors, fonts, and assets, and has a Bulk Create workflow for data-driven variants.

**Implication:** Brand consistency and efficient variants are expected capabilities for business-oriented creators. Our version should carry a creator’s identity through video sections and generated variants, not just allow a logo to be overlaid at the end.

Sources: [Canva video editor](https://www.canva.com/video-editor/), [Canva Brand Kit](https://www.canva.com/help/brand-kit/), [Canva Bulk Create](https://www.canva.com/help/bulk-create/).

### Adobe Express

Adobe Express offers mobile video templates, search by channel, video type, aesthetic, or niche, and supports customizing colors, fonts, and imagery. Its mobile guidance covers scenes, transitions, and design elements.

**Implication:** Broad templates and basic customizability are also established territory. Our differentiation should be the transformation from a reference clip to a guided, reusable structure and the quality of the creator workflow around that transformation.

Sources: [Adobe mobile video templates](https://www.adobe.com/express/templates/video/mobile), [Adobe Express video creation on mobile](https://helpx.adobe.com/au/express/mobile/video-creation-and-editing/create-videos/create-videos.html).

### Meta Edits

Meta describes Edits as a mobile video creation app with direct sharing to Instagram and Facebook, and Meta has announced AI video-editing tools across Edits and its other products.

**Implication:** Platform-native editors can make editing and publishing convenient. We should be useful across multiple destinations and should not base the business on privileged access to any single platform’s feed or algorithm.

Source: [Meta announcement about AI video editing in Edits](https://about.fb.com/news/2025/06/edit-videos-with-meta-ai/).

## 4. Template design patterns and observed weaknesses

These findings combine competitor documentation and anecdotal user reports. They identify design risks and opportunities; they do **not** establish how common each pain point is. User interviews and usability testing should verify them.

| Common pattern / weakness | Evidence and confidence | How our product could improve it |
|---|---|---|
| Replaceable clips are chosen by the template author; users may not know what footage belongs in each slot. | CapCut provides explicit replaceable-clip setup and recommends cues and a small number of editable clips. **Documented workflow; user impact to validate.** | Give every slot a purpose, example, framing guide, suggested duration, and a sample shot prompt. Offer optional auto-matching from the user’s camera roll. |
| Fixed clip slots can make it difficult to fit footage or change pacing. | Third-party forum and community posts report frustration with short fixed slots and limited timing changes. This is anecdotal, not representative research. | Let users change section duration, reorder or remove optional sections, and choose “keep beat,” “keep total length,” or “keep clip duration” when the timing changes. |
| A template can produce a recognizable copy rather than a distinctive new idea. | This is a product-design inference from repeated use of the same fixed sequence; prevalence and audience response need testing. | Provide structured variation: alternate hooks, section order, tone, text angle, shot type, and ending. Show which creative ingredients are preserved and which are changed. |
| Template discovery can be organized around trends or aesthetics without enough context to choose well. | Competitors expose search, categories, and template metadata; the precise discovery problem is not measured here. | Explain what the template is for, what source footage it needs, difficulty, duration, suitable platforms, and why it may fit the user’s brief. |
| A trend can be stale or culturally inappropriate by the time a user finds or reuses it. | Product risk based on the fast-changing nature of trends; validate through creator research. | Show freshness and last-reviewed dates, allow curators to expire templates, and provide a timeless “structure” alternative when a specific trend fades. |
| The source may contain music, footage, faces, or marks the user cannot republish. | CapCut itself reminds template creators to check soundtrack copyright compliance. | Keep source analysis distinct from permission to reuse. Use user-owned or licensed replacement media, show rights prompts, and support takedown/reporting and provenance records. |

Research source for anecdotal fixed-duration pain: [CapCut community discussion about template timing](https://www.capeditcut.com/community/capcut-pro/editing-template-time-length/), plus individual community posts such as [short fixed clip slots](https://www.reddit.com/r/CapCut/comments/1px4s9q/how_do_i_edit_templates_to_fit_longer_clips/). Treat these as leads for user interviews, not as proof of broad market demand.

## 5. Differentiation: make the app “above ordinary templates”

### A. A reference-to-recipe engine

Represent each template as structured parts rather than a flattened video:

- **Creative intent:** audience, message, emotion, hook type, and call to action.
- **Sections:** role, order, target duration, optionality, and transitions.
- **Media slots:** expected subject/action, framing, orientation, minimum quality, and example prompt.
- **Text/audio/effect layers:** editable status, style constraints, timing, and source/license metadata.
- **Adaptation rules:** what may change, what must stay, and how to retime the rest.
- **Outputs:** supported aspect ratios, duration limits, safe areas, export settings, and platform-specific variants.

AI can propose this recipe, but users need a quick review screen to correct scene boundaries, text, and slot roles. The app should show confidence or mark uncertain detections rather than pretending every interpretation is correct.

### B. Guided creation, not just replacement

For each slot, tell users what to film or select: “Show the problem,” “Capture the product in use,” or “End with the result.” Add an optional shot checklist, framing guide, and examples. Let users capture missing shots from within the flow. This turns a template into a small production plan.

### C. Intentional variation

Offer variants with a purpose rather than random visual changes:

- Different hook: question, surprising result, problem statement, or reveal.
- Different narrative: before/after, steps, reaction, comparison, or mini-story.
- Different pacing: calm, standard, or energetic.
- Different audience and call to action.
- Different destination while preserving content and brand identity.

Always let the user preview and edit each change. Track lineage so a new template can be derived from another without silently copying creator-owned assets.

### D. Visual transformation beyond clip replacement

Let users change the person/character, foreground object, product, or background after the template is created. Keep these as separate, reversible edits with a before/after preview. The product should try to retain the original motion, timing, camera movement, and scene continuity while clearly exposing where the result may look imperfect. This extends a template from “put different footage in the same slot” to “reimagine the scene while retaining its useful composition.”

This capability depends on reliable subject selection, masks that track over time, and temporal consistency. It should be validated on supported footage and treated as a staged capability, not assumed to work perfectly for every video.

### E. A useful template hub

Make discovery answer “Can I make this with the footage I have?” Include search and filters for goal, category, duration, required clips, difficulty, aspect ratio, freshness, and rights status. Preview the editable structure and sample slot prompts, not only a finished example. Curated owner templates can establish high-quality standards; community publishing can expand variety later.

### F. A personal reusable library

Allow users to save sections (for example, intros, product demonstrations, captions, and calls to action), assemble them into their own template, and maintain a brand profile. Support private, link-only, and public sharing, with clear ownership and attribution settings.

## 6. Recommended MVP

Resist building a full CapCut replacement at the start. Prove that the video-to-recipe loop is valuable with a focused mobile product.

### MVP workflow

1. **Import:** accept a local video no longer than 30 seconds; validate duration, orientation, audio presence, and file decodability.
2. **Analyze:** detect candidate scenes/cuts, speech/text, audio beats, and basic motion/composition cues. Produce an editable timeline with uncertainty markers.
3. **Explain:** label each section’s likely role (hook, context, demonstration, payoff, CTA) and show a short reason for that label.
4. **Convert:** create a structured template with replaceable media slots, editable text, timing, and transition/audio guidance.
5. **Personalize:** let the user choose a goal/category and provide their own footage and text. Offer fit guidance and missing-shot prompts.
6. **Create variants:** produce a small number of editable alternatives, preserving user-selected elements.
7. **Export and save:** render a clean vertical video, save the template privately, and let the user reuse it.

### Defer until the core loop works

- A massive open community feed and creator monetization.
- A broad, professional-grade multitrack editor.
- Automated posting to every social platform.
- Claims or scoring that predict virality.
- Complex public remix chains before provenance, moderation, and rights workflows exist.

## 7. Success measures and research plan

### Product metrics

- **Time to first usable template:** upload to user-approved editable recipe.
- **Correction burden:** number and duration of manual fixes after analysis.
- **Time to first export:** start to finished video.
- **Reuse rate:** percentage of users who create a second output from the same recipe.
- **Originality action rate:** percentage who alter at least one meaningful creative dimension, not only replace media.
- **Completion rate:** percentage who finish after importing a reference.
- **Quality checks:** export failures, missing media, text overflow, crop mismatch, and audio sync issues.
- **Trust:** rights/ownership comprehension, report rate, and user confidence in detected sections.

Do not optimize for template views alone. A popular preview that users cannot adapt is not product success.

### Discovery before broad implementation

1. Interview 12–20 creators across beginners, small businesses, and frequent short-form publishers. Ask them to bring videos they have tried to recreate and observe their current workflow.
2. Run a concept test comparing (a) a normal clip-swap template and (b) an explained, editable recipe with guided shot prompts.
3. Build a clickable mobile prototype and measure task completion with users unfamiliar with video editing.
4. Test with a small set of reference formats (for example: before/after, product demo, storytime, tutorial, and mini-vlog) rather than an open-ended “all viral videos” promise.
5. Validate permission and publishing expectations with creators before enabling public template sharing.

## 8. Architecture implications for this repository

The existing Python project handles early technical video inspection, frame decoding, and heuristic quality scoring. It is useful as an analysis prototype, but it is not yet the mobile product or the template engine.

Before extending its current contracts, align the code with the product’s core data model:

- `SourceVideo`: identity, duration policy, technical metadata, rights/provenance declarations.
- `AnalysisRun`: versioned detections, timestamps, confidence, and tool/model versions.
- `TemplateRecipe`: sections, slots, timing constraints, layers, adaptation rules, and output profiles.
- `CreatorAssets`: media, brand settings, saved sections, and permissions.
- `RenderJob`: source mapping, edits, output configuration, status, and recoverable result.

Important foundation gaps include the absence of a user-facing mobile app, template schema, scene/section analysis, rendering/export pipeline, accounts, library/search, moderation, and rights management. The current 30-second policy should be enforced as a real processing gate, not only recorded as a probe state. See the existing [stage 2.1 contract](../specs/stage2_1_contract_boundary.md), which specifies an ingestion gate, and [stage 2.2 source identity](../specs/stage2_2_source_identity.md), whose project-state notes say implementation remains outstanding.

## 9. Risks and decisions to resolve

| Decision / risk | Recommendation |
|---|---|
| “Viral video” source | Start with user-uploaded local files and permitted links/imports only; do not build around scraping or downloading from platforms without authorization. |
| Rights to reference media | Analyze for structure while preventing accidental republishing of protected source footage/music. Make replacement media the default for exports. Obtain qualified legal review for public remix features. |
| What counts as a template | Freeze a versioned, platform-independent recipe schema before storing templates long term. Keep render implementation separate from recipe meaning. |
| AI reliability | Make analysis reviewable, expose uncertainty, and allow manual correction. Measure correction burden. |
| Viral promise | Position around faster learning and repeatable creation, never guaranteed reach. |
| Mobile scope | Choose iOS/Android strategy and rendering approach only after testing target-device performance, export reliability, and supported formats. |
| Community quality | Begin with curated content; add community publishing after reporting, moderation, provenance, and removal controls are ready. |

## 10. Research conclusion

The strongest opportunity is not to outnumber CapCut’s templates or match every editing feature. It is to make a short reference video understandable and reusable: split it into sections, let users select what to edit, keep, or exclude, confirm a clean sequence, guide them to capture suitable replacement footage, allow meaningful changes to pacing, story, and visual elements, and help them make several distinct outputs while retaining their own identity.

The next development decision should follow validation of that core loop. The current video-analysis code can support experiments in ingestion and media inspection, but the product direction requires a template recipe model and mobile-first user research before major feature expansion.

## Sources reviewed

- CapCut: [replaceable material clips](https://www.capcut.com/help/how-to-set-replaceable-material-clips), [create templates](https://www.capcut.com/help/how-to-create-templates-in-capcut), [use/export templates](https://www.capcut.com/help/use-and-export-templates-in-capcut).
- Canva: [video editor](https://www.canva.com/video-editor/), [Brand Kit](https://www.canva.com/help/brand-kit/), [Bulk Create](https://www.canva.com/help/bulk-create/).
- Adobe: [mobile video templates](https://www.adobe.com/express/templates/video/mobile), [mobile video editing](https://helpx.adobe.com/au/express/mobile/video-creation-and-editing/create-videos/create-videos.html).
- Meta: [AI video editing in Edits](https://about.fb.com/news/2025/06/edit-videos-with-meta-ai/).
- Anecdotal template timing discussions: [CapCut community forum](https://www.capeditcut.com/community/capcut-pro/editing-template-time-length/), [Reddit discussion](https://www.reddit.com/r/CapCut/comments/1px4s9q/how_do_i_edit_templates_to_fit_longer_clips/).
