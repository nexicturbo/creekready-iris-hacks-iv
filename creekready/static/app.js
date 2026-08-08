"use strict";

const copy = {
  en: {
    skip: "Skip to the planner",
    checking: "Checking planner…",
    readyAI: "Featherless AI assist configured",
    readyFallback: "Vetted guidance ready",
    unavailable: "Planner connection unavailable",
    eyebrow: "Official alert → household action",
    heroTitle: "Make the next safe step clear.",
    heroLede: "Paste an official emergency alert. CreekReady separates its facts from general guidance, then organizes a practical plan around your household.",
    trustOne: "Sources stay attached",
    trustTwo: "No live tracking",
    trustThree: "English + Español",
    routeOneTitle: "Paste",
    routeOneText: "the complete alert",
    routeTwoTitle: "Personalize",
    routeTwoText: "for household needs",
    routeThreeTitle: "Act",
    routeThreeText: "with sources in view",
    routeNote: "One alert in. A calm, staged plan out.",
    plannerEyebrow: "Build your action map",
    plannerTitle: "Start with the alert itself.",
    plannerIntro: "Use the full wording from the issuing agency. CreekReady does not fetch or monitor alerts for you.",
    alertLabel: "Paste an official alert",
    required: "Required",
    alertHint: "Include its location, timing, and instructions. Do not enter private information.",
    trySample: "Try a fictional sample:",
    sampleFlood: "Flash flood",
    sampleWildfire: "Wildfire",
    sampleHeat: "Extreme heat",
    alertPlaceholder: "Paste the complete official alert here…",
    sampleWarning: "Samples are demonstrations—not active warnings.",
    needsLegend: "Who should this plan account for?",
    needsHint: "Select any that apply. This changes planning details, not the alert facts.",
    needChildren: "Children",
    needOlder: "Older adult",
    needPet: "Pet",
    needMobility: "Limited mobility",
    needVehicle: "No vehicle",
    languageLabel: "Plan language",
    aiToggleTitle: "Featherless AI assist",
    aiToggleText: "Sends this alert to Featherless. Turn off to keep it on this CreekReady server.",
    submit: "Build my action map",
    building: "Building your action map…",
    errorTitle: "We couldn’t build that plan.",
    loading: "Reading the alert, checking sources, and organizing next steps…",
    resultsEyebrow: "Your action map",
    resultsTitle: "Read now. Prepare next.",
    copy: "Copy plan",
    read: "Read aloud",
    stopReading: "Stop reading",
    edit: "Edit alert",
    factsLabel: "Alert facts only",
    factsTitle: "What the pasted alert says",
    hazard: "Hazard",
    location: "Location",
    timeWindow: "Time window",
    officialInstructions: "Instructions found in the alert",
    householdPlan: "Household fit",
    traceableLabel: "Traceable guidance",
    sourcesTitle: "Sources",
    limitsLabel: "Know the boundary",
    limitsTitle: "Limitations",
    safetyTitle: "Official instructions come first.",
    safetyText: "CreekReady cannot see current conditions. For an immediate life-threatening emergency in the U.S., call 911.",
    footer: "A clarity tool for the moments between alert and action.",
    shortAlert: "Paste at least 13 words from the official alert, including its place, time, or instructions.",
    networkError: "The planner could not be reached. Check your connection and try again.",
    genericError: "Something went wrong while building the plan. Please try again.",
    copied: "Plan copied.",
    copyFailed: "Copy failed. Select the plan text and try again.",
    reading: "Reading the plan aloud.",
    readingStopped: "Reading stopped.",
    readUnsupported: "Read aloud is not supported by this browser.",
    editReady: "The alert is ready to edit.",
    modeAI: "Featherless-ranked plan",
    modeFallback: "Vetted guidance mode",
    confidenceHigh: "High extraction confidence",
    confidenceMedium: "Medium extraction confidence",
    confidenceLow: "Low extraction confidence",
    generated: "Generated",
    stage: "Stage",
    source: "source",
    sources: "sources",
    openSource: "Open official source ↗",
    planTitle: "CreekReady household action map",
    planFacts: "ALERT FACTS",
    planSources: "SOURCES",
    planLimits: "LIMITATIONS",
    reason: "Why",
    sourceLabel: "Sources"
  },
  es: {
    skip: "Ir al planificador",
    checking: "Verificando el planificador…",
    readyAI: "Asistencia de Featherless configurada",
    readyFallback: "Orientación verificada lista",
    unavailable: "No hay conexión con el planificador",
    eyebrow: "Aviso oficial → acción del hogar",
    heroTitle: "Aclare el siguiente paso seguro.",
    heroLede: "Pegue un aviso oficial de emergencia. CreekReady separa los hechos de la orientación general y organiza un plan práctico para su hogar.",
    trustOne: "Las fuentes permanecen unidas",
    trustTwo: "Sin rastreo en vivo",
    trustThree: "English + Español",
    routeOneTitle: "Pegue",
    routeOneText: "el aviso completo",
    routeTwoTitle: "Personalice",
    routeTwoText: "según las necesidades",
    routeThreeTitle: "Actúe",
    routeThreeText: "con las fuentes a la vista",
    routeNote: "Un aviso entra. Un plan tranquilo y ordenado sale.",
    plannerEyebrow: "Cree su mapa de acción",
    plannerTitle: "Comience con el aviso.",
    plannerIntro: "Use el texto completo de la agencia emisora. CreekReady no busca ni monitorea avisos.",
    alertLabel: "Pegue un aviso oficial",
    required: "Obligatorio",
    alertHint: "Incluya ubicación, horario e instrucciones. No ingrese información privada.",
    trySample: "Pruebe una muestra ficticia:",
    sampleFlood: "Inundación repentina",
    sampleWildfire: "Incendio forestal",
    sampleHeat: "Calor extremo",
    alertPlaceholder: "Pegue aquí el aviso oficial completo…",
    sampleWarning: "Las muestras son demostraciones, no avisos activos.",
    needsLegend: "¿A quién debe tomar en cuenta este plan?",
    needsHint: "Seleccione lo que corresponda. Esto cambia los detalles del plan, no los hechos del aviso.",
    needChildren: "Niños",
    needOlder: "Adulto mayor",
    needPet: "Mascota",
    needMobility: "Movilidad limitada",
    needVehicle: "Sin vehículo",
    languageLabel: "Idioma del plan",
    aiToggleTitle: "Asistencia de Featherless AI",
    aiToggleText: "Envía este aviso a Featherless. Desactive la opción para mantenerlo en este servidor de CreekReady.",
    submit: "Crear mi mapa de acción",
    building: "Creando su mapa de acción…",
    errorTitle: "No pudimos crear ese plan.",
    loading: "Leyendo el aviso, revisando fuentes y organizando los próximos pasos…",
    resultsEyebrow: "Su mapa de acción",
    resultsTitle: "Lea ahora. Prepárese después.",
    copy: "Copiar plan",
    read: "Leer en voz alta",
    stopReading: "Detener lectura",
    edit: "Editar aviso",
    factsLabel: "Solo hechos del aviso",
    factsTitle: "Lo que dice el aviso pegado",
    hazard: "Peligro",
    location: "Ubicación",
    timeWindow: "Periodo",
    officialInstructions: "Instrucciones encontradas en el aviso",
    householdPlan: "Ajuste al hogar",
    traceableLabel: "Orientación rastreable",
    sourcesTitle: "Fuentes",
    limitsLabel: "Conozca los límites",
    limitsTitle: "Limitaciones",
    safetyTitle: "Las instrucciones oficiales tienen prioridad.",
    safetyText: "CreekReady no puede ver las condiciones actuales. Para una emergencia inmediata que amenaza la vida en EE. UU., llame al 911.",
    footer: "Una herramienta de claridad para los momentos entre aviso y acción.",
    shortAlert: "Pegue al menos 13 palabras del aviso oficial e incluya el lugar, horario o instrucciones.",
    networkError: "No se pudo conectar con el planificador. Revise su conexión e inténtelo de nuevo.",
    genericError: "Ocurrió un problema al crear el plan. Inténtelo de nuevo.",
    copied: "Plan copiado.",
    copyFailed: "No se pudo copiar. Seleccione el texto del plan e inténtelo de nuevo.",
    reading: "Leyendo el plan en voz alta.",
    readingStopped: "Lectura detenida.",
    readUnsupported: "Este navegador no admite la lectura en voz alta.",
    editReady: "El aviso está listo para editar.",
    modeAI: "Plan ordenado por Featherless",
    modeFallback: "Modo de orientación verificada",
    confidenceHigh: "Confianza alta en la extracción",
    confidenceMedium: "Confianza media en la extracción",
    confidenceLow: "Confianza baja en la extracción",
    generated: "Generado",
    stage: "Etapa",
    source: "fuente",
    sources: "fuentes",
    openSource: "Abrir fuente oficial ↗",
    planTitle: "Mapa de acción del hogar de CreekReady",
    planFacts: "HECHOS DEL AVISO",
    planSources: "FUENTES",
    planLimits: "LIMITACIONES",
    reason: "Por qué",
    sourceLabel: "Fuentes"
  }
};

