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

Each action identifies its source, and the result displays limitations rather than pretending the system has live situational awareness. When configured, Featherless ranks and selects only from a server-owned catalog of vetted action IDs; it never authors the safety guidance shown to the user. If that call is missing, disabled, fails, or returns content that does not validate, the application automatically switches to a deterministic official-guidance fallback, so the core workflow remains demonstrable without a network model call.

## How we built it

CreekReady uses a lightweight Flask application with a browser-based interface. The backend validates incoming alert text, household selections, and language using Pydantic. A planning service then selects official references for the likely hazard.

The optional AI path uses the OpenAI Python client against Featherless's OpenAI-compatible endpoint. The model receives the pasted alert, selected needs, and a small catalog of approved, source-linked actions, then returns only ordered action IDs in a fixed three-stage JSON shape. Pydantic and catalog checks reject extra prose, unknown or duplicate IDs, wrong-stage selections, and omissions of required actions. The server expands validated IDs into the localized action, reason, and citation text. Crucially, the displayed place, time, and official-instruction panel always comes from a conservative local extractor—even in Featherless mode—so the model cannot inject facts into the trusted panel.

Reliability was part of the architecture rather than an afterthought. If the provider is unavailable or its output fails validation, CreekReady falls back to deterministic flood, wildfire, heat, or unclassified-alert guidance. The application stores no accounts or plans and uses no live weather, location, road, or emergency-services data.

Technologies used: Python, Flask, Pydantic, HTML, CSS, JavaScript, the OpenAI Python client, and the Featherless-compatible chat-completions API.

## Challenges we ran into

The central challenge was not producing more text; it was keeping model influence bounded. Emergency information has a much higher cost of hallucination than a typical chatbot response. I separated locally extracted facts from AI-assisted ranking, moved all visible safety language into a reviewed server-owned catalog, validated every selected ID and stage, and made invalid AI output trigger a safe fallback.

A second challenge was making household personalization useful without implying medical expertise or live knowledge. CreekReady treats selections such as limited mobility or no vehicle as planning constraints and gives general preparation prompts while continuing to defer to the source alert and authorities.

The third challenge was reliability under hackathon conditions. Network access, provider availability, and model output can all vary, so I made the same end-to-end interaction work in a deterministic no-key mode.

## Accomplishments that we're proud of

- A complete alert-to-plan workflow with explicit facts, three action stages, source links, and limitations.
- A trusted fact panel that the AI cannot populate with invented locations, timing, or official instructions.
- An ID-only AI contract: Featherless can rank vetted actions but cannot write visible safety guidance.
- Request and response validation that rejects unknown, duplicate, misplaced, missing-required, or free-form model output.
- Automatic fallback when Featherless is not configured, errors, or returns an invalid payload.
- Household-aware planning for children, an older adult, pets, limited mobility, and no vehicle.
- English and Spanish plan generation.
- A deliberately small privacy footprint: no accounts, database, geolocation, or persistent alert storage.
- A 99-test network-free suite covering boundaries, served frontend assets and provider-transmission copy, English and Spanish hazard extraction, mixed and expired-alert handling, conservative extraction confidence, grounded fallback behavior, all household needs, adversarial provider payloads, source validation, Unicode output, rate limiting, timestamps, and security headers.
- Verified live Featherless integration with fictional English, Spanish, and prompt-injection-shaped alerts; every checked call returned only approved catalog IDs with required actions intact.

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
- Project status: local prototype; do not mark it deployed unless a public build is later verified
- Team: Henderson Damian Mejia Gonzales, solo entrant
- Presentation script: `docs/pitch-script.md`
- Judge deck: `docs/CreekReady-Iris-Hacks-IV.pptx`

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

- Code: **[ADD PUBLIC OR JUDGE-ACCESSIBLE GITHUB URL]**
- Try it: **[ADD ONLY IF DEPLOYED AND VERIFIED]**
- Presentation: `docs/CreekReady-Iris-Hacks-IV.pptx` (also upload or link it in the final Devpost form if required)
- Video: **[ADD ONLY IF REQUIRED, UPLOADED, AND VERIFIED]**
- Cover image: `docs/assets/creekready-cover.png` — generated editorial illustration; it does not depict a live emergency or live conditions.
- Interface image: `docs/assets/creekready-hero.png` — verified local build with Featherless configured.
- Result image: `docs/assets/creekready-live-demo.png` — verified fictional-sample result; not a current alert.

## Submitter

Henderson Damian Mejia Gonzales — solo entrant
