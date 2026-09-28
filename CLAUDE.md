# CLAUDE.md — Vietnamese Film Streaming Site (Django + Tailwind)

This file tells Claude how to build and maintain this project. Read it fully before writing code.

## 1. Project overview

A movie and drama streaming **website** for the **Vietnamese market**, built with **Python Django** (server-rendered pages).
The layout and user flows take inspiration from **vieon.vn** (and Netflix): a dark, cinematic look, a large hero banner, poster rows that scroll sideways, VIP badges, and a free tier with ads.

**Inspiration only. Never copy.** Do NOT use VieON's name, logo, brand colors, icons, images, copy text, or code. Take layout ideas and UX patterns only. The brand below is our own.

- Brand name: `{{BRAND_NAME}}` (placeholder, default "PhimHay"). Set once in `settings.BRAND_NAME` and read it in templates through a context processor. Never hard-code it.
- Language: Vietnamese UI (`<html lang="vi">`). All user-facing text is in Vietnamese.
- Audience: mobile-first, 4G connections, fans of Korean, Chinese and Vietnamese dramas and movies.
- Business model: free tier with ads + paid **VIP** tier with no ads.

## 2. Tech stack

- **Python 3.12+**, **Django 5.2 LTS**.
- **Database**: **MySQL 8.4** in every environment (dev runs it in Docker via `docker-compose.yml`, host port 3307). Driver: `mysqlclient`. Always `utf8mb4` (charset set in `DATABASES.OPTIONS`) so Vietnamese text is stored correctly. `DATABASE_URL` comes from the environment.
- **Cache**: **Redis 7** through Django's built-in `RedisCache`, used **only when `REDIS_URL` is set** (production). Development leaves `REDIS_URL` unset and gets `DummyCache` (no caching), so admin edits show immediately. Tests use `LocMemCache` so caching logic is still tested. To try Redis locally: `docker compose --profile redis up -d` and set `REDIS_URL=redis://127.0.0.1:6380/0`.
- **Templates**: Django templates, server-rendered. No React or Vue. No SPA.
- **Tailwind CSS v4** via the standalone CLI (npm):
  `npx @tailwindcss/cli -i ./static/src/input.css -o ./static/css/output.css --minify`
  Use `--watch` while developing. Never edit `static/css/output.css` by hand.
- **Vanilla JavaScript** (ES modules) only for interactions: carousel, row scrolling, tabs, player UI, menus. No jQuery. HTMX is allowed later for partial updates (filters, "load more"), but ask first.
- **Static files**: `django.contrib.staticfiles` + **WhiteNoise** in production.
- **Images**: `ImageField` (Pillow). Serve WebP/AVIF renditions with `srcset`.
- **Icons**: inline SVG in templates (e.g., Lucide or Heroicons copied as SVG). No icon fonts.
- **Font**: Be Vietnam Pro (Google Fonts), weights 400 / 500 / 700. It fully supports Vietnamese diacritics.
- **Config**: secrets and per-environment values come from environment variables (`.env` in dev via `django-environ`). Never commit secrets.
- Allowed packages: `Django`, `Pillow`, `whitenoise`, `django-environ`, `mysqlclient`, `redis`. Dev only (`requirements-dev.txt`): `ruff`, `django-debug-toolbar`. **Ask before adding any other dependency.**

## 3. File structure

