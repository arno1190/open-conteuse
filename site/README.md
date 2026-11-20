# Galia showcase

Original static French/English showcase for the Galia engineering project. The identity is a working name; no trademark clearance is implied. `index.html?lang=fr` and `index.html?lang=en` select the language. Everything uses relative asset paths for GitHub Pages project hosting.

Build with `python3 scripts/build_site.py`, then serve `work/site-public/` over HTTP (fetch is required). The build copies current source-derived CAD images rather than keeping duplicate hero renders in this directory. No analytics, account, form or microphone permission. The six local Kokoro neural recordings are downloadable synthetic demonstrations, not approved final narration. Browser speech is an explicit opt-in fallback after a recording fails or is absent; it may use a network voice service. Stop, closing the story, changing language and leaving the page cancel the reading. Text remains available when voice support is missing.

`content/` is generated from the canonical starter collection. Printable paper artwork does not operate the physical contact-ID reader. All story/voice review states remain pending. Product drawings are labelled styling studies; the hardware still requires physical, safety and manufacturing validation. The €99/€129 VAT-inclusive figures are unquoted retail objectives, never an order offer.

Original HTML, JS, CSS and style-study SVG: MIT, as the repository. Original collection artwork/text: see `content/index.json` and canonical collection licence. No competitor assets or text are copied.

## Verification

- `node --check site/app.js`
- `python3 site/check.py`: internal static paths, language keys, bilingual collection/art references and absence of commerce forms.
- Visual browser QA, speech quality and final hardware integration are separate from static checks.

Deployment owner: repository GitHub Pages workflow. Never publish the local parent studio as part of this site.

## Publication

The root repository workflow `.github/workflows/pages.yml` checks PRs and deploys only a passing `main` build (or manual workflow invocation on `main`). Configure GitHub Pages source to **GitHub Actions** once through repository settings/API. Published GitHub Pages URLs:

- French: https://arno1190.github.io/open-conteuse/?lang=fr
- English: https://arno1190.github.io/open-conteuse/?lang=en

Pages is enabled and the public deployment has been verified. The root owns independent review, merge and post-deployment checks. A design-source release must not be described as a certified child-ready product release.

See [PRICING.md](PRICING.md) for dated official market observations and the direct-sales price-target model.

The Pages workflow runs `python3 scripts/build_site.py` to assemble `work/site-public/`: showcase, full CAD gallery/images and the engineering PDF/cost downloads. This includes only public static sources, never the local parent studio or private state.

Development UI regressions: `npm ci --ignore-scripts && npm run test:site`. The maintained test runs the real HTML, separate FR/EN copy and playback code against controlled DOM/media. No test dependencies are shipped to the public site.
