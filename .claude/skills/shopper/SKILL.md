---
name: shopper
description: >-
  Deep comparison-shopping research: finds the genuinely best buy for a product
  (or a shopping list, or "beat this listing"), restricted to options that
  credible third-party testers recommend, priced across big AND small
  retailers, with mix-and-match bundles, sale-event timing (Black Friday,
  Prime Day, announced + historical lows), and promo codes that are tested in a
  real cart where possible. Use whenever the user wants to buy something, asks
  "what's the best X under $Y", pastes a product link and wants something
  better/cheaper, asks for promo/coupon codes, asks whether a deal or seller is
  legit, or wants to know if they should wait for a sale. Invoke as /shopper
  <product, link, or list> [constraints]. Not for building e-commerce code,
  stock prices, or order tracking.
argument-hint: "<product | benchmark URL | shopping list> [budget, must-haves, region]"
---

# shopper

A rigorous buying-research pipeline. It combines two things:

- the **shop-scout** discipline (MIT, © Omar Alwahiby — see
  `scripts/LICENSE-shop-scout`): effective-price ranking, deterministic seller
  shortlists, strict coupon classification, seller-trust verdicts with sources,
  and a hard "no invented data" output gate;
- a **benchmark-and-review layer** proven on real research: define what
  "similar" means, admit only products credible testers recommend, sweep big +
  specialty retailers, compute mix-and-match bundles, research sale timing, and
  verify promo codes in a cart.

The user's goal is a decision they can act on today, with honest confidence
labels. Clarity over completeness: a short true answer beats a long padded one.

`$SKILL_DIR` = the folder containing this file. Reference bundled files through it.

---

## 0. Parse the request and lock the brief (do this before any search)

Extract and write down, in one short block:

| Field | Example |
|---|---|
| **Mode** | `benchmark` (beat a given listing) · `best-in-category` · `list` (several items) |
| **Benchmark** (if any) | product, price, URL, and its *spec sheet* (fetch it) |
| **Equivalence rule** | what makes a substitute "similar": quantity/piece count, size, key spec (e.g. 5-ply vs tri-ply), materials, warranty |
| **Hard constraints** | must be cheaper than $X · credible reviews only · region · new only? |
| **Allowed tactics** | mix-and-match within one retailer? factory seconds/open-box? wait for a sale? card-gated offers? |
| **Deliverable** | at least one promo code per finalist (if user asked) · table · artifact |

If the benchmark page hides specs (JS-rendered), get them via search snippets,
the same product on another region's site, or a browser render. **Never compare
against a benchmark you haven't spec'd** — the piece list decides "similar."

Ask the user only if a hard constraint is genuinely ambiguous and changes the
answer (e.g. "is tri-ply acceptable or must it be 5-ply?"). Otherwise choose
the sensible default, state it, and flag the trade-off in the output.

---

## 1. Candidate discovery — reviews gate entry

Only products recommended by **credible third-party testers** enter the
candidate pool. Sources and red flags: `references/review-sources.md`.

1. Read the category's top editorial roundups directly (Wirecutter, ATK,
   Consumer Reports, RTINGS, etc. per category). List **every** pick they make
   (top, budget, upgrade, "also great") with the price they show.
2. Also note **former picks that were dropped and why** (e.g. "skillets warped
   in testing") — this is high-value signal that blogs never surface.
3. Reject: brand-owned blogs, affiliate-spam sites with no stated methodology,
   Amazon-review-only products, AI-generated "best of" pages.
4. Screen each candidate in one line: *credible praise? plausibly under the
   price ceiling?* Drop failures with a one-line reason — the user wants to know
   what was ruled out and why.
5. Record per survivor: outlet + award + short quote + URL, and the main
   criticism.

---

## 2. Price sweep — big and small retailers

For each survivor, fetch prices across the retailer list in
`references/retailers.md` (big-box, department, kitchen/specialty, brand
direct, warehouse clubs, outlets/factory seconds). Rules (from shop-scout):

- **Same SKU check.** Brands sell look-alike variants (different model number,
  glass vs steel lids, a "Costco exclusive" piece mix, an "Everyday" line).
  Confirm model numbers. Flag mismatches; never silently merge them.
- **Effective price = price − applicable coupon + shipping + sourced tax/fees.**
  Unsourced shipping is `n/a`, never assumed free.
- **Deterministic shortlist.** Fixed retailer order (pinned → first-party/brand
  → others alphabetical), cap at `SHOP_MAX_LISTINGS` (default 6) per product,
  rows never re-sorted by price. The winner is named in the recommendation line.
- **Stock matters.** Out-of-stock can't be the best buy ("cheaper if restocked").
- **Mix-and-match.** If allowed, compute the cheapest way to reach the
  benchmark's piece set *within one retailer* (smaller set + open-stock pieces,
  or two sets). Show the arithmetic.