```
/
├── manage.py
├── requirements.txt
├── requirements-dev.txt      ruff, django-debug-toolbar
├── docker-compose.yml        MySQL (3307) for local dev; Redis (6380) behind the "redis" profile
├── package.json              Tailwind CLI scripts (build, watch)
├── .env.example
├── config/                   Project package
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py / asgi.py
│   └── context_processors.py brand name, user tier (free|vip)
├── apps/
│   ├── catalog/              Movie, Season, Episode, Country, Genre, Banner
│   │                         views: home, listing (phim bộ / phim lẻ), detail, search
│   ├── player/               watch view, WatchProgress
│   ├── accounts/             custom User (phone number), login UI (phone + OTP, UI only)
│   ├── billing/              Plan, Subscription (VIP), plans + payment UI (UI only)
│   └── ads/                  AdSlot, Creative, SponsoredRow, template tags
├── templates/
│   ├── base.html             <html lang="vi">, head, header, footer, bottom nav
│   ├── includes/             header.html, footer.html, bottom_nav.html,
│   │                         card.html, card_rank.html, card_continue.html,
│   │                         row.html, ad_slot.html, house_ad.html
│   ├── catalog/              home.html, listing.html, detail.html, search.html
│   ├── player/               watch.html
│   ├── billing/              vip.html
│   └── accounts/             login.html
├── static/
│   ├── src/input.css         Tailwind entry + @theme tokens
│   ├── css/output.css        Built CSS (do not edit)
│   ├── js/                   main.js, carousel.js, row-scroll.js, player.js, search.js, my-list.js
│   └── img/                  logo.svg, placeholder images
├── media/                    Uploaded posters/backdrops (not committed)
└── apps/catalog/management/commands/seed_demo.py   Demo data (placeholder images only)
```

Each app has its own models, `views.py`, `urls.py`, `admin.py`, `tests/`. Keep apps small and focused.

**Models: one file per model.** An app with two or more models uses a `models/` package (e.g. `apps/catalog/models/movie.py`, `season.py`, `episode.py`). A model's QuerySet/Manager lives in the same file as the model, and shared abstract bases go in `models/base.py`. `models/__init__.py` imports and lists (`__all__`) every model, so code always imports from the package: `from apps.catalog.models import Movie`. When adding a model, add its file and register it in `__init__.py`. An app with a single model (accounts, player) keeps a plain `models.py`.

## 4. Design tokens (Tailwind v4 `@theme`)

Put these in `static/src/input.css`. Always use these tokens. Never hard-code hex values in templates.

```css
@import "tailwindcss";

@source "../../templates";
@source "../../apps";
@source "../js";

@theme {
  --font-sans: "Be Vietnam Pro", system-ui, sans-serif;

  --color-bg:        #0B0B0F;  /* page background */
  --color-surface:   #16161D;  /* cards, panels */
  --color-surface-2: #22222B;  /* hover, inputs */
  --color-line:      #2E2E38;  /* borders */
  --color-text:      #F5F5F7;
  --color-muted:     #A1A1AA;

  --color-brand:       #1D6FF2;  /* blue: primary CTAs, active states, focus */
  --color-brand-hover: #3D86FF;
  --color-brand-soft:  #5B9BFF;  /* links and blue text on dark backgrounds */
  --color-brand-ink:   #FFFFFF;  /* text on brand */
  --color-vip:         #F5B301;  /* gold: VIP badges and the VIP upgrade only */
  --color-vip-ink:     #1A1300;  /* text on VIP gold */
  --color-live:      #E5484D;  /* LIVE and "Mới" (new) badges only */
  --color-ad:        #3A3322;  /* ad slot background */

  --radius-card: 0.5rem;
}
```

Rules:
- Dark theme only. The body is `bg-bg text-text font-sans antialiased`.
- **Blue is the brand color.** One blue CTA per screen ("Xem ngay", watch now). Other buttons are outline or ghost.
- **Gold is only for VIP**: VIP badges, the "Nâng cấp VIP" button and the VIP plans page. Never use gold for ordinary buttons.
- Blue text on dark backgrounds uses `text-brand-soft` (not `text-brand`) so it stays readable.
- Do not use red as the main brand color.
- Title line height is at least `leading-snug`, so Vietnamese stacked accents (ắ, ễ, ợ) never clip.

## 5. Layout and responsive rules

