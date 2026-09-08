from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pipe4.domain.observation.models import ObservationRecord
from pipe4.domain.state.models import StateVersion


@dataclass(frozen=True)
class ContradictionAssessment:
    material: bool
    reason: str


class ContradictionEngine:
    def assess(
        self,
        *,
        incumbent: StateVersion,
        observation: ObservationRecord,
        equivalence_seconds: int,
    ) -> ContradictionAssessment:
        if incumbent.identity.key != observation.identity.key:
            return ContradictionAssessment(False, "different state identity")
        delta = abs((incumbent.observed_at - observation.observed_at).total_seconds())
        if delta > equivalence_seconds:
            return ContradictionAssessment(False, "reports are not temporally equivalent")
        if incumbent.value.model_dump(mode="json") == observation.proposed_value.model_dump(mode="json"):
            return ContradictionAssessment(False, "values agree")
        return ContradictionAssessment(True, "temporally equivalent values conflict")
