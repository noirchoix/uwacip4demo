import {describe,expect,it} from 'vitest';
import {stateValueSchema} from '$lib/schemas/pipe4';
describe('state value runtime boundary',()=>{it('rejects malformed values',()=>{expect(stateValueSchema.safeParse({kind:'boolean',value:'yes'}).success).toBe(false)});it('accepts quantity state',()=>{expect(stateValueSchema.parse({kind:'quantity',available:2,total_capacity:10,unit:'unit'}).available).toBe(2)})});
