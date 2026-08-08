# CreekReady

[![Verify CreekReady](https://github.com/nexicturbo/creekready-iris-hacks-iv/actions/workflows/ci.yml/badge.svg)](https://github.com/nexicturbo/creekready-iris-hacks-iv/actions/workflows/ci.yml)

**Official alert in. Clear household plan out.**

![CreekReady editorial illustration showing an alert becoming a household action plan](docs/assets/creekready-cover.png)

*Generated editorial illustration for the project; it does not depict a live emergency or a screenshot of live conditions.*

See the verified [interface capture](docs/assets/creekready-hero.png), [consent-control capture](docs/assets/creekready-interface.png), [desktop product proof](docs/assets/creekready-desktop-result.png), and [live Featherless result](docs/assets/creekready-live-demo.png); every alert shown in them is explicitly fictional.

Judge materials are included as the final [Devpost project story](docs/devpost-story.md), a [browser-viewable PDF](output/pdf/CreekReady-Iris-Hacks-IV.pdf), an editable [PowerPoint deck](docs/CreekReady-Iris-Hacks-IV.pptx), a [pitch script](docs/pitch-script.md), and a transparent [verification matrix](docs/evaluation.md).

CreekReady turns pasted emergency-alert text into a source-linked **Now / Next / If conditions worsen** plan. A household can account for children, an older adult, pets, limited mobility, or no vehicle, and request English or Spanish output.

CreekReady is a preparedness aid, not an alerting or prediction system. It does not observe live conditions, contact authorities, or replace the original alert and instructions from officials.

## How it works

1. A user pastes the text of an official alert and selects household needs and a language.
2. The Flask API validates the request and identifies the likely hazard class.
3. A conservative deterministic extractor creates the displayed fact panel and tokenizes exact directive sentences from the pasted text. Even in AI mode, the model cannot insert a place, time, or official instruction into this trusted panel.
4. If `FEATHERLESS_API_KEY` is configured and the user leaves AI assist on, CreekReady sends only parser-selected directive sentences, the selected needs/language, and a server-owned catalog of vetted actions to Featherless. It does not send the raw alert as a separate field.
5. Featherless returns two flat, prose-free ID rankings: exact alert-instruction IDs and approved action IDs. Pydantic rejects malformed, unknown, duplicate, or extra output. Within each fixed stage, the server restores every omitted required action ahead of selected optional actions and supplies all displayed action, reason, citation, and exact-quote text.
6. If the provider is unavailable, unconfigured, malformed, or fails validation, CreekReady returns a deterministic plan grounded in its checked-in official-guidance catalog.
7. The interface displays extracted facts, actions, sources, limitations, and which mode produced the result.

```text
Browser
  -> Flask routes and request validation
     -> PlanningService
        -> deterministic facts + exact directive candidates
        -> FeatherlessPlanner -> validated instruction/action ID rankings
        -> server stage mapping + required-action restoration
        -> guided fallback    -> deterministic structured result
     -> source-linked JSON response
  -> accessible plan interface
```

Key modules:

- `creekready/__init__.py`: Flask application factory, API routes, payload limits, and security headers.
- `creekready/service.py`: request validation, provider selection, and automatic fallback.
- `creekready/catalog.py`: localized, source-linked action catalog and ID expansion.
- `creekready/provider.py`: Featherless/OpenAI-compatible request and strict ID-selection validation.
- `creekready/fallback.py`: hazard detection, conservative fact extraction, and deterministic actions.
- `creekready/models.py`: Pydantic contracts for facts, stages, sources, and the complete plan.
- `creekready/sources.py`: allowlisted official guidance and hazard-to-source mapping.
- `creekready/static/` and `creekready/templates/`: responsive bilingual interface and accessible browser interactions.

No account, database, location permission, background tracking, or server-side persistence is used.

## Run locally

Python 3.11 or newer is recommended.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

On macOS or Linux, activate the environment with `source .venv/bin/activate`. Then open [http://127.0.0.1:5000](http://127.0.0.1:5000).

The app works without an API key in guided-fallback mode. To enable the optional Featherless path, copy the example and edit the local `.env` file:

```powershell
Copy-Item .env.example .env
```

```dotenv
FEATHERLESS_API_KEY=
FEATHERLESS_MODEL=Qwen/Qwen3-8B
TRUSTED_PROXY_HOPS=0
```

Never commit `.env` or an API key. `FEATHERLESS_MODEL` is optional; the value above is the current code default and can be changed to a compatible model available to the account.

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/health
```

The response reports `guided_fallback` unless a Featherless key was present when the app started. The result payload's `mode` field records which path actually returned each plan.

For a Linux production host, the repository includes a non-root `Dockerfile`, `Procfile`, and environment-driven Gunicorn configuration. The production start command is:

```text
gunicorn --config gunicorn.conf.py app:app
```

`TRUSTED_PROXY_HOPS` defaults to `0`, so untrusted `X-Forwarded-For` headers cannot change the client address used for rate limiting. When deploying behind a reverse proxy, set it to the exact number of proxy hops controlled by the operator (maximum `10`) only after verifying that the edge replaces incoming forwarding headers. An invalid, negative, or larger value stops startup. CreekReady trusts only `X-Forwarded-For`; forwarded host, protocol, port, and path-prefix headers remain untrusted. The correct hop count is host-specific and is intentionally not assumed here.

## Demo fixtures

CreekReady's deterministic path covers flood, wildfire, extreme heat, and an unclassified-alert safe state. For a repeatable no-key demo:

1. Leave `FEATHERLESS_API_KEY` unset and start the app.
2. Use one of the interface's sample alerts, or paste at least 40 characters and 13 words from an official alert.
3. Select household needs, choose English or Spanish, and generate the plan.
4. Confirm the result identifies `guided_fallback`, includes exactly three stages, and displays its official sources and limitations.

For the judged demo, use the checked-in sample controls rather than representing a sample as a current real-world alert. Do not use CreekReady to infer whether an emergency exists now.

## API

`POST /api/plan`

```json
{
  "alert_text": "Full text copied from an official alert...",
  "household_needs": ["older_adult", "pet"],
  "language": "en",
  "use_ai": true
}
```

Supported household needs are `children`, `older_adult`, `pet`, `limited_mobility`, and `no_vehicle`; languages are `en` and `es`. Alert text must contain 40–8,000 characters and at least 13 words. Set `use_ai` to `false` to process the request on the CreekReady server without forwarding it to Featherless.

`GET /api/health` returns application status and the configured provider mode.

## Tests

After installing the requirements, run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
```

Current verified result: **124 tests passed** in the network-free suite. Coverage includes input and size boundaries, provider, fallback, trusted-proxy and rate-limit behavior, and served-frontend modes, English and Spanish flood/wildfire/heat/unclassified behavior, mixed and expired-alert handling, all supported household needs, Spanish Unicode output, conservative fact extraction and confidence, exact instruction tokenization, provider data minimization, strict flat ID contracts, required-action restoration, prompt-injection-shaped inputs, frontend accessibility/runtime invariants, provider failures and invalid payloads, UTC timestamps, configuration normalization, and security headers.

The same suite and dependency check also pass in a clean Python 3.12 environment matching the release container.

The final flattened Featherless contract has also been live-verified with recorded fictional English wildfire, Spanish flood, and prompt-injection-shaped flood requests. Each recorded call returned `mode: featherless`, selected only allowlisted IDs, preserved exact alert wording, and retained every required server-owned action. See the [verification matrix](docs/evaluation.md) for the exact observations and limitations. These are integration checks, not an accuracy, latency, or availability claim.

## Safety and privacy

- Every live-model response is parsed into an ID-only schema before use.
- The model may only rank exact instruction IDs and action IDs from request-specific allowlists; it cannot author visible safety guidance, quotes, reasons, facts, or citations.
- IDs cannot repeat, unknown IDs and extra fields fail validation, and the server—not the model—owns stage assignment.
- The model's ranking hint cannot remove required actions: within each fixed stage, the server restores every omitted required item ahead of selected optional actions.
- The displayed place, time, and official-instruction facts always come from the conservative deterministic extractor, not model-authored fields.
- Provider errors and invalid outputs fail closed to the guided fallback.
- The plan endpoint is rate-limited by the client address observed by Flask to protect the hosted inference path; `PLAN_RATE_LIMIT` can tune the default `12 per minute` policy. `TRUSTED_PROXY_HOPS=0` ignores spoofable forwarding headers by default; a reverse-proxy deployment must set the exact verified hop count as described above. The included Gunicorn configuration uses one threaded worker so the default in-memory limit is process-consistent. A multi-worker deployment should configure a shared `RATELIMIT_STORAGE_URI`.
- Results carry an explicit limitation and retain links to the underlying guidance.
- CreekReady has no live alert feed, weather feed, map, road status, or emergency-services integration.
- Submitted alert text is processed in memory and is not persistently stored by the application. With Featherless enabled, parser-selected directive sentences, selected needs/language, and the vetted action catalog are sent to that provider; the raw alert is not sent as a separate field. Because selected sentences can still contain sensitive text, consult the provider's policies and do not paste private information. Users can turn AI assist off per request so the CreekReady server processes it without forwarding anything to Featherless.

If danger is immediate, follow local authorities and use emergency services—not this application.

## Current limitations

- CreekReady accepts pasted text; it does not verify that the text is authentic or current.
- Rule-based hazard detection currently targets flood, wildfire, and extreme heat.
- Deterministic fact extraction is intentionally simple and may miss complex locations or time windows.
- Spanish mode translates the plan interface/output but does not certify an official translation of the source alert.
- Household selections provide general preparedness prompts, not medical or individualized professional advice.
- Live Featherless behavior depends on account access, model availability, network conditions, and provider output. The checked-in model ID was available and the integration passed the documented smoke checks, but no ongoing performance, accuracy, or availability claim is made.
- Production packaging is included, but no public deployment is claimed until its host, TLS, environment variables, and end-to-end behavior have been verified.
- The project has not undergone formal emergency-management review, accessibility certification, user research, or field validation.

## Official guidance used

- [NOAA National Weather Service — Flood Safety](https://www.weather.gov/safety/flood)
- [NOAA National Weather Service — Heat Safety](https://www.weather.gov/safety/heat)
- [FEMA Ready.gov — Wildfires](https://www.ready.gov/wildfires)
- [FEMA Ready.gov — Make a Plan](https://www.ready.gov/plan)
- [Bastrop County — Wildfire Mitigation Program](https://www.co.bastrop.tx.us/page/em.wildfire_mitigation_program) (project context)

The short excerpts shown by CreekReady are maintained in `creekready/sources.py`; the linked agencies remain authoritative.

## Open-source dependencies

- [Flask](https://github.com/pallets/flask) — web application framework, BSD-3-Clause.
- [Flask-Limiter](https://github.com/alisaifee/flask-limiter) — request rate limiting, MIT.
- [OpenAI Python](https://github.com/openai/openai-python) — OpenAI-compatible HTTP client used with Featherless, Apache-2.0.
- [Pydantic](https://github.com/pydantic/pydantic) — request and response validation, MIT.
- [python-dotenv](https://github.com/theskumar/python-dotenv) — local environment loading, BSD-3-Clause.
- [pytest](https://github.com/pytest-dev/pytest) — automated testing, MIT.
- [Gunicorn](https://github.com/benoitc/gunicorn) — Linux WSGI application server, MIT.

Provider integration follows the [Featherless quickstart](https://featherless.ai/docs/quickstart-guide). CreekReady was created for [Iris Hacks IV](https://iris-hacks-iv.devpost.com/) by Henderson Damian Mejia Gonzales.