- **Real discount check.** Compare to price history (camelcamelcamel/Keepa,
  Slickdeals threads). A "was" price nobody charges is cosmetic.

Mark every price with its evidence level:
`seen live` (you loaded the page) · `snippet` (search result only — say so) ·
`stale` (dated older than ~2 weeks).

---

## 3. Sale-event timing

If a major sale is within ~6 weeks (Black Friday/Cyber Monday, Prime Day,
Memorial/Labor Day, brand anniversary sales), or the user asks: follow
`references/deal-timing.md`.

- **Announced:** published ad scans, brand sale pages with dates, early deals
  already live. "Confirmed" only if seen on the retailer's page/ad or a dated,
  credible deals article.
- **Historical:** prior-year lows for the *exact* SKU (Slickdeals, price
  trackers). Watch for SKU drift — a past "$249 10-piece" may have been a
  different line or a price error.
- **Verdict per candidate:** likelihood it crosses the target price (high /
  medium / low) and where. Also check whether the *benchmark itself* goes on
  sale — that moves the goalpost.
- Note price-adjustment / price-match policies (many retailers refund the
  difference within 14–30 days; many suspend this during holiday events).

---

## 4. Promo codes — find, classify, test

Sources and the cart-test protocol: `references/coupon-verification.md`.

1. **Gap math first.** For each candidate, compute the discount needed to reach
   the target: `needed % = 1 − target / price`. If no realistic code reaches it
   (typical codes are 10–25%), say so up front instead of hunting forever.
2. **Find** codes in this order: product page/site banner → retailer's official
   offers/terms page → email/SMS/app first-order offers → card-linked/portal
   cashback → aggregators (RetailMeNot, Slickdeals, Knoji, DealSpotr, Wethrift,
   Honey) → social/influencer codes.
3. **Classify** (shop-scout rule, unchanged):
   - ✅ **applicable** — every condition verified (not expired, min spend met,
     brand/category not excluded, eligibility true). Only these change
     effective price.
   - ❔ **unknown** — any condition unverifiable. Show as FYI, never fold in.
   - ❌ **not applicable** — known to fail. Omit (or list under "ruled out" if
     the user asked about it).
4. **Test in a cart when a browser tool is available** (browser-use, Claude in
   Chrome, built-in browser): add the item, apply the code, record subtotal
   before/after and the exact message. Never check out, never enter payment
   details, never create accounts or sign up for emails without the user's say-so.
   A code that applied in a cart is labelled `cart-verified <timestamp>`.
5. **Never stack** unless the retailer's T&Cs say so (link them).
6. If the user requires "at least one code per option": return the best code
   you have for each, with its honest label. If a retailer genuinely has no
   codes (Costco, most Amazon listings use clip coupons, MAP-priced brands),
   say that explicitly and give the nearest equivalent (clip coupon, card offer,
   cashback portal, first-order signup %), rather than padding with a dead code.

---

## 5. Seller trust (shop-scout rule)

Each row gets ✅ Trusted / ⚠️ Mixed / ❌ Risky + one-line reason + **source
link**. For marketplaces judge the actual third-party seller holding the buy
box. Unknown small retailers: check BBB/Trustpilot/Reddit and how long the
domain has existed. No source → "insufficient data", never a guess.

---

