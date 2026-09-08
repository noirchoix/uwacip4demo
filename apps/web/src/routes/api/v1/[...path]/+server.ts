import { env } from '$env/dynamic/private';
import { error, type RequestHandler } from '@sveltejs/kit';
import { devBearer } from '$lib/server/devJwt';

const forward: RequestHandler = async ({ request, params, url, fetch }) => {
  const origin=env.PIPE4_API_ORIGIN ?? 'http://localhost:8000';
  const path=params.path ?? '';
  const target=new URL(`/api/v1/${path}`,origin); target.search=url.search;
  const headers=new Headers(request.headers); headers.delete('host'); headers.set('accept','application/json');
  if (!headers.has('authorization') && env.PIPE4_WEB_DEV_MODE==='true' && env.PIPE4_JWT_HS256_SECRET) headers.set('authorization',`Bearer ${devBearer(env.PIPE4_JWT_HS256_SECRET)}`);
  if (path.startsWith('internal/') && env.PIPE4_INTERNAL_API_TOKEN) headers.set('x-internal-token',env.PIPE4_INTERNAL_API_TOKEN);
  const body=['GET','HEAD'].includes(request.method)?undefined:await request.arrayBuffer();
  const upstream=await fetch(target,{method:request.method,headers,body,redirect:'manual'});
  return new Response(upstream.body,{status:upstream.status,headers:upstream.headers});
};
export const GET=forward;export const POST=forward;export const DELETE=forward;export const PATCH=forward;export const PUT=forward;