- **Mobile first.** Write base classes for about 360px, then add `md:` and `lg:` overrides.
- Side padding: `px-4 md:px-8 lg:px-12`. No horizontal page scroll, ever.
- Poster rows: `flex gap-3 overflow-x-auto snap-x scroll-smooth` with the scrollbar hidden. Desktop shows arrow buttons.
- Poster sizes: portrait 2:3 (`aspect-[2/3]`), width `w-32 md:w-40 lg:w-44`. Landscape 16:9 for "Xem tiếp" (continue watching).
- Mobile: a bottom tab bar (Trang chủ, Tìm kiếm, Tải xuống, Tài khoản). Desktop: a top nav.
- Tap targets are at least 44×44px.
- Rows are rendered **on the server**, so the page has its final layout on first paint. Do not load rows with JS unless there is a clear reason.

## 6. Django conventions

### URLs (Vietnamese slugs, always named)
| Page | URL | Name |
|---|---|---|
| Trang chủ | `/` | `catalog:home` |
| Phim bộ | `/phim-bo/` | `catalog:series` |
| Phim lẻ | `/phim-le/` | `catalog:movies` |
| Chi tiết phim | `/phim/<slug>/` | `catalog:detail` |
| Trình phát | `/xem/<slug>/tap-<int:number>/` (movies: `/xem/<slug>/`) | `player:watch` |
| Tìm kiếm | `/tim-kiem/?q=…` | `catalog:search` |
| Gói VIP | `/vip/` | `billing:plans` |
| Đăng nhập | `/dang-nhap/` | `accounts:login` |

Always use `{% url %}` and `reverse()`. Never hard-code paths.

### Models (core fields)
- `Movie`: `title`, `original_title`, `slug` (from the Vietnamese title with diacritics stripped), `kind` (`bo`/`le`), `country` (FK), `genres` (M2M), `year`, `age_rating` (choices: P, K, T13, T16, T18), audio as three booleans `has_vietsub` / `has_thuyet_minh` / `has_long_tieng` (at least one, checked in `clean()`; `audio_labels` for display), `access` (`free`/`vip`), `synopsis`, `poster`, `backdrop`, `trailer` (optional short MP4), `duration_minutes` (movies), `schedule_text` (series, e.g. "Cập nhật thứ 3, 4 hàng tuần"), `search_text` (see §7).
- `Season` → `Episode`: `number`, `title`, `video`, `duration`, `intro_end` (seconds, for "Bỏ qua giới thiệu"), `published_at`.
- "Mới" badge: computed from the latest episode's `published_at` (e.g. within 7 days). Do not store it as a flag.
- `WatchProgress`: `user`, `episode`, `position_seconds`, `updated_at`. Drives the "Xem tiếp" row.
- `MyListItem`: `user`, `movie` ("Danh sách của tôi").
- `Banner`: hero slides, `order`, `is_active`, start/end dates, either a `movie` or sponsored content (`sponsor_name`, `image`, `link`).
- `Plan`: `months`, `price_vnd` (integer, VND has no decimals), `is_best_value`. `Subscription`: `user`, `plan`, `starts_at`, `ends_at`.
- Every model registers in `admin.py` with useful `list_display`, `search_fields` and filters. The admin is the content management tool.

### Views and queries
- Prefer class-based generic views (`ListView`, `DetailView`) and keep views thin. Put query logic in model managers/querysets (e.g. `Movie.objects.free()`, `.series()`, `.new_episodes()`).
- Avoid N+1 queries: use `select_related` / `prefetch_related` on every list (rows, grids, search). Check with Django Debug Toolbar in dev (dev-only dependency, allowed).
- Paginate listings (`paginate_by = 24`).
- Home rows are built in the view as a list of `{title, see_all_url, movies}` and rendered with one `{% include "includes/row.html" %}` loop.
- Cache the home page rows (`cache.get_or_set`, short TTL) but never cache per-user parts (Xem tiếp, VIP state).

### Templates
- Every page extends `base.html`. Reusable pieces live in `templates/includes/` and are used with `{% include ... with ... only %}`.
- Card include takes a movie: `{% include "includes/card.html" with movie=m only %}`.
- Custom filters/tags live in `apps/<app>/templatetags/` (e.g. `vnd`, `ad_slot`, `srcset`).
- Keep template comments minimal and in English. Keep UI text in Vietnamese.

