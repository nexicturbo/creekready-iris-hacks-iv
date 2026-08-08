# CreekReady — two-minute pitch and demo choreography

## Before presenting

- Start the server and open the app in a clean browser window.
- Use the checked-in wildfire sample with Featherless AI assist on. The automatic guided fallback remains the recovery path if the provider is slow or unavailable.
- Preselect **older adult** and **pet**, with English as the initial language.
- Keep a completed result open in a second tab as a backup.
- Increase browser zoom enough for judges to read the result.
- Close notifications and unrelated tabs. Do not show an API key or `.env` file.
- Never describe the sample as a current alert or imply that CreekReady has live conditions.

## Script

### 0:00–0:15 — Hook

**Say:**

“An emergency alert can describe a threat to an entire community—but a family still has to answer: what do we do next? In Cedar Creek, that plan may include an older adult, a pet, or no transportation.”

**Show:** The empty CreekReady screen. Keep the cursor near the sample-alert control.

### 0:15–0:30 — Product promise

**Say:**

“CreekReady turns an official alert into a cited household plan. It does not predict emergencies or replace officials; it makes the warning you received easier to act on.”

**Show:** The safety statement and the alert input.

### 0:30–1:10 — The magic moment

**Say while acting:**

“Here is a sample wildfire alert—not a live event. I’ll account for an older adult and a pet.”

**Do:** Load the wildfire sample, confirm **older adult** and **pet**, and submit.

**Say when the result appears:**

“The three-stage plan appears first: Now, Next, and If conditions worsen. A deterministic extractor creates the fact panel below; the model cannot inject a place, time, or official instruction.”

**Show:** Sweep across the three stage headings, pause on one household-specific action and its source chip, then point to the fact panel.

### 1:10–1:30 — Trust, sources, and language

**Say:**

“Every action carries a source ID—either the pasted alert or checked-in FEMA/National Weather Service guidance. The interface keeps those sources distinct, states which mode ran, and names what CreekReady cannot know.”

**Show:** Open or point to one source and the limitations/mode label. Do not merely flip the language selector on an existing result: a Spanish result requires submitting the Spanish fixture again. Omit that extra interaction in the two-minute demo and describe it in one sentence instead.

**Optional sentence:** “CreekReady can generate the plan in Spanish without calling it an official alert translation.”

### 1:30–1:48 — Engineering and reliability

**Say:**

“Featherless receives only parser-selected directive sentences, needs, language, and a vetted action catalog. It ranks exact instruction IDs and action IDs, writing neither the quote nor the guidance. Unknown, duplicate, malformed, or extra output fails closed, and the server restores every required action before an optional one.”

**Show:** Point to the mode label and bounded-AI receipt; do not leave the demo to show code unless a judge asks.

### 1:48–2:00 — Close

**Say:**

“CreekReady does not create a warning. It helps a household act on one—with the official signal still in control. Official alert in. Clear household plan out.”

**Show:** End on the complete three-stage plan and CreekReady name.

## Fast recovery lines

- **If Featherless fails:** “This is the reliability behavior I designed: CreekReady has switched to its bounded official-guidance fallback, and it labels that mode directly.” Continue the demo.
- **If the request errors:** Switch to the pre-generated backup tab and say, “I have the same sample result ready so we can focus on the workflow.” Do not invent a cause.
- **If asked whether alerts are live:** “No. This prototype processes text the user supplies and has no live alert, weather, road, or location feed.”
- **If asked whether it is emergency advice:** “It is a preparedness aid. The original alert, local authorities, and emergency services remain authoritative.”
- **If asked about accuracy:** “We have not established an accuracy metric or completed field validation. We constrain the output structurally and visibly fall back, but formal evaluation is essential future work.”
- **If asked about privacy:** “The app stores no account or plan. With Featherless enabled, parser-selected directive sentences, selected needs/language, and the vetted action catalog are sent to that provider; the raw alert is not sent as a separate field. Those sentences can still contain sensitive text, so users should avoid private information and review provider policies. The AI toggle turns that forwarding off.”

## Judge-question anchors

- **Innovation:** household constraints plus source-bounded structured output, not an open-ended emergency chatbot.
- **Impact:** bridges the gap between receiving an official warning and preparing a specific household.
- **Why Featherless is purposeful:** the model performs semantic prioritization over variable English/Spanish alert directives and household-aware action candidates. The deterministic server owns facts, exact visible wording, stage assignment, required actions, validation, and fallback. It is a bounded decision component, not a decorative chat layer.
- **Execution:** deterministic fact isolation, data-minimized ID-only provider adapter, required-action restoration, 113 passing offline tests, recorded live English/Spanish/adversarial-shaped integration checks, rate limiting, deterministic fallback, and explicit limitations.
- **Responsible AI:** no prediction, no invented live data, no replacement of official instructions, and no unverified performance claims.