const samples = {
  en: {
    flood: "SAMPLE ALERT — NOT AN ACTIVE WARNING\nThe National Weather Service has issued a Flash Flood Warning for the fictional Pine Creek area, including Example Road and Demo Crossing, until 9:30 PM. Heavy rain may flood low-water crossings. Do not drive around barricades or enter flooded roads. Move to higher ground if local officials direct you to do so. Monitor the issuing agency for updates.",
    wildfire: "SAMPLE ALERT — NOT AN ACTIVE WARNING\nCedar County Emergency Management has issued an evacuation warning for the fictional Juniper Ridge area from 3:00 PM until further notice because of a nearby wildfire. Residents should prepare to leave, gather medications and pets, and use Canyon Road if an evacuation order is issued. Avoid Ridge Road. Monitor county alerts for changes.",
    heat: "SAMPLE ALERT — NOT AN ACTIVE WARNING\nThe National Weather Service has issued an Excessive Heat Warning for the fictional Clear Valley area from noon Monday through 8:00 PM Tuesday. Dangerously hot conditions are expected. Drink water, reduce strenuous outdoor activity, use air conditioning when possible, and check on people vulnerable to heat. Monitor the issuing agency for updates."
  },
  es: {
    flood: "AVISO DE MUESTRA — NO ES UNA ALERTA ACTIVA\nEl Servicio Meteorológico Nacional emitió una advertencia de inundación repentina para la zona ficticia de Pine Creek, incluidas Example Road y Demo Crossing, hasta las 9:30 p. m. La lluvia intensa puede inundar cruces bajos. No rodee barricadas ni entre en caminos inundados. Vaya a un lugar más alto si las autoridades locales se lo indican.",
    wildfire: "AVISO DE MUESTRA — NO ES UNA ALERTA ACTIVA\nGestión de Emergencias del condado ficticio de Cedar emitió una advertencia de evacuación para Juniper Ridge desde las 3:00 p. m. y hasta nuevo aviso por un incendio forestal cercano. Los residentes deben prepararse para salir, reunir medicamentos y mascotas, y usar Canyon Road si se emite una orden. Evite Ridge Road y monitoree los avisos del condado.",
    heat: "AVISO DE MUESTRA — NO ES UNA ALERTA ACTIVA\nEl Servicio Meteorológico Nacional emitió una advertencia de calor excesivo para la zona ficticia de Clear Valley desde el mediodía del lunes hasta las 8:00 p. m. del martes. Beba agua, reduzca la actividad intensa al aire libre, use aire acondicionado cuando sea posible y revise a las personas vulnerables al calor."
  }
};

