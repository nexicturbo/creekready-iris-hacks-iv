from __future__ import annotations

import re
import unicodedata

from .catalog import build_action_catalog, deterministic_stages
from .models import AlertFacts, PlanStage


HAZARD_TERMS = {
    "flood": (
        "flash flood",
        "flood warning",
        "flood watch",
        "flooding",
        "flood",
        "inundacion repentina",
        "advertencia de inundacion",
        "aviso de inundacion",
        "inundaciones",
        "inundacion",
    ),
    # A generic evacuation warning/order can be issued for hazmat, storms, or
    # many other incidents. It is not evidence of a wildfire by itself.
    "wildfire": (
        "wildfire",
        "wild fire",
        "brush fire",
        "forest fire",
        "incendio forestal",
        "incendios forestales",
        "fuego forestal",
    ),
    "heat": (
        "excessive heat",
        "heat warning",
        "heat advisory",
        "extreme heat",
        "heat index",
        "calor excesivo",
        "advertencia de calor",
        "aviso de calor",
        "calor extremo",
        "indice de calor",
    ),
}

# Ignore hazard names inside a clause that explicitly says the notice is no
# longer active. A stale warning pasted beside a newer warning must never win
# classification merely because its hazard name appears first or more often.
_INACTIVE_NOTICE_TERMS = (
    "expired",
    "has expired",
    "cancelled",
    "canceled",
    "has been cancelled",
    "has been canceled",
    "no longer in effect",
    "lifted",
    "expirado",
    "expirada",
    "ha expirado",
    "cancelado",
    "cancelada",
    "se cancela",
    "ya no esta vigente",
    "levantado",
    "levantada",
)

_CLAUSE_BREAK = re.compile(
    r"(?:[.;!?\n]+|\bbut\b|\bhowever\b|\bpero\b|\bsin\s+embargo\b)",
    flags=re.IGNORECASE,
)


def _fold_for_matching(value: str) -> str:
    """Case-fold text and remove accents for language-agnostic matching."""

    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def detect_hazard(alert_text: str) -> str:
    folded = _fold_for_matching(alert_text)
    active_clauses = [
        clause
        for clause in _CLAUSE_BREAK.split(folded)
        if clause.strip()
        and not any(term in clause for term in _INACTIVE_NOTICE_TERMS)
    ]
    active_text = "\n".join(active_clauses)
    scores = {
        hazard: sum(
            len(re.findall(rf"(?<!\w){re.escape(term)}(?!\w)", active_text))
            for term in terms
        )
        for hazard, terms in HAZARD_TERMS.items()
    }
    detected = [hazard for hazard, score in scores.items() if score]
    # CreekReady produces a single-hazard plan. Mixed alerts are intentionally
    # left unclassified rather than choosing a plan by term count or tie order.
    return detected[0] if len(detected) == 1 else "other"


def _clean_line(line: str) -> str:
    return re.sub(r"^[*•\-\s]+", "", line).strip()


_CLOCK_TIME = r"\d{1,2}(?::\d{2})?\s*(?:(?:a|p)\s*\.?\s*m\.?)?"
_WEEKDAY = (
    r"(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
    r"lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)"
)
_MONTH = (
    r"(?:january|february|march|april|may|june|july|august|september|october|"
    r"november|december|enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
    r"septiembre|octubre|noviembre|diciembre)"
)
_DAYPART = (
    r"(?:today|tonight|tomorrow|morning|afternoon|evening|overnight|noon|"
    r"midnight|hoy|esta\s+noche|ma[nñ]ana|madrugada|tarde|noche|"
    r"mediod[ií]a|medianoche)"
)
_TIME_VALUE = (
    rf"(?:{_CLOCK_TIME}|{_WEEKDAY}|{_MONTH}|{_DAYPART}|immediately|"
    rf"further\s+notice|inmediatamente|nuevo\s+aviso)"
)
_TIME_SUFFIX = (
    rf"(?:\s+(?:(?:on\s+)?(?:{_WEEKDAY}|{_DAYPART})|"
    rf"(?:de|del)\s+(?:{_WEEKDAY}|{_MONTH}|{_DAYPART})))?"
)
_TIME_POINT = rf"(?:(?:las?|el|los)\s+)?{_TIME_VALUE}{_TIME_SUFFIX}"
_TIME_START = re.compile(
    rf"\b(?:until|through|from|effective|hasta|desde|vigente|a\s+partir\s+de)"
    rf"\s+{_TIME_POINT}"
    rf"(?:\s+(?:(?:y\s+)?(?:until|through|to|hasta))\s+{_TIME_POINT})?",
    flags=re.IGNORECASE,
)

