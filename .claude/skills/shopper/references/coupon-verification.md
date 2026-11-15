# Promo codes: find, rank, test, report

This builds on promo-code-hunter (MIT, © mariaboger; see
`scripts/LICENSE-promo-code-hunter`), adapted for US shopping.

**The checkout is the source of truth.** Lessons from real cart testing:
- Coupon sites list wrong amounts. Three codes listed as "15%" gave 10% at checkout.
- Coupon sites list dead codes. The top pick from research alone was rejected in the cart.
- Banner codes can be scoped. A site's own banner code was *accepted* but gave
  $0 on the item, because it only covered one category.
- Codes are country-specific. A code posted for the .ca or .co.uk site often fails on the US site.

## 0. Gap math (do first)

`needed % off = 1 − target_price / current_price`

Typical ceilings: aggregator codes 10–25%, first-order signups 10–20%,
friends-and-family events 20–30%. If `needed %` is above ~30%, a code alone
won't do it. Say so, and spend the budget on sale events, seconds, bundles and
the levers in §4.

**Budget per retailer:** about 25 research calls, about 35 for big retailers,
plus up to 20 code attempts in a cart. Stop code-hunting once you have about 5
credible candidates, or after about 6 searches in a row that add nothing new.

## 1. Basket

- Use the official **US** store, and the exact SKU from the comparison.
- If no product is given, test two items, one full-price and one bundle/set.
  Codes behave differently on them; set-exclusions are common.
- Note whether the item is already on sale. Many codes exclude sale items.
- Note **who sells it**. Marketplace third-party sellers usually get no
  retailer codes, no price match and no cashback.
- For multi-brand retailers (Macy's, Kohl's, Sur La Table, Williams Sonoma,
  Nordstrom, Wayfair), the **brand exclusion list** decides everything. Check the
  brand against the current terms.
- Platform check (browser): `!!window.Shopify`. Shopify stores accept codes from
  guests at `/checkout`. Big custom stores often hide the voucher field behind a login.

## 2. Where codes come from, and how to rank evidence

**Evidence rank** (highest first):
1. The store shows it today (banner, product page, promo or terms page).
2. A third party shows a recent **timestamped** human check. Examples: a
   Slickdeals thread with dated "worked for me" comments, or an editor-verified card.
3. A creator posted it in the last ~60 days.
4. A single aggregator lists it, or the listing is old.

Rules:
- One code copied across many aggregators counts as **one** source.
- Ignore auto-generated "verified today" stamps and success-rate percentages.
- Never trust the claimed amount. If sources disagree, show the range.

**A. The store.** Check:
- the announcement bar, banners, the sale/promo page and the newsletter popup;
- first-order, email/SMS and **app** offers (first app order, app-only codes);
- refer-a-friend, loyalty/member, birthday, subscription and bundle offers;
- automatic offers ("buy 2, save 10%"), which are often the best deal.

Report first-order, email and app offers even when the code only arrives after
signup, as a 👤 step. Say where the info came from and what the user would do.
Search: `"<store>" first order discount`, `"<store>" app discount`,
`"<store>" promotional offers terms`.

**B. Deal communities.** Slickdeals (search `site:slickdeals.net <store> <brand>`; comment threads like "dead as of…" are strong signals), r/frugal and category subreddits, and DealNews.

**C. Creator, influencer and podcast codes.** These are often the codes that actually work.
- Instagram and TikTok are barely indexed. Run **one** `site:instagram.com` query at most.
- Queries that tend to work: `"<brand>" code influencer <year>`, `"<brand>" "use code"`,
  `"<brand>" podcast code`, `"<brand>" code youtube` (video descriptions get indexed).
  Run the main one in **extended** search mode.
- If the brand's partners are known, run **one** combined query:
  `"<brand>" code (creatorA OR creatorB)`.
- Learn the brand's **code format** (e.g. `NAME10`, `NAME15`, a rotating
  campaign code). Use it to judge leads.

