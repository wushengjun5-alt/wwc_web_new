# WWC Shop - Development Planning Document

**Project**: Wallah We Can E-Commerce Platform
**Last Updated**: 2026-03-19
**Purpose**: Track what has been built, what is pending, and the full development roadmap.

---

## Project Overview

An e-commerce platform for Wallah We Can's GreenSchool initiative. Parents of students work on farms producing goods; every purchase directly supports students with transparent social impact tracking.

**Core tagline**: "Thanks to your purchase of [product], 6 energy bars will be provided to students at Sidi Mechreg"

**Architecture**:
- **Backend**: Django 5 REST API (`/backend`)
- **Frontend**: WordPress plugin (`/wordpress-plugin/wwc-shop`)

---

## What Has Been Done

### Backend - Django REST API

#### Data Models (all with migrations)
- [x] `Producer` - Farm producers (parents of GreenSchool students), with multilingual bio (FR/EN/AR), earnings tracking
- [x] `ProductCategory` - 7 categories (SOINS, NUTRITION, BIEN-ETRE, MAISON, COFFRETS, CADEAUX D'ENTREPRISE, COMPOSER MA BOX), hierarchical, multilingual
- [x] `Product` - Full product model with:
  - Multilingual fields (FR/EN/AR) for name, description, ingredients, usage
  - Dual-currency pricing: TND + EUR
  - B2B wholesale pricing with minimum quantities
  - Product badges: natural, organic, handmade, vegan, cruelty-free
  - Social impact fields: `impact_description`, `impact_school`, `impact_quantity`, `impact_item`
  - Inventory tracking with low-stock threshold and backorder support
  - SEO fields, ratings (calculated from reviews)
- [x] `ProductImage` - Multiple images per product, primary image designation
- [x] `ComposableBox` - "COMPOSER MA BOX" box templates with eligible product M2M
- [x] `Review` - Product reviews with verification and approval
- [x] `Cart` / `CartItem` - Session-based and user-based carts, guest-to-user cart merging, composable box support
- [x] `Order` / `OrderItem` - Full order lifecycle (pending → paid → processing → shipped → delivered → cancelled/refunded), impact captured at order time, UUID primary key, auto-generated order numbers (WWC-YYYYMMDD-XXXX)
- [x] `ImpactEvent` - Real-world impact events funded by purchases (transparency layer)
- [x] `Customer` - B2C/B2B profiles, cumulative impact stats, preferred currency/language, wishlist, saved addresses
- [x] `CustomerAddress` - Multiple saved addresses per customer
- [x] `Wishlist` - Per-customer product wishlist

#### API Views & Endpoints
- [x] Products: list, detail, featured, related, reviews, add-review (CRUD read-only public)
- [x] Categories: list, detail (with menu/parent filters)
- [x] Producers: list, detail, products-by-producer
- [x] Composable Boxes: list, detail
- [x] Cart: get, add, update item, remove item, clear, impact summary, set currency
- [x] Checkout: create order from cart (handles stock deduction, impact calculation)
- [x] Orders: list and detail (authenticated, lookup by order_number or UUID)
- [x] Customer Dashboard: profile, recent orders, wishlist, impact summary
- [x] Customer Profile: view/update
- [x] Customer Addresses: full CRUD
- [x] Wishlist: add/remove/list
- [x] Impact Events: list with filters
- [x] Impact Summary: global stats (total items donated, total orders, recent events)
- [x] Auth: user registration (B2C/B2B with auto-created Customer profile via signal)
- [x] Payments: Stripe PaymentIntent, Stripe Checkout Session, webhook handler, payment status

#### Admin API (WordPress-facing, API key protected)
- [x] `AdminProductViewSet` - Full CRUD for products, image upload, bulk actions
- [x] `AdminCategoryManageViewSet` - Category management
- [x] `AdminProducerManageViewSet` - Producer management
- [x] `AdminCategoryListView`, `AdminProducerListView`, `AdminStatsView`
- [x] `AdminAPIKeyAuthentication` - API key auth for admin endpoints

#### Infrastructure
- [x] Django REST Framework with JWT auth (`djangorestframework-simplejwt`)
- [x] CORS headers configured
- [x] Django Filters for filtering/searching/ordering
- [x] Stripe integration (PaymentIntent + hosted Checkout Session + webhook)
- [x] Settings with `python-decouple` for env config
- [x] Celery + Redis configured in requirements (async email/tasks - not yet implemented)
- [x] Gunicorn for production
- [x] Sample data management commands: `populate_sample_data`, `create_sample_orders`
- [x] Django admin registration for all models

### Frontend - WordPress Plugin

#### Plugin Core (`wwc-shop.php`)
- [x] Singleton plugin class, loads all dependencies
- [x] Enqueues JS/CSS assets with localized AJAX vars and nonce

#### PHP Classes
- [x] `WWC_API_Client` - Full HTTP client for Django API: GET/POST/PATCH/DELETE, WordPress transient caching (5 min) for GET requests, session key for guest carts, JWT token storage in user meta, methods for all API resources
- [x] `WWC_Cart` - AJAX handlers: add, update, remove, get, clear, apply coupon (stub), checkout; price formatting (TND/EUR)
- [x] `WWC_Checkout` - Shipping countries (TN/FR/BE/CH/DE), payment methods, Tunisia governorates, shipping cost calculation with free-shipping thresholds, checkout validation
- [x] `WWC_Product` - Product display helpers (class exists)
- [x] `WWC_Impact` - Impact section display helpers (class exists)

#### Templates (PHP)
- [x] `product-grid.php` - Product listing grid
- [x] `single-product.php` - Single product detail page
- [x] `categories-nav.php` - Category navigation bar
- [x] `cart-page.php` - Full cart page
- [x] `cart-sidebar.php` - Sliding cart sidebar/drawer
- [x] `checkout.php` - Checkout form
- [x] `customer-dashboard.php` - Customer account dashboard with impact stats
- [x] `impact-section.php` - Impact events display

#### WordPress Admin UI
- [x] `dashboard.php` - Admin dashboard overview
- [x] `settings.php` - Plugin settings page (API URL, Stripe keys, currency)
- [x] `class-products-admin.php` - Products admin management class
- [x] `admin/views/products-list.php` - Products list view in WP admin
- [x] `admin/views/product-edit.php` - Product edit form in WP admin

#### Shortcodes (defined in plugin)
- [x] `[wwc_products]` - Product grid
- [x] `[wwc_products category="slug"]` - Category-filtered products
- [x] `[wwc_products featured="true"]` - Featured products
- [x] `[wwc_product slug="..."]` - Single product
- [x] `[wwc_categories]` - Category navigation
- [x] `[wwc_cart]` - Cart page
- [x] `[wwc_checkout]` - Checkout page
- [x] `[wwc_customer_dashboard]` - Customer dashboard
- [x] `[wwc_impact]` - Impact section

#### Assets
- [x] `shop.css` - Main shop stylesheet
- [x] `cart.js` - Cart AJAX operations
- [x] `product.js` - Product page interactions

---

## What Is Missing / Not Yet Done

### CRITICAL - Not Working Without These

#### Backend
- [x] **JWT login endpoint** - Already present in `wwc_shop/urls.py`
- [x] **Django `settings.py` complete** - All env vars wired; `.env` file created
- [x] **Celery task configuration** - `wwc_shop/celery.py` created
- [x] **Email notifications** - `_send_order_confirmation_email()` implemented in `payments.py`
- [x] **Stripe + TND** - Stripe charges in EUR using configurable `TND_TO_EUR_RATE`; customer's bank handles conversion
- [ ] **Coupon/discount system** - stub only, Phase 3

#### WordPress Plugin
- [x] **Shortcode registration** - All shortcodes registered in `wwc-shop.php`
- [x] **AJAX action registration** - All `wp_ajax_*` actions registered
- [x] **Cart session stability** - Fixed: stable `wwc_cart_token` cookie replaces unreliable PHP session ID
- [x] **Checkout JS handler** - Added `handleCheckout` to `cart.js`; form no longer does plain HTML POST
- [x] **Checkout success page** - `templates/checkout-success.php` + `[wwc_checkout_success]` shortcode
- [ ] **Authentication flow** - Phase 2

### HIGH PRIORITY - Important Features Missing

- [ ] **Composable Box builder UI** - The `ComposableBox` model and `[wwc_composer_box]` shortcode are not implemented in templates; no JS box-builder interface exists
- [ ] **Product search UI** - No search bar / search results page template; API supports `search_fields` but no frontend
- [ ] **Product filtering UI** - No filter sidebar (price range, badges, in-stock toggle) in templates
- [ ] **Pagination** - API returns paginated results but product grid template needs pagination controls
- [ ] **Order confirmation page** - No `checkout/success/` page template for post-payment redirect
- [ ] **Order tracking page** - No template for customers to view individual order detail
- [ ] **Password reset flow** - No forgot-password or reset-password endpoints or templates
- [ ] **Email verification** - `email_verified` field exists on Customer model but no verification flow
- [ ] **Stock update on cancel/refund** - When an order is cancelled, stock is not restored
- [ ] **Admin order management** - No Django admin views or API endpoints for managing order status (shipping, tracking number updates)

### MEDIUM PRIORITY - Quality & Completeness

- [ ] **Multilingual support implementation** - Models have `name_fr/en/ar` fields but no language-switching UI or `django-modeltranslation` / WPML integration
- [ ] **Real exchange rate** - TND/EUR conversion is hardcoded at 0.30; need a live rate or configurable rate in settings
- [ ] **Shipping cost calculation in API** - Checkout view hardcodes `shipping_cost = 7.00`; should use country-aware logic matching `WWC_Checkout::calculate_shipping()`
- [ ] **B2B registration flow** - No dedicated B2B signup form or company verification process
- [ ] **Product reviews submission UI** - `add_review` API endpoint exists but no review form in `single-product.php`
- [ ] **Wishlist UI** - Wishlist model and API exist but no wishlist page template or add-to-wishlist button in product templates
- [ ] **Cart count badge in header** - Cart sidebar exists but updating the cart count in the WP header requires theme integration
- [ ] **API error handling in JS** - `cart.js` and `product.js` need robust error messaging UI (toasts/alerts)
- [ ] **CSS responsiveness audit** - `shop.css` needs review for mobile breakpoints

### LOW PRIORITY - Nice to Have

- [ ] **Coupon system** - Full coupon model with discount types (%, fixed), usage limits, expiry dates
- [ ] **Product comparison** - No compare feature
- [ ] **Recently viewed products** - No tracking
- [ ] **Newsletter signup** - `newsletter_subscribed` field exists on Customer but no signup UI
- [ ] **Social sharing** - No share buttons on product pages
- [ ] **SEO meta tags** - Meta title/description fields exist on Product but no output in WP head
- [ ] **Analytics integration** - No Google Analytics / Meta Pixel events for add-to-cart, purchase, etc.
- [ ] **Sitemap** - No product sitemap for SEO
- [ ] **Rate limiting** - No rate limiting on API endpoints

---

## Full Development Roadmap

### Phase 1 - Make It Work (MVP Fixes) ✓ COMPLETE

**Goal**: Get a functioning end-to-end purchase flow working.

| Task | Component | Status | Notes |
|------|-----------|--------|-------|
| Fix JWT URL configuration | Backend | DONE (was already present) | `TokenObtainPairView`/`TokenRefreshView` in `wwc_shop/urls.py` |
| Complete `settings.py` | Backend | DONE (was already complete) | Stripe keys, SITE_URL, MEDIA_ROOT, email all wired |
| Create `celery.py` | Backend | DONE | `wwc_shop/celery.py` + updated `__init__.py` |
| Verify shortcode registration | WP Plugin | DONE (was already present) | All shortcodes registered in `wwc-shop.php` |
| Verify AJAX hook registration | WP Plugin | DONE (was already present) | All `wp_ajax_*` actions registered in `wwc-shop.php` |
| Create checkout success page template | WP Plugin | DONE | `templates/checkout-success.php` + `[wwc_checkout_success]` shortcode |
| TND/Stripe currency policy (Option B) | Backend + WP | DONE | TND → bank_transfer only; EUR → Stripe only; enforced in `CheckoutView` + `payments.py` + `class-cart.php` |
| Fix shipping cost calculation | Backend | DONE | `_calculate_shipping()` in `views.py` replaces hardcoded 7.00; country-aware with free-shipping thresholds |
| Basic order confirmation email | Backend | DONE | `_send_order_confirmation_email()` in `payments.py`; called on Stripe webhook success and on bank transfer order creation |

**Deliverable**: Customer can browse products, add to cart, checkout, pay via Stripe (EUR) or bank transfer (TND), receive confirmation email.

---

### Phase 2 - Complete Core Features

**Goal**: Full shopping experience with account management.

| Task | Component | Notes |
|------|-----------|-------|
| Auth UI (register/login/logout) | WP Plugin | Registration form, login form, integrate with WP user system |
| Password reset flow | Backend + WP | Django email-based reset or WP native |
| Email verification | Backend | Send verification email on registration |
| Composable Box builder | WP Plugin + Backend | Multi-step box builder UI with JS |
| Product search page | WP Plugin | Search bar + results template |
| Product filter sidebar | WP Plugin | Price range, badges, in-stock filters |
| Pagination in product grid | WP Plugin | API pagination support already exists |
| Order detail page | WP Plugin | Template for single order view |
| Wishlist page + buttons | WP Plugin | Template + add/remove AJAX calls |
| Product review form | WP Plugin | Submit review form in product detail |
| Cart count in WP header | WP Plugin | Theme hook or widget |
| Admin order management API | Backend | Endpoints to update order status, add tracking number |

**Deliverable**: Complete customer journey including account, wishlist, reviews, composable boxes.

---

### Phase 3 - Business Features

**Goal**: B2B support, multilingual, coupons, operations.

| Task | Component | Notes |
|------|-----------|-------|
| Multilingual UI switching | WP Plugin | Language switcher, store language preference in session/cookie |
| B2B registration + approval | Backend + WP | Company form, admin approval workflow |
| Coupon system | Backend + WP | `Coupon` model, validation API, apply-coupon UI |
| Real exchange rate | Backend | Daily TND/EUR rate fetch via external API or admin-configurable |
| Stock restore on cancel/refund | Backend | Signal or webhook handler to restore inventory |
| Shipping management in admin | Backend | Configurable rates per country, free-shipping thresholds in DB |
| SEO meta output | WP Plugin | Output `meta_title`/`meta_description` in WP `wp_head` |
| Analytics events | WP Plugin | GTM / GA4 events: view_item, add_to_cart, purchase |

**Deliverable**: Platform ready for B2B customers, multi-language, promotions, and operational management.

---

### Phase 4 - Production Hardening

**Goal**: Production-ready, scalable, and maintainable.

| Task | Component | Notes |
|------|-----------|-------|
| Production deployment setup | Backend | Nginx + Gunicorn config, systemd service |
| PostgreSQL setup | Backend | Migrate from SQLite to PostgreSQL |
| Redis setup | Backend | For Celery task queue and session cache |
| Celery workers for async email | Backend | Move email sending to Celery tasks |
| API rate limiting | Backend | `django-ratelimit` or DRF throttling |
| SSL / HTTPS | Infrastructure | Let's Encrypt cert for api.wallahwecan.org |
| Stripe webhooks in production | Backend | Register endpoint in Stripe dashboard |
| Error monitoring | Backend + WP | Sentry integration |
| Logging | Backend | Structured logs, log rotation |
| Backup strategy | Infrastructure | Daily DB backups, media file backup |
| End-to-end test suite | Backend | pytest with factory_boy for critical flows |
| Load testing | Backend | Ensure API handles concurrent cart/checkout |

**Deliverable**: Production-deployed, monitored, and resilient system.

---

## Key Technical Decisions Needed

1. **TND + Stripe**: Stripe does not support TND. Options:
   - Always charge in EUR (convert display price for Tunisian customers)
   - Use a Tunisia-compatible gateway (Konnect, Flouci, or bank direct) alongside Stripe for EUR
   - Accept bank transfer for TND orders only

2. **Auth strategy**: WP users vs Django users are separate. Options:
   - Keep separate: WP for CMS, Django for shop accounts (current approach, need login UI)
   - Sync: on WP login, auto-login to Django via API
   - Use WP as auth source: pass WP user cookie/token to Django

3. **Media storage**: Product images currently stored on Django server filesystem. For production: use S3-compatible storage (AWS S3 or Cloudflare R2).

4. **Hosting**: Where will `api.wallahwecan.org` run? VPS (DigitalOcean, Hetzner), PaaS (Railway, Render), or shared hosting?

---

## File Structure Reference

```
wwc_web_new/
├── backend/
│   ├── api/
│   │   ├── admin_auth.py          # API key auth for admin endpoints
│   │   ├── admin_serializers.py   # Admin-facing serializers
│   │   ├── admin_views.py         # Admin CRUD views (products, categories, producers)
│   │   ├── payments.py            # Stripe PaymentIntent, Checkout Session, webhook
│   │   ├── serializers.py         # Public API serializers
│   │   ├── urls.py                # All API URL patterns
│   │   └── views.py               # All public API views
│   ├── customers/
│   │   ├── admin.py
│   │   └── models.py              # Customer, CustomerAddress, Wishlist
│   ├── orders/
│   │   ├── admin.py
│   │   ├── models.py              # Cart, CartItem, Order, OrderItem, ImpactEvent
│   │   └── management/commands/create_sample_orders.py
│   ├── products/
│   │   ├── admin.py
│   │   ├── models.py              # Producer, ProductCategory, Product, ProductImage, ComposableBox, Review
│   │   └── management/commands/populate_sample_data.py
│   ├── wwc_shop/
│   │   ├── settings.py            # Django settings
│   │   └── urls.py                # Root URL config
│   ├── .env.example
│   └── requirements.txt
└── wordpress-plugin/wwc-shop/
    ├── admin/
    │   ├── class-products-admin.php
    │   ├── dashboard.php
    │   ├── settings.php
    │   └── views/
    │       ├── product-edit.php
    │       └── products-list.php
    ├── assets/
    │   ├── css/shop.css
    │   └── js/cart.js, product.js
    ├── includes/
    │   ├── class-api-client.php   # HTTP client for Django API
    │   ├── class-cart.php         # Cart AJAX handlers
    │   ├── class-checkout.php     # Checkout logic, shipping, payment methods
    │   ├── class-impact.php       # Impact display helpers
    │   └── class-product.php      # Product display helpers
    ├── templates/
    │   ├── cart-page.php
    │   ├── cart-sidebar.php
    │   ├── categories-nav.php
    │   ├── checkout.php
    │   ├── customer-dashboard.php
    │   ├── impact-section.php
    │   ├── product-grid.php
    │   └── single-product.php
    └── wwc-shop.php               # Main plugin file
```
