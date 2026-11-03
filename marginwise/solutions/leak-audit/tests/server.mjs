// Tiny static server for the fixture sites. Maps extension-less paths to
// .html files (so /products/merino-tee serves products/merino-tee.html) and
// returns 404 for anything missing (e.g. /products.json, /llms.txt).

import http from 'node:http';
import { readFile } from 'node:fs/promises';
import path from 'node:path';

const TYPES = { '.html': 'text/html; charset=utf-8', '.txt': 'text/plain; charset=utf-8', '.json': 'application/json' };

export function startServer(root) {
  const server = http.createServer(async (req, res) => {
    const pathname = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    let rel = pathname === '/' ? 'index.html' : pathname.slice(1);
    if (!path.extname(rel)) rel += '.html';
    const file = path.join(root, path.normalize(rel));
    if (!file.startsWith(root)) { res.writeHead(403).end(); return; }
    try {
      const body = await readFile(file);
      res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' });
      res.end(body);
    } catch {
      res.writeHead(404, { 'content-type': 'text/plain' }).end('not found');
    }
  });
  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => {
      const { port } = server.address();
      resolve({ url: `http://127.0.0.1:${port}`, close: () => new Promise((r) => server.close(r)) });
    });
  });
}
