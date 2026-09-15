# Host adapters

Victory owns adapter composition with Samuel review.

Adapters should implement the module ports without moving owner-module business rules into Pipe 4.

Expected adapters:

- `KnowledgePort` -> Knowledge `TrustService` using provenance-per-observation.
- `WitnessInterpretationPort` -> Core AI typed `AIGateway`.
- `SpeechTranscriptionPort` -> approved Core AI transcription-only boundary (not direct provider duplication).
- `NotificationPort` -> Notification service / host domain event handling.
- `EntityDirectoryPort` -> Presence/Locator owner modules when contracts exist; until then keep provisional reality explicit.

Never import provider SDKs into `current_state.domain` or `current_state.services`.
