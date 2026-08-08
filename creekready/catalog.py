from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Protocol

from .models import ActionItem, PlanStage


StageKey = Literal["now", "next", "worse"]
STAGE_ORDER: tuple[StageKey, ...] = ("now", "next", "worse")
ActionSpec = tuple[
    str,
    StageKey,
    bool,
    tuple[str, ...],
    str,
    str,
    str,
    str,
]


class SelectionLike(Protocol):
    key: StageKey
    action_ids: list[str]


@dataclass(frozen=True)
class CatalogAction:
    """Server-owned emergency guidance that a model may select, never rewrite."""

    id: str
    stage: StageKey
    action: str
    reason: str
    source_ids: tuple[str, ...]
    required: bool = False

    def as_prompt_item(self) -> dict[str, object]:
        return {
            "id": self.id,
            "stage": self.stage,
            "action": self.action,
            "reason": self.reason,
            "source_ids": list(self.source_ids),
            "required": self.required,
        }

    def as_action_item(self) -> ActionItem:
        return ActionItem(
            id=self.id,
            action=self.action,
            reason=self.reason,
            source_ids=list(self.source_ids),
        )


# Stable IDs are deliberately language-independent. Each tuple contains:
# id, stage, required, source IDs, English action/reason, Spanish action/reason.
_HAZARD_ACTIONS: dict[str, tuple[ActionSpec, ...]] = {
    "flood": (
        (
            "flood.now.avoid_water",
            "now",
            True,
            ("NWS-FLOOD",),
            "Do not walk or drive into floodwater, and never go around a barricade.",
            "Water depth and road damage can be impossible to judge.",
            "No camine ni conduzca por agua de inundación y no rodee barricadas.",
            "La profundidad y el estado del camino pueden ser imposibles de evaluar.",
        ),
        (
            "flood.now.follow_alert",
            "now",
            False,
            ("ALERT-TEXT",),
            "Follow the locations, timing, and instructions in the complete official alert.",
            "CreekReady does not replace the issuing authority.",
            "Siga las ubicaciones, los horarios y las instrucciones del aviso oficial completo.",
            "CreekReady no reemplaza a la autoridad que emitió el aviso.",
        ),
        (
            "flood.next.stage_route",
            "next",
            True,
            ("READY-PLAN",),
            "Stage communications, medication, and a route that avoids low-water crossings.",
            "A prepared route reduces decisions during rapidly changing conditions.",
            "Prepare comunicaciones, medicamentos y una ruta que evite cruces de agua baja.",
            "Una ruta preparada reduce decisiones durante cambios rápidos.",
        ),
        (
            "flood.worse.higher_ground_if_directed",
            "worse",
            True,
            ("ALERT-TEXT", "NWS-FLOOD"),
            "Move away from threatened areas or to higher ground when the issuing authority directs it.",
            "Observed conditions and official orders always outrank this summary.",
            "Aléjese de las áreas amenazadas o vaya a un lugar más alto cuando la autoridad emisora lo indique.",
            "Las condiciones observadas y las órdenes oficiales siempre tienen prioridad sobre este resumen.",
        ),
    ),
    "wildfire": (
        (
            "wildfire.now.review_alert",
            "now",
            True,
            ("ALERT-TEXT", "READY-WILDFIRE"),
            "Review the official alert and be ready to leave immediately if authorities direct it.",
            "Local routes and orders reflect conditions this app cannot observe.",
            "Revise el aviso oficial y prepárese para salir de inmediato si las autoridades lo ordenan.",
            "Las rutas y órdenes locales reflejan condiciones que esta aplicación no puede observar.",
        ),
        (
            "wildfire.now.identify_routes",
            "now",
            False,
            ("READY-WILDFIRE",),
            "Identify two ways out and, if you have a vehicle, keep it positioned for departure.",
            "Fire or smoke can close a route with little notice.",
            "Identifique dos rutas de salida y, si tiene vehículo, manténgalo orientado hacia la salida.",
            "El fuego o el humo pueden cerrar una ruta con poco aviso.",
        ),
        (
            "wildfire.next.stage_essentials",
            "next",
            True,
            ("READY-PLAN", "READY-WILDFIRE"),
            "Gather medication, documents, water, phones, and supplies for household members and pets.",
            "Staging essentials now supports a faster departure.",
            "Reúna medicamentos, documentos, agua, teléfonos y artículos para los miembros del hogar y las mascotas.",
            "Preparar lo esencial ahora facilita una salida más rápida.",
        ),
        (
            "wildfire.worse.evacuate_if_directed",
            "worse",
            True,
            ("ALERT-TEXT", "READY-WILDFIRE"),
            "Evacuate immediately when authorities tell you to; do not wait for confirmation from this app.",
            "CreekReady has no live fire, smoke, or road data.",
            "Evacúe inmediatamente cuando las autoridades se lo indiquen; no espere confirmación de esta aplicación.",
            "CreekReady no tiene datos en vivo sobre fuego, humo ni carreteras.",
        ),
    ),
    "heat": (
        (
            "heat.now.cool_hydrate",
            "now",
            True,
            ("NWS-HEAT",),
            "Move to air conditioning, drink water, and reduce strenuous activity.",
            "Cooling, hydration, and lower exertion reduce heat exposure.",
            "Vaya a un lugar con aire acondicionado, beba agua y reduzca la actividad intensa.",
            "El enfriamiento, la hidratación y menos esfuerzo reducen la exposición al calor.",
        ),
        (
            "heat.now.check_alert",
            "now",
            False,
            ("ALERT-TEXT",),
            "Check the complete official alert for its timing and instructions.",
            "Duration and severity must come from the issuing authority.",
            "Revise el aviso oficial completo para conocer sus horarios e instrucciones.",
            "La duración y la gravedad deben venir de la autoridad emisora.",
        ),
        (
            "heat.next.check_household",
            "next",
            True,
            ("NWS-HEAT", "READY-PLAN"),
            "Call or visit vulnerable household members and confirm access to cooling and water.",
            "Age, health, and air-conditioning access can change heat risk.",
            "Llame o visite a personas vulnerables del hogar y confirme que tengan refrigeración y agua.",
            "La edad, la salud y el acceso al aire acondicionado pueden cambiar el riesgo.",
        ),
        (
            "heat.worse.seek_help",
            "worse",
            True,
            ("NWS-HEAT",),
            "Seek emergency medical help for confusion, fainting, or other severe symptoms.",
            "Severe heat illness needs medical help, not an app response.",
            "Busque atención médica de emergencia ante confusión, desmayo u otros síntomas graves.",
            "Las enfermedades graves por calor necesitan ayuda médica, no una respuesta de la aplicación.",
        ),
    ),
    "other": (
        (
            "other.now.read_alert",
            "now",
            True,
            ("ALERT-TEXT",),
            "Read and follow the complete official alert; do not act on this summary alone.",
            "The hazard type could not be identified confidently.",
            "Lea y siga el aviso oficial completo; no actúe basándose solo en este resumen.",
            "El tipo de peligro no se identificó con suficiente confianza.",
        ),
        (
            "other.next.prepare_plan",
            "next",
            True,
            ("READY-PLAN",),
            "Prepare your household communication, shelter, or evacuation plan.",
            "Basic preparation is useful while you seek more official information.",
            "Prepare el plan de comunicación, refugio o evacuación de su hogar.",
            "La preparación básica es útil mientras busca más información oficial.",
        ),
        (
            "other.worse.use_official_source",
            "worse",
            True,
            ("ALERT-TEXT",),
            "Use the alert's official source or emergency services if there is an immediate threat.",
            "CreekReady cannot observe real-time conditions.",
            "Use la fuente oficial del aviso o los servicios de emergencia si existe una amenaza inmediata.",
            "CreekReady no puede observar condiciones en tiempo real.",
        ),
    ),
}