### Settings
```python
LANGUAGE_CODE = "vi"
TIME_ZONE = "Asia/Ho_Chi_Minh"
USE_I18N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True
DATE_FORMAT = "d/m/Y"
AUTH_USER_MODEL = "accounts.User"
```

## 7. Pages and key components

### Header (desktop)
Logo · Trang chủ · Phim bộ · Phim lẻ · Quốc gia ▾ · Thể loại ▾ · Truyền hình · search · bell · avatar · "Nâng cấp VIP" button (`bg-vip text-vip-ink`, hidden for VIP users).
It is sticky, transparent over the hero, and becomes `bg-bg/95 backdrop-blur` after scrolling. The active nav item is marked with `aria-current="page"` on the server (from `request.resolver_match`).

### Home (`catalog/home.html`)
1. Hero carousel (5 slides from `Banner`): backdrop, title, badges, a short synopsis (2 lines), "Xem ngay" + "+ Danh sách". Trailers autoplay only on desktop (mouse, ≥1024px) and fast connections: the backdrop shows first for ~3s, then the trailer fades in (muted, one video at a time, next slide after the trailer ends). Mobile and touch tablets show the static image plus a "Xem trailer" button: the video downloads and plays (with sound) only when tapped, and returns to the image when it ends. Never autoplay video on mobile. One slide may be a sponsored slide (see §9).
2. **Ad slot: billboard** (free tier).
3. Row: Xem tiếp (from `WatchProgress`, progress bar on each card; logged-in users only)
4. Row: Top 10 hôm nay (large outlined numbers beside the posters)
5. Row: Phim bộ mới cập nhật
6. **Ad slot: in-feed** (repeat after every 3–4 rows)
7. Rows: Phim Hàn Quốc · Phim Trung Quốc · Phim Việt chiếu rạp · Anime
8. Sponsored row: "… · Được tài trợ bởi [Brand]"
9. Footer

### Poster card (`includes/card.html`)
- The image uses `loading="lazy"`, has width/height, a fixed aspect ratio, and a skeleton background.
- Top-left: a **VIP** badge (`bg-vip text-vip-ink`) or a **Miễn phí** (free) badge (`bg-brand text-brand-ink`).
- Top-right: **Mới** (red) when a new episode is out.
- Bottom: the audio badge **Vietsub / Thuyết minh / Lồng tiếng**, and **Tập 12/40** for series.
- Hover (desktop): scale 1.05 with a short info overlay. No hover-only information on mobile.

### Title detail (`catalog/detail.html`)
Backdrop, title (Vietnamese + original name), year · country · age rating · number of episodes, audio options, "Xem ngay", "+ Danh sách", share (Zalo, Facebook, copy link).
Series: a season dropdown and a **numbered episode grid** (`grid-cols-6 md:grid-cols-10`). Watched episodes are dimmed (from `WatchProgress`), and the current episode is highlighted.
Schedule line from `schedule_text`.
Desktop right sidebar: **ad slot 300×250** + "Phim tương tự" (similar titles: same genres/country, excluding the current title).
Add Open Graph tags (title, description, backdrop) so links look good when shared on Zalo and Facebook.

### Player (`player/watch.html`)
The custom controls UI sits over an HTML5 `<video>` (use a sample MP4 or a placeholder).
Controls: play/pause, ±10s, timeline, volume, **Vietsub ⇄ Thuyết minh switch**, quality (including "Tiết kiệm dữ liệu", data saver), "Bỏ qua giới thiệu" (skip intro, from `intro_end`), "Tập tiếp theo" with an 8s countdown, and fullscreen.
Fullscreen must be requested on the **player container** (not the `<video>`) so the ad overlays stay visible in fullscreen.
Save progress with a small JSON `POST` (CSRF token included) every ~15s and on pause/leave. VIP-only titles redirect free users to `billing:plans`.

