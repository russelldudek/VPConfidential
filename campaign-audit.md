# Candidate Campaign Audit

## Campaign state

`building` until the complete package is committed by the publication workflow and the live GitHub Pages deployment is independently verified.

## Manifest

- [x] `index.html`
- [x] `resume.html`
- [x] `cover-letter.html`
- [x] `interview-brief.html`
- [x] `120-day-plan.html`
- [x] `hard-objection.html`
- [x] `manufacturing-shape-review.html`
- [x] `styles.css`
- [x] `brand-tokens.css`
- [x] `app.js`
- [x] `brand-intelligence.md`
- [x] `source-notes.md`
- [x] `assets/brand/confidential-organization.svg`
- [x] Generated PDF set under `docs/`
- [x] Deterministic standard-library PDF generator under `scripts/`

## Evidence integrity

- Titles and dates match the verified candidate evidence record.
- No global VP tenure, unverified metrics, production deployments, or undisclosed clients are claimed.
- Verified scale measures retain qualifiers such as `approximately`.
- Candidate vision clearly separates industry context from company fact.

## Confidentiality

- The employer remains unidentified.
- No private campaign-system name or private source repository appears in candidate-facing surfaces.
- No source repository link appears in website or documents.
- The confidential identity asset is explicitly candidate-created and non-official.

## Interaction and accessibility

- Smart default scenario: Balanced growth.
- Four native-button scenarios update a consequential operating posture.
- State changes are exposed through `aria-pressed` and an `aria-live` readout.
- Keyboard operation is native.
- `prefers-reduced-motion` removes scenario animation without removing information.

## Local rendered QA

- Seven routes reviewed at 1440x900, 1280x800, 768x1024, and 390x844.
- Zero horizontal-overflow findings.
- Zero browser-console errors.
- Scenario state change and reset behavior passed.
- Reduced-motion behavior passed.
- All local links resolved.

## Print contracts

- Resume PDF: 2 pages.
- Cover letter PDF: 1 page.
- Interview thesis brief PDF: 4 pages.
- First 120-day entry plan PDF: 3 pages.
- Hard-objection analysis PDF: 2 pages.
- Manufacturing Shape Review PDF: 2 pages.

All fourteen PDF pages were rendered and visually inspected locally. Live download parity remains a publication audit item.

## Deployment status

The repository is structured for publication from `main` and `/ (root)`. GitHub Pages administration and live-route verification remain external deployment checks and must not be reported as passed until observed.
