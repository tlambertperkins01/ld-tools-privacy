# Sub-agent brief templates

The manager writes these and sends them. It does not do the legwork itself.
Each heading gives the **model tier** to pass on the Agent tool. Launch independent
agents in parallel in one message. Each sub-agent sees only its brief. Paste the **locked brief** from SKILL.md
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
Every price you report MUST come with the direct product-page URL (exact SKU) where you saw it; if you have none,
write "no URL". Never construct URLs.
Do not make purchases, create accounts, or sign up for emails. Mark anything unverified.
EXCLUDE student, education/teacher, military/veteran, first-responder, nurse/healthcare and any ID.me/SheerID/
UNiDAYS/GovX-verified discounts. The user does not qualify. Only report one if it needs no verification at all.
Tools: load WebSearch via ToolSearch "select:WebSearch"; use WebFetch or the web-fetch agent;
a browser tool may be available via ToolSearch "browser".
```

## Review-sweep agent — `sonnet` (1 agent, runs first)

```
Category: <category>. Read the CURRENT roundups from the credible sources above directly (use a browser
if fetch is blocked; otherwise use snippets and label them). For each outlet, list EVERY pick (top/budget/upgrade/also-great),
the price shown, the review date, and a short quote. Also list picks the outlet DROPPED or WARNS AGAINST, and why.
Reject brand blogs and listicle spam. Return: one table (outlet · pick · award · date · price shown · quote · URL)
plus a "dropped/warned" list. Facts only. No recommendation.
```

## Pricing-sweep agent — `haiku` (parallel; 2–3 candidates or one retailer group each)

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
   label (✅ / ⚠️ / 🟡 / ⚪ / 👤 / ❌ per coupon-verification.md), and whether the retailer simply has no codes (then list levers: clip coupons, gift-card discounts, price match, rebates, cashback).
Return: a table per candidate, then notes.
```

## Sale-timing agent — `haiku` (`sonnet` if SKU drift needs judging; 1 agent)

```
Sets: <list>, plus the benchmark itself.
For each: (1) deals ANNOUNCED this year (price, retailer, dates, URL; "confirmed" only if seen on the retailer's page/ad
or a dated credible deals article); (2) HISTORICAL lows for this event in the last 2 years (exact SKU, date, URL;
watch for SKU drift and price errors); (3) likelihood it crosses <target> (high/med/low) and where;
(4) relevant price-adjustment policies.
Return: one compact table, then notes.
```

## Cart-verification agent — `sonnet` (finalists only, runs last)

```
Test promo codes by adding products to a cart and applying each code. Follow the cart-test protocol in
coupon-verification.md §3 (pasted below): guest only, no accounts, no email signup, no payment details, never place an order,
voucher field only, at most 20 attempts per store, at most 10 guesses (small stores only, never big retailers), stop at any CAPTCHA,
never touch private/staff codes, and remove each code before testing the next. Record the REAL discount (discount line ÷ subtotal);
accepted-but-$0 is ⚠️.
<paste §3 of coupon-verification.md here>
Products/codes: <retailer, product URL, codes to test>.
Report a table: retailer · product · code · applied/rejected/excluded · subtotal before → after ·
exact message · timestamp. If a site blocks the browser, write "not tested" and check the official
terms page instead.
```

## Review-rating agent: `haiku` collectors (2–3 finalists each), then a `sonnet` scorer

Collector brief:
```
Finalists (exact SKUs + model numbers): <list with product URLs>.
For each, collect (facts only, no scoring):
1. Retailer star average + review count + product URL + date read (Amazon, Walmart, Target, Costco, brand site,
   specialty stores). Flag listings that merge other variants' reviews.
2. Editorial verdicts and any retest/long-term update (outlet, date, URL).
3. Owner discussion: Reddit/forums/long-term reviews (2–4 links), with recurring themes.
4. Top 3 recurring praise + top 3 recurring complaints, with a rough frequency (e.g. "~15% of 1–2★ reviews mention warping").
5. Red flags: incentivized reviews, review spikes, very low counts.
Search-snippet values are OK if labelled "snippet". Never invent counts.
Return: one table per finalist + a themes list.
```

Scorer brief (`sonnet`, or the manager):
```
Apply the step-4b rubric in SKILL.md to these collector reports: count-weighted base (sources ≥50 reviews; smaller
ones at half weight), ±1.0 max adjustment in 0.25 steps with stated reasons, round to 0.5, confidence label,
and one line "Owners love: …; Owners complain: …". Show the arithmetic. If data is insufficient, say so.
```

## Spot-check (manager, or one `sonnet` verifier)

```
Re-open these specific URLs and confirm the live price, stock, and (if browser) the code result for the winning row(s) only:
<URLs + expected values>. Report any mismatch with the observed value and a timestamp.
```
