"""Builds the Australia problem/solution ad creatives as HTML for rendering at 4:5 and 9:16."""
ADS = [
 ("surcharge", "Card fees",
  "The surcharge is gone.<br>The card fee isn't.",
  "Since 1 October, Australian stores can't surcharge Visa, Mastercard or eftpos. Removing the line is easy. The fee now comes out of your margin.",
  "We find leftover surcharge text in your theme and apps, then show margin by product so you know what to reprice.",
  "Source: Reserve Bank of Australia, media release 2026-10"),
 ("shipping", "Shipping",
  "Sendle has closed.<br>Is your shipping still set up right?",
  "If your store relied on Sendle, check your rates, delivery promises and shipping options at checkout.",
  "We set up multi-carrier rates and show a delivery date on product and checkout pages.",
  "Source: The New Daily, 12 Jan 2026"),
 ("checkout", "Checkout",
  "7 in 10 carts<br>never become orders.",
  "The top fixable reasons: surprise costs, forced account creation, and too many steps.",
  "We fix your checkout: costs shown early, guest checkout, Afterpay and express pay where shoppers look for them.",
  "Source: Baymard Institute, average of 50 studies (70.22%)"),
 ("speed", "Site speed",
  "0.1 seconds faster.<br>8.4% more retail conversions.",
  "That was the average across 37 brands in a Deloitte study for Google. Every extra app and heavy image adds load time to each page.",
  "We remove what slows your store on a phone and measure the result.",
  "Source: Deloitte Digital and Google, Milliseconds Make Millions, 2020"),
 ("sync", "Xero and MYOB",
  "Still fixing Shopify orders in Xero by hand?",
  "Failed syncs, missing SKUs and payouts that don't match the bank feed. Someone sorts them out every morning.",
  "We connect Shopify to Xero, MYOB or Cin7, and an AI agent fixes the safe errors and flags the rest for a person.",
  ""),
 ("aisearch", "AI search",
  "Ask ChatGPT for the best brand in your category.",
  "Is your store in the answer? Some shoppers now ask an AI assistant what to buy before they search Google.",
  "We make your product pages easy for Google and AI assistants to read, trust and quote.",
  ""),
]
CSS = """*{box-sizing:border-box;margin:0;padding:0}
.s{background:#1F2A44;color:#fff;font-family:Inter,sans-serif;position:relative;overflow:hidden;display:flex;flex-direction:column}
.f{width:1080px;height:1350px;padding:110px 88px 0}
.v{width:1080px;height:1920px;padding:270px 88px 0}
.top{display:flex;gap:16px;align-items:center;margin-bottom:48px}
.tag{background:#2E9E7E;color:#fff;font-weight:700;font-size:28px;letter-spacing:.08em;text-transform:uppercase;padding:10px 22px;border-radius:999px}
.tag2{color:#9AA6BD;font-weight:600;font-size:28px;letter-spacing:.08em;text-transform:uppercase}
h1{font-family:"Inter Display",Inter;font-weight:800;letter-spacing:-.02em;line-height:1.04;font-size:80px}
.v h1{font-size:88px}
.p{font-size:38px;line-height:1.4;color:#D9DEE8;margin-top:40px}
.fix{margin-top:44px;border-left:8px solid #2E9E7E;padding:6px 0 6px 32px}
.fix b{display:block;color:#2E9E7E;font-size:30px;letter-spacing:.1em;text-transform:uppercase;margin-bottom:12px}
.fix span{font-size:40px;line-height:1.35;font-weight:600}
.src{font-size:24px;color:#8E98AD;margin-top:auto;padding-bottom:28px}
.cta{background:#fff;color:#1F2A44;display:flex;justify-content:space-between;align-items:center;padding:34px 88px;margin:0 -88px}
.v .cta{margin-bottom:300px}
.cta b{font-size:40px;font-weight:800}
.cta span{font-size:30px;font-weight:600;color:#2E9E7E}
"""
def card(key, cls, tag, h, p, fix, src):
    return f'''<div class="s {cls}" id="{key}-{cls}"><div class="top"><span class="tag">AU stores</span><span class="tag2">{tag}</span></div>
<h1>{h}</h1><p class="p">{p}</p><div class="fix"><b>The fix</b><span>{fix}</span></div>
<p class="src">{src}</p><div class="cta"><b>Free 2-minute store teardown</b><span>marginwise.in</span></div></div>'''
html = "<!doctype html><html><head><meta charset='utf-8'><style>"+CSS+"</style></head><body>"
for a in ADS:
    for cls in ("f","v"):
        html += card(a[0], cls, *a[1:])
open("creatives.html","w").write(html+"</body></html>")
print(" ".join(f"{a[0]}-f {a[0]}-v" for a in ADS))
