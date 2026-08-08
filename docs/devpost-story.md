# CreekReady — Devpost project story

Final, fact-checked project-story copy prepared for Iris Hacks IV.

## Inspiration

An emergency alert can describe what is happening across an entire community. A household still has to answer a personal question: what do we do next? For a family in Cedar Creek, Texas, that answer may need to account for an older adult, a pet, limited mobility, no vehicle, children, or a preferred language. Dense, time-sensitive warnings make that translation harder precisely when clarity matters most.

CreekReady explores a different role for AI in safety: not predicting emergencies or inventing advice, but helping people prioritize the exact directions they received and organize vetted preparedness actions around their household.

## What it does

A user pastes text from an official emergency alert, selects relevant household needs, and chooses English or Spanish. CreekReady produces:

- a trusted fact panel extracted from the alert;
- a cited action plan organized into **Now**, **Next**, and **If conditions worsen**;
- visible household-specific actions, sources, limitations, and the mode that produced the plan.

Every action points to either the pasted alert or checked-in FEMA/National Weather Service guidance. The interface keeps those sources distinct and never claims live situational awareness.

With AI assist enabled, Featherless performs two narrow semantic tasks: it prioritizes exact directive sentences already in the alert and ranks a server-owned catalog of vetted actions for the selected household constraints. It returns IDs only—it cannot write the facts, quotations, or safety guidance shown to the user. A visible receipt shows the exact unchanged alert wording it selected and aggregate candidate/ranking counts.

If AI is off, unavailable, or invalid, CreekReady switches automatically to deterministic official-guidance fallback. It has no live alert, weather, road, location, or emergency-services feed and must not replace the original alert, local authorities, or emergency services.

## How we built it

CreekReady is a lightweight Flask application with a responsive HTML, CSS, and JavaScript interface. Pydantic validates alert text, household selections, language, and provider output. A deterministic parser creates the fact panel, identifies the likely hazard, and tokenizes exact directive sentence candidates.

The AI path uses the OpenAI Python client with Featherless's compatible endpoint. Featherless receives parser-selected directive spans, selected needs and language, the vetted action catalog, and request-specific IDs and target counts—not the raw alert as a separate field. Those spans can still contain sensitive text, so the interface warns users not to paste private information; turning AI off prevents forwarding to Featherless.

On Featherless, **Qwen/Qwen3-8B** ranks request-specific instruction and action IDs across variable English and Spanish alerts. Thinking is disabled and output is capped at 300 tokens because only two short ID arrays are needed. This is the model's purposeful decision surface, not a decorative chat layer.

The server rejects extra prose, unknown or duplicate IDs, and incorrect counts; keeps the three stages fixed; within each stage, restores omitted required actions ahead of selected optional actions; and expands validated IDs into unchanged alert wording plus server-owned localized actions, reasons, and citations. Invalid output fails closed. CreekReady uses no accounts, database, geolocation, or persistent alert/plan storage.

## Challenges we ran into

The hardest problem was limiting model influence where hallucination has a high cost. Prompting alone was not enough, so I separated deterministic facts from semantic ranking, constrained the model to allowlisted IDs, retained required actions server-side, and made failure visible and recoverable.

The second challenge was useful personalization without implying medical expertise or live knowledge. Household selections are planning constraints, never diagnoses. The third was making the same complete interaction reliable without a provider key or network call.

## Accomplishments that we're proud of

- A complete, bilingual alert-to-plan workflow with a polished responsive interface, clear hierarchy, keyboard support, Read aloud, reduced-motion support, and printable results.
- An auditable AI receipt, exact-source citations, explicit uncertainty, and deterministic fallback.
- A **124-test, network-free suite** covering input boundaries, English/Spanish hazard extraction, mixed and expired alerts, every household need, fallback behavior, injection-shaped and malformed provider payloads, required-action restoration, accessibility/runtime invariants, rate limiting, configuration, and security headers.
- Recorded live Featherless checks using fictional English wildfire, Spanish flood, and injection-shaped flood requests. Each returned only allowlisted IDs, preserved exact selected wording, and retained every required action. These are integration observations, not accuracy, latency, or availability claims.

## What we learned

Responsible AI design is as much about boundaries as capability. A narrow decision surface, structured validation, reviewed catalogs, visible uncertainty, and graceful failure are stronger together than prompting alone. A deterministic fallback also improves both reliability and honesty. The safest role for CreekReady is to help a household act on official information while keeping that information visible and primary.

**Official alert in. Clear household plan out—with the official signal still in control.**

## What's next for CreekReady

Next comes evaluation, not unchecked feature growth: co-design with emergency managers and accessibility groups, formal extraction-quality testing, and review by native Spanish speakers. With that foundation, future versions could add more languages, accessible document/image ingestion, and opt-in authenticated official alert feeds. Production use would also require a reviewed privacy policy, provider-data assessment, security testing, and operational ownership. These are future directions, not submitted capabilities.

## Open-source acknowledgements

CreekReady is released under the [MIT License](https://github.com/nexicturbo/creekready-iris-hacks-iv/blob/main/LICENSE).

[Flask](https://github.com/pallets/flask) (BSD-3-Clause), [Flask-Limiter](https://github.com/alisaifee/flask-limiter) (MIT), [OpenAI Python](https://github.com/openai/openai-python) (Apache-2.0), [Pydantic](https://github.com/pydantic/pydantic) (MIT), [python-dotenv](https://github.com/theskumar/python-dotenv) (BSD-3-Clause), [pytest](https://github.com/pytest-dev/pytest) (MIT), and [Gunicorn](https://github.com/benoitc/gunicorn) (MIT).

## Official source acknowledgements

Checked-in guidance links to [NWS Flood Safety](https://www.weather.gov/safety/flood), [NWS Heat Safety](https://www.weather.gov/safety/heat), [FEMA Wildfires](https://www.ready.gov/wildfires), and [FEMA Make a Plan](https://www.ready.gov/plan). These agencies—not CreekReady—are authoritative.

Built by **Henderson Damian Mejia Gonzales**, solo, for Iris Hacks IV.
