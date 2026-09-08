from __future__ import annotations

from pipe4.domain.evidence.models import EvidenceRef


class CorroborationEngine:
    @staticmethod
    def independent_origin_count(evidence: list[EvidenceRef]) -> int:
        return len({item.origin_key for item in evidence})

    @staticmethod
    def duplicate_evidence_ids(evidence: list[EvidenceRef]) -> set[str]:
        seen: set[tuple[str, str]] = set()
        duplicates: set[str] = set()
        for item in evidence:
            signature = (item.origin_key, item.content_hash)
            if signature in seen:
                duplicates.add(item.evidence_id)
            seen.add(signature)
        return duplicates
