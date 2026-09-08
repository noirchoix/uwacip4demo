from __future__ import annotations

from pipe4.domain.state.enums import StateType

from .config import PolicyBundle, StateTypePolicy


class PolicyRegistry:
    def __init__(self, bundle: PolicyBundle) -> None:
        self.bundle = bundle

    def state_type(self, state_type: StateType | str) -> StateTypePolicy:
        canonical = state_type if isinstance(state_type, StateType) else StateType(state_type)
        return self.bundle.state_types[canonical]

    def decision_context(self, name: str):
        try:
            return self.bundle.decision_contexts[name]
        except KeyError as exc:
            raise ValueError(f"unsupported decision context: {name}") from exc
