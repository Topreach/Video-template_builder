# Media Privacy, Security, and Data Lifecycle

**Prepared:** 3 October 2026  
**Status:** Product and engineering baseline. Processing location, launch markets, storage implementation, and cloud retention limits remain decision-gated. This is not a legal compliance determination.  
**Related:** [MVP coverage and traceability](mvp_coverage_and_traceability.md), [workflow specification](video_template_workflow_spec.md), [account/security research](../research/account_security_monetization_and_editor_scope.md), [architecture build plan](mvp_architecture_and_build_plan.md).

## 1. Purpose and security posture

The app receives private video that may show identifiable people, voices, locations, conversations, or copyrighted material. A video can reveal more than its filename or account profile. The product should collect and retain the smallest useful amount of data, process locally when feasible, explain each upload before it occurs, and provide deletion controls across source media, derived data, projects, jobs, and exports.

This document establishes threat and lifecycle requirements that must inform architecture and UI. It does not assume that local processing is already selected, that a cloud provider has been approved, or that an OS picker removes every later storage obligation.

## 2. Data inventory and handling rules

| Data class | Examples | Default handling rule | User-facing control |
|---|---|---|---|
| Source media | Imported reference video, replacement clips, images, audio | Keep in app-private temporary storage only as long as needed; do not upload unless the user is told what leaves the device and why. | Cancel import/analysis; remove source from project; processing disclosure. |
| Derived media | Thumbnails, sampled frames, waveforms, proxy files, preview renders | Treat as sensitive as the source; derive only needed samples; keep private; delete with the source/job unless explicitly retained for a saved project. | Clear cache; delete source/project. |
| Analysis signals | Shot boundaries, OCR, transcript, speech timing, beat map, motion cues, labels | Store only signals needed to resume/edit the recipe; avoid retaining full transcript or OCR text by default if timing/role data suffices. | Clear analysis with source/project; explain optional signal processing. |
| Project and recipe | Slot ranges, crop, text, audio choices, exclusions, edit history | Private by default; stable schema/version; local-first. Recipe may still reveal the structure/content of a private clip. | Rename, duplicate, delete. |
| Account and credentials | Email, provider ID, session tokens, recovery state | Collect minimum identity data; tokens in platform secure storage; never put secrets in logs, ordinary settings storage, or source control. | Sign out, revoke sessions, delete account. |
| Render output | Temporary render, final MP4, poster frame | Keep temporary outputs private and clean on cancel/failure; final export is user-controlled and saved/shared explicitly. | Delete project output; save/share via OS UI. |
| Diagnostics | App version, platform, error class, duration bucket, performance metrics | Minimize and pseudonymize; no raw media, frames, transcript, filenames, paths, or free-form clip labels by default. | Diagnostics and analytics settings/notice as appropriate to chosen market. |
| Support content | User-authored support message and optional attachment | Do not attach media automatically; warn before user voluntarily attaches a clip or screenshot. | Preview/remove attachment before send. |
| Billing records (future) | Entitlement and store transaction references | Defer until monetization is selected; segregate billing metadata from media content. | Plan, restore, cancel, and deletion explanation. |

## 3. Data-flow lifecycle

