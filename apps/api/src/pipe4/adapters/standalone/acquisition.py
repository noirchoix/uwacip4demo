from __future__ import annotations

from datetime import datetime, timezone

from pipe4.domain.acquisition.models import DecisionContext
from pipe4.domain.observation.models import LocationEvidenceType
from pipe4.domain.state.enums import EpistemicStatus, StateType
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.state.values import BooleanStateValue, DurationStateValue
from pipe4.ports.acquisition import AcquiredObservation


class FixtureAcquisitionConnector:
    """Developer/acceptance fixture only. Never registered when dev fixtures are disabled."""
    async def acquire(self, *, identity: StateIdentity, decision_context: DecisionContext) -> AcquiredObservation:
        if identity.state_type in {StateType.AVAILABLE, StateType.ACCESSIBLE, StateType.WORKING}:
            value=BooleanStateValue(value=True)
        elif identity.state_type==StateType.TIME:
            value=DurationStateValue(seconds=900)
        else:
            from pipe4.domain.state.values import ChangeStateValue
            value=ChangeStateValue(changed=True,category='fixture_change',summary='Developer fixture change')
        return AcquiredObservation(source_id='fixture-source',value=value,observed_at_iso=datetime.now(timezone.utc).isoformat(),epistemic_status=EpistemicStatus.SYSTEM_REPORTED,origin_key='fixture:stable-origin',location_type=LocationEvidenceType.UNKNOWN)
