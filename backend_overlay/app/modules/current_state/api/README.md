# API workstream

Victory + Jacob should implement the HTTP boundary here after the Pydantic contract is frozen.

Rules:

- router prefix is `/pipe4`; root app already adds `/api/v1`;
- every route uses the existing `SuccessResponse` / error envelope;
- use `RequestID` and `get_current_principal`;
- routes authorize + validate + call services + return DTOs only;
- no SQL or cross-module workflow in router functions;
- endpoint paths must match `contracts/endpoint_manifest.json`;
- keep raw provider names/internal trust details out of mobile DTOs;
- include OpenAPI summary, description, responses and stable `operation_id`.

Do not register this router in `app/api/v1/router.py` until focused contract tests are green.