1. **Select:** Use the iOS Photos picker or Android Photo Picker for user-selected items. Request broad photo/video-library permission only if a separately justified feature truly needs library-wide access. Picker selection is not blanket consent to upload or publish the selected media. [Apple Photos picker](https://developer.apple.com/documentation/PhotoKit/selecting-photos-and-videos-in-ios), [Android Photo Picker](https://developer.android.com/training/data-storage/shared/photo-picker), [Android permission minimization](https://developer.android.com/privacy-and-security/minimize-permission-requests)
2. **Validate:** Check actual decodability and probed media properties, not just filename or declared MIME type. Enforce agreed byte, duration, dimensions, frame-rate, track-count, and decode-time limits at the import and processing boundary. Reject corrupt, unsupported, or resource-exhausting inputs with a recoverable explanation. Numeric limits remain an engineering decision tied to device and service capacity.
3. **Stage:** Copy only when a native decoder/job needs a stable local file. Keep scratch, frame, proxy, and partial-output files in an app-private location; use random internal names; do not place raw media in preferences, ordinary logs, analytics, or public shared storage.
4. **Analyze:** Default to on-device processing if chosen feature quality and device support permit it. If cloud analysis is selected, show a just-in-time disclosure of media/signals uploaded, processing purpose, provider, retention/deletion, and account requirement before transfer. Separate analysis consent from rights to publish or reuse source content.
5. **Review and save:** Persist only project data needed to recover a draft or reuse a recipe. Make source references and retained footage visible. Excluded footage must not enter recipe output or render inputs.
6. **Render:** Render from an immutable project snapshot. Temporary outputs are private and removed after completion, cancellation, or failure according to a cleanup policy. Validate completion before exposing a final file; do not report a partial file as finished.
7. **Export:** Let the user choose where to save or share via platform UI. Explain that an exported copy is outside app-controlled project deletion; user-created copies may remain in Downloads, Photos, a recipient app, or a backup.
8. **Delete:** Delete local source, derivatives, draft, recipe, and app-owned output together when the user chooses project deletion, with individually selectable source retention only if the UI makes its consequences clear. For cloud jobs/assets, request deletion, revoke access, retry failures, and report pending/completed status honestly.

## 4. Threat model

### Assets to protect

- Raw video/audio and identifiable frame samples.
- Analysis results that expose dialogue, text, people, events, or timing.
- Recipes and project names that reveal private activity.
- Account credentials, session tokens, job identifiers, and signed links.
- Render outputs, temporary files, support attachments, and diagnostic events.

### Threat actors and abuse cases

- Someone with temporary or persistent access to an unlocked/shared/lost device.
- A malformed media file exploiting a decoder, excessive dimensions, long duration, or pathological frame rate.
- A user or attacker guessing another user's project/job ID (broken object-level authorization / IDOR).
- An attacker obtaining an upload URL, session token, bucket URL, or stale render link.
- Accidental disclosure through backups, crash reports, analytics SDKs, debug logs, notification previews, or support attachments.
- A compromised account, employee/tooling with overbroad storage access, or provider retaining data beyond the disclosed purpose.
- Race conditions leaving orphan uploads, frames, temporary renders, or undeleted cancelled jobs.

### Required controls and evidence

| Threat | Required control | Evidence before release | OWASP MASVS area |
|---|---|---|---|
| Unauthorized local read | App-private media storage; OS file protection; secrets in Keychain/Keystore-backed storage; no media in logs or preferences. | Storage inventory; inspect files/logs on representative devices; lock/restart behavior. | Storage, Platform |
| Backup restores deleted/private media | Explicit backup inclusion/exclusion policy for media, databases, and credentials on each platform; test restore behavior. | Android backup rules reviewed for cloud backup and device transfer; iOS backup exclusion/behavior documented; restore test. | Storage, Privacy |
| Malformed input / resource exhaustion | Actual decoder validation, caps, timeouts, cancellation, bounded frame extraction, and safe failure. | Corpus with truncated, oversized, unusual timing/dimensions, and no-audio cases; memory/time limits recorded. | Resilience |
| Cloud cross-user access | Server authorization on every project, asset, job, and result; opaque identifiers alone are never authorization. | Negative authorization tests for altered IDs and expired/revoked sessions; access audit. | Auth, Network |
| Stolen transfer link/token | Short-lived, least-scope upload/download capability; one job/object where possible; TLS; revocation and expiration. | Expiry/replay/revocation checks; no credential in application logs. | Auth, Network |
| Provider or bucket exposure | Private buckets, least privilege, encryption in transit/at rest, provider terms and no-training setting where available, documented deletion. | Cloud configuration review, provider/data-flow inventory, deletion exercise. | Network, Privacy |
| Diagnostic leakage | Redaction by schema; allowlisted event fields; no content-bearing free text; SDK collection reviewed. | Capture and inspect production-like events/crash reports, including failure paths. | Privacy, Storage |
| Orphaned/cancelled data | Idempotent cleanup state machine, retry queue, server TTL as backstop, deletion status. | Cancel, timeout, retry, app-kill, and delete lifecycle evidence; orphan reconciliation metric. | Resilience, Privacy |
| Account takeover | Mature identity provider, rate limits, recovery protection, session revocation, authorization re-checks. | Auth/recovery abuse review; revocation verified across active jobs and links. | Auth |
| Public export surprise | Explicit save/share action; clarify app deletion does not remove externally saved copies. | UX review of save, share, and delete language. | Privacy |

Use the OWASP MASVS control groups for a structured verification baseline, especially storage, cryptography, authentication, network, platform, resilience, and privacy. [OWASP MASVS](https://mas.owasp.org/MASVS/)

## 5. Local storage, backup, and key handling

- Store media and derived files only in app-private directories unless the user explicitly exports them.
- Use platform data protection appropriate to foreground/background requirements. Apple file protection makes files unavailable under selected lock states; choose and test a class compatible with export/background jobs rather than assuming one class works for all files. [Apple file protection](https://developer.apple.com/documentation/uikit/encrypting-your-app-s-files)
- On Android, review Auto Backup because most app data is included by default; explicitly decide what can be backed up and distinguish cloud backup from device-to-device transfer rules. [Android Auto Backup](https://developer.android.com/identity/data/autobackup)
- Store small credentials/tokens in OS-backed secure storage. Expo SecureStore is a candidate for secrets, not video, project databases, or large blobs; verify exact behavior in the chosen development/production builds. [Expo SecureStore](https://docs.expo.dev/versions/latest/sdk/securestore/)
- Choose whether project metadata needs database-level encryption after data classification and threat review. OS sandboxing and device encryption reduce risk but do not by themselves answer backups, forensic exposure, or compromised-device scenarios.
- Do not promise secure physical erasure from flash storage. Deletion means removing app references/files and revoking access; backups, snapshots, exported copies, and storage wear-leveling may affect when bytes become unrecoverable. Define and communicate exact cloud backup deletion windows only after platform/provider behavior is known.

## 6. Cloud-processing guardrails (only if selected)

Cloud processing is not implied by user consent to analyze a video. Before a production cloud path exists, define:

- What is sent: full source, audio, selected frames, or derived signals; avoid sending more than the operation requires.
- Processing purpose, named providers/subprocessors, hosting regions, encryption, provider training/use controls, and retention.
- Upload initiation after clear user action and disclosure; cancellation behavior while upload or processing is active.
- Per-user/per-job authorization; server-side media validation; private object storage; short-lived scoped transfer URLs; separate service identity from user identity.
- Automatic expiration as a backstop plus explicit delete, cancel, and account deletion workflows. Cloud source retention should be ephemeral by default; exact time limits and recovery window are open decisions.
- Failure-safe cleanup for partial uploads, retries, abandoned jobs, generated frames, and final outputs; operational reconciliation must not rely only on the mobile client.
- Provider contract, subprocessors, data residency, incident process, and deletion evidence reviewed for each target market.

## 7. Deletion and retention semantics

The UI and backend must distinguish these objects: imported source, app-created copy, derived frames/proxies/signals, recipe/project, analysis job, temporary render, final export, account, and provider backup. A deletion action must list object classes affected and copies outside app control.

- **Cancel analysis/render:** stop new work promptly, invalidate job access, delete partial objects, and retry cleanup if a remote provider is temporarily unavailable.
- **Delete source only:** remove source and source-derived material, then mark any recipe that cannot function without it as incomplete; preserve only data the user explicitly chose to retain.
- **Delete project:** remove project metadata and associated app-owned media/derivatives/outputs. If an output was exported elsewhere, explain that the app cannot delete it.
- **Delete account (if accounts are enabled):** revoke sessions and access tokens, stop/revoke jobs, cascade deletion to user-linked projects and media, report any pending deletion, and retain billing/legal records only where justified and disclosed.
- **Retention schedule:** set a short, documented TTL for cloud job inputs and temporary outputs; never retain cloud source media indefinitely by accident. Exact duration, backup expiry, and legal exceptions are DEC-016 pending provider and market choice.
- **Local delete semantics:** remove files and metadata from app-managed storage; do not claim forensic or physical overwrite guarantees.

## 8. Product and engineering release gates

1. Complete data inventory and data-flow diagram for the selected architecture, including all SDKs and subprocessors.
2. Decide storage, backup, file protection, secure credential store, retention, and deletion behavior for iOS and Android.
3. Threat review endpoints and object authorization before any backend project/job/media endpoint is reachable.
4. Verify no raw media or content-bearing derived data appears in logs, crash reporting, analytics, or notifications.
5. Demonstrate deletion and cleanup under normal completion, cancellation, network loss, retries, app termination, and account deletion where applicable.
6. Review age, privacy, copyright, biometric/voice, data residency, and store-policy obligations with qualified counsel for selected launch markets. This document does not establish legal compliance.
7. Keep secrets, real user media, tokens, signing materials, production URLs, and provider credentials out of Git and test fixtures. Synthetic fixtures only; review dependencies and build secrets before releases.

## 9. Decisions to resolve

| Decision | Current recommendation | Evidence/owner needed |
|---|---|---|
| DEC-001: launch market, age floor, languages, residency | Do not finalize legal notices, age gates, or regions before selecting target market. | Product owner plus qualified privacy/store-policy review. |
| DEC-002: processing location | Local-first; cloud only for a named capability with clear disclosure and user action. | Device quality, latency, battery, privacy and cost study. |
| DEC-006: persistence and retention | App-private local files; data inventory and deletion semantics defined here; exact database and backup policy still open. | Platform prototype, restore/delete evidence, migration review. |
| DEC-010: backend/auth/storage | No cloud asset service until tenancy, authorization, provider contracts, and deletion are designed. | Architecture/security owner; threat review. |
| DEC-011: analytics | Minimal allowlisted events; do not collect content-bearing values. | Product metric plan, privacy review, consent/retention by market. |
| DEC-015: local encryption and backup policy | Use OS protections; choose metadata encryption and backup inclusion per data classification. | Platform engineering and recovery/usability proof. |
| DEC-016: cloud retention and deletion TTLs | Ephemeral job processing; exact TTL and backup expiry must be published only after provider capabilities are verified. | Backend owner and legal/privacy review. |

## 10. Primary technical references

- Apple, [Selecting photos and videos in iOS](https://developer.apple.com/documentation/PhotoKit/selecting-photos-and-videos-in-ios).
- Apple, [Encrypting your app's files](https://developer.apple.com/documentation/uikit/encrypting-your-app-s-files).
- Android, [Photo Picker](https://developer.android.com/training/data-storage/shared/photo-picker) and [minimize permission requests](https://developer.android.com/privacy-and-security/minimize-permission-requests).
- Android, [Back up user data with Auto Backup](https://developer.android.com/identity/data/autobackup).
- Expo, [SecureStore](https://docs.expo.dev/versions/latest/sdk/securestore/).
- OWASP, [MASVS](https://mas.owasp.org/MASVS/) and [MASVS storage controls](https://mas.owasp.org/MASVS/controls/MASVS-STORAGE-1/).
