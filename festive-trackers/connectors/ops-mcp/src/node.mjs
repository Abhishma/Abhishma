// Local or self-hosted entry: `node src/node.mjs` with the same variables set in the environment.
import { createServer } from 'node:http';
import { createHandler } from './server.mjs';

const handle = createHandler();
const port = Number(process.env.PORT || 8787);

createServer(async (req, res) => {
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const request = new Request(`http://${req.headers.host}${req.url}`, {
    method: req.method, headers: req.headers, body: ['GET', 'HEAD'].includes(req.method) ? undefined : Buffer.concat(chunks),
  });
  const r = await handle(request, process.env);
  res.writeHead(r.status, Object.fromEntries(r.headers));
  res.end(Buffer.from(await r.arrayBuffer()));
}).listen(port, () => console.log(`ops-mcp listening on :${port} (path /mcp/<MCP_PATH_TOKEN>)`));
