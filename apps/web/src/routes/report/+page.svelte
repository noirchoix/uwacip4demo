<script lang="ts">
 import { page } from '$app/state';
 import { witnessInterpretationSchema } from '$lib/schemas/pipe4';
 import type { EntityCandidate, WitnessInterpretation, WitnessReceipt } from '$lib/types/pipe4';

 let text = $state('');
 let locationDescription = $state('');
 let latitude = $state<number | null>(null);
 let longitude = $state<number | null>(null);
 let locating = $state(false);
 let interpretation = $state<WitnessInterpretation | null>(null);
 let selectedEntity = $state<string | null>(null);
 let provisionalName = $state('');
 let result = $state<WitnessReceipt | null>(null);
 let error = $state<string | null>(null);
 let busy = $state(false);
 const targetedRequestId = $derived(page.url.searchParams.get('targeted_request_id'));

 async function locate() {
  locating = true;
  error = null;
  try {
   if (!navigator.geolocation) throw new Error('Browser location is unavailable.');
   const position = await new Promise<GeolocationPosition>((resolve, reject) =>
    navigator.geolocation.getCurrentPosition(resolve, reject, {
     enableHighAccuracy: false,
     timeout: 8000
    })
   );
   latitude = position.coords.latitude;
   longitude = position.coords.longitude;
  } catch (caught) {
   error = caught instanceof Error ? caught.message : 'Location unavailable';
  } finally {
   locating = false;
  }
 }

 async function interpret() {
  if (!text.trim()) return;
  busy = true;
  error = null;
  result = null;
  try {
   const response = await fetch('/api/v1/pipe4/witness/interpret', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
     text: text.trim(),
     ...(latitude != null && longitude != null ? { latitude, longitude } : {})
    })
   });
   const payload = await response.json();
   if (!response.ok || !payload.success) throw new Error(payload.error?.message ?? 'Interpretation failed');
   interpretation = witnessInterpretationSchema.parse(payload.data);
   selectedEntity = interpretation.selected_entity_id ?? null;
  } catch (caught) {
   error = caught instanceof Error ? caught.message : 'Unable to interpret report';
  } finally {
   busy = false;
  }
 }

 function choose(candidate: EntityCandidate) {
  selectedEntity = candidate.entity_id;
 }

 async function provisional() {
  if (!provisionalName.trim()) return;
  busy = true;
  error = null;
  try {
   const response = await fetch('/api/v1/pipe4/entities/provisional', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
     entity_type: 'reported_reality',
     display_name: provisionalName.trim(),
     ...(latitude != null && longitude != null ? { latitude, longitude } : {})
    })
   });
   const payload = await response.json();
   if (!response.ok || !payload.success) throw new Error(payload.error?.message ?? 'Unable to create provisional reality');
   selectedEntity = payload.data.entity_id;
  } catch (caught) {
   error = caught instanceof Error ? caught.message : 'Unable to create provisional reality';
  } finally {
   busy = false;
  }
 }

 async function submit() {
  busy = true;
  error = null;
  result = null;
  try {
   const body = {
    text: text.trim(),
    observed_at: new Date().toISOString(),
    ...(selectedEntity ? { entity_id: selectedEntity } : {}),
    ...(interpretation?.state_type ? { state_type: interpretation.state_type } : {}),
    ...(interpretation?.value ? { value: interpretation.value } : {}),
    ...(latitude != null && longitude != null ? { latitude, longitude } : {}),
    ...(locationDescription.trim() ? { location_description: locationDescription.trim() } : {}),
    ...(targetedRequestId ? { targeted_request_id: targetedRequestId } : {})
   };
   const response = await fetch('/api/v1/pipe4/witness/reports', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
   });
   const payload = await response.json();
   if (!response.ok || !payload.success) throw new Error(payload.error?.message ?? 'Report failed');
   result = payload.data as WitnessReceipt;
  } catch (caught) {
   error = caught instanceof Error ? caught.message : 'Unable to send report';
  } finally {
   busy = false;
  }
 }
</script>

<div class="page">
 <header class="page-head">
  <div>
   <h1>Report current reality</h1>
   <p>Describe what happened first. Uwaci infers the likely state and asks only for the smallest missing clarification.</p>
  </div>
 </header>

 {#if targetedRequestId}<p class="notice">You accepted a nearby confirmation request. This report uses the same normal evidence workflow.</p>{/if}
 {#if error}<p class="error">{error}</p>{/if}

 <div class="grid">
  <section class="surface">
   <label>What is happening now?<textarea bind:value={text} oninput={() => { interpretation = null; selectedEntity = null; }} placeholder="The ATM beside the station isn't working."></textarea></label>
   <div class="button-row"><button disabled={busy || !text.trim()} onclick={interpret}>Continue</button></div>

   {#if interpretation}
    <div class="clarification">
     <p class="eyebrow">Uwaci understood</p>
     {#if interpretation.state_type && interpretation.value}<p><strong>{interpretation.state_type}</strong> · structured current-state proposal</p>{/if}
     {#if interpretation.clarification_question}<p>{interpretation.clarification_question}</p>{/if}
     {#if interpretation.entity_candidates.length && !selectedEntity}
      <div class="candidate-list">
       {#each interpretation.entity_candidates as candidate}
        <button class="candidate" onclick={() => choose(candidate)}><strong>{candidate.display_name}</strong><span>{candidate.entity_type}{candidate.distance_m != null ? ` · ${Math.round(candidate.distance_m)} m away` : ''}</span></button>
       {/each}
      </div>
     {/if}
     {#if !selectedEntity}
      <label style="margin-top:14px">None of these? Name the place or object<input bind:value={provisionalName} placeholder="ATM beside the main gate" /></label>
      <div class="button-row"><button class="secondary" disabled={busy || !provisionalName.trim()} onclick={provisional}>Use provisional reality</button></div>
     {/if}
     {#if selectedEntity}<p class="notice">Place/object identified. Your report remains evidence; it is not automatically canonical state.</p>{/if}
     <div class="button-row"><button disabled={busy || !text.trim()} onclick={submit}>Submit report</button></div>
    </div>
   {/if}
  </section>

  <aside class="surface" style="position:static;height:auto">
   <h2 style="margin-top:0">Location evidence</h2>
   <p class="muted">Location helps when physical presence matters but is not mandatory for a legitimate report.</p>
   <button class="secondary" disabled={locating} onclick={locate}>{locating ? 'Checking…' : 'Use browser location'}</button>
   {#if latitude != null && longitude != null}
    <p class="notice">Location captured.</p>
   {:else}
    <label style="margin-top:14px">Or describe the location<input bind:value={locationDescription} placeholder="Beside the main station gate" /></label>
   {/if}
  </aside>
 </div>

 {#if result}
  <article class="surface" style="margin-top:20px">
   <p class="eyebrow">You reported</p>
   <h2>{result.you_reported}</h2>
   <p class="eyebrow">Uwaci status</p>
   <p class="notice">{result.uwaci_status}{result.observation ? ' · Observation accepted as evidence; verification continues.' : ' · More clarification is required.'}</p>
  </article>
 {/if}
</div>
