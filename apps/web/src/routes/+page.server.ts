import type { PageServerLoad } from './$types';
import { api } from '$lib/api/client';
import { currentStateSchema } from '$lib/schemas/pipe4';
export const load:PageServerLoad=async({fetch,url})=>{const entity=url.searchParams.get('entity')??'entity-1';const stateType=url.searchParams.get('state_type')??'AVAILABLE';try{return{current:await api(fetch,`/pipe4/current?entity_id=${encodeURIComponent(entity)}&state_type=${encodeURIComponent(stateType)}`,undefined,currentStateSchema),entity,stateType}}catch(error){return{current:null,entity,stateType,error:error instanceof Error?error.message:'Unable to load current state'}}};
