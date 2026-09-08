from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class _ValueBase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class BooleanStateValue(_ValueBase):
    kind: Literal["boolean"] = "boolean"
    value: bool


class QuantityStateValue(_ValueBase):
    kind: Literal["quantity"] = "quantity"
    available: float
    unit: str = Field(min_length=1, max_length=32)
    total_capacity: float | None = None

    @model_validator(mode="after")
    def validate_capacity(self) -> "QuantityStateValue":
        if self.available < 0:
            raise ValueError("available quantity cannot be negative")
        if self.total_capacity is not None:
            if self.total_capacity < 0:
                raise ValueError("total_capacity cannot be negative")
            if self.available > self.total_capacity:
                raise ValueError("available cannot exceed total_capacity")
        return self


class DurationStateValue(_ValueBase):
    kind: Literal["duration"] = "duration"
    seconds: int = Field(ge=0)
    label: str | None = Field(default=None, max_length=120)


class RangeStateValue(_ValueBase):
    kind: Literal["range"] = "range"
    minimum: float
    maximum: float
    unit: str = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def validate_order(self) -> "RangeStateValue":
        if self.minimum > self.maximum:
            raise ValueError("minimum cannot exceed maximum")
        return self


class ChangeStateValue(_ValueBase):
    kind: Literal["change"] = "change"
    changed: bool
    category: str | None = Field(default=None, max_length=80)
    summary: str | None = Field(default=None, max_length=500)
    previous_value_hash: str | None = Field(default=None, max_length=128)


class CategoricalStateValue(_ValueBase):
    kind: Literal["categorical"] = "categorical"
    value: str = Field(min_length=1, max_length=120)


StateValue = Annotated[
    BooleanStateValue
    | QuantityStateValue
    | DurationStateValue
    | RangeStateValue
    | ChangeStateValue
    | CategoricalStateValue,
    Field(discriminator="kind"),
]
