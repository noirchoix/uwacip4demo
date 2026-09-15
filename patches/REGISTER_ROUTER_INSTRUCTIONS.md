# Router registration — do this only after contract tests pass

In `app/api/v1/router.py`:

```python
from app.modules.current_state.api.router import router as current_state_router
...
api_router.include_router(current_state_router)
```

The module router itself should use `prefix="/pipe4"` because `app.main` already mounts the root router at `/api/v1`.

Do not apply this registration while the API package is still an incomplete scaffold.
