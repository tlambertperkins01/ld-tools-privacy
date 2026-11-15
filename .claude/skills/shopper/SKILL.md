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

A rigorous buying-research pipeline. It combines three things:

- the **shop-scout** discipline (MIT, © Omar Alwahiby — see
  `scripts/LICENSE-shop-scout`): effective-price ranking, deterministic seller
  shortlists, strict coupon classification, seller-trust verdicts with sources,
  and a hard "no invented data" output gate;
- the **promo-code-hunter** method (MIT, © mariaboger — see
  `scripts/LICENSE-promo-code-hunter`): evidence-ranked codes, creator/
  influencer code search, safe checkout testing with hard attempt limits, and
  no-code levers for big retailers;
- a **benchmark-and-review layer** proven on real research: define what
  "similar" means, admit only products credible testers recommend, sweep big +
  specialty retailers, compute mix-and-match bundles, research sale timing, and
  verify promo codes in a cart.

The user's goal is a decision they can act on today, with honest confidence
labels. Clarity over completeness: a short true answer beats a long padded one.

`$SKILL_DIR` = the folder containing this file. Reference bundled files through it.

---

## Operating rule: the manager delegates and compiles

The agent that receives `/shopper` is the **manager**. It runs on the
expensive model, so its tokens go to judgment, not legwork.

**The manager does:** lock the brief (step 0), write sub-agent briefs, decide
who survives each stage, cross-check the few numbers that decide the winner,
and write the final report.

**The manager does not:** run broad searches, sweep retailer pages, trawl
coupon sites, or drive carts. Each of those goes to a cheaper sub-agent.
Its own searching budget is **about 5 direct tool calls per run**, reserved for:
fetching the benchmark spec, spot-checking the winning price/code, and filling
one gap no agent covered. If it is about to do a 6th search itself, it
delegates instead.