_HOUSEHOLD_ACTIONS: dict[str, tuple[str, str, str, str]] = {
    "children": (
        "Assign one adult to each child and keep their essentials together.",
        "Clear responsibility reduces last-minute decisions.",
        "Asigne a un adulto para cada niño y mantenga juntos sus artículos esenciales.",
        "Un responsable claro reduce las decisiones de último minuto.",
    ),
    "older_adult": (
        "Confirm medications, devices, and who will assist the older adult.",
        "Medical and mobility needs often require extra time.",
        "Revise medicamentos, dispositivos y quién ayudará al adulto mayor.",
        "Las necesidades médicas y de movilidad suelen requerir tiempo adicional.",
    ),
    "pet": (
        "Stage a leash or carrier, water, and medication for every pet.",
        "Pets need to be included in the household's shelter or evacuation plan.",
        "Prepare correa o transportadora, agua y medicamentos para cada mascota.",
        "Las mascotas deben formar parte del plan de refugio o evacuación del hogar.",
    ),
    "limited_mobility": (
        "Place mobility aids, medication, and support contacts by the exit.",
        "Sheltering or leaving can take longer with limited mobility.",
        "Coloque ayudas de movilidad, medicamentos y contactos de apoyo junto a la salida.",
        "Refugiarse o salir puede tomar más tiempo con movilidad limitada.",
    ),
    "no_vehicle": (
        "Arrange transportation with a trusted person or local resource early, while continuing to follow official instructions.",
        "Alternative transportation may take time to arrange.",
        "Coordine temprano el transporte con una persona de confianza o un recurso local mientras sigue las instrucciones oficiales.",
        "El transporte alternativo puede tardar en organizarse.",
    ),
}


