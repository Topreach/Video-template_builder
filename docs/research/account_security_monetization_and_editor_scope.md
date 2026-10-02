# Account, Security, Monetization, and Editor Scope Research

**Prepared:** 1 October 2026  
**Status:** MVP direction agreed: local-first/accountless where feasible, no launch paywall, and no professional editor in v1. Authentication provider, monetization model, and future editor scope remain unselected.  
**Related:** [Mobile frontend design specification](../design/mobile_frontend_design_spec.md), [MVP product blueprint](../product/mvp_product_blueprint.md), [technology research](mvp_technology_and_design_research.md), [media privacy and lifecycle plan](../product/media_privacy_security_and_data_lifecycle.md)

## 1. Executive decisions

1. Let users explore and try a first local template workflow before forcing registration, unless a chosen cloud-analysis feature technically requires an account. Ask for account creation when they want cloud backup, cross-device sync, or other account-bound benefits.
2. Support secure email sign-in and platform identity providers only after choosing a backend. Avoid collecting profile details that are not necessary. Include account recovery, session management, sign-out, account deletion, and clear media deletion/retention controls.
3. Treat subscriptions as a later monetization experiment, not a launch requirement. First learn whether creators return and which recurring costs exist (licensed media, cloud storage, AI processing, support). If digital features are sold in-app, comply with the storefront and regional rules in force at release; these rules vary and change.
4. Notifications must be opt-in, useful, low-volume, and controllable. Core editing/export must work without push permission.
5. A professional multitrack editor is technically possible, but it is a separate large product investment. Keep the MVP focused on applying the template and downloading the MP4. A later finishing editor can be scoped as its own phase after creation/reuse demand is proven.

## 2. Account and profile requirements

### Account creation and login

- Offer **Continue without account** for local draft/template creation where feasible; explain which features require an account.
- Email sign-up/sign-in with verification and secure password reset, or passwordless email link if the selected identity provider supports reliable delivery and recovery.
- Add Apple/Google sign-in only after provider selection and correct platform configuration. Do not make social account linking necessary to create/export videos.
- Prevent account enumeration in recovery responses; rate-limit sign-in, reset, and verification requests; provide a clear locked/retry path.
- Show the account's verified email, linked identity providers, session/device list if supported, and sign-out controls.
- Keep identity separate from creator presentation. A creator profile (display name, avatar, bio, optional brand colors/logo) is optional and should not be confused with login identity.

### Guest-to-account migration

- On registration, offer to attach existing local projects and settings to the account.
- Detect ID conflicts and duplicates; never silently overwrite cloud projects with local versions.
- Explain that local media may remain on-device while only recipe metadata is synced, unless the user explicitly enables cloud media backup.
- If cloud analysis is used, disclose which exact clip data is uploaded, why, where it is processed, retention duration, and the deletion action before upload.

## 3. Settings information architecture

Use grouped settings rather than one long, undifferentiated screen:

| Group | Settings |
|---|---|
| Creator profile | Display name, avatar, optional logo/brand colors, preferred language/tone, caption defaults. |
| Account and security | Email/provider links, verification, password/recovery, active sessions, sign out, delete account. |
| Creation defaults | Default aspect ratio/profile, preferred resolution, caption behavior, audio preview behavior, save location. |
| Notifications | Product updates, render completion, template/editorial inspiration, account/security notices; category toggles and OS permission status. |
| Privacy and media | Processing mode disclosure, cloud backup toggle, source retention, delete source/project/export, analytics/AI controls, privacy notice. |
| Plan and billing | Current entitlement, renewal/expiry, restore purchases, manage/cancel subscription link, receipts/support. |
| Accessibility | Text size follows system, captions, reduced motion, haptic preference, contrast/appearance where supported. |
| Help and legal | Help center, report a problem, terms, privacy policy, copyright/asset license explanations. |

## 4. Notification policy and UX