_LOCATION_END = (
    r"(?=\s+(?:until|through|from|effective|hasta|desde|vigente|"
    r"a\s+partir\s+de)\b|[.;\n]|$)"
)
_LOCATION_PATTERNS = (
    re.compile(
        rf"(?:for|including|affecting)\s+(?P<location>.{{3,140}}?){_LOCATION_END}",
        flags=re.IGNORECASE,
    ),
    # Spanish ``para`` is common outside location clauses, so require a
    # recognizable alert/order type immediately before it. This prevents text
    # such as "monitoree ... para obtener cambios" from becoming a location.
    re.compile(
        rf"(?:alerta|aviso|advertencia|orden)\s+(?:de\s+)?(?:"
        rf"inundaci[oó]n(?:\s+repentina)?|evacuaci[oó]n|"
        rf"calor\s+(?:excesivo|extremo)|incendio\s+forestal)"
        rf"[^.;\n]{{0,70}}?\s+para\s+(?P<location>.{{3,140}}?){_LOCATION_END}",
        flags=re.IGNORECASE,
    ),
    re.compile(
        rf"(?:que\s+afecta\s+a|afectando\s+a)\s+"
        rf"(?P<location>.{{3,140}}?){_LOCATION_END}",
        flags=re.IGNORECASE,
    ),
)

_INSTRUCTION_TERMS = (
    # English alert directives.
    "evacuate",
    "prepare",
    "shelter",
    "avoid",
    "do not",
    "stay",
    "move",
    "turn around",
    "drink",
    "monitor",
    "call",
    # Spanish imperative or explicitly directive forms. Generic nouns such as
    # "evacuación" are intentionally excluded.
    "evacue",
    "evacuar",
    "preparese",
    "prepararse",
    "refugiese",
    "refugiarse",
    "evite",
    "no conduzca",
    "no maneje",
    "no rodee",
    "no entre",
    "mantengase",
    "quedese",
    "vaya",
    "dirijase",
    "de la vuelta",
    "beba",
    "tome agua",
    "reduzca",
    "use",
    "revise",
    "vigile",
    "monitoree",
    "monitorear",
    "llame",
    "siga",
    "salga",
    "reuna",
    "reunir",
)


def _missing_fact(language: str) -> str:
    return (
        "No se indica claramente en el aviso"
        if language == "es"
        else "Not clearly stated in the alert"
    )


def _split_sentences(text: str) -> list[str]:
    """Split alerts without breaking Spanish ``p. m.``/``a. m.`` times."""

    return re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜÑ¿¡])", text)


def _extract_location(alert_text: str) -> tuple[str | None, bool]:
    for pattern in _LOCATION_PATTERNS:
        match = pattern.search(alert_text)
        if match:
            location = match.group("location").strip(" ,")
            if location:
                return location, True
    return None, False


def _extract_time_window(alert_text: str, language: str = "en") -> str:
    """Extract only phrases that begin with an actual temporal value.

    In particular, ordinary attribution such as "updates from local officials"
    must not become a fabricated time window merely because it contains "from".
    """

    match = _TIME_START.search(alert_text)
    if not match:
        return _missing_fact(language)

    # The grammar ends at the final explicit temporal value. Causal text such
    # as "because of a fire" / "por un incendio" is never absorbed.
    extracted = match.group(0).strip().rstrip(" ,")
    # A sentence-ending period after plain ``AM``/``PM`` is punctuation, while
    # the final period in Spanish ``p. m.``/``a. m.`` belongs to the abbreviation.
    if re.search(r"\b(?:AM|PM)\.$", extracted, flags=re.IGNORECASE):
        extracted = extracted[:-1]
    return extracted


def extract_facts(alert_text: str, hazard_key: str, language: str = "en") -> AlertFacts:
    lines = [_clean_line(line) for line in alert_text.splitlines() if _clean_line(line)]
    default_headline = "Aviso oficial" if language == "es" else "Official alert"
    first_line = next((line for line in lines if len(line) >= 8), default_headline)
    headline = _split_sentences(first_line)[0][:180]

    extracted_location, location_found = _extract_location(alert_text)
    location = extracted_location or _missing_fact(language)
    time_window = _extract_time_window(alert_text, language)
    time_found = time_window != _missing_fact(language)

    sentence_candidates: list[str] = []
    for line in lines:
        sentence_candidates.extend(_split_sentences(line))
    instructions = [
        sentence.strip()[:220]
        for sentence in sentence_candidates
        if any(
            re.search(rf"(?<!\w){re.escape(term)}(?!\w)", _fold_for_matching(sentence))
            for term in _INSTRUCTION_TERMS
        )
    ][:4]

    hazard_labels = (
        {
            "flood": "Inundación o inundación repentina",
            "wildfire": "Incendio forestal",
            "heat": "Calor extremo",
            "other": "Aviso oficial sin clasificar",
        }
        if language == "es"
        else {
            "flood": "Flood or flash flood",
            "wildfire": "Wildfire",
            "heat": "Extreme heat",
            "other": "Unclassified official alert",
        }
    )
    fact_completeness = sum((location_found, time_found, bool(instructions)))
    if hazard_key == "other" or fact_completeness == 0:
        confidence = "low"
    elif fact_completeness == 3:
        confidence = "high"
    else:
        confidence = "medium"

    return AlertFacts(
        headline=headline,
        hazard=hazard_labels[hazard_key],
        location=location[:160],
        time_window=time_window[:160],
        official_instructions=instructions,
        confidence=confidence,
    )


def build_fallback_stages(
    hazard_key: str, needs: list[str], language: str
) -> list[PlanStage]:
    catalog = build_action_catalog(hazard_key, needs, language)
    return deterministic_stages(catalog, language)
