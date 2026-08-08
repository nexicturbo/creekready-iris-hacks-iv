from __future__ import annotations

from datetime import datetime
import json

import pytest

from creekready.fallback import detect_hazard, extract_facts


ALERTS = {
    "flood": (
        "FLASH FLOOD WARNING for Cedar Creek, Texas until 8:00 PM. "
        "Avoid flooded roads, stay away from creeks, and follow local instructions."
    ),
    "wildfire": (
        "WILDFIRE EVACUATION WARNING affecting Cedar Creek through Saturday evening. "
        "Residents should prepare to evacuate and monitor instructions from local officials."
    ),
    "heat": (
        "EXCESSIVE HEAT WARNING for Bastrop County until 9:00 PM Sunday. "
        "Drink water, stay in air conditioning, and reduce strenuous outdoor activity."
    ),
}


SPANISH_ALERTS = {
    "flood": (
        "AVISO DE MUESTRA — NO ES UNA ALERTA ACTIVA\n"
        "El Servicio Meteorológico Nacional emitió una advertencia de inundación "
        "repentina para la zona ficticia de Pine Creek, incluidas Example Road y "
        "Demo Crossing, hasta las 9:30 p. m. La lluvia intensa puede inundar cruces "
        "bajos. No rodee barricadas ni entre en caminos inundados. Vaya a un lugar "
        "más alto si las autoridades locales se lo indican."
    ),
    "wildfire": (
        "AVISO DE MUESTRA — NO ES UNA ALERTA ACTIVA\n"
        "Gestión de Emergencias del condado ficticio de Cedar emitió una advertencia "
        "de evacuación para Juniper Ridge desde las 3:00 p. m. y hasta nuevo aviso por "
        "un incendio forestal cercano. Los residentes deben prepararse para salir, "
        "reunir medicamentos y mascotas, y usar Canyon Road si se emite una orden. "
        "Evite Ridge Road y monitoree los avisos del condado."
    ),
    "heat": (
        "AVISO DE MUESTRA — NO ES UNA ALERTA ACTIVA\n"
        "El Servicio Meteorológico Nacional emitió una advertencia de calor excesivo "
        "para la zona ficticia de Clear Valley desde el mediodía del lunes hasta las "
        "8:00 p. m. del martes. Beba agua, reduzca la actividad intensa al aire libre, "
        "use aire acondicionado cuando sea posible y revise a las personas vulnerables "
        "al calor."
    ),
}


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (ALERTS["flood"], "flood"),
        (ALERTS["wildfire"], "wildfire"),
        (ALERTS["heat"], "heat"),
        ("A civil notice contains no recognized weather or fire hazard phrase.", "other"),
    ],
)
def test_detect_hazard(text, expected):
    assert detect_hazard(text) == expected


@pytest.mark.parametrize("hazard_key", ["flood", "wildfire", "heat"])
def test_spanish_browser_samples_classify_into_their_real_hazard(hazard_key):
    assert detect_hazard(SPANISH_ALERTS[hazard_key]) == hazard_key


@pytest.mark.parametrize(
    ("hazard_key", "expected_location", "expected_time", "instruction_fragments"),
    [
        (
            "flood",
            "la zona ficticia de Pine Creek, incluidas Example Road y Demo Crossing",
            "hasta las 9:30 p. m.",
            ("No rodee barricadas", "Vaya a un lugar más alto"),
        ),
        (
            "wildfire",
            "Juniper Ridge",
            "desde las 3:00 p. m. y hasta nuevo aviso",
            ("deben prepararse para salir", "Evite Ridge Road"),
        ),
        (
            "heat",
            "la zona ficticia de Clear Valley",
            "desde el mediodía del lunes hasta las 8:00 p. m. del martes",
            ("Beba agua", "revise a las personas vulnerables"),
        ),
    ],
)
def test_spanish_browser_samples_extract_only_stated_facts_and_instructions(
    hazard_key, expected_location, expected_time, instruction_fragments
):
    facts = extract_facts(SPANISH_ALERTS[hazard_key], hazard_key, "es")

    assert facts.location == expected_location
    assert facts.time_window == expected_time
    assert facts.confidence == "high"
    joined_instructions = " ".join(facts.official_instructions)
    assert all(fragment in joined_instructions for fragment in instruction_fragments)


@pytest.mark.parametrize(
    ("hazard_key", "expected_source", "expected_action_fragment"),
    [
        ("flood", "NWS-FLOOD", "agua de inundación"),
        ("wildfire", "READY-WILDFIRE", "prepárese para salir"),
        ("heat", "NWS-HEAT", "aire acondicionado"),
    ],
)
def test_spanish_browser_samples_return_localized_hazard_actions(
    client, hazard_key, expected_source, expected_action_fragment
):
    response = client.post(
        "/api/plan",
        json={
            "alert_text": SPANISH_ALERTS[hazard_key],
            "language": "es",
            "use_ai": False,
        },
    )

    assert response.status_code == 200
    plan = response.get_json()
    assert expected_source in {source["id"] for source in plan["sources"]}
    actions = " ".join(
        item["action"] for stage in plan["stages"] for item in stage["items"]
    )
    assert expected_action_fragment in actions


