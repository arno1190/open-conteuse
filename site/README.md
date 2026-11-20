# Galia showcase

Original static French/English showcase for the Galia engineering project. The identity is a working name; no trademark clearance is implied. `index.html?lang=fr` and `index.html?lang=en` select the language. Everything uses relative asset paths for GitHub Pages project hosting.

Serve this directory over HTTP (fetch is required for the story collection). No build dependencies, analytics, account, form or microphone permission. The six local eSpeak NG recordings are downloadable synthetic demonstrations, not approved final narration. Browser speech synthesis remains a device-dependent fallback and may use a network voice service. Stop, closing the story, changing language and leaving the page cancel the reading. Text remains available when voice support is missing.

`content/` is generated from the canonical starter collection. Printable paper artwork does not operate the physical contact-ID reader. All story/voice review states remain pending. Product drawings are labelled styling studies; the hardware still requires physical, safety and manufacturing validation. The €99/€129 VAT-inclusive figures are unquoted retail objectives, never an order offer.

Original HTML, JS, CSS and style-study SVG: MIT, as the repository. Original collection artwork/text: see `content/index.json` and canonical collection licence. No competitor assets or text are copied.

## Verification

- `node --check site/app.js`
- `python3 site/check.py`: internal static paths, language keys, bilingual collection/art references and absence of commerce forms.
- Visual browser QA, speech quality and final hardware integration are separate from static checks.

Deployment owner: repository GitHub Pages workflow. Never publish the local parent studio as part of this site.

## Publication

The root repository workflow `.github/workflows/pages.yml` checks PRs and deploys only a passing `main` build (or manual workflow invocation on `main`). Configure GitHub Pages source to **GitHub Actions** once through repository settings/API. Public target URLs after a successful deployment:

- French: https://arno1190.github.io/open-conteuse/?lang=fr
- English: https://arno1190.github.io/open-conteuse/?lang=en

These are planned URLs until the owner verifies a successful Pages deployment. No deployment was performed by the site implementation task. The root owns review, merge, enabling Pages and verifying the returned public URL. A design-source release must not be described as a certified child-ready product release.

See [PRICING.md](PRICING.md) for dated official market observations and the direct-sales price-target model.

The Pages workflow runs `python3 scripts/build_site.py` to assemble `work/site-public/`: showcase, full CAD gallery/images and the engineering PDF/cost downloads. This includes only public static sources, never the local parent studio or private state.