const state = {
  language: "en",
  currentPlan: null,
  speaking: false,
  healthProvider: null
};

const form = document.querySelector("#plan-form");
const alertText = document.querySelector("#alert-text");
const languageSelect = document.querySelector("#language");
const useAi = document.querySelector("#use-ai");
const submitButton = document.querySelector("#submit-button");
const submitLabel = submitButton.querySelector("span:first-child");
const errorPanel = document.querySelector("#form-error");
const errorMessage = document.querySelector("#error-message");
const loadingPanel = document.querySelector("#loading-panel");
const results = document.querySelector("#results");
const toolStatus = document.querySelector("#tool-status");
const readButton = document.querySelector("#read-plan");

function t(key) {
  return copy[state.language][key] || copy.en[key] || key;
}

function makeElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function translatePage() {
  state.language = languageSelect.value === "es" ? "es" : "en";
  document.documentElement.lang = state.language;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });
  updateHealthLabel();
  if (!state.speaking) readButton.querySelector("span:last-child").textContent = t("read");
}

function updateCount() {
  document.querySelector("#alert-count").textContent = `${alertText.value.length.toLocaleString()} / 8,000`;
}

function updateHealthLabel() {
  const pill = document.querySelector("#system-pill");
  const label = document.querySelector("#system-status");
  if (state.healthProvider === "featherless") {
    pill.classList.add("is-ready");
    label.textContent = t("readyAI");
  } else if (state.healthProvider === "guided_fallback") {
    pill.classList.add("is-ready");
    label.textContent = t("readyFallback");
  } else if (state.healthProvider === "error") {
    pill.classList.remove("is-ready");
    label.textContent = t("unavailable");
  } else {
    label.textContent = t("checking");
  }
}