## 6. Execution: fan out, then verify

This research is wide. Use parallel sub-agents when the runtime has them:

- **Discovery/pricing agents:** group 2–3 candidates per agent (by brand).
  Templates in `references/subagent-briefs.md`. Each brief carries the locked
  brief from step 0 verbatim, the credible-source list, and the evidence-label
  rules, and asks for a compact structured report with URLs.
- **Timing agent:** one agent for sale events across all candidates.
- **Verification agent (last):** cart-tests codes for finalists only.
- Synthesize yourself. Treat agent reports as claims: cross-check any number
  that decides the winner (e.g. re-open the winning listing yourself).
- Without sub-agents, run the same stages sequentially.

Backends for reading pages, best first (announce which you used):
1. A real browser tool (renders JS, can test carts).
2. Firecrawl — self-host `FIRECRAWL_API_URL` or cloud `FIRECRAWL_API_KEY`, via
   `$SKILL_DIR/scripts/firecrawl.sh search|scrape` (needs only curl; sends
   `maxAge:0` so prices aren't cached). Never write a key to a file.
3. Built-in search + fetch. Many retailers (Amazon, Walmart, Target, Macy's,
   Williams Sonoma, Kohl's) block this; fall back to search snippets and label
   them `snippet`.

Respect site terms; don't hammer sites; don't bypass logins or paywalls.

---

## 7. Output

Lead with the answer. Structure:

1. **Bottom line** (2–4 lines): the recommended buy, its effective price vs the
   benchmark, and the single biggest trade-off (e.g. "tri-ply, not 5-ply").
2. **Benchmark** spec line.
3. **Comparison table**, one row per finalist (fixed columns, fixed order):

   | Product | Reviewed by (award) | Pieces / key spec | Retailer | Price | Effective price | Evidence | Promo code (label) | Trust | Buy link |

4. **Mix-and-match** builds, with arithmetic.
5. **Sale timing**: announced deals + historical lows + wait-or-buy call.
6. **Codes table**: code · savings · conditions · source · label
   (`cart-verified` / ✅ / ❔) · "verify at checkout".
7. **Ruled out**: one line each (price, reviews, or spec).
8. **Gaps**: sites that blocked you and what that leaves unverified.

**Data-floor gate:** if half or more of a product's rows have no real price,
don't print a table for it — give an honest summary (what it is, where sold,
prices actually read with sources).

**Pre-output checklist** — every row has a sourced price, a trust verdict with
a link, and a direct product link; no invented prices, codes, shipping, or
history; best buy is in stock; all rows are the same SKU class; only
✅/cart-verified codes touch effective price; nothing stacked without T&Cs.

Be direct about trade-offs. If the honest answer is "the benchmark is already
the best value for what you asked" or "wait 12 days," say that.

For long results, offer (or, if the user will share it, publish) an HTML
artifact version of the report.

---

## Configuration (env vars, all optional)

| Var | Default | Meaning |
|---|---|---|
| `SHOP_REGION` | `US` | Country for retailer list, currency, and Firecrawl `location.country` |
| `SHOP_STORES` | — | Comma list of pinned retailers, searched first |
| `SHOP_MAX_LISTINGS` | `6` | Max retailers priced per product |
| `SHOP_PARALLEL` | `4` | Max concurrent sub-agents |
| `SHOP_BACKEND` | `auto` | `auto` · `browser` · `firecrawl` · `builtin` |
| `FIRECRAWL_API_URL` / `FIRECRAWL_API_KEY` | — | Firecrawl self-host / cloud |

## Reference files

- `references/review-sources.md`: credible testers by category, plus red flags
- `references/retailers.md`: US big + small/specialty retailers by category, outlets, seconds
- `references/coupon-verification.md`: where codes hide, the cart-test protocol, label definitions
- `references/deal-timing.md`: sale calendar, historical-price sources, SKU-drift traps
- `references/subagent-briefs.md`: copy-ready prompts for each fan-out stage
- `scripts/firecrawl.sh`: Firecrawl search/scrape wrapper (from shop-scout, MIT)
