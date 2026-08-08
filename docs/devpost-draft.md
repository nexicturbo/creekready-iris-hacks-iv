# CreekReady — Devpost submission draft

> Finalization checklist: replace bracketed links, confirm every feature below in the final build, and remove this note before submission. Do not claim a deployment, video, study, metric, or award unless it has been independently verified.

## Project name

CreekReady

## Tagline

Official alert in. Clear household plan out.

## Elevator pitch

CreekReady turns dense emergency-alert text into a source-linked **Now / Next / If conditions worsen** plan adapted to a household's practical needs. It is designed to help people understand an alert they already received—not predict emergencies or replace officials.

## Inspiration

Receiving an emergency alert is not the same as knowing what to do next. Alerts need to cover entire communities, so they can be dense, time-sensitive, and difficult to translate into concrete household decisions. Those decisions become even harder when a family needs to account for children, an older adult, pets, limited mobility, transportation, or a language preference.

That problem feels especially tangible in Cedar Creek, Texas, where wildfire, flood, and extreme-heat preparedness all matter. I built CreekReady around a simple question: can AI make an official alert easier to act on while preserving the authority and limitations of the original source?

## What it does

A user pastes text from an official emergency alert, selects relevant household needs, and chooses English or Spanish. CreekReady extracts a compact fact panel and organizes next steps into three clear stages:

- **Now** — immediate actions grounded in the alert and official safety guidance.
- **Next** — practical household preparation.
- **If conditions worsen** — a clear reminder that official instructions and observed conditions take priority.

Each action identifies its source, and the result displays limitations rather than pretending the system has live situational awareness. With AI assist enabled, Featherless solves two bounded semantic tasks: it prioritizes exact directive sentences already present in the pasted alert and ranks a server-owned catalog of vetted actions around the selected household constraints. It returns IDs only and never authors the safety guidance or quotes shown to the user. A visible selection receipt shows the exact unchanged alert wording it prioritized, the candidate counts, and how many required actions the server retained. If that call is disabled, unavailable, fails, or returns content that does not validate, the application automatically switches to a deterministic official-guidance fallback.

## How we built it

CreekReady uses a lightweight Flask application with a browser-based interface. The backend validates incoming alert text, household selections, and language using Pydantic. A planning service then selects official references for the likely hazard.

The AI-assisted path uses the OpenAI Python client against Featherless's OpenAI-compatible endpoint. A deterministic parser first extracts the fact panel and tokenizes exact directive sentences. Featherless receives only those parser-selected sentence spans, the selected needs/language, and the vetted action catalog; the raw alert is not sent as a separate field. The model returns a flat JSON object containing two ID lists: prioritized instruction IDs and ranked action IDs. Pydantic and allowlist checks reject extra prose, unknown IDs, duplicates, and incorrect counts. The server fixes the three stages, restores every required action before any selected optional action, and expands the validated IDs into unchanged alert wording plus localized action, reason, and citation text. The model cannot inject facts into the trusted panel or author visible safety guidance.

Reliability was part of the architecture rather than an afterthought. If the provider is unavailable or its output fails validation, CreekReady falls back to deterministic flood, wildfire, heat, or unclassified-alert guidance. The application stores no accounts or plans and uses no live weather, location, road, or emergency-services data.

Technologies used: Python, Flask, Pydantic, HTML, CSS, JavaScript, the OpenAI Python client, and the Featherless-compatible chat-completions API.

## Challenges we ran into

The central challenge was not producing more text; it was keeping model influence bounded. Emergency information has a much higher cost of hallucination than a typical chatbot response. I separated deterministically extracted facts from AI-assisted ranking, moved all visible safety language into a reviewed server-owned catalog, minimized what leaves the server, validated every returned ID, restored required actions server-side, and made invalid AI output trigger a safe fallback.

A second challenge was making household personalization useful without implying medical expertise or live knowledge. CreekReady treats selections such as limited mobility or no vehicle as planning constraints and gives general preparation prompts while continuing to defer to the source alert and authorities.

The third challenge was reliability under hackathon conditions. Network access, provider availability, and model output can all vary, so I made the same end-to-end interaction work in a deterministic no-key mode.

## Accomplishments that we're proud of

