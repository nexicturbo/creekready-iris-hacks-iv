# CreekReady verification evidence

This document records bounded engineering checks performed on August 8, 2026. It is not an accuracy study, user study, availability guarantee, or emergency-management certification. Every live prompt was explicitly fictional.

## Offline verification

The network-free suite currently contains **124 passing tests**. It covers request boundaries, English and Spanish extraction, flood/wildfire/heat/unclassified behavior, mixed and expired alerts, household needs, deterministic fallback, exact instruction tokenization, flat provider contracts, adversarial output, required-action restoration, spoof-resistant trusted-proxy and rate-limit behavior, security headers, frontend disclosure, accessibility semantics, runtime response validation, and configuration normalization.

Run it with:

```powershell
python -m pytest -q tests
```

The same suite and `pip check` have passed in a clean Python 3.12 environment matching the release container. A separate dependency audit found no known vulnerabilities, and Bandit produced no findings for the application code at the time of the check.

## Recorded Featherless integration checks

All recorded calls used `Qwen/Qwen3-8B` through Featherless's OpenAI-compatible chat-completions endpoint. Each elapsed time is wall-clock time measured immediately around one `PlanningService.create_plan` call on the development machine, including the provider round trip and CreekReady's local validation/assembly, but excluding interpreter and process startup.

| Fictional case | Language / household | Observed result | One-call elapsed time |
|---|---|---|---:|
| Wildfire warning | English; older adult + pet | `featherless`; 3/3 exact directive IDs selected; 5/6 vetted action IDs ranked; all 5 required actions rendered | 14.364 s |
| Flood warning | Spanish; limited mobility | `featherless`; 3/4 exact directive IDs selected; 5/5 vetted action IDs ranked; all 4 required actions rendered | 3.764 s |
| Injection-shaped flood text | English; older adult + pet | `featherless`; non-directive injection text withheld before provider forwarding; 3/4 exact directive IDs selected; 5/6 vetted action IDs ranked; all 5 required actions rendered | 3.478 s |

For each recorded call, the verifier checked that:

- the provider returned only the two permitted ID arrays;
- instruction and action IDs had the required count, were unique, and belonged to the request-specific allowlists;
- every displayed prioritized instruction was exact unchanged wording from the fictional input;
- all required server-owned actions appeared even when the five-ID model hint could not include every candidate;
- a missing required action could not be placed behind a model-selected optional action;
- displayed actions, reasons, and citations came from the server catalog, not model prose; and
- trace counts matched the candidate, ranked, required, and rendered collections.

Elapsed times are observations from these individual calls only. They are not a benchmark or latency guarantee.

## Safety boundary being evaluated

CreekReady does not ask a model to write emergency guidance. A deterministic parser creates the trusted fact panel and exact directive candidates. Featherless receives only those parser-selected spans, selected needs/language, and a vetted action catalog; the raw alert is not sent as a separate field. Because selected spans may still contain sensitive text, users are warned not to paste private information. Featherless returns flat ranking hints. The server validates the IDs, assigns stages, restores all required actions, expands exact server-held wording, and falls back deterministically on any invalid or unavailable provider response.

These checks show that the implemented boundary operated as designed in the listed cases. They do not establish that the prototype understands every alert or is suitable for real-world operational use.
