from uuid import UUID

from app.modules.current_state.domain.enums import StateType
from app.modules.current_state.domain.identity import StateIdentity

ENTITY = UUID("11111111-1111-4111-8111-111111111111")


def test_state_identity_is_stable_across_qualifier_order() -> None:
    left = StateIdentity(
        entity_id=ENTITY,
        object_key="fuel",
        state_type=StateType.AVAILABLE,
        qualifiers={"grade": "AGO", "pump": 2},
    )
    right = StateIdentity(
        entity_id=ENTITY,
        object_key="fuel",
        state_type=StateType.AVAILABLE,
        qualifiers={"pump": 2, "grade": "AGO"},
    )

    assert left.key == right.key


def test_different_truth_qualifier_changes_identity() -> None:
    base = StateIdentity(
        entity_id=ENTITY,
        object_key="fuel",
        state_type=StateType.AVAILABLE,
        qualifiers={"grade": "AGO"},
    )
    different = base.model_copy(update={"qualifiers": {"grade": "PMS"}})

    assert base.key != different.key