### Search (`catalog/search.html`)
- **Must match text without diacritics.** Store a normalized `search_text` on `Movie` (title + original title), updated in `save()`, and normalize the query the same way:
  ```python
  import unicodedata


  def normalize_vi(text: str) -> str:
      text = text.replace("đ", "d").replace("Đ", "D")
      text = unicodedata.normalize("NFD", text)
      text = "".join(c for c in text if unicodedata.category(c) != "Mn")
      return text.lower().strip()
  ```
  Then filter with `search_text__icontains=normalize_vi(q)`. Keep this even though MySQL's default `utf8mb4_0900_ai_ci` collation is already accent-insensitive: it keeps `đ`/`d` matching and does not depend on collation settings.
- Filters (GET params, so results are shareable): Loại (Phim bộ/Phim lẻ), Quốc gia, Thể loại, Năm, Âm thanh (Vietsub/Thuyết minh).
- Show "Tìm kiếm phổ biến" (popular searches) when the query is empty.

### VIP (`billing/vip.html`)
Plan cards in VND with a `vnd` template filter (`99.000 ₫` format): 1 tháng · 3 tháng · 12 tháng (highlight this one as "Tiết kiệm nhất", best value, with a gold `border-vip` frame). The "Đăng ký" (subscribe) buttons are blue.
Payment methods in this order: **MoMo, ZaloPay, VNPay, bank QR**, then card. UI only. No real payment code and no payment API keys.

### Login (`accounts/login.html`)
Phone number + OTP first, then Zalo, Google, Facebook, and email. UI only: the OTP step can accept a fixed demo code in `DEBUG` mode only. Never send real SMS.

## 8. Content rules (Vietnam-specific)

- "Phim bộ" (series) and "Phim lẻ" (movies) are top-level navigation, not just filters.
- Every title shows its audio type: Vietsub, Thuyết minh, or Lồng tiếng.
- Country categories: Hàn Quốc, Trung Quốc, Việt Nam, Thái Lan, Nhật Bản, Âu Mỹ.
- Dates use the format `dd/mm/yyyy`. Numbers use `vi-VN` formatting (`1.234.567`).
- Use natural Vietnamese UI copy. Glossary:

| Meaning | Use |
|---|---|
| Watch now | Xem ngay |
| My list | Danh sách của tôi |
| Continue watching | Xem tiếp |
| Episode | Tập |
| Next episode | Tập tiếp theo |
| Skip intro | Bỏ qua giới thiệu |
| Advertisement | Quảng cáo |
| Upgrade | Nâng cấp VIP |
| See all | Xem tất cả |
| New | Mới |

## 9. Ad slots

Ads show **only for free users**. A context processor exposes `user_tier` (`"vip"` when the user has an active `Subscription`, otherwise `"free"`), and `base.html` renders `<body data-user="{{ user_tier }}">`.
- For VIP users, **do not render ad markup at all** on the server. Keep the CSS rule `[data-user="vip"] .ad-slot { display:none }` as a safety net only.
- Render every ad with one template tag: `{% ad_slot "ad-billboard" %}` → `includes/ad_slot.html`.

Every ad slot:
- Reserves a **fixed height** so the layout never shifts (CLS = 0).
- Has a small grey "Quảng cáo" label in the top-left corner and a subtle frame (`bg-ad rounded-card border border-line`).
- Has a small "Ẩn quảng cáo" (hide ads) link → `billing:plans`.
- Shows a **house ad** (a VIP promo, `includes/house_ad.html`) when no active creative exists or the creative fails to load.
- Paid creative links use `rel="sponsored noopener"`.

| Slot id | Where | Desktop | Mobile |
|---|---|---|---|
| `ad-billboard` | Under the hero | 970×250 | 320×100 |
| `ad-infeed` | Every 3–4 rows | 728×90 | 320×100 |
| `ad-sidebar` | Title detail page | 300×250 | Inline 300×250 below the synopsis |
| `ad-sponsored-row` | Home row | Poster row with a sponsor label | Same |
| `ad-hero-slide` | Hero carousel | 1 slide of 5 | Same |