def test_spanish_missing_fact_labels_are_localized_without_inference():
    facts = extract_facts(
        "AVISO OFICIAL: Monitoree a la autoridad emisora para obtener cambios.",
        "other",
        "es",
    )

    assert facts.location == "No se indica claramente en el aviso"
    assert facts.time_window == "No se indica claramente en el aviso"


def test_spanish_generic_evacuation_does_not_imply_wildfire():
    alert = (
        "ADVERTENCIA DE EVACUACIÓN para el distrito industrial por una fuga química. "
        "Siga las instrucciones de la autoridad emisora."
    )

    assert detect_hazard(alert) == "other"


def test_spanish_updates_from_authorities_are_not_a_time_window():
    alert = (
        "AVISO OFICIAL: Refúgiese bajo techo y monitoree actualizaciones desde las "
        "autoridades locales."
    )

    facts = extract_facts(alert, "other", "es")

    assert facts.time_window == "No se indica claramente en el aviso"
    assert "autoridades" not in facts.time_window


@pytest.mark.parametrize(
    ("hazard_key", "hazard_label", "hazard_source", "expected_phrase"),
    [
        ("flood", "Flood or flash flood", "NWS-FLOOD", "floodwater"),
        ("wildfire", "Wildfire", "READY-WILDFIRE", "leave immediately"),
        ("heat", "Extreme heat", "NWS-HEAT", "air conditioning"),
    ],
)
def test_each_fallback_hazard_has_three_grounded_action_stages(
    client, hazard_key, hazard_label, hazard_source, expected_phrase
):
    response = client.post(
        "/api/plan",
        json={"alert_text": ALERTS[hazard_key], "language": "en"},
    )

    assert response.status_code == 200
    plan = response.get_json()
    assert plan["mode"] == "guided_fallback"
    assert plan["facts"]["hazard"] == hazard_label
    assert plan["facts"]["confidence"] == "high"
    assert [stage["key"] for stage in plan["stages"]] == ["now", "next", "worse"]
    assert all(stage["items"] for stage in plan["stages"])
    assert hazard_source in {source["id"] for source in plan["sources"]}
    all_actions = " ".join(
        item["action"] for stage in plan["stages"] for item in stage["items"]
    ).lower()
    assert expected_phrase in all_actions

    parsed_time = datetime.fromisoformat(plan["generated_at"])
    assert parsed_time.tzinfo is not None
    assert parsed_time.utcoffset().total_seconds() == 0


@pytest.mark.parametrize("hazard_key", ["flood", "wildfire", "heat"])
def test_fallback_action_source_ids_always_exist_in_returned_sources(client, hazard_key):
    response = client.post(
        "/api/plan",
        json={
            "alert_text": ALERTS[hazard_key],
            "household_needs": ["children", "no_vehicle"],
            "language": "en",
        },
    )

    assert response.status_code == 200
    plan = response.get_json()
    returned_source_ids = {source["id"] for source in plan["sources"]}
    cited_source_ids = {
        source_id
        for stage in plan["stages"]
        for item in stage["items"]
        for source_id in item["source_ids"]
    }
    assert cited_source_ids
    assert cited_source_ids <= returned_source_ids


def test_spanish_fallback_is_unicode_clean_and_uses_spanish_copy(client):
    response = client.post(
        "/api/plan",
        json={
            "alert_text": ALERTS["flood"],
            "household_needs": ["children"],
            "language": "es",
        },
    )

    assert response.status_code == 200
    plan = response.get_json()
    assert plan["mode"] == "guided_fallback"
    assert plan["stages"][0]["title"] == "Ahora"
    assert plan["stages"][1]["title"] == "Después"
    assert "No predice emergencias" in plan["disclaimer"]
    rendered = json.dumps(plan, ensure_ascii=False)
    assert "niño" in rendered
    assert "inundación" in rendered
    assert "Ã" not in rendered
    assert "Â" not in rendered


def test_unknown_hazard_is_low_confidence_and_conservative(client):
    alert = (
        "OFFICIAL COMMUNITY NOTICE: Residents should monitor the issuing authority "
        "and follow all instructions printed in this notice today."
    )
    response = client.post("/api/plan", json={"alert_text": alert, "language": "en"})

    assert response.status_code == 200
    plan = response.get_json()
    assert plan["facts"]["hazard"] == "Unclassified official alert"
    assert plan["facts"]["confidence"] == "low"
    assert plan["facts"]["location"] == "Not clearly stated in the alert"
    assert {source["id"] for source in plan["sources"]} == {
        "ALERT-TEXT",
        "READY-PLAN",
    }
    assert "do not act on this summary alone" in plan["stages"][0]["items"][0][
        "action"
    ].lower()


