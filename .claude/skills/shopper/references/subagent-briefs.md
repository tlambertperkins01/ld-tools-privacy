# Sub-agent brief templates

Each sub-agent sees only its brief. Paste the **locked brief** from SKILL.md
step 0 into every prompt verbatim, then add the stage-specific block. Always ask
for a compact structured report with URLs and evidence labels.

## Shared header (prepend to every brief)

```
Today is <DATE>. <Upcoming sale event + date, if any.>
LOCKED BRIEF:
- Benchmark: <product> at <price> (<key specs; full piece list>), <URL>
- Similar means: <equivalence rule>
- Hard constraints: <e.g. must be < $X after discounts; credible third-party reviews only>
- Allowed: <mix-and-match same retailer / seconds / waiting for sale>
Credible review sources: Wirecutter, ATK/Cook's Illustrated, Consumer Reports, Serious Eats,
CNN Underscored, Good Housekeeping, Reviewed, Food & Wine, Food Network, The Spruce Eats,
Forbes Vetted (if tested), RTINGS (electronics). NOT brand blogs or affiliate-spam listicles.
Evidence labels: "seen live" (page loaded), "snippet" (search result only), "stale" (>2 weeks old).
Do not make purchases, create accounts, or sign up for emails. Mark anything unverified.
Tools: load WebSearch via ToolSearch "select:WebSearch"; use WebFetch or the web-fetch agent;
a browser tool may be available via ToolSearch "browser".
```

## Discovery + pricing agent (2–3 candidates each)

```
Your candidates: <A>, <B>, <C>.
First screen each in one line: credible third-party praise? Plausibly under the ceiling? Drop failures and say why.
For survivors:
1. Outlets and awards (short quote, URL, date); main criticism; any outlet that dropped or warns against it.
2. Exact contents/spec with model number; build; where made; warranty. Flag look-alike SKUs.
3. Current prices at big retailers AND small/specialty ones (see retailers list): price, stock,
   URL, evidence label.
4. Mix-and-match within one retailer to match the benchmark contents, with arithmetic.
5. Promo codes for the cheapest 1–2 retailers: code, discount, exclusions, expiry, source URL,
   label (✅ / ❔), and whether the retailer simply has no codes.
Return: a table per candidate, then notes.
```

## Sale-timing agent (all candidates)

```
Sets: <list>, plus the benchmark itself.
For each: (1) deals ANNOUNCED this year (price, retailer, dates, URL; "confirmed" only if seen on the retailer's page/ad
or a dated credible deals article); (2) HISTORICAL lows for this event in the last 2 years (exact SKU, date, URL;
watch for SKU drift and price errors); (3) likelihood it crosses <target> (high/med/low) and where;
(4) relevant price-adjustment policies.
Return: one compact table, then notes.
```

## Cart-verification agent (finalists only, run last)

```
Test promo codes by adding products to a cart and applying each code. Follow the cart-test protocol:
guest only, no accounts, no email signup, no payment details, never place an order, and remove each code
before testing the next.
Products/codes: <retailer, product URL, codes to test>.
Report a table: retailer · product · code · applied/rejected/excluded · subtotal before → after ·
exact message · timestamp. If a site blocks the browser, write "not tested" and check the official
terms page instead.
```
