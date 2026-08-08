from __future__ import annotations

from .models import SourceReference


SOURCES: dict[str, SourceReference] = {
    "ALERT-TEXT": SourceReference(
        id="ALERT-TEXT",
        title="Alert text supplied by the user",
        agency="Issuing authority shown in the alert",
        url="",
        excerpt="Facts such as place, timing, and official instructions must come directly from the pasted alert.",
    ),
    "NWS-FLOOD": SourceReference(
        id="NWS-FLOOD",
        title="Flood Safety",
        agency="NOAA National Weather Service",
        url="https://www.weather.gov/safety/flood",
        excerpt="Stay out of floodwater, never drive around barricades, and turn around when a road is flooded.",
    ),
    "READY-WILDFIRE": SourceReference(
        id="READY-WILDFIRE",
        title="Wildfires",
        agency="FEMA Ready.gov",
        url="https://www.ready.gov/wildfires",
        excerpt="Follow local alerts, know more than one evacuation route, include pets in the plan, and leave immediately when authorities instruct you to evacuate.",
    ),
    "NWS-HEAT": SourceReference(
        id="NWS-HEAT",
        title="Heat Safety",
        agency="NOAA National Weather Service",
        url="https://www.weather.gov/safety/heat",
        excerpt="Limit strenuous activity, drink water, use air conditioning when possible, and check on people who are more vulnerable to heat.",
    ),
    "READY-PLAN": SourceReference(
        id="READY-PLAN",
        title="Make a Plan",
        agency="FEMA Ready.gov",
        url="https://www.ready.gov/plan",
        excerpt="Plan how household members will receive alerts, communicate, shelter, evacuate, and meet individual needs.",
    ),
}


HAZARD_SOURCE_IDS = {
    "flood": ["ALERT-TEXT", "NWS-FLOOD", "READY-PLAN"],
    "wildfire": ["ALERT-TEXT", "READY-WILDFIRE", "READY-PLAN"],
    "heat": ["ALERT-TEXT", "NWS-HEAT", "READY-PLAN"],
    "other": ["ALERT-TEXT", "READY-PLAN"],
}


def sources_for(hazard_key: str) -> list[SourceReference]:
    return [SOURCES[source_id] for source_id in HAZARD_SOURCE_IDS[hazard_key]]
