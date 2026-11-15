# Promo codes: find, classify, verify

## Gap math (do first)

`needed % off = 1 − target_price / current_price`

Typical ceilings: aggregator codes 10–25%, first-order signups 10–20%,
friends-and-family events 20–30%. If `needed %` exceeds about 30%, a code alone
won't do it. Say so, then look at sale events, seconds, or bundles instead.

## Where codes come from (most to least reliable)

1. **On the product page or site banner** (e.g. "Friends & Family 20% off, code FRIEND20").
2. **The retailer's official promo/offer/terms page** (e.g. `/promotional-offers`,
   `/coupons`, `/deals`). These state exclusions; read them.
3. **First-order offers by email, SMS or app** (10–20%). These need a signup. Report them,
   but don't sign up on the user's behalf. Check whether they exclude sets or sale items.
4. **Card-linked and cashback offers**: Amex Offers, Chase Offers, Rakuten, TopCashback,
   Capital One Shopping. Count these as ❔ unless the user holds the card or account.
5. **Status discounts**: military, teacher, student, first-responder, nurse (ID.me,
   SheerID), AARP. These only count if the user is eligible.
6. **Aggregators**: RetailMeNot, Slickdeals (comment threads show real
   success and failure), Knoji, DealSpotr, Wethrift, CouponBirds, DealDrop,
   DontPayFull, Honey. Expect many dead codes. Prefer codes with dated "worked"
   reports from the last 7 days.
7. **Social and influencer codes**: brand Instagram/TikTok bios, YouTube descriptions,
   podcast sponsor codes (often 10–15%, and frequently do work).

Retailers with **no codes**, so say so plainly: Costco and Sam's (member pricing
and instant savings instead), Amazon (clip coupons and Subscribe & Save
instead), and MAP-protected brands (codes exclude them).

## Common exclusions to check

Brand exclusions (Sur La Table, Macy's, Kohl's, Williams Sonoma often exclude
premium brands) · "sale items excluded" · "sets excluded" (Made In first-order) ·
minimum spend · one per customer · new customers only · not valid with other
offers · not valid on doorbusters.

## Labels

| Label | Meaning | Changes effective price? |
|---|---|---|
| `cart-verified <timestamp>` | The code applied in a real cart, with the before/after subtotal recorded | Yes |
| ✅ applicable | Official source, and every condition verified | Yes |
| ❔ unknown | Any condition unverified (aggregator-only, exclusions unclear) | No, FYI only |
| ❌ not applicable | Expired, excluded, or ineligible | No; omit it |

Every code shown ends with **"verify at checkout."**

## Cart-test protocol (when a browser tool exists)

1. Open the product page in a fresh tab. Confirm the SKU and price.
2. Add to cart as a guest. **No account. No email signup. No payment details.
   Never press the final order button.**
3. Record the cart subtotal.
4. Enter the code in the promo field. Record the exact response message and the new subtotal.
5. Remove the code before trying the next one, so codes don't stack by accident.
6. Clear the cart when done.
7. Some sites only accept codes at the shipping/payment step. If reaching that step
   would require personal data, stop and label the code ❔ "requires checkout
   step to test."
8. Bot walls or CAPTCHAs: stop; don't bypass. Fall back to the official terms page.

Report: `retailer · product · code · result (applied/rejected/excluded) ·
subtotal before → after · message text · timestamp`.
