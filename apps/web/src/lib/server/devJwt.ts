import crypto from 'node:crypto';
function b64url(input: string | Buffer): string { return Buffer.from(input).toString('base64url'); }
export function devBearer(secret: string): string {
  const now=Math.floor(Date.now()/1000);
  const header=b64url(JSON.stringify({alg:'HS256',typ:'JWT'}));
  const payload=b64url(JSON.stringify({sub:'web-demo',roles:['uwaci_internal','owner','verifier'],permissions:['*'],iat:now,exp:now+3600}));
  const sig=crypto.createHmac('sha256',secret).update(`${header}.${payload}`).digest('base64url');
  return `${header}.${payload}.${sig}`;
}
