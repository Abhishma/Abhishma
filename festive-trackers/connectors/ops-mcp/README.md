# r4r-ops: custom connector for Unicommerce and ClickPost

A small read-only MCP server that exposes R for Rabbit's Unicommerce and ClickPost data to claude.ai as one custom connector. Pages, routines and chats can then read warehouse stock, orders and delivery status the same way they read Shopify.

No dependencies. Runs on Cloudflare Workers (recommended) or any Node 20+ host.

## Tools

All tools are read-only. None of them can create, change or cancel anything upstream.

| Tool | Returns | Feeds |
|---|---|---|
| `unicommerce_inventory_snapshot` | Stock per SKU in a facility: inventory, open sale, open purchase, putaway pending, blocked | Stock and sales-loss views, with warehouse stock instead of Shopify's |
| `unicommerce_search_sale_orders` | Order headers for an IST date window, paged | Order volume and status mix |
| `unicommerce_get_sale_order` | One order with items and shipping packages (AWB, courier) | Drill-down, the join to ClickPost |
| `clickpost_track` | Latest status for up to 50 AWBs, each in a bucket: pre_transit, in_transit, out_for_delivery, delivered, ndr, rto, cancelled, exception, lost, damaged, other, not_found | Delivery view |
| `order_delivery_status` | For up to 20 orders: each package with AWB, courier and its ClickPost status | Delivery drill-down |

Linkrunner is not included. The original trackers used a connector named `Linkrunner` with a `run_funnel` tool, which most likely came from Linkrunner itself. Ask Linkrunner for their MCP server URL and add it as its own custom connector. If they have none, send their data API docs and it can be added here as one more tool.

## Configuration

| Name | Kind | Value |
|---|---|---|
| `MCP_PATH_TOKEN` | secret | Random string, at least 32 characters. Part of the connector URL. |
| `UNICOMMERCE_TENANT` | secret | The subdomain in `https://<tenant>.unicommerce.com` |
| `UNICOMMERCE_USERNAME`, `UNICOMMERCE_PASSWORD` | secret | An API user with read-only roles |
| `CLICKPOST_USERNAME`, `CLICKPOST_KEY` | secret | ClickPost API credentials |
| `UNICOMMERCE_FACILITY` | var | Default facility code for stock |
| `CLICKPOST_CP_IDS` | var | JSON map from courier name as Unicommerce reports it to ClickPost courier id, for example `{"Delhivery": 4}` |

## Deploy on Cloudflare Workers

```
cd connectors/ops-mcp
npx wrangler login
npx wrangler secret put MCP_PATH_TOKEN        # paste: node -e "console.log(require('crypto').randomBytes(24).toString('hex'))"
npx wrangler secret put UNICOMMERCE_TENANT
npx wrangler secret put UNICOMMERCE_USERNAME
npx wrangler secret put UNICOMMERCE_PASSWORD
npx wrangler secret put CLICKPOST_USERNAME
npx wrangler secret put CLICKPOST_KEY
# set UNICOMMERCE_FACILITY and CLICKPOST_CP_IDS in wrangler.toml
npx wrangler deploy
```

The connector URL is `https://r4r-ops-mcp.<your-subdomain>.workers.dev/mcp/<MCP_PATH_TOKEN>`.

To run it elsewhere: set the same variables and run `node src/node.mjs` (port 8787, or `PORT`), behind HTTPS.

## Add to claude.ai

1. Open https://claude.ai/customize/connectors, then add a custom connector. On a Team or Enterprise plan an owner adds it for the organisation.
2. Name it `R4R Ops` and paste the connector URL. Leave the OAuth fields empty.
3. Start a new session, since connectors load when a session starts. Ask Claude to call `unicommerce_inventory_snapshot` for two or three SKUs, and `clickpost_track` for one recent AWB.

## Security

- **The URL is the password.** Anyone with the full URL can read what these tools return. Share it only with the people who add the connector. If it leaks, rotate it with `wrangler secret put MCP_PATH_TOKEN` and update the connector. For per-person sign-in, the next step is OAuth in front of the Worker, for example Cloudflare Access.
- **Use a dedicated API user with read-only roles** in Unicommerce, and the narrowest ClickPost key available.
- **Error messages never include credentials** or upstream URLs.

## Check on the first live call

These details come from the vendors' docs as far as they could be confirmed. The `VERIFY` comments in `src/` mark the rest:

- Unicommerce: the `client_id` value for the token call, the `Facility` header, `searchOptions` field names, the `saleorder/get` path and response shape, and the SKU batch size (500 now)
- ClickPost: whether several waybills go in one request comma separated, and how results are keyed; status codes above 13 are bucketed from their description

If a call fails or a field comes back empty, compare one raw response with the client code. Each check is a one-line fix.

## Tests

`node --test test/*.test.mjs`. These run against mocked Unicommerce and ClickPost responses and cover the protocol, path-token check, batching, IST date bounds, token refresh and redaction of credentials from errors.
