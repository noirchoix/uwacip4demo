export type StateType='AVAILABLE'|'ACCESSIBLE'|'WORKING'|'TIME'|'CHANGED';
export type StateStatus='CURRENT'|'VERIFYING'|'DISPUTED'|'STALE'|'INFERRED'|'UNKNOWN';
export type PresentationKind='STATE'|'PROTECTED'|'UNKNOWN';
export type StateValue=
 | {kind:'boolean';value:boolean}
 | {kind:'quantity';available:number;unit:string;total_capacity?:number|null}
 | {kind:'duration';seconds:number;label?:string|null}
 | {kind:'range';minimum:number;maximum:number;unit:string}
 | {kind:'change';changed:boolean;category?:string|null;summary?:string|null;previous_value_hash?:string|null}
 | {kind:'categorical';value:string};
export interface StateIdentity{entity_id:string;object_key:string;state_type:StateType;location_key?:string|null;qualifiers?:Record<string,string|number|boolean>}
export interface CurrentStatePresentation{kind:PresentationKind;status:StateStatus;entity:{entity_id:string;display_name?:string|null;entity_type?:string|null;distance_m?:number|null};identity?:StateIdentity|null;state_type?:StateType|null;value?:StateValue|null;observed_at?:string|null;expires_at?:string|null;freshness_seconds?:number|null;confidence?:number|null;epistemic_status?:string|null;verification_status?:string|null;state_version_id?:string|null;access_request_status?:string|null;actions:string[];message?:string|null;provenance?:{source_count:number;evidence_count:number;independent_origin_count:number;public_source_labels:string[]}|null}
export interface ApiResponse<T>{success:true;data:T;meta:{request_id:string;timestamp?:string}}
export interface ApiFailure{success:false;error:{code:string;message:string;details?:unknown};meta:{request_id:string;timestamp?:string}}
export interface NearbyResult{score:number;distance_m:number;current:CurrentStatePresentation}
export interface WatchCondition{identity:StateIdentity;operator:'EQ'|'NEQ'|'GT'|'GTE'|'LT'|'LTE';target:StateValue;decision_context?:{name?:string;urgency?:number;uncertainty_consequence?:number;requested_quantity?:number|null;unit?:string|null};permission_scope_key?:string}
export interface WatchView{watch_id:string;watch_process_id:string;subscriber_subject:string;status:'ACTIVE'|'ALERTING'|'PAUSED';condition:WatchCondition;created_at:string;updated_at:string;last_triggered_at?:string|null}
export interface AccessRequest{access_request_id:string;requester_subject:string;target_entity_id:string;target_identity_key?:string|null;requested_permission:string;requested_scope:Record<string,string|number|boolean>;status:'PENDING'|'APPROVED'|'DENIED'|'REVOKED'|'EXPIRED'|'CANCELLED';requested_at:string;decided_at?:string|null;decision_reason?:string|null;expires_at?:string|null}
export interface EntityCandidate{entity_id:string;display_name:string;entity_type:string;distance_m?:number|null;confidence:number}
export interface WitnessInterpretation{state_type?:StateType|null;value?:StateValue|null;interpretation_confidence:number;entity_candidates:EntityCandidate[];selected_entity_id?:string|null;requires_clarification:boolean;clarification_question?:string|null;used_ai:boolean}
export interface WitnessReceipt{interpretation?:WitnessInterpretation|null;observation?:{observation_id:string}|null;you_reported:string;uwaci_status:string}
export interface TargetedAcquisitionView{targeted_request_id:string;state_request_id:string;target_subject:string;status:'OFFERED'|'ACCEPTED'|'DECLINED'|'EXPIRED'|'COMPLETED';offered_at:string;expires_at:string;accepted_at?:string|null;completed_observation_id?:string|null;reward_label?:string|null;identity?:StateIdentity|null;what_to_confirm?:string|null}
