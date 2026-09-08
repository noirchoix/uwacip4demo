from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from pipe4.domain.acquisition.models import DecisionContext, GapReason, StateRequest
from pipe4.domain.observation.models import ObservationRecord
from pipe4.domain.principal import Principal
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.state.values import StateValue
from pipe4.repositories.protocols import StateRepository
from pipe4.exceptions import NotFound

from .observations import ObservationService
from .resolution import ResolutionService


class DisputeReceipt(BaseModel):
    model_config = ConfigDict(extra='forbid')
    identity_key: str
    current_state_version_id: str
    observation: ObservationRecord | None = None
    state_request: StateRequest | None = None
    status: str


class DisputeService:
    """Open a dispute without treating the dispute itself as established truth."""

    def __init__(
        self,
        *,
        states: StateRepository,
        observations: ObservationService,
        resolution: ResolutionService,
    ) -> None:
        self.states = states
        self.observations = observations
        self.resolution = resolution

    async def open(
        self,
        principal: Principal,
        *,
        identity: StateIdentity,
        reason: str,
        proposed_value: StateValue | None = None,
        observed_at=None,
        latitude: float | None = None,
        longitude: float | None = None,
        location_accuracy_m: float | None = None,
        location_description: str | None = None,
    ) -> DisputeReceipt:
        current = await self.states.current(identity.key)
        if not current:
            raise NotFound('there is no current state to dispute')
        if proposed_value is not None:
            if observed_at is None:
                raise ValueError('observed_at is required when a competing value is supplied')
            observation = await self.observations.submit(
                principal,
                identity=identity,
                value=proposed_value,
                observed_at=observed_at,
                latitude=latitude,
                longitude=longitude,
                location_accuracy_m=location_accuracy_m,
                location_description=location_description,
                original_input_ref=reason,
            )
            return DisputeReceipt(
                identity_key=identity.key,
                current_state_version_id=current.state_version_id,
                observation=observation,
                status='VERIFYING',
            )
        request = await self.resolution.request(
            principal,
            identity=identity,
            decision_context=DecisionContext(name='operational_coordination'),
            reason=GapReason.DISPUTED,
        )
        return DisputeReceipt(
            identity_key=identity.key,
            current_state_version_id=current.state_version_id,
            state_request=request,
            status='VERIFYING',
        )