def test_known_hazard_with_missing_facts_is_not_high_confidence():
    alert = (
        "FLASH FLOOD WARNING for Cedar Creek, Texas. "
        "Monitor the complete notice from the issuing authority."
    )

    facts = extract_facts(alert, "flood", "en")

    assert facts.location == "Cedar Creek, Texas"
    assert facts.time_window == "Not clearly stated in the alert"
    assert facts.confidence == "medium"


@pytest.mark.parametrize(
    "alert",
    [
        (
            "HAZARDOUS MATERIALS RELEASE affecting the industrial district. "
            "An evacuation order is active; follow the issuing agency's instructions."
        ),
        (
            "CIVIL EMERGENCY MESSAGE for the county. An evacuation warning is active "
            "for some residents; monitor the official notice for updates."
        ),
    ],
)
def test_generic_evacuation_language_does_not_imply_wildfire(alert):
    assert detect_hazard(alert) == "other"


def test_expired_hazard_does_not_override_current_hazard():
    alert = (
        "The FLASH FLOOD WARNING has expired for Cedar Creek. "
        "An EXCESSIVE HEAT WARNING is now in effect for Bastrop County until 8 PM. "
        "Drink water and stay in air conditioning."
    )

    assert detect_hazard(alert) == "heat"


def test_mixed_active_hazards_are_unclassified_and_low_confidence(client):
    alert = (
        "A FLASH FLOOD WARNING and EXCESSIVE HEAT WARNING are in effect for "
        "Bastrop County until 8 PM. Follow the complete notices from officials."
    )

    response = client.post(
        "/api/plan",
        json={"alert_text": alert, "language": "en", "use_ai": False},
    )

    assert response.status_code == 200
    plan = response.get_json()
    assert plan["facts"]["hazard"] == "Unclassified official alert"
    assert plan["facts"]["confidence"] == "low"
    assert {source["id"] for source in plan["sources"]} == {
        "ALERT-TEXT",
        "READY-PLAN",
    }


@pytest.mark.parametrize(
    "alert",
    [
        "La advertencia de inundación ha expirado para Pine Creek.",
        "The wildfire warning is no longer in effect for Juniper Ridge.",
    ],
)
def test_inactive_notice_alone_is_not_treated_as_active_hazard(alert):
    assert detect_hazard(alert) == "other"


def test_updates_from_local_officials_is_never_extracted_as_a_time():
    alert = (
        "OFFICIAL HAZARDOUS MATERIALS NOTICE affecting Cedar Creek. Residents should "
        "shelter indoors and monitor updates from local officials for more information."
    )

    facts = extract_facts(alert, "other", "en")

    assert facts.time_window == "Not clearly stated in the alert"
    assert "local officials" not in facts.time_window.lower()


@pytest.mark.parametrize(
    ("phrase", "expected"),
    [
        ("until 8:00 PM", "until 8:00 PM"),
        ("through Saturday evening", "through Saturday evening"),
        ("effective immediately", "effective immediately"),
    ],
)
def test_real_time_phrases_remain_extractable(phrase, expected):
    alert = f"OFFICIAL FLOOD WARNING for Cedar Creek {phrase}. Avoid flooded roads."
    facts = extract_facts(alert, "flood", "en")
    assert facts.time_window == expected


def test_time_window_stops_before_causal_clause():
    alert = (
        "WILDFIRE WARNING for Juniper Ridge from 3:00 PM until further notice "
        "because of a nearby wildfire. Residents should prepare to leave."
    )

    facts = extract_facts(alert, "wildfire", "en")

    assert facts.time_window == "from 3:00 PM until further notice"


def test_evacuate_instruction_is_kept_but_evacuation_notice_is_not():
    alert = (
        "WILDFIRE EVACUATION WARNING for Juniper Ridge until 8:00 PM. "
        "Evacuate immediately if local authorities issue an order."
    )

    facts = extract_facts(alert, "wildfire", "en")

    assert facts.official_instructions == [
        "Evacuate immediately if local authorities issue an order."
    ]


def test_all_five_household_needs_survive_fallback_without_truncation(client):
    needs = ["children", "older_adult", "pet", "limited_mobility", "no_vehicle"]

    response = client.post(
        "/api/plan",
        json={
            "alert_text": ALERTS["flood"],
            "household_needs": needs,
            "language": "en",
            "use_ai": False,
        },
    )

    assert response.status_code == 200
    plan = response.get_json()
    household_ids = {
        item["id"]
        for stage in plan["stages"]
        for item in stage["items"]
        if item["id"].startswith("household.next.")
    }
    assert household_ids == {f"household.next.{need}" for need in needs}
    assert all(
        item["source_ids"] == ["READY-PLAN"]
        for stage in plan["stages"]
        for item in stage["items"]
        if item["id"] in household_ids
    )
