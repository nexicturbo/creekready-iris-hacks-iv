from __future__ import annotations

import pytest

from creekready.catalog import STAGE_ORDER, build_action_catalog
from creekready.sources import sources_for


ALL_NEEDS = ["children", "older_adult", "pet", "limited_mobility", "no_vehicle"]


@pytest.mark.parametrize("hazard", ["flood", "wildfire", "heat", "other"])
def test_catalog_ids_are_unique_grounded_and_language_stable(hazard):
    english = build_action_catalog(hazard, ALL_NEEDS, "en")
    spanish = build_action_catalog(hazard, ALL_NEEDS, "es")
    english_ids = [item.id for item in english]
    approved_sources = {source.id for source in sources_for(hazard)}

    assert english_ids == [item.id for item in spanish]
    assert len(english_ids) == len(set(english_ids))
    assert all(set(item.source_ids) <= approved_sources for item in english)
    assert {item.stage for item in english} == set(STAGE_ORDER)
    assert {f"household.next.{need}" for need in ALL_NEEDS} <= set(english_ids)


def test_household_actions_are_required_and_never_truncated():
    catalog = build_action_catalog("flood", ALL_NEEDS, "en")
    household = [item for item in catalog if item.id.startswith("household.next.")]

    assert len(household) == len(ALL_NEEDS)
    assert all(item.required for item in household)
    assert all(item.stage == "next" for item in household)
    assert all(item.source_ids == ("READY-PLAN",) for item in household)
