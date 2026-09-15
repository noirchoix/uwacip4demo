# Mobile Contract Freeze — Pipe 4

The current mobile client calls the following `/api/v1/pipe4` routes:

| Method | Path | Mobile consumer |
|---|---|---|
| GET | `/pipe4/current` | current-state query |
| GET | `/pipe4/nearby` | nearby reality feed |
| GET | `/pipe4/watches` | Following |
| POST | `/pipe4/watches` | create WATCH |
| POST | `/pipe4/watches/{id}/pause` | pause WATCH |
| POST | `/pipe4/watches/{id}/resume` | resume WATCH |
| DELETE | `/pipe4/watches/{id}` | remove WATCH |
| GET | `/pipe4/access-requests` | access list |
| POST | `/pipe4/access-requests` | request protected read scope |
| POST | `/pipe4/witness/interpret` | natural-language interpretation |
| POST | `/pipe4/witness/reports` | witness report |
| POST | `/pipe4/witness/audio-reports` | native/web audio upload |
| POST | `/pipe4/entities/resolve` | candidate resolution |
| POST | `/pipe4/entities/provisional` | `None of these` / provisional reality |
| GET | `/pipe4/acquisition-requests` | nearby confirmation requests |
| POST | `/pipe4/acquisition-requests/{id}/accept` | opt in |
| POST | `/pipe4/acquisition-requests/{id}/decline` | decline |

All JSON endpoints use the existing UWACI envelope:

```json
{
  "success": true,
  "data": {},
  "meta": {"request_id": "...", "timestamp": "..."}
}
```

## Contract corrections required by backend truth

These are backward-compatible or narrowly-scoped mobile fixes and are supplied in `patches/mobile-contract-backend-truth.patch`:

1. `Pipe4StateVersion.confidence` becomes nullable. Knowledge confidence is optional and Pipe 4 must not fabricate one.
2. `Pipe4StateVersion.expires_at` becomes nullable. Not every legitimate current state has an expiry at creation time.
3. witness `entity_id` becomes optional at the contract boundary so natural reporting can precede entity resolution; the current UI can still send it when known.
4. `targeted_request_id` is accepted by text and audio witness reporting so targeted acquisition can reuse the ordinary witness path.
5. the audio-upload helper permits an omitted `entity_id` at the transport boundary; the current UI may still require entity selection until its inference-first flow is deliberately revised.
6. public `Pipe4StateVersion` drops unused internal `source_ids`, `evidence_ids`, and `observation_ids`; evidence remains linked internally and is exposed through privacy-safe provenance presentation instead.
7. WATCH delete should return the response shape the current mobile mutation already expects, unless mobile is changed in the same coordinated PR.
8. WATCH operators are narrowed to `eq|ne|lt|lte|gt|gte|changed_to` and targets to JSON-safe scalars; arbitrary `string`/`unknown` contracts are not retained.
9. access requests use `READ` plus typed `Pipe4AccessScope`; responses may include an `approved_scope` that is narrower than the requested scope.

## Contract rule

Backend implementation must not silently change mobile-visible shapes. Any deliberate change requires:

- Pydantic schema change;
- OpenAPI change;
- contract test;
- mobile TypeScript contract update;
- migration/compatibility note if persistence is affected.