Creatives, sponsored rows and sponsored hero slides are managed in the Django admin (with start/end dates and an active flag).

**Player ad states** (inside the player container, so they also work in fullscreen):
1. **Pre-roll**: full-frame video; "Quảng cáo · 1/2 · 0:12" at top-left; "Bỏ qua sau 5s" at bottom-right; a "Xem không quảng cáo → VIP" link.
2. **Mid-roll**: only for movies over 60 minutes. Show a "Quảng cáo sau 5 giây" countdown first, and yellow markers on the timeline.
3. **Pause ad**: a 300×250 panel beside the dimmed video when paused, with a close ✕ button. It hides on play.
4. **End card**: a "Tập tiếp theo" card with a small banner beside it.

Never: pop-ups, pop-unders, redirects, autoplay ads with sound, sticky ads covering the video or controls, or anything over the subtitle area (the bottom 20% of the video).

## 10. Accessibility, performance and security

- Semantic HTML (`header`, `nav`, `main`, `section`, `footer`). One `<h1>` per page. Every row has an `<h2>`.
- All images have Vietnamese `alt` text. Icon-only buttons have `aria-label`.
- Visible focus rings (`focus-visible:ring-2 ring-brand`). Carousels and rows can be used with the keyboard.
- Respect `prefers-reduced-motion`: no autoplay, no scale animations.
- Lazy-load everything below the fold. Serve images as WebP or AVIF with `srcset`. The first hero image is eager with `fetchpriority="high"`.
- Budget: first load under 1.5 MB on mobile. Lighthouse mobile performance ≥ 85.
- Security: CSRF on every form and JSON `POST`; `DEBUG=False`, `SECRET_KEY` and `ALLOWED_HOSTS` from the environment in production; `SECURE_*` and `SESSION_COOKIE_SECURE` settings on in production; validate uploads (image types and size). Always escape user input (never `|safe` on user data).

## 11. Coding conventions

- Python: PEP 8, format with `ruff format`, lint with `ruff check`. Type hints on new functions. Model and variable names in English; UI strings in Vietnamese.
- Tailwind utility classes first. Extract to `@layer components` only when a pattern repeats 3 or more times (e.g., `.btn-primary`, `.badge`, `.ad-slot`).
- Class order: layout → box → typography → color → state (`hover:`, `focus:`) → responsive.
- JS: small modules, no global variables, `type="module"`. Use event delegation for rows and cards. Read server data from `data-*` attributes or `{{ value|json_script:"id" }}`, never by building JS strings in templates.
- Use placeholder images (e.g., `https://placehold.co/400x600`) or generated gradients in `seed_demo`. Never real movie posters or copyrighted artwork.
- Migrations are committed. Never edit an applied migration; add a new one.

## 12. Commands

```bash
docker compose up -d                               # MySQL :3307 (Redis is off in dev)
python -m venv .venv && .venv\Scripts\activate      # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements-dev.txt
copy .env.example .env                             # then set SECRET_KEY
npm install
npm run watch                                      # Tailwind → static/css/output.css
python manage.py migrate
python manage.py seed_demo                         # demo titles, banners, plans, ads (--flush to recreate)
python manage.py createsuperuser
python manage.py runserver 8001                    # port 8000 is used by another project on this machine
python manage.py test                              # needs the MySQL container; run before finishing any task
ruff format . && ruff check .
```

## 13. Definition of done (check before finishing any page)

- [ ] Works at 360px, 768px and 1440px with no horizontal scroll
- [ ] Vietnamese diacritics render correctly and titles don't clip
- [ ] Ad slots reserve space, show the "Quảng cáo" label, and are not rendered for VIP users
- [ ] Player ad overlays still show in fullscreen
- [ ] Search finds "hau due mat troi" → "Hậu Duệ Mặt Trời" (covered by a test)
- [ ] Keyboard navigation and focus states work
- [ ] No N+1 queries on list pages
- [ ] `python manage.py test` passes, and `ruff check` is clean
- [ ] No VieON branding, assets or copy anywhere