async function checkHealth() {
  try {
    const response = await fetch("/api/health", { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error("health");
    const data = await response.json();
    state.healthProvider = data.provider;
  } catch (_error) {
    state.healthProvider = "error";
  }
  updateHealthLabel();
}

function showError(message) {
  errorMessage.textContent = message;
  errorPanel.hidden = false;
  alertText.setAttribute("aria-invalid", "true");
  errorPanel.focus();
}

function clearError() {
  errorPanel.hidden = true;
  errorMessage.textContent = "";
  alertText.removeAttribute("aria-invalid");
}

function setLoading(isLoading) {
  form.setAttribute("aria-busy", String(isLoading));
  loadingPanel.hidden = !isLoading;
  submitButton.disabled = isLoading;
  submitLabel.textContent = isLoading ? t("building") : t("submit");
}

function sourceDomId(sourceId) {
  return `source-${String(sourceId).replace(/[^a-zA-Z0-9_-]/g, "-")}`;
}

function renderFacts(facts) {
  document.querySelector("#fact-headline").textContent = facts.headline || "";
  document.querySelector("#fact-hazard").textContent = facts.hazard || "";
  document.querySelector("#fact-location").textContent = facts.location || "";
  document.querySelector("#fact-time").textContent = facts.time_window || "";

  const confidence = ["high", "medium", "low"].includes(facts.confidence) ? facts.confidence : "low";
  const confidenceBadge = document.querySelector("#confidence-badge");
  confidenceBadge.dataset.confidence = confidence;
  confidenceBadge.textContent = t(`confidence${confidence.charAt(0).toUpperCase()}${confidence.slice(1)}`);

  const wrapper = document.querySelector("#official-instructions-wrap");
  const list = document.querySelector("#official-instructions");
  list.replaceChildren();
  const instructions = Array.isArray(facts.official_instructions) ? facts.official_instructions : [];
  wrapper.hidden = instructions.length === 0;
  instructions.forEach((instruction) => list.append(makeElement("li", "", instruction)));
}

function renderStages(stages) {
  const grid = document.querySelector("#stage-grid");
  grid.replaceChildren();
  (Array.isArray(stages) ? stages : []).forEach((stage, index) => {
    const stageKey = ["now", "next", "worse"].includes(stage.key) ? stage.key : "next";
    const card = makeElement("article", "stage-card");
    card.dataset.stage = stageKey;
    card.dataset.number = `0${index + 1}`;

    const header = makeElement("header", "stage-header");
    header.append(makeElement("p", "stage-kicker", `${t("stage")} 0${index + 1}`));
    header.append(makeElement("h3", "", stage.title || ""));
    header.append(makeElement("p", "stage-subtitle", stage.subtitle || ""));
    card.append(header);

    const actionList = makeElement("ol", "action-list");
    (Array.isArray(stage.items) ? stage.items : []).forEach((item) => {
      const row = makeElement("li", "action-item");
      row.append(makeElement("p", "action-text", item.action || ""));
      row.append(makeElement("p", "action-reason", item.reason || ""));
      const citations = makeElement("div", "citation-row");
      (Array.isArray(item.source_ids) ? item.source_ids : []).forEach((sourceId) => {
        const link = makeElement("a", "citation-link", sourceId);
        link.href = `#${sourceDomId(sourceId)}`;
        link.setAttribute("aria-label", `${t("sourceLabel")}: ${sourceId}`);
        citations.append(link);
      });
      row.append(citations);
      actionList.append(row);
    });
    card.append(actionList);
    grid.append(card);
  });
}

function safeHttpUrl(rawUrl) {
  if (!rawUrl) return null;
  try {
    const parsed = new URL(rawUrl);
    return ["https:", "http:"].includes(parsed.protocol) ? parsed.href : null;
  } catch (_error) {
    return null;
  }
}

function renderSources(sources) {
  const list = document.querySelector("#source-list");
  list.replaceChildren();
  const safeSources = Array.isArray(sources) ? sources : [];
  document.querySelector("#source-count").textContent = `${safeSources.length} ${t(safeSources.length === 1 ? "source" : "sources")}`;

  safeSources.forEach((source) => {
    const card = makeElement("article", "source-card");
    card.id = sourceDomId(source.id);
    card.append(makeElement("span", "source-id", source.id || ""));
    card.append(makeElement("h4", "", source.title || ""));
    card.append(makeElement("p", "source-agency", source.agency || ""));
    card.append(makeElement("p", "source-excerpt", source.excerpt || ""));

    const url = safeHttpUrl(source.url);
    if (url) {
      const link = makeElement("a", "source-link", t("openSource"));
      link.href = url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      card.append(link);
    }
    list.append(card);
  });
}

function renderLimitations(limitations) {
  const list = document.querySelector("#limitations-list");
  list.replaceChildren();
  (Array.isArray(limitations) ? limitations : []).forEach((item) => list.append(makeElement("li", "", item)));
}

function renderPlan(plan) {
  state.currentPlan = plan;
  const modeBadge = document.querySelector("#mode-badge");
  const isAi = plan.mode === "featherless";
  modeBadge.textContent = t(isAi ? "modeAI" : "modeFallback");
  modeBadge.classList.toggle("is-fallback", !isAi);

  const parsedDate = new Date(plan.generated_at);
  const dateText = Number.isNaN(parsedDate.getTime())
    ? ""
    : new Intl.DateTimeFormat(state.language === "es" ? "es-US" : "en-US", {
      hour: "numeric", minute: "2-digit", month: "short", day: "numeric"
    }).format(parsedDate);
  document.querySelector("#generated-time").textContent = dateText ? `${t("generated")} ${dateText}` : "";
  document.querySelector("#disclaimer").textContent = plan.disclaimer || "";
  document.querySelector("#household-summary").textContent = plan.household_summary || "";

  renderFacts(plan.facts || {});
  renderStages(plan.stages);
  renderSources(plan.sources);
  renderLimitations(plan.limitations);

  results.hidden = false;
  document.querySelector("#results-title").focus({ preventScroll: true });
  results.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
}

function planAsText(plan) {
  const lines = [t("planTitle"), "", plan.disclaimer || "", "", t("planFacts")];
  lines.push(plan.facts?.headline || "");
  lines.push(`${t("hazard")}: ${plan.facts?.hazard || ""}`);
  lines.push(`${t("location")}: ${plan.facts?.location || ""}`);
  lines.push(`${t("timeWindow")}: ${plan.facts?.time_window || ""}`, "");
  lines.push(plan.household_summary || "", "");

  (plan.stages || []).forEach((stage) => {
    lines.push(`${stage.title}: ${stage.subtitle}`);
    (stage.items || []).forEach((item, index) => {
      lines.push(`${index + 1}. ${item.action}`);
      lines.push(`   ${t("reason")}: ${item.reason}`);
      lines.push(`   ${t("sourceLabel")}: ${(item.source_ids || []).join(", ")}`);
    });
    lines.push("");
  });

  lines.push(t("planSources"));
  (plan.sources || []).forEach((source) => lines.push(`- ${source.id}: ${source.title} — ${source.agency}${source.url ? ` (${source.url})` : ""}`));
  lines.push("", t("planLimits"));
  (plan.limitations || []).forEach((limit) => lines.push(`- ${limit}`));
  return lines.join("\n");
}

async function copyPlan() {
  if (!state.currentPlan) return;
  try {
    const text = planAsText(state.currentPlan);
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      const helper = makeElement("textarea", "clipboard-helper");
      helper.value = text;
      helper.setAttribute("readonly", "");
      document.body.append(helper);
      helper.select();
      const copied = document.execCommand("copy");
      helper.remove();
      if (!copied) throw new Error("copy");
    }
    toolStatus.textContent = t("copied");
  } catch (_error) {
    toolStatus.textContent = t("copyFailed");
  }
}

function updateReadButton() {
  readButton.querySelector("span:last-child").textContent = t(state.speaking ? "stopReading" : "read");
}

function readPlan() {
  if (!state.currentPlan || !("speechSynthesis" in window)) {
    toolStatus.textContent = t("readUnsupported");
    return;
  }
  if (state.speaking) {
    window.speechSynthesis.cancel();
    state.speaking = false;
    updateReadButton();
    toolStatus.textContent = t("readingStopped");
    return;
  }

  const utterance = new SpeechSynthesisUtterance(planAsText(state.currentPlan));
  utterance.lang = state.language === "es" ? "es-MX" : "en-US";
  utterance.rate = 0.95;
  utterance.onend = () => {
    state.speaking = false;
    updateReadButton();
    toolStatus.textContent = "";
  };
  utterance.onerror = () => {
    state.speaking = false;
    updateReadButton();
    toolStatus.textContent = t("readUnsupported");
  };
  state.speaking = true;
  updateReadButton();
  toolStatus.textContent = t("reading");
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

async function submitPlan(event) {
  event.preventDefault();
  clearError();
  toolStatus.textContent = "";
  const text = alertText.value.trim();
  if (text.length < 40 || text.split(/\s+/).length < 13) {
    showError(t("shortAlert"));
    return;
  }

  const householdNeeds = Array.from(document.querySelectorAll('input[name="household_needs"]:checked')).map((input) => input.value);
  setLoading(true);
  try {
    const response = await fetch("/api/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({
        alert_text: text,
        household_needs: householdNeeds,
        language: state.language,
        use_ai: useAi.checked
      })
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || t("genericError"));
    renderPlan(data);
  } catch (error) {
    const message = error instanceof TypeError ? t("networkError") : (error.message || t("genericError"));
    showError(message);
  } finally {
    setLoading(false);
  }
}

document.querySelectorAll("[data-sample]").forEach((button) => {
  button.addEventListener("click", () => {
    alertText.value = samples[state.language][button.dataset.sample];
    clearError();
    updateCount();
    alertText.focus();
  });
});

alertText.addEventListener("input", () => {
  updateCount();
  if (alertText.hasAttribute("aria-invalid")) clearError();
});

languageSelect.addEventListener("change", translatePage);
form.addEventListener("submit", submitPlan);
document.querySelector("#copy-plan").addEventListener("click", copyPlan);
readButton.addEventListener("click", readPlan);
document.querySelector("#edit-alert").addEventListener("click", () => {
  document.querySelector("#planner").scrollIntoView({ behavior: "smooth", block: "start" });
  alertText.focus({ preventScroll: true });
  toolStatus.textContent = t("editReady");
});

if (!("speechSynthesis" in window)) {
  readButton.disabled = true;
  readButton.title = t("readUnsupported");
}

translatePage();
updateCount();
checkHealth();