**Model tiers** (pass `model` on the Agent tool; fall back to the default if a
tier isn't available):

| Work | Tier | Why |
|---|---|---|
| Web searches, page fetches, price/stock extraction, aggregator code lists, historical-price lookups, retailer sweeps | `haiku` | Repetitive, high-volume, low-judgment |
| Review screening (credible vs spam), SKU look-alike checks, sale-timing synthesis | `sonnet` | Needs judgment, but is bounded |
| Cart testing with a browser (voucher field, safety limits) | `sonnet` | Multi-step UI work with safety rules |
| Brief, survivor decisions, final verification, the report | manager (session model) | The decision itself |

**Making cheap agents reliable:**
- The brief is everything: the locked brief verbatim, explicit candidate list,
  exact fields to return, evidence labels, and a return format (a table
  schema). Narrow scope per agent: 1–3 products, or one retailer group.
- Ask for raw facts with URLs, not recommendations. The manager recommends.
- Run independent agents **in parallel in one message**, up to `SHOP_PARALLEL`.
- Treat every report as a claim. Before the final answer the manager
  re-verifies (itself, or with one `sonnet` verifier) the **winning row's**
  price, stock, and code, and any number that flips the ranking.
- If a haiku agent returns thin or contradictory results, re-brief it once
  with a narrower scope, or escalate that slice to `sonnet`. Don't redo
  it yourself.
- Keep the user updated briefly as stages land. Don't relay raw agent dumps.

Without sub-agents, run the stages sequentially yourself, using the same briefs as checklists.

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

### 0b. Intake question pass (mandatory, once per search)

Every search gets **one** round of questions about what matters, asked early,
so stars, rankings and the recommendation match how the user will actually
use the product.

1. **Use context first.** Before asking, gather what's already known: the
   request itself, the benchmark's specs, earlier answers in this conversation,
   saved preferences and memory, and the **standing profile** below. Don't ask
   anything that context already answers. Say in one line what you inferred
   ("assuming induction isn't a factor since all finalists support it").
2. **Ask 2–4 questions**, tailored to the category, in a single
   AskUserQuestion call (or one compact message if that tool isn't available).
   - Only ask what changes the ranking or the stars: use pattern (e.g. how
     they cook, how often), must-have sizes or features, deal-breakers
     (materials, glass lids, origin, weight), care (dishwasher), compatibility
     (cooktop, phone ecosystem, room size), and how much to trade price
     against quality.
   - Give 2–4 concrete options each, explain the trade-off in the option
     text, put a recommended default first, and allow multi-select where
     choices combine.
   - Example for cookware: cooking style (high-heat searing vs quick everyday) ·
     must-have pieces (12" skillet, big stockpot) · care (dishwasher) ·
     deal-breakers (glass lids).
3. **Don't block the work.** Send the questions right after locking the brief, and
   start the discovery and pricing agents whose work doesn't depend on the
   answers. Apply the answers when pruning, rating and starring.
4. **"Any is okay"** or no preference means no stars on those attributes. Don't
   re-ask.
5. Ask again later only if a genuinely new fork appears that the first round
   couldn't have anticipated. Keep it to one question.

**Standing profile** (applies to every search; edit as preferences change):
- Not eligible for student, education, military/veteran, first-responder or
  healthcare discounts. Never propose them (see step 4).
- Wants direct product links for everything shown.
- Prefers depth over speed: big and small retailers, credible reviews only.

Beyond the intake pass, ask only if a hard constraint is genuinely ambiguous
and changes the answer. Otherwise choose the sensible default, state it, and
flag the trade-off in the output.

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
- **Effective price = price − ✅ coupon + shipping + sourced tax/fees.**
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

## 4. Promo codes — find, rank, test (follow `references/coupon-verification.md`)

The checkout is the source of truth. Coupon sites state wrong amounts and list
dead codes, and a code can be accepted yet give $0 on this item.

1. **Gap math first.** `needed % = 1 − target / price`. Above ~30%, codes
   alone won't do it. Say so up front, and spend the effort on sales,
   seconds, bundles and no-code levers.
2. **Collect candidates** by evidence rank:
   1. store shows it today;
   2. a timestamped human check;
   3. a creator/influencer/podcast post from the last ~60 days;
   4. a single aggregator.
   A code copied across aggregators is one source. Ignore auto "verified" stamps.
   Never trust the claimed amount.
3. **Big retailers with no public codes** (Amazon, Costco, Walmart, Target…):
   don't guess. Use the levers instead: clip coupons, member pricing, discounted
   gift cards, price match/adjustment, manufacturer rebates, cashback, and the
   👤 "check your accounts" list.
4. **Test in a cart** when a browser exists (delegate to a `sonnet` agent). Use the
   voucher field only, at most 20 attempts per store, at most 10 guesses (small stores only), stop at
   any CAPTCHA, and never create accounts, enter personal or payment data, or place
   orders. Never touch private/staff/internal codes.
5. **Labels:** ✅ works · ⚠️ accepted but $0 here · 🟡 likely · ⚪ unchecked ·
   👤 your step · ❌ rejected. **Only ✅ changes effective price.** Never
   stack without linked T&Cs. Every code says "verify at checkout."
6. **Never propose verified-status discounts** (student, education/teacher,
   military/veteran, first responder, nurse/healthcare, ID.me, SheerID, UNiDAYS,
   GovX…). The user doesn't qualify. Show one only if it needs no verification
   at all, and then present it as an ordinary sale.
7. If the user requires "at least one code per option": give the best code
   for each with its honest label. Where a retailer genuinely has none, say so
   and put the best lever in that row. Never pad with a dead code.

---

## 4b. Review-rating pass (after the shortlist is narrowed)

Once finalists are chosen (usually 3–6), run one more pass that rates each
finalist **1–5 stars on the general feedback of online reviews**. This is
separate from the editorial gate in step 1: that gate asks *do experts
recommend it?*; this pass asks *what do owners say after living with it?*

Delegate it: one `haiku` agent per 2–3 finalists collects the data, then one `sonnet` agent (or the manager) scores. Template:
`references/subagent-briefs.md` → "Review-rating agent".

**Collect per finalist (exact SKU; flag reviews of look-alike variants):**
- Retailer star averages + review counts (Amazon, Walmart, Target, Costco,
  brand site, specialty stores), each with its product URL and date read.
- Editorial verdicts (from step 1) and any long-term or retest updates.
- Owner discussion: Reddit / forums / long-term reviews. Note recurring themes.
- Top recurring **praise** and **complaints** (aim for 3 each), with how often
  each appears, especially durability problems (warping, pitting, rivets
  loosening, handles, lids), QC issues, and customer-service and warranty experience.
- Red flags: review-count spikes, incentivized/"free product" reviews, merged
  listings (reviews from a different product), and very low counts.

**Scoring rubric (show the arithmetic):**
1. **Base** = review-count-weighted average of retailer stars, using only
   sources with ≥ 50 reviews (fewer → note it and weight at half).
2. **Adjust** by up to ±1.0 total, in 0.25 steps, for:
   - durability or QC complaints recurring in ≥ 10% of negative reviews, or flagged by an editor's retest (−0.25 to −1.0);
   - consistent long-term owner praise on Reddit/forums (+0.25 to +0.5);
   - suspected review inflation or merged listings (−0.25 to −0.5, and say why).
3. Round to the nearest 0.5 and display it as ★ (e.g. ★★★★☆ 4.0) with a
   **confidence** label: High (≥ 1,000 reviews across ≥ 2 sources), Medium,
   or Low (< 200 reviews or a single source).
4. One line: "Owners love: …; Owners complain: …".

Never invent counts or averages. A source that won't load can be cited from a
search snippet, labelled `snippet`. If there's too little data, the rating is
"insufficient data", not a guess. The star rating is shown in the final table
(a "Owner rating" column) and **does not override** price or the editorial gate.
It informs the recommendation, and a ≤ 3.0 rating must be called out.

## 5. Seller trust (shop-scout rule)

Each row gets ✅ Trusted / ⚠️ Mixed / ❌ Risky + one-line reason + **source
link**. For marketplaces judge the actual third-party seller holding the buy
box. Unknown small retailers: check BBB/Trustpilot/Reddit and how long the
domain has existed. No source → "insufficient data", never a guess.

---

## 6. Execution: fan out, then verify

Follow the **Operating rule** above. The stages and their tiers (templates are in
`references/subagent-briefs.md`):

1. **Review sweep** (`sonnet`, 1 agent): every pick from the category's credible
   roundups, plus dropped picks → the candidate list.
2. **Pricing sweeps** (`haiku`, parallel, 2–3 candidates or one retailer group
   each) → raw price, stock and code tables.
3. **Sale timing** (`haiku` to collect, or `sonnet` if it must judge SKU drift; 1 agent).
4. **Review-rating pass** (`haiku` collectors in parallel, then one `sonnet` scorer; finalists only). See step 4b.
5. **Cart verification** (`sonnet`, last, finalists only; can run in parallel with 4).
6. **Manager:** prune between stages, spot-check the winner, write the report.

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

**Link rule (applies to every message, not just the final report):** every
product you name gets a direct **product-page link** at the retailer whose price
you quote. That includes interim progress updates, shortlists, the benchmark,
mix-and-match pieces, ruled-out items, and Black Friday deals. Rules:
- Link the exact SKU page, not a homepage, search page or category page. If a
  price comes from a different retailer than the link, say so.
- Use only URLs an agent actually loaded or got from search results. Never
  build or guess a URL. If no product URL is known, write `(link not found)`
  and get one from a cheap agent before the final report.
- Sub-agents must return a product URL for every price they report (the
  brief templates require it).
- Mark scam/lookalike domains as warnings, never as buy links.

Lead with the answer. Structure:

1. **Bottom line** (2–4 lines): the recommended buy, its effective price vs the
   benchmark, and the single biggest trade-off (e.g. "tri-ply, not 5-ply").
2. **Benchmark** spec line.
3. **Comparison table**, one row per finalist (fixed columns, fixed order):

   | Product | Reviewed by (award) | Owner rating (★, confidence) | Pieces / key spec | Retailer | Price | Effective price | Evidence | Promo code (label) | Trust | Buy link |

   **"What each one has" bullets.** When finalists differ in ways that matter
   (construction such as 5-ply vs tri-ply, sizes or contents, materials, lid
   type, oven or dishwasher rating, origin, warranty, returns), add a short
   bullet block per product, benchmark included, right under the table:
   - 3–6 bullets per product, with the facts only (e.g. "Tri-ply, aluminum core ·
     8"/10" skillets · 6 qt deep sauté · steel lids · 500°F · Brazil").
   - Put a ⭐ on an attribute **only** if it makes that product genuinely
     superior to the others *on that attribute*, and only when the advantage
     is real: backed by testing, physics, or an objective spec (the largest
     pan, the highest oven rating, the longest return window, the only one
     with steel lids). Marketing claims don't earn a star. More layers is
     not automatically better: 5-ply holds heat and spreads it more evenly, but heats and
     responds more slowly, so star it only if the user's priorities favour it.
   - Mark real weaknesses with ⚠️ (e.g. "⚠️ skillets warped in Wirecutter's retest").
   - If whether something is superior depends on how the user cooks (searing vs
     sauces, induction, dishwasher use, needing a 12" skillet, weight or wrist
     strain), **ask** in one short question with options (AskUserQuestion
     where available) rather than guessing. Until they answer, show the
     bullets without stars on the disputed attributes and say what each answer
     would change.
4. **Mix-and-match** builds, with arithmetic.
5. **Sale timing**: announced deals + historical lows + wait-or-buy call.
6. **Codes table**: code · savings · conditions · source · label
   (✅ / ⚠️ / 🟡 / ⚪ / 👤, with ❌ rejected listed below) · "verify at checkout".
7. **Ruled out**: one line each (price, reviews, or spec).
8. **Gaps**: sites that blocked you and what that leaves unverified.

**Data-floor gate:** if half or more of a product's rows have no real price,
don't print a table for it — give an honest summary (what it is, where sold,
prices actually read with sources).

**Pre-output checklist** — every row has a sourced price, a trust verdict with
a link, and a direct product link; every product named anywhere in the message
(including ruled-out items and interim updates) is linked or marked
`(link not found)`; no invented prices, codes, shipping, or
history; best buy is in stock; all rows are the same SKU class; only
✅ codes touch effective price; nothing stacked without T&Cs.

Be direct about trade-offs. If the honest answer is "the benchmark is already
the best value for what you asked" or "wait 12 days," say that.

### Visual report (default for any run with 3+ finalists)

**Start from `$SKILL_DIR/assets/report-template.html`.** It is the approved
layout and design (a worked cookware example). Copy it, replace the content, keep
the structure and CSS, and fill photos with
`python3 -I $SKILL_DIR/scripts/embed_images.py page.html out.html key=img.jpg …`.
Adapt the labels to the category (e.g. "Pieces" → "Specs" for electronics).
Don't redesign it unless the user asks.

Publish one unified HTML page (Artifact tool) and give the link alongside a short chat summary. Read it top to
bottom in these groups:
0. **WAIT banner** (top of the page, and the first line of the chat summary), shown only when a
   sale is likely within the next **14 days**. Show it when either:
   - a major sale event (Black Friday/Cyber Monday, Prime Day, Memorial/Labor
     Day, brand friends-and-family or anniversary sales) starts within 14 days, **and**
     at least one finalist has dropped during that event before (exact SKU, a
     dated source) or a deal for it is already announced; or
   - a retailer or brand has announced a sale on a finalist starting within 14 days.

   Content: the event and its start date with a day count · one line per
   finalist with its past event low or announced deal (or "no past data") ·
   **exceptions to buy now** (a code or price that expires before the sale,
   low stock) · whether the retailer's price-adjustment policy covers buying now (only if
   verified). Don't show the banner for vague "prices may drop" claims, and
   delete the block entirely when the conditions aren't met. If waiting means losing a
   time-limited deal, say which is likely cheaper.

   **When the banner is shown, offer a price watch.** Right after
   presenting the report, ask once (AskUserQuestion) whether to create a
   scheduled task that re-checks prices. Options: **Daily** · **Every 3 days** ·
   **Start of each week (Monday)** · **No thanks**. If the user's time zone isn't
   known, ask it in the same call. On a yes:
   - Create it with the scheduled-task tool (`create_trigger`), set to start a fresh
     session on each firing and send push notifications. Use these schedules,
     written in the user's time zone with `CRON_TZ=`:
     - Daily: `M H * * *`
     - Every 3 days: `M H */3 * *`
     - Weekly: `M H * * 1`

     Pick a time outside 6–9 AM Pacific and a minute that isn't :00 or :30.
     Every-3-days counts by day of the month, so it resets on the 1st; say so in one line.
   - The prompt must stand on its own. Include: each finalist with its exact
     SKU, product URL and the price/code at the time of the report · the
     benchmark price · the target to beat · the sale dates · the user's standing
     profile (no status discounts; links on everything). Instruct it to run a
     lean `/shopper` re-check (pricing sweep plus code re-test, using `haiku` agents),
     report only changes (a new low, a new code, an expired deal, out of stock),
     and say "no change" in one line otherwise.
   - **Auto-stop:** the prompt tells the task to disable itself
     (`update_trigger enabled=false`) once the sale window has ended (default:
     3 days after the event's last day) or once the user buys, and to send a
     final summary.
   - **Add it to the user's watchlist page**, "Waiting On":
     https://claude.ai/artifact/FLYkd9RBwTa9YfwFBiYJvY. That is the one place the user
     tracks every wait. Never create a second watchlist; add to this one.
     Use the ArtifactData tool to `set` one document in collection `watches`, with
     doc_id `<slug>-<event>-<year>`, and these fields:
     - `title`, `category`, `status:"waiting"`, `target`
     - `taskIds[]`: the scheduled task id(s) from `create_trigger`. The page's **Purchased** button
       uses these to switch the tasks off through the Claude Code Remote connector.
     - `image`, `imageAlt`: the best option's photo for the landing tile
     - `report`: the full research, rendered in the search's detail view. Fields:
       - `asOf`, `useCase`, `answer[{k,text,url}]`, `wait{title,lines[],exception}` (omit when not a WAIT)
       - `benchmark{name,url,price,note,image,facts[{t,k}]}`
       - `finalists[]`, each with `name, meta, ribbon, top, image, price, listPrice, how, rating` (number or
         null), `ratingText, expert, facts[{t,k:"plus"|"minus"}], owners`, `codes[{code,text,status,label}]`,
         `buyLabel, url`, `alt{label,url}`
       - `compare{cols[],groups[{name,rows[[label,[values],bestIndex]]}]}` (bestIndex `-1` = none)
       - `ruledOut[{name,url,image,why}]`, `ruledOutNote`, `warnings[]`, `unverified[]`, `sources[[name,url]]`
     - **Photos:** never put image data in the database. Each document is capped at 256 KiB, and photos
       fill it fast. Upload the ~560px WebP files once with the Artifact tool
       (`asset: true`, `file_paths`, `url` = the watchlist), then store each returned `/_blob/<id>`
       path in `image` fields.
     - `benchmark{name,price,url}`, `bestNow{name,price,retailer,url}`
     - `saleEvent{name,start,end}` (ISO dates), `schedule` (human text), `nextCheck` (ISO), `stopDate`
     - `reportUrl` (this run's report), `taskName`, `summary`, `updatedAt`
     - `items[]`: one per finalist with `name, retailer, url, price, effective, trend, low, lowNote, code,
       codeStatus` (`works|rejected|unchecked|your-step|none`) and `codeStatusLabel`

     Also add a starting entry in `checks`:
     `{watchId, at, headline, changes[], noChange}`. Write both in one `batch`.
   - The scheduled task's prompt must also say:
     - **Step 1:** read its watch doc. If its status is `bought` or `ended` (the user
       pressed **Purchased** or **Stop watching**, which archives the search) or the stop date has passed,
       disable itself and mark the doc ended. Never overwrite `purchased`. Statuses:
       `waiting` · `buy-now` · `purchased` · `ended`. `purchased` and `ended` show in the page's Archive.
     - **Step 2:** after every run, `update` the doc (pinning `if_version`) with new
       items, bestNow, summary, updatedAt and nextCheck. Set status to `buy-now` when a finalist hits
       its past low or a deal is about to end. Then add a `checks` entry `<date>-<slug>`.
     - Leave `image`, `imageAlt`, `taskIds` and `report` untouched (live prices go in `items`). If an update hits a version conflict (the user
       may have just pressed Purchased), re-read the doc and apply the stop rules first.
     - **If ArtifactData is unavailable**, say so in its report.
   - The watchlist page itself: a landing view with every active search as a tile (photo, status,
     best price vs target, sale countdown, next check), plus an Archive. Tap a tile to open `#w-<id>`,
     which shows the WAIT banner, answer, live prices, the full `report` (benchmark, finalist
     cards with owner ★ ratings, expert badges, ★/⚠ facts and codes, quick compare, ruled out,
     warnings), the log, sources and the Purchased / Stop watching buttons. Don't
     redesign or republish it during a search; only write data to it.
   - Confirm to the user what was created: how often, the time, and the stop date,
     plus the watchlist link.
     Call it a "scheduled task", never a trigger or cron job. If the tool is
     unavailable, say so and give the user a reminder date to re-run `/shopper`.
1. **Answer**: 2–3 lines (buy · cheapest · the key caveat).
2. **Benchmark**: one card (if there is one).
3. **Finalists**: one card each, all the same shape: product photo · name + model ·
   price (struck list price, price after code) · owner ★ rating · expert badge ·
   ★/⚠ fact bullets · best code with status pill · "View at <retailer> →" link.
   Two columns on desktop, one on a phone.
4. **Price chart**: every set on one dollar scale, a dashed benchmark line,
   and listed vs after-code bars.
5. **Quick compare**: a short table grouped as Price / Pieces / Build & care / Reviews,
   with the best cell in each row shaded.
6. **Ruled out**: compact rows with thumbnails and the one-line reason.
7. **Timing and warnings**: the sale calendar, scam lookalikes, what isn't verified.

**Product photos:** the page can't load images from other hosts, so download
them and embed them. Have a `haiku` agent collect the URLs: check the product page's `og:image`, the
Shopify `/products/<handle>.json` → `product.image.src`, then the image of the same SKU at another retailer. Check that each image shows the
exact set (piece count, lid type). Resize to ~560px WebP and embed as data URIs
(keep the page well under 1 MB). If none is available, show a "No photo" placeholder. Never use an
image of a look-alike variant.

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
- `assets/report-template.html`: the approved visual report (worked example)
- `scripts/embed_images.py`: resizes photos and embeds them into the report's double-brace photo slots
