import pytest
from pydantic import TypeAdapter, ValidationError

from app.modules.current_state.domain.values import QuantityStateValue, RangeStateValue, StateValue


def test_quantity_cannot_exceed_capacity() -> None:
    with pytest.raises(ValidationError):
        QuantityStateValue(available=11, total_capacity=10, unit="litre")


def test_range_must_be_ordered() -> None:
    with pytest.raises(ValidationError):
        RangeStateValue(minimum=9, maximum=3, unit="minutes")


def test_discriminated_value_round_trip() -> None:
    adapter = TypeAdapter(StateValue)
    value = adapter.validate_python({"kind": "boolean", "value": True})
    assert adapter.dump_python(value) == {"kind": "boolean", "value": True}