**D. Aggregators** (lowest rank): RetailMeNot, Knoji, DealSpotr, Wethrift,
CouponBirds, DealDrop, DontPayFull, Honey, Capital One Shopping.

**E. Skip:** personal referral IDs, other people's single-use codes, and
expired offers. Give one line listing the dead codes the user might stumble on.

**F. Guesses** (browser mode only, **10 at most**). Build them from the brand's
format and the current event (BLACKFRIDAY26, CYBER20, HOLIDAY15), plus a few
welcome codes (WELCOME10, `<BRAND>10`). **Never guess at big retailers.** Their
real codes are personal, so guessing only burns attempts.

**Hands off** anything marked private, internal, staff, employee, corporate,
partner-event or test, even if a site's source exposes it. Don't test it and
don't report it. Using such codes can get orders cancelled.

## 3. Cart-test protocol (browser mode)

Asking for working codes is consent to try codes in the voucher field. Nothing past the voucher field.

1. **Cookie banner:** decline optional cookies. A hidden banner can silently
   block add-to-cart. If a click does nothing, take a screenshot.
2. Add the basket item with the store's own **Add to cart** button. Bundle
   builders reject direct cart-API calls.
3. **Find the voucher field.** Look in the cart drawer, the cart page, or the
   collapsed order summary at checkout. On Shopify, `/checkout` works as a guest;
   no email is needed to apply a code.
   **Control first:** apply one obviously fake code (e.g. `ZZFAKE999`) and
   record the message. If real codes get the *same* message, the site can't
   tell an invalid code from an excluded product, so report that ambiguity.
   (Seen in testing: Made In said "Not Applicable" to everything, and the set
   page said "Additional discounts do not apply".) Count the control
   toward the 20-attempt limit. Also read the product page for "no additional
   discounts" text before testing.
4. **Enter one code at a time**, at least 3 s apart:
   1. Locate the voucher **textbox** and its **Apply** button. Confirm the
      textbox is *not* the zip, address or email field.
   2. Remove the previously applied code and wait ~2 s.
   3. Click the textbox, type the code, click Apply, and wait 3 s.
   4. Read the result (read-only):
      ```js
      const t = document.body.innerText;
      ({msg: (t.match(/[^\n]*(valid|invalid|minimum|not applicable|excluded|only for|expired)[^\n]*/i)||[])[0],
        summary: (t.match(/(Subtotal|Order summary)[\s\S]{0,250}/i)||[])[0]})
      ```
   5. Record: accepted or rejected, the store's message, and the **real
      discount** (the discount line ÷ subtotal). Accepted with $0 off means ⚠️.
5. **Hard limits:**
   - At most 20 attempts per store per session.
   - Normal voucher field only. No discount-API calls, no permutations, no brute force.
   - Stop at the first CAPTCHA or rate-limit message.
   - **Never** create an account, enter an email, address or payment details, press
     Enter in or submit any non-voucher form, click Continue/Pay/Place order,
     or place an order.
   - Some conditions ("first order only") are only checked after an email is
     entered. Report those as "condition not verified."
   - If the field needs a login, the user logs in themselves, or you fall back to a "try these" list.
6. **Shopify discount config** (optional, read-only). On the homepage, read only
   *public* campaign data. It shows what a code covers before you test it.
   ```js
   const html = document.documentElement.outerHTML;
   [...html.matchAll(/["']?(campaigns?|discounts?|influencers?|promotions?|coupons?)["']?\s*[:=]\s*[\[{]/gi)]
     .slice(0, 10).map(m => html.slice(m.index, m.index + 600));
   ```
7. **Clean up:** remove the code and empty the cart (Shopify:
   `fetch('/cart/clear.js',{method:'POST'})`).

**No-browser mode:** do §1–2 only and give an ordered "try these" list. Say
plainly that nothing was tested at checkout.

## 4. Big retailers without public codes

