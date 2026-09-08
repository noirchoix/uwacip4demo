# Pipe 4 mobile integration

Target baseline: `origin/dev` commit `4c8951880cc50bfe2ccdb4b14e1b63acf1b0f375`.

## Apply

```bash
git checkout dev
git pull --ff-only
git apply --check uwaci-pipe4-uwaci-mobile-integration-v1.0.patch
git apply uwaci-pipe4-uwaci-mobile-integration-v1.0.patch
npx expo install expo-location
npm run validate
```

The patch updates `package.json` with the Expo SDK 57 compatible `expo-location` range. The release does **not** fabricate a `package-lock.json` entry without npm registry metadata; `npx expo install expo-location` is the intended dependency reconciliation step and will update the lock file.

## Architecture

- Pipe 4 behavior lives under `src/features/pipe4`.
- Existing `baseApi` remains the only RTK Query API root.
- Auth remains centralized in `prepareHeaders`.
- Device location is a reusable platform capability under `src/core/location`; Pipe 4 owns only the reporting fallback semantics.
- The client never calculates confidence, verification, credits, authority, or canonical state.
- Natural witness reporting is inference-first: text/voice and location first, then minimal entity clarification.
- `None of these` creates a provisional reality rather than overwriting an existing entity.
- A report receipt keeps “You reported” distinct from “Uwaci status”.
- Targeted acquisition acceptance routes back into the normal witness-report flow.

## Native dependency

`expo-location` is required for foreground device location. If location is denied/unavailable, reporting remains available with a written location description.
