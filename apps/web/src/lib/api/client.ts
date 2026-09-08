import { z } from 'zod';
import type { ApiFailure, ApiResponse } from '$lib/types/pipe4';
export class Pipe4ApiError extends Error { constructor(public code:string,message:string,public requestId?:string){super(message)} }
export async function api<T>(fetcher: typeof fetch,path:string,init?:RequestInit,schema?:z.ZodType<T>):Promise<T>{
  const response=await fetcher(`/api/v1${path}`,{...init,headers:{Accept:'application/json',...(init?.body?{'Content-Type':'application/json'}:{}),...(init?.headers??{})}});
  const raw:unknown=await response.json();
  if (!raw || typeof raw!=='object') throw new Pipe4ApiError('INVALID_RESPONSE','Uwaci returned an invalid response.');
  const envelope=raw as ApiResponse<unknown>|ApiFailure;
  if (!response.ok || envelope.success===false){const failure=envelope as ApiFailure;throw new Pipe4ApiError(failure.error?.code??'REQUEST_FAILED',failure.error?.message??'Request failed.',failure.meta?.request_id)}
  const data=(envelope as ApiResponse<unknown>).data;
  return schema?schema.parse(data):(data as T);
}
