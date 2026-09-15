# Victory Azundo — Service/API Composition & Host Adapters

## Production destination paths

```text
app/modules/current_state/api/
app/modules/current_state/services/
app/modules/current_state/adapters/
app/modules/current_state/ports/  # only coordinated interface changes
```

## Primary tasks

- build thin FastAPI routes matching `contracts/endpoint_manifest.json`;
- use `SuccessResponse`, `ResponseMeta`, `RequestID`, verified principal;
- implement witness text orchestration;
- integrate typed Core AI interpretation through `AIGateway`;
- implement Knowledge adapter using provenance-per-observation;
- implement Notification adapter/event handlers;
- coordinate audio transcription boundary without copying provider logic;
- keep provider/internal trust metadata out of mobile responses.

## TDD order

1. contract test for route shape and auth;
2. failing service test using port fakes;
3. service implementation;
4. adapter test against owner-module public service;
5. API test;
6. OpenAPI drift/shape test.

## Do not

- import Deepgram/Gemini SDKs into current_state;
- write Knowledge/Notification tables directly;
- put business policy in route functions;
- introduce infrastructure adapters that are not required by the host architecture.
