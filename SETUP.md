# Garden & Grace — Setup

Drop-in-keys checklist for going live with Supabase auth + Stripe billing.

## What changed

- Sign-in is now **Supabase magic link** — user enters email, clicks the link in their inbox.
- Each signed-in user gets **5 free queries per UTC day** across all AI features (garden, birds, fishing, recipe, build, catch ID). The 6th call returns HTTP 402 and the frontend pops the paywall.
- "Upgrade" button starts a **Stripe Checkout** subscription. The webhook flips the user to `premium` (unlimited).
- All AI endpoints now require `Authorization: Bearer <Supabase JWT>`. Anonymous traffic is rejected with 401.
- Removed the broken email-PDF feature (`/features/recipe/email`, `/features/build/email`) and the legacy magic-link auth routes (`/auth/*`).

## 1. Supabase

1. Create a project at https://supabase.com.
2. **Authentication → Providers → Email**: enable. Disable "Confirm email" if you only want magic links (no password). The default magic-link template works as-is.
3. **Authentication → URL Configuration**: set the Site URL to your Render URL (e.g. `https://garden-and-grace-public.onrender.com`). Add the same URL plus `https://localhost:8000` to "Redirect URLs".
4. From **Project Settings → API**, copy:
   - `Project URL` → `SUPABASE_URL`
   - `anon` `public` key → `SUPABASE_ANON_KEY`
   - `JWT secret` (under "JWT Settings") → `SUPABASE_JWT_SECRET`

## 2. Stripe

1. Create a product + recurring price at https://dashboard.stripe.com/products. Copy the price ID (`price_…`) → `STRIPE_PRICE_ID`.
2. From **Developers → API keys**, copy your secret key (`sk_test_…` to start) → `STRIPE_SECRET_KEY`.
3. **Developers → Webhooks → Add endpoint**:
   - URL: `https://<your-render-url>/billing/webhook`
   - Events: `checkout.session.completed`, `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`
   - Copy the signing secret (`whsec_…`) → `STRIPE_WEBHOOK_SECRET`.

## 3. Render

In the Render dashboard for `garden-and-grace-public`, set these env vars (all already declared in `render.yaml` with `sync: false`):

| Key | Value |
| --- | --- |
| `ANTHROPIC_API_KEY` | Anthropic key (sk-ant-…) |
| `APP_URL` | Your Render URL (e.g. `https://garden-and-grace-public.onrender.com`) |
| `SUPABASE_URL` | from step 1 |
| `SUPABASE_ANON_KEY` | from step 1 |
| `SUPABASE_JWT_SECRET` | from step 1 |
| `STRIPE_SECRET_KEY` | from step 2 |
| `STRIPE_PRICE_ID` | from step 2 |
| `STRIPE_WEBHOOK_SECRET` | from step 2 |

Optional:
- `FREE_DAILY_LIMIT` (default `5`) — change the free-tier daily cap.

Deploy. Done.

## 4. Smoke test

1. Visit your URL → enter an email → click the link in your inbox → land on home.
2. Use Garden / Birds / Fishing / Recipe / Build. Counter shows "X of 5 remaining".
3. Hit the limit. Paywall appears. Click "Upgrade".
4. Stripe Checkout opens. Use test card `4242 4242 4242 4242`, any future date, any CVC.
5. Redirects back to `/?upgraded=1`. Counter switches to "Premium · unlimited".

## Endpoints

- `GET /health` — public liveness.
- `GET /config` — public; returns `{supabaseUrl, supabaseAnonKey, billingEnabled, freeDailyLimit}` for the frontend bootstrap.
- `GET /features/daily-verse` — public.
- `POST /features/{garden|birds|fishing|fishing/catch-recipe|recipe|build}` — auth + quota.
- `POST/GET /features/catches` — auth (POST), public (GET).
- `GET /billing/status` — auth.
- `POST /billing/create-checkout-session` — auth.
- `POST /billing/webhook` — Stripe-signed.

## Notes

- Quota is tracked in SQLite (`usage` table) by Supabase user id + UTC date.
- Subscription state cached in `subscriptions` table, updated by Stripe webhook. Stripe is the source of truth; the local row is a projection.
- The frontend never sees Stripe secrets or the JWT secret — only the Supabase URL + anon key.