def build_action_catalog(
    hazard_key: str, needs: list[str], language: str
) -> list[CatalogAction]:
    localized: list[CatalogAction] = []
    for (
        action_id,
        stage,
        required,
        source_ids,
        action_en,
        reason_en,
        action_es,
        reason_es,
    ) in _HAZARD_ACTIONS[hazard_key]:
        action, reason = (
            (action_es, reason_es)
            if language == "es"
            else (action_en, reason_en)
        )
        localized.append(
            CatalogAction(
                id=action_id,
                stage=stage,
                required=required,
                source_ids=source_ids,
                action=action,
                reason=reason,
            )
        )

    for need in needs:
        if need not in _HOUSEHOLD_ACTIONS:
            continue
        copy = _HOUSEHOLD_ACTIONS[need]
        action, reason = (copy[2], copy[3]) if language == "es" else (copy[0], copy[1])
        localized.append(
            CatalogAction(
                id=f"household.next.{need}",
                stage="next",
                action=action,
                reason=reason,
                source_ids=("READY-PLAN",),
                required=True,
            )
        )
    return localized


def _stage_copy(language: str) -> dict[StageKey, tuple[str, str]]:
    if language == "es":
        return {
            "now": ("Ahora", "En los próximos minutos"),
            "next": ("Después", "Prepárese sin perder de vista el aviso"),
            "worse": ("Si empeora", "Las órdenes oficiales tienen prioridad"),
        }
    return {
        "now": ("Now", "In the next few minutes"),
        "next": ("Next", "Prepare without losing the official signal"),
        "worse": ("If conditions worsen", "Official instructions take priority"),
    }


def validate_selections(
    selections: Iterable[SelectionLike], catalog: list[CatalogAction]
) -> None:
    selection_list = list(selections)
    if [stage.key for stage in selection_list] != list(STAGE_ORDER):
        raise ValueError("The model returned an invalid stage order.")

    approved = {item.id: item for item in catalog}
    seen: set[str] = set()
    for stage in selection_list:
        for action_id in stage.action_ids:
            if action_id not in approved:
                raise ValueError("The model returned an unapproved action ID.")
            if action_id in seen:
                raise ValueError("The model returned a duplicate action ID.")
            if approved[action_id].stage != stage.key:
                raise ValueError("The model returned an action ID in the wrong stage.")
            seen.add(action_id)

    required = {item.id for item in catalog if item.required}
    if not required.issubset(seen):
        raise ValueError("The model omitted a required action ID.")


def expand_selections(
    selections: Iterable[SelectionLike],
    catalog: list[CatalogAction],
    language: str,
) -> list[PlanStage]:
    selection_list = list(selections)
    validate_selections(selection_list, catalog)
    approved = {item.id: item for item in catalog}
    stage_copy = _stage_copy(language)
    return [
        PlanStage(
            key=selection.key,
            title=stage_copy[selection.key][0],
            subtitle=stage_copy[selection.key][1],
            items=[approved[action_id].as_action_item() for action_id in selection.action_ids],
        )
        for selection in selection_list
    ]


def deterministic_stages(
    catalog: list[CatalogAction], language: str
) -> list[PlanStage]:
    """Use every curated item in catalog order for the network-free fallback."""

    stage_copy = _stage_copy(language)
    return [
        PlanStage(
            key=stage,
            title=stage_copy[stage][0],
            subtitle=stage_copy[stage][1],
            items=[item.as_action_item() for item in catalog if item.stage == stage],
        )
        for stage in STAGE_ORDER
    ]