Amazon, Costco, Sam's, Walmart, Target, Best Buy, Home Depot, Lowe's. Spend at most
~5 calls hunting codes, and the rest on levers that exist:
- **Amazon:** the product page's **coupon checkbox**, Subscribe & Save,
  "save X% on 2", Amazon Resale (Warehouse), Prime-exclusive prices, gift-card
  reload bonuses, price history (Keepa/camelcamelcamel).
- **Costco / Sam's:** member pricing, instant savings in the monthly book, and the
  Executive reward (2%).
- **Target:** Circle offers (in the app) and the Target Circle Card (5% off).
- **Discounted gift cards:** Costco and Sam's sell gift cards for many retailers
  below face value; grocery fuel-point promos (Kroger) also count. These usually
  stack with codes. Say so when the terms confirm it.
- **Price match / price adjustment:** read the current terms, including the competitor list,
  stock rules and holiday blackouts. Name the cheapest competitor that actually **qualifies**.
- **Manufacturer promotions:** rebates, gift with purchase, registration
  bonuses, extended warranty (`"<brand>" rebate <year>`).
- **Cashback portals:** Rakuten, TopCashback, Capital One Shopping. Cashback may be voided
  when an outside code is used.

## 5. "Check your accounts" checklist (👤)

These are perks only the user can see. Name a program only if it fits this store, or there's evidence it
lists or has listed the store. Give the click path where known.
- **Card-linked offers:** Amex Offers, Chase Offers, Capital One Offers, BofA Deals.
- **Employer perk portals:** PerksAtWork, Corporate Perks, Beneplace, Abenity.
- **Store and club memberships:** loyalty programs, birthday rewards, member prices, AAA, AARP.

**Excluded: identity- or status-verified discounts.** Do not search for, list or
propose discounts for students, teachers or educators, military or veterans,
first responders, nurses or healthcare workers, or anything gated by ID.me,
SheerID, UNiDAYS, Student Beans, GovX or similar verification. The user does
not qualify. **One exception:** if the offer is open to everyone, with no
verification of any kind (e.g. a store-wide "Teacher Appreciation" sale anyone
can use), show it as an ordinary sale and don't mention the group.
Sub-agents must drop these from their reports too.

Use the user's known circumstances only to rank this list. Don't speculate about accounts they may not have.

## 6. Labels

| Label | Meaning | Changes effective price? |
|---|---|---|
| ✅ **works** | Accepted in a cart today (record the real amount and timestamp), or the store itself shows it today with conditions verified | Yes |
| ⚠️ **accepted, $0 on this item** | The code is scoped elsewhere; say what it does cover | No |
| 🟡 **likely** | Recent timestamped third-party check, or a creator post from the last ~60 days | No (FYI) |
| ⚪ **unchecked** | Single aggregator or an old post | No (FYI) |
| 👤 **your step** | Needs the user's account or action (signup, app, card offer, login) | No, until done |
| ❌ **rejected** | A *found* code that failed at checkout; one line, so the user doesn't retry it | No |

- Never show a guessed code that wasn't accepted.
- Mark a working guess "guessed, ✅ at checkout".
- **Never stack** codes unless the store's T&Cs say so (link them).
- Every code shown ends with "verify at checkout."

## 7. Code reply format

**First line:** the best option and what it does to *this* basket
("FRIEND20: −20%, ✅ in cart: $799.95 → $639.96"). If there are no public
codes, say so, then name the best lever with an estimated price.

| Code / offer | Real discount | Conditions | Source (date) | Status |
|---|---|---|---|---|

Under the table: the best combination with an estimated final price incl.
shipping (say what doesn't stack) · buy-now vs wait · no-code options · the
"check your accounts" list · in no-browser mode, "try in this order: …" · Sources.

If the user requires "at least one code per option" and a retailer genuinely
has none, say so and give the best lever in that row instead. Never pad the
table with a dead code.
