// Cloudflare Workers entry. Secrets come from `wrangler secret put` (see README).
import { createHandler } from './server.mjs';

const handle = createHandler();
export default { fetch: (request, env) => handle(request, env) };