- Do not request notification permission at first launch. Request contextually only after the user chooses a feature that benefits from notifications, such as a long cloud render.
- Explain the benefit before showing the operating-system prompt, then provide in-app category controls and respect an OS-level denial.
- MVP push use should be limited to render completion/failure only when the user has opted in and the render is remote/long-running. If rendering is local and fast, use in-app completion instead.
- Optional later notifications: saved-template updates or a user-requested reminder. Do not send generic engagement prompts, fake urgency, or duplicate events.
- Avoid sensitive clip names, previews, or account information in lock-screen notification text. Let the user open the relevant draft from the notification.
- Support foreground delivery without interruptive banners; update the active job screen instead.

Apple recommends consent and concise, high-value notifications and advises against repeated or sensitive notification content. [Apple HIG: Notifications](https://developer.apple.com/design/human-interface-guidelines/notifications)

## 5. Security and privacy baseline

This app handles personal video, faces/voices, possibly private conversations, user identity, and potentially paid entitlements. Threat modeling must therefore include device loss, shared-device exposure, account takeover, insecure temporary files, upload leakage, storage bucket misconfiguration, unauthorized project access, and stale render links.

- Use a mature identity provider or a well-maintained authentication framework; do not implement cryptography or password storage from scratch.
- Enforce authorization server-side for every project, asset, analysis job, export, and account operation; do not rely on hidden UI controls.
- Use TLS for network traffic; short-lived signed upload/download URLs; least-privilege storage access; server-side validation for file type, size, duration, and ownership.
- Keep credentials/tokens in platform-secure storage; minimize sensitive content in app logs, analytics, crash reports, and notifications.
- Encrypt remote storage and establish explicit retention/deletion policies for source videos, extracted frames, generated assets, and outputs.
- Define a threat model and use OWASP MASVS control groups covering storage, cryptography, authentication/authorization, network communication, platform interaction, and resilience as a release checklist. MASVS is a verification baseline, not a substitute for a product-specific security review. [OWASP MASVS](https://mas.owasp.org/MASVS/02-Frontispiece/), [MASVS storage](https://mas.owasp.org/MASVS/controls/MASVS-STORAGE-1/)
- Provide account deletion and data export/retention explanation. Deleting an account should revoke sessions and enqueue deletion of cloud source media, projects, derived frames, and render outputs according to a documented policy, with any legal/financial records retained only as required.
- Apply age/market and privacy-law requirements after target launch markets are chosen; do not collect birthdate unless necessary for an applicable requirement.

## 6. Subscription and purchase strategy

### Product hypothesis

Potential paid value could include larger cloud storage, premium curated templates, licensed asset access, higher-resolution exports, or a measured quantity of cloud AI operations. None is validated yet. Avoid paywalls on basic import, section review, template editing, or downloading a user's local project until willingness-to-pay evidence exists.

### Recommended validation sequence

1. Pilot the core product without paid complexity or use a clearly labeled research-only pricing study.
2. Measure repeat creation, template reuse, export completion, and variable cloud/model/media costs.
3. Choose whether a free tier, subscription, one-time asset purchase, or hybrid matches recurring value and costs.
4. Present exact renewal price, billing period, trial terms, included limits, and cancellation path before purchase; explain what happens to projects and assets when a plan expires.
5. Implement restore purchases, entitlement reconciliation, refunds/support path, and server-side receipt/transaction validation as needed.
6. Recheck store rules for every target storefront and region immediately before launch. Store policies differ by territory/program and can change.

For digital functionality/content sold inside a storefront app, Apple and Google policies generally require their in-app purchase/billing mechanisms except for applicable regional/program exceptions. Apple requires subscriptions to deliver ongoing value and be available across the user's devices. Exact implementation and external-link rules need a release-time legal/policy review. [Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/uk/), [Apple IAP configuration](https://developer.apple.com/help/app-store-connect/configure-in-app-purchase-settings/overview-for-configuring-in-app-purchases/), [Google Play payments policy](https://support.google.com/googleplay/android-developer/answer/9858738?hl=en)

### Paywall UX requirements if approved later

- Show plan benefits in terms of this product (e.g., extra cloud processing minutes), not vague labels such as “AI power.”
- Distinguish free/local features from paid/cloud features before a user invests time in an upload or render.
- Avoid dark patterns: clear close control, no preselected trial consent, easy restore and cancellation guidance, and no misleading countdown.
- Provide a predictable entitlement state on both platforms and explain offline behavior.

## 7. Professional editor feasibility and scope

### Technical feasibility

A mobile editor that imports additional video, trims and reorders clips, adds audio/text, previews, and exports is achievable with native media APIs or a hybrid architecture. However, each additional editor feature multiplies complexity in the recipe schema, touch interactions, preview/render parity, device performance, accessibility, undo/history, project migration, and cross-platform testing. Advanced masks/keyframes/effects materially increase this cost.

### Product recommendation

Do **not** put a general professional editor in this MVP. It would make the app compete head-on with mature editors before the distinctive reference-to-reusable-template workflow has been proven. Keep the promised v1 outcome as a downloadable MP4 and hand off through the platform share sheet to the user's preferred editor.

Reserve a later **Finishing Studio** phase if research finds a real gap after export. A bounded first version could support:

- Import one or more extra clips after the template output, with a basic trim/reorder timeline.
- Add a closing clip, intro/outro, voiceover, captions, simple audio ducking, and a small transition set.
- Preserve the template render as a named, reversible segment rather than flattening every edit.
- Export the composed MP4; no direct posting or full pro feature set initially.

Before committing, interview creators who currently leave the app after export. Measure how often they add other clips, which edits they need, drop-off caused by external handoff, and whether a lightweight finishing flow would be enough. Compare feature demand against engineering effort and render reliability. If users need keyframes, layered compositing, precise audio mixing, and broad codec/timeline control, integrate or hand off to a mature editor rather than promising parity.

## 8. Updated roadmap boundary

### MVP must include

- Local-first private draft, template library, and export flow.
- Optional account for cloud sync/backup and any chosen server processing.
- Essential settings: account/privacy, creation defaults, help, and system permissions.
- In-app render status. Push notifications are optional and only for opted-in remote jobs.
- No subscription until a value/cost hypothesis is supported; architecture may leave room for entitlement checks without shipping a paywall.
- Template-based render and download, then system share sheet.

### Later, after validation

- Cross-device account sync and cloud media backup.
- Public profiles and user-published template marketplace.
- Paid template/asset catalog or creator subscription.
- Optional Finishing Studio as a separately validated phase.
- Community notifications and social graph only with explicit product need, moderation, and privacy readiness.

## 9. Research still required

- Select launch market(s), age expectations, languages, data residency needs, and applicable privacy rules.
- Decide local-only accountless MVP vs account-required cloud analysis after infrastructure decision.
- Interview creators on sign-in tolerance, cloud backup value, notification preferences, and editor handoff behavior.
- Estimate recurring costs before proposing tiers or free quotas.
- Conduct a threat model and security review against the chosen backend and asset-storage design.
- Verify payment policy for selected storefronts/regions at launch; this study is product planning, not legal advice.

## 10. Sources checked 1 October 2026

- [Apple notification guidance](https://developer.apple.com/design/human-interface-guidelines/notifications)
- [Apple privacy permissions guidance](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/uk/)
- [Apple in-app purchase setup](https://developer.apple.com/help/app-store-connect/configure-in-app-purchase-settings/overview-for-configuring-in-app-purchases/)
- [Google Play payments policy](https://support.google.com/googleplay/android-developer/answer/9858738?hl=en)
- [OWASP MASVS](https://mas.owasp.org/MASVS/02-Frontispiece/), [MASVS storage control](https://mas.owasp.org/MASVS/controls/MASVS-STORAGE-1/)