- A complete alert-to-plan workflow with explicit facts, three action stages, source links, and limitations.
- A trusted fact panel that the AI cannot populate with invented locations, timing, or official instructions.
- An ID-only AI contract: Featherless prioritizes exact alert wording and vetted actions but cannot write either one.
- A visible, auditable selection receipt with exact unchanged quotes and candidate/ranking counts.
- Request and response validation that rejects unknown, duplicate, incorrectly sized, or free-form model output, while server-side restoration prevents any required action from disappearing.
- Automatic fallback when Featherless is not configured, errors, or returns an invalid payload.
- Household-aware planning for children, an older adult, pets, limited mobility, and no vehicle.
- English and Spanish plan generation.
- A deliberately small privacy footprint: no accounts, database, geolocation, or persistent alert storage.
- A 113-test network-free suite covering boundaries, served frontend assets and disclosure copy, English and Spanish hazard extraction, mixed and expired-alert handling, conservative extraction confidence, exact instruction tokenization, grounded fallback behavior, all household needs, flat/adversarial provider payloads, required-action restoration, source validation, Unicode output, accessibility/runtime invariants, rate limiting, timestamps, configuration normalization, and security headers.
- Recorded live Featherless checks with fictional English wildfire, Spanish flood, and injection-shaped flood requests; each returned only allowlisted IDs, preserved exact selected wording, and retained every required server-owned action. These are integration observations, not accuracy or availability claims.

## What we learned

Responsible AI design is as much about boundaries as capabilities. Prompting alone is not a sufficient safety layer: a narrow decision surface, structured validation, reviewed catalogs, visible uncertainty, and graceful failure all matter. I also learned that a deterministic fallback can improve both reliability and honesty. Rather than disguising an outage—or forcing users to send an alert to a provider—CreekReady offers a server-only deterministic path that does not forward the alert to Featherless, and it labels which mode produced the plan.

Most importantly, an AI safety tool should not try to become the authority. CreekReady is most useful when it helps a household act on official information while keeping that information visible and primary.

## What's next for CreekReady

Future work would begin with evaluation, not feature growth: co-design with emergency managers and accessibility groups, formal testing of extraction quality, and review by native Spanish speakers. With that foundation, CreekReady could add more languages, additional hazard guides, accessible document/image ingestion, and opt-in integration with authenticated official alert feeds. A production version would also need a reviewed privacy policy, provider-data assessment, security testing, and clear operational ownership.

These are future directions, not capabilities of the submitted prototype.

## Built with

- Python
- Flask
- Pydantic
- HTML
- CSS
- JavaScript
- OpenAI Python client
- Featherless-compatible API integration
- pytest

## Suggested Devpost metadata

- Category: Machine Learning/AI
- Additional tags: emergency preparedness, responsible AI, Flask, Featherless, bilingual, accessibility
- Project status: public source repository; local demo verified; do not mark it deployed until a public build is verified
- Team: Henderson Damian Mejia Gonzales, solo entrant
- Presentation script: `docs/pitch-script.md`
- Judge deck PDF: `output/pdf/CreekReady-Iris-Hacks-IV.pdf`
- Editable judge deck: `docs/CreekReady-Iris-Hacks-IV.pptx`

## Open-source acknowledgements

- [Flask](https://github.com/pallets/flask), BSD-3-Clause
- [Flask-Limiter](https://github.com/alisaifee/flask-limiter), MIT
- [OpenAI Python](https://github.com/openai/openai-python), Apache-2.0
- [Pydantic](https://github.com/pydantic/pydantic), MIT
- [python-dotenv](https://github.com/theskumar/python-dotenv), BSD-3-Clause
- [pytest](https://github.com/pytest-dev/pytest), MIT
- [Gunicorn](https://github.com/benoitc/gunicorn), MIT

## Official source acknowledgements

CreekReady's checked-in guidance links to [NWS Flood Safety](https://www.weather.gov/safety/flood), [NWS Heat Safety](https://www.weather.gov/safety/heat), [FEMA Wildfires](https://www.ready.gov/wildfires), and [FEMA Make a Plan](https://www.ready.gov/plan). These agencies—not CreekReady—are authoritative.

## Links and media

- Code: https://github.com/nexicturbo/creekready-iris-hacks-iv
- Try it: **[ADD ONLY IF DEPLOYED AND VERIFIED]**
- Presentation: https://github.com/nexicturbo/creekready-iris-hacks-iv/blob/main/output/pdf/CreekReady-Iris-Hacks-IV.pdf
- Editable presentation source: `docs/CreekReady-Iris-Hacks-IV.pptx`
- Video: **[ADD ONLY IF REQUIRED, UPLOADED, AND VERIFIED]**
- Cover image: `docs/assets/creekready-cover.png` — generated editorial illustration; it does not depict a live emergency or live conditions.
- Devpost thumbnail: `docs/assets/creekready-devpost-thumbnail.png` — a 3:2 reframing of the same generated editorial concept, prepared for Devpost's recommended thumbnail ratio.
- Interface image: `docs/assets/creekready-hero.png` — verified local build with Featherless configured.
- Desktop product proof: `docs/assets/creekready-desktop-result.png` — clean 16:9 fictional result showing mode, household fit, all three action stages, and source IDs.
- Result image: `docs/assets/creekready-live-demo.png` — verified fictional-sample result; not a current alert.

## Submitter

Henderson Damian Mejia Gonzales — solo entrant
