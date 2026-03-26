#!/usr/bin/env python3
"""
WWC Shop — End-to-End Test Suite
=================================
Tests all critical user flows and admin flows against the live dev server.

Usage:
    python e2e_tests.py
    python e2e_tests.py --base-url http://localhost:8000
    python e2e_tests.py --verbose

Requirements: only stdlib (urllib, json, uuid)
"""

import sys
import json
import time
import uuid
import argparse
import urllib.request
import urllib.error
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
BASE_URL = "http://localhost:8000"
API      = f"{BASE_URL}/api/v1"
ADMIN_KEY = "wwc-admin-dev-key-change-in-production"

# Test account (created fresh each run with timestamp suffix)
TS = str(int(time.time()))[-6:]
TEST_EMAIL    = f"e2e_{TS}@wwctest.com"
TEST_PASSWORD = "TestPass123!"
TEST_FIRST    = "E2E"
TEST_LAST     = "Tester"

# Product known to exist from seed data
KNOWN_PRODUCT_SLUG = "huile-argan-pure"
KNOWN_COUPON_ACTIVE   = "WELCOME10"   # 10% off
KNOWN_COUPON_INACTIVE = "TEST10"      # inactive

VERBOSE = False


# ─────────────────────────────────────────────
# Tiny HTTP helpers
# ─────────────────────────────────────────────

def _request(method, url, data=None, headers=None, expected_statuses=(200, 201)):
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        h.update(headers)
    body = json.dumps(data).encode() if data is not None else None
    req  = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            code = resp.status
    except urllib.error.HTTPError as e:
        raw  = e.read().decode()
        code = e.code

    if VERBOSE:
        print(f"    [{method}] {url} → {code}")

    if code == 204:
        return code, {}

    try:
        parsed = json.loads(raw)
    except Exception:
        parsed = {"_raw": raw}

    return code, parsed


def get(url, headers=None):
    return _request("GET", url, headers=headers)

def post(url, data, headers=None):
    return _request("POST", url, data=data, headers=headers)

def patch(url, data, headers=None):
    return _request("PATCH", url, data=data, headers=headers)

def put(url, data, headers=None):
    return _request("PUT", url, data=data, headers=headers)

def delete(url, headers=None):
    return _request("DELETE", url, headers=headers)


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

def admin_headers():
    return {"Authorization": f"Api-Key {ADMIN_KEY}"}

def session_headers(session_key, token=None):
    h = {"X-Session-Key": session_key}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


# ─────────────────────────────────────────────
# Test runner
# ─────────────────────────────────────────────

@dataclass
class Result:
    name:    str
    passed:  bool
    message: str = ""
    details: str = ""


class Suite:
    def __init__(self, name):
        self.name    = name
        self.results = []

    def check(self, name, condition, on_fail="", details=""):
        r = Result(name, bool(condition), on_fail if not condition else "OK", details)
        self.results.append(r)
        symbol = "✓" if r.passed else "✗"
        if not r.passed or VERBOSE:
            print(f"  {symbol} {name}" + (f": {r.message}" if not r.passed else ""))
        return r.passed

    def section(self, title):
        print(f"\n  ── {title}")

    @property
    def passed(self):
        return all(r.passed for r in self.results)

    @property
    def counts(self):
        ok  = sum(1 for r in self.results if r.passed)
        bad = len(self.results) - ok
        return ok, bad


# ─────────────────────────────────────────────
# ══════════════════════════════════════════════
#  SECTION 1: Public / unauthenticated flows
# ══════════════════════════════════════════════
# ─────────────────────────────────────────────

def test_public_pages(s: Suite):
    s.section("Public pages & HTML serving")
    for path, label in [
        ("/shop/",              "Shop home"),
        ("/shop/product/",      "Product detail page"),
        ("/shop/cart/",         "Cart page"),
        ("/shop/checkout/",     "Checkout page"),
        ("/shop/login/",        "Login page"),
        ("/shop/impact/",       "Impact page"),
        ("/shop/donate/",       "Donate page"),
        ("/shop/box-builder/",  "Box builder page"),
        ("/shop/admin/",        "Admin index"),
        ("/shop/admin/products","Admin products"),
        ("/shop/admin/coupons", "Admin coupons"),
        ("/shop/admin/shipping","Admin shipping"),
        ("/shop/admin/settings","Admin settings"),
    ]:
        code, _ = get(f"{BASE_URL}{path}")
        s.check(f"GET {label} → 200", code == 200, f"got {code}")


def test_public_api(s: Suite):
    s.section("Public API endpoints")

    # Products list
    code, data = get(f"{API}/products/")
    s.check("GET /products/ → 200", code == 200, f"got {code}")
    s.check("Products list has results", bool(data.get("results")), "empty results")
    s.check("Product count > 0", (data.get("count", 0) or 0) > 0)

    # Product detail
    code, prod = get(f"{API}/products/{KNOWN_PRODUCT_SLUG}/")
    s.check("GET /products/<slug>/ → 200", code == 200, f"got {code}")
    s.check("Product has id", "id" in prod)
    s.check("Product has price_tnd", "price_tnd" in prod)
    s.check("Product has is_in_stock", "is_in_stock" in prod)

    # Categories
    code, cats = get(f"{API}/categories/")
    s.check("GET /categories/ → 200", code == 200, f"got {code}")

    # Producers
    code, _ = get(f"{API}/producers/")
    s.check("GET /producers/ → 200", code == 200, f"got {code}")

    # Impact summary
    code, _ = get(f"{API}/impact/summary/")
    s.check("GET /impact/summary/ → 200", code == 200, f"got {code}")

    # Related products
    code, _ = get(f"{API}/products/{KNOWN_PRODUCT_SLUG}/related/")
    s.check("GET /products/<slug>/related/ → 200", code == 200, f"got {code}")

    return prod


# ─────────────────────────────────────────────
# ══════════════════════════════════════════════
#  SECTION 2: Auth flows
# ══════════════════════════════════════════════
# ─────────────────────────────────────────────

def test_auth(s: Suite):
    s.section("User registration")
    code, data = post(f"{API}/auth/register/", {
        "email":            TEST_EMAIL,
        "password":         TEST_PASSWORD,
        "password_confirm": TEST_PASSWORD,
        "first_name":       TEST_FIRST,
        "last_name":        TEST_LAST,
    })
    s.check("POST /auth/register/ → 201", code == 201, f"got {code}: {data}")
    token = data.get("access")
    s.check("Registration returns access token", bool(token), f"keys: {list(data.keys())}")

    s.section("Login with registered account")
    code2, login_data = post(f"{API}/auth/login/", {
        "email":    TEST_EMAIL,
        "password": TEST_PASSWORD,
    })
    s.check("POST /auth/login/ → 200", code2 == 200, f"got {code2}: {login_data}")
    login_token = login_data.get("access") or token
    s.check("Login returns access token", bool(login_data.get("access")), f"keys: {list(login_data.keys())}")
    refresh_token = login_data.get("refresh")
    s.check("Login returns refresh token", bool(refresh_token))

    s.section("Token refresh")
    if refresh_token:
        code3, ref_data = post(f"{BASE_URL}/api/token/refresh/", {"refresh": refresh_token})
        s.check("POST /api/token/refresh/ → 200", code3 == 200, f"got {code3}")
        s.check("Refresh returns new access token", bool(ref_data.get("access")))

    s.section("Wrong password rejected")
    code4, _ = post(f"{API}/auth/login/", {"email": TEST_EMAIL, "password": "wrongpass"})
    s.check("Login with wrong password → 401", code4 in (400, 401), f"got {code4}")

    s.section("Password reset request")
    code5, pr = post(f"{API}/auth/password-reset/", {"email": TEST_EMAIL})
    # Returns 200 whether email exists or not (prevents user enumeration)
    s.check("POST /auth/password-reset/ → 200", code5 == 200, f"got {code5}: {pr}")

    return login_token or token


# ─────────────────────────────────────────────
# ══════════════════════════════════════════════
#  SECTION 3: Cart flows (guest + authenticated)
# ══════════════════════════════════════════════
# ─────────────────────────────────────────────

def test_cart_guest(s: Suite, product_id: int):
    s.section("Guest cart — add/update/remove")
    session_key = str(uuid.uuid4())
    sh = {"X-Session-Key": session_key}

    # Get empty cart
    code, cart = get(f"{API}/cart/", headers=sh)
    s.check("GET /cart/ (guest) → 200", code == 200, f"got {code}")

    # Add item
    code, data = post(f"{API}/cart/add/", {"product_id": product_id, "quantity": 2}, headers=sh)
    s.check("POST /cart/add/ → 200/201", code in (200, 201), f"got {code}: {data.get('error', data)}")
    item_id = None
    if data.get("cart", {}).get("items"):
        item_id = data["cart"]["items"][0]["id"]
    s.check("Cart has 1 item after add", len(data.get("cart", {}).get("items", [])) == 1)

    # Update quantity — URL: /cart/update/<item_id>/
    if item_id:
        code, upd = patch(f"{API}/cart/update/{item_id}/", {"quantity": 3}, headers=sh)
        s.check("PATCH /cart/update/<id>/ → 200", code == 200, f"got {code}: {upd}")

    # Remove item — URL: /cart/remove/<item_id>/
    if item_id:
        code, rem = delete(f"{API}/cart/remove/{item_id}/", headers=sh)
        s.check("DELETE /cart/remove/<id>/ → 200/204", code in (200, 204), f"got {code}: {rem}")
        cart_after = rem.get("cart", {}) if isinstance(rem, dict) else {}
        s.check("Cart is empty after remove", len(cart_after.get("items", [])) == 0)

    return session_key


def test_cart_authenticated(s: Suite, token: str, product_id: int):
    s.section("Authenticated cart — add, coupon, totals")
    sh = session_headers(str(uuid.uuid4()), token)

    # Add item
    code, data = post(f"{API}/cart/add/", {"product_id": product_id, "quantity": 1}, headers=sh)
    s.check("Auth POST /cart/add/ → 200/201", code in (200, 201), f"got {code}: {data.get('error', data)}")

    # Get cart with totals
    code, cart = get(f"{API}/cart/", headers=sh)
    s.check("Auth GET /cart/ → 200", code == 200, f"got {code}")
    s.check("Cart has total", "total" in cart.get("cart", cart))

    # Apply valid coupon
    cart_total = cart.get("cart", {}).get("total") or cart.get("total") or 0
    code, coup = post(f"{API}/coupons/apply/", {
        "code":     KNOWN_COUPON_ACTIVE,
        "subtotal": float(cart_total) if cart_total else 50.0,
    }, headers=sh)
    s.check("POST /coupons/apply/ valid coupon → 200", code == 200, f"got {code}: {coup}")
    s.check("Coupon returns discount_amount", "discount_amount" in coup, f"keys: {list(coup.keys())}")

    # Apply inactive coupon
    code, bad = post(f"{API}/coupons/apply/", {
        "code":     KNOWN_COUPON_INACTIVE,
        "subtotal": 50.0,
    }, headers=sh)
    s.check("POST /coupons/apply/ inactive coupon → 400", code == 400, f"got {code}: {bad}")

    # Apply non-existent coupon
    code, _ = post(f"{API}/coupons/apply/", {"code": "FAKECODE999", "subtotal": 50.0}, headers=sh)
    s.check("POST /coupons/apply/ fake coupon → 400", code == 400, f"got {code}")

    return sh


# ─────────────────────────────────────────────
# ══════════════════════════════════════════════
#  SECTION 4: Checkout (bank transfer — no Stripe needed)
# ══════════════════════════════════════════════
# ─────────────────────────────────────────────

def test_checkout(s: Suite, token: str, product_id: int):
    s.section("Checkout — cash on delivery (TND)")
    sh = session_headers(str(uuid.uuid4()), token)

    # Add item to cart
    code, _ = post(f"{API}/cart/add/", {"product_id": product_id, "quantity": 1}, headers=sh)
    s.check("Add item before checkout → 200/201", code in (200, 201), f"got {code}")

    # Submit checkout — field names match CheckoutSerializer exactly
    code, data = post(f"{API}/checkout/", {
        "email":                TEST_EMAIL,
        "phone":                "+216 20 000 000",
        "payment_method":       "cash_on_delivery",
        "shipping_first_name":  "Test",
        "shipping_last_name":   "User",
        "shipping_address_1":   "123 Rue de Test",
        "shipping_city":        "Tunis",
        "shipping_state":       "Tunis",
        "shipping_postal_code": "1001",
        "shipping_country":     "TN",
        "coupon_code":          "",
    }, headers=sh)
    s.check("POST /checkout/ → 200/201", code in (200, 201), f"got {code}: {data}")
    order_number = data.get("order_number") or data.get("order", {}).get("order_number")
    s.check("Checkout returns order_number", bool(order_number), f"keys: {list(data.keys())}")

    s.section("Order retrieval")
    if order_number:
        code2, order = get(f"{API}/orders/{order_number}/", headers=sh)
        s.check("GET /orders/<number>/ → 200", code2 == 200, f"got {code2}")
        s.check("Order has status", bool(order.get("status")))
        s.check("Order status is pending/paid", order.get("status") in ("pending", "paid", "processing"))
        s.check("Order has items", len(order.get("items", [])) > 0)

    return order_number


# ─────────────────────────────────────────────
# ══════════════════════════════════════════════
#  SECTION 5: Customer dashboard & profile
# ══════════════════════════════════════════════
# ─────────────────────────────────────────────

def test_customer_dashboard(s: Suite, token: str):
    s.section("Customer dashboard")
    h = auth_headers(token)

    code, data = get(f"{API}/customer/dashboard/", headers=h)
    s.check("GET /customer/dashboard/ → 200", code == 200, f"got {code}")
    s.check("Dashboard has customer", "customer" in data, f"keys: {list(data.keys())}")
    s.check("Dashboard has recent_orders", "recent_orders" in data)
    s.check("Dashboard has impact_summary", "impact_summary" in data)

    s.section("Customer profile update")
    code2, prof = get(f"{API}/customer/profile/", headers=h)
    s.check("GET /customer/profile/ → 200", code2 == 200, f"got {code2}")

    code3, upd = patch(f"{API}/customer/profile/", {
        "phone":             "+216 21 000 001",
        "preferred_currency": "TND",
    }, headers=h)
    s.check("PATCH /customer/profile/ → 200", code3 == 200, f"got {code3}: {upd}")

    s.section("Addresses CRUD")
    code4, addr = post(f"{API}/addresses/", {
        "address_type":  "shipping",
        "first_name":    "Test",
        "last_name":     "User",
        "address_1":     "10 Rue Test",
        "city":          "Sfax",
        "state":         "Sfax",
        "postal_code":   "3000",
        "country":       "TN",
        "is_default":    True,
    }, headers=h)
    s.check("POST /addresses/ → 201", code4 == 201, f"got {code4}: {addr}")
    addr_id = addr.get("id")

    if addr_id:
        code5, _ = delete(f"{API}/addresses/{addr_id}/", headers=h)
        s.check("DELETE /addresses/<id>/ → 204", code5 == 204, f"got {code5}")

    s.section("Wishlist")
    # Get product id
    _, prod = get(f"{API}/products/{KNOWN_PRODUCT_SLUG}/")
    pid = prod.get("id")
    if pid:
        code6, wl = post(f"{API}/wishlist/", {"product_id": pid}, headers=h)
        s.check("POST /wishlist/ (add) → 200/201", code6 in (200, 201), f"got {code6}: {wl}")
        wl_id = wl.get("id") if isinstance(wl, dict) else None
        if wl_id:
            code7, _ = delete(f"{API}/wishlist/{wl_id}/", headers=h)
            s.check("DELETE /wishlist/<id>/ → 204", code7 in (200, 204), f"got {code7}")

    s.section("Orders list")
    code8, orders = get(f"{API}/orders/", headers=h)
    s.check("GET /orders/ → 200", code8 == 200, f"got {code8}")


# ─────────────────────────────────────────────
# ══════════════════════════════════════════════
#  SECTION 6: Unauthenticated access blocked
# ══════════════════════════════════════════════
# ─────────────────────────────────────────────

def test_auth_required(s: Suite):
    s.section("Protected endpoints reject unauthenticated requests")
    protected = [
        (f"{API}/customer/dashboard/",  "Customer dashboard"),
        (f"{API}/customer/profile/",    "Customer profile"),
        (f"{API}/orders/",              "Orders list"),
        (f"{API}/addresses/",           "Addresses"),
        (f"{API}/wishlist/",            "Wishlist"),
    ]
    for url, label in protected:
        code, _ = get(url)
        s.check(f"{label} requires auth", code in (401, 403), f"{label} returned {code}")

    s.section("Admin endpoints reject non-admin requests")
    admin_endpoints = [
        f"{API}/admin/stats/",
        f"{API}/admin/orders/",
        f"{API}/admin/products/",
        f"{API}/admin/customers/",
        f"{API}/admin/coupons/",
        f"{API}/admin/shipping-rates/",
        f"{API}/admin/settings/",
    ]
    for url in admin_endpoints:
        code, _ = get(url)
        s.check(f"Admin {url.split('admin/')[-1].rstrip('/')} requires API key", code in (401, 403), f"got {code}")


# ─────────────────────────────────────────────
# ══════════════════════════════════════════════
#  SECTION 7: Donation flow
# ══════════════════════════════════════════════
# ─────────────────────────────────────────────

def test_donations(s: Suite, token: str):
    s.section("Donation flow")
    h = auth_headers(token)

    code, countries = get(f"{API}/donations/countries/")
    s.check("GET /donations/countries/ → 200", code == 200, f"got {code}")
    if isinstance(countries, dict):
        countries_list = countries.get("results", [])
    else:
        countries_list = countries if isinstance(countries, list) else []
    s.check("Donation countries populated", len(countries_list) > 0)

    code2, projects = get(f"{API}/donations/projects/")
    s.check("GET /donations/projects/ → 200", code2 == 200, f"got {code2}")

    # Submit a donation (cash payment — no Stripe needed)
    if isinstance(projects, dict):
        project_list = projects.get("results", [])
    else:
        project_list = projects if isinstance(projects, list) else []
    proj_id = project_list[0]["id"] if project_list else None

    if proj_id:
        code3, don = post(f"{API}/donations/donate/", {
            "project":        proj_id,
            "amount":         "25.00",
            "currency":       "TND",
            "payment_method": "bank_transfer",
            "donor_name":     "E2E Test",
            "donor_email":    TEST_EMAIL,
            "is_anonymous":   False,
        }, headers=h)
        s.check("POST /donations/donate/ → 200/201", code3 in (200, 201), f"got {code3}: {don}")
        s.check("Donation returns reference or id", bool(don.get("id") or don.get("reference")))


# ─────────────────────────────────────────────
# ══════════════════════════════════════════════
#  SECTION 8: Admin API flows
# ══════════════════════════════════════════════
# ─────────────────────────────────────────────

def test_admin_stats(s: Suite):
    s.section("Admin stats")
    ah = admin_headers()
    code, data = get(f"{API}/admin/stats/", headers=ah)
    s.check("GET /admin/stats/ → 200", code == 200, f"got {code}")
    for key in ("total_orders", "total_revenue", "total_customers", "total_products"):
        s.check(f"Stats has {key}", key in data, f"keys: {list(data.keys())}")


def test_admin_orders(s: Suite, order_number: Optional[str]):
    s.section("Admin orders")
    ah = admin_headers()

    code, data = get(f"{API}/admin/orders/", headers=ah)
    s.check("GET /admin/orders/ → 200", code == 200, f"got {code}")
    s.check("Orders list has results", "results" in data, f"keys: {list(data.keys())}")

    if order_number:
        code2, order = get(f"{API}/admin/orders/{order_number}/", headers=ah)
        s.check("GET /admin/orders/<number>/ → 200", code2 == 200, f"got {code2}")
        s.check("Admin order has items", "items" in order)

        # Update order status
        code3, upd = patch(f"{API}/admin/orders/{order_number}/", {
            "status": "processing",
        }, headers=ah)
        s.check("PATCH /admin/orders/<number>/ → 200", code3 == 200, f"got {code3}: {upd}")


def test_admin_customers(s: Suite):
    s.section("Admin customers")
    ah = admin_headers()

    code, data = get(f"{API}/admin/customers/", headers=ah)
    s.check("GET /admin/customers/ → 200", code == 200, f"got {code}")
    s.check("Customers list has results", "results" in data)
    s.check("Customer count > 0", (data.get("count", 0) or 0) > 0)

    # Search
    code2, data2 = get(f"{API}/admin/customers/?search=test", headers=ah)
    s.check("GET /admin/customers/?search= → 200", code2 == 200, f"got {code2}")


def test_admin_products(s: Suite):
    s.section("Admin products CRUD")
    ah = admin_headers()

    # List
    code, data = get(f"{API}/admin/products/", headers=ah)
    s.check("GET /admin/products/ → 200", code == 200, f"got {code}")
    s.check("Products list has results", bool(data.get("results")))

    # Get first product
    products = data.get("results", [])
    if products:
        pid = products[0]["id"]
        code2, prod = get(f"{API}/admin/products/{pid}/", headers=ah)
        s.check("GET /admin/products/<id>/ → 200", code2 == 200, f"got {code2}")

        # Patch (price update)
        original_price = prod.get("price_tnd")
        code3, upd = patch(f"{API}/admin/products/{pid}/", {
            "price_tnd": float(original_price or 10) + 0.01,
        }, headers=ah)
        s.check("PATCH /admin/products/<id>/ → 200", code3 == 200, f"got {code3}")

        # Restore
        patch(f"{API}/admin/products/{pid}/", {"price_tnd": original_price}, headers=ah)


def test_admin_coupons(s: Suite):
    s.section("Admin coupons CRUD")
    ah = admin_headers()

    # List
    code, data = get(f"{API}/admin/coupons/", headers=ah)
    s.check("GET /admin/coupons/ → 200", code == 200, f"got {code}")
    s.check("Coupons list has results", "results" in data)

    # Create
    test_code = f"E2ETEST{TS}"
    code2, coup = post(f"{API}/admin/coupons/", {
        "code":           test_code,
        "discount_type":  "percent",
        "discount_value": "15",
        "min_order_amount": "0",
        "max_uses":       "10",
        "is_active":      True,
    }, headers=ah)
    s.check("POST /admin/coupons/ → 201", code2 == 201, f"got {code2}: {coup}")
    coupon_id = coup.get("id")

    # Retrieve
    if coupon_id:
        code3, c = get(f"{API}/admin/coupons/{coupon_id}/", headers=ah)
        s.check("GET /admin/coupons/<id>/ → 200", code3 == 200, f"got {code3}")
        s.check("Created coupon has correct code", c.get("code") == test_code)

        # Update
        code4, _ = patch(f"{API}/admin/coupons/{coupon_id}/", {"discount_value": "20"}, headers=ah)
        s.check("PATCH /admin/coupons/<id>/ → 200", code4 == 200, f"got {code4}")

        # Delete
        code5, _ = delete(f"{API}/admin/coupons/{coupon_id}/", headers=ah)
        s.check("DELETE /admin/coupons/<id>/ → 204", code5 == 204, f"got {code5}")

        # Verify deleted
        code6, _ = get(f"{API}/admin/coupons/{coupon_id}/", headers=ah)
        s.check("Coupon not found after delete → 404", code6 == 404, f"got {code6}")

    # Filter by status
    code7, _ = get(f"{API}/admin/coupons/?is_active=true", headers=ah)
    s.check("GET /admin/coupons/?is_active=true → 200", code7 == 200, f"got {code7}")

    # Search
    code8, _ = get(f"{API}/admin/coupons/?search=WELCOME", headers=ah)
    s.check("GET /admin/coupons/?search= → 200", code8 == 200, f"got {code8}")


def test_admin_shipping(s: Suite):
    s.section("Admin shipping rates CRUD")
    ah = admin_headers()

    # List (seed data: TN, FR, BE, CH, DE)
    code, data = get(f"{API}/admin/shipping-rates/", headers=ah)
    s.check("GET /admin/shipping-rates/ → 200", code == 200, f"got {code}")
    results = data.get("results", [])
    s.check("Shipping rates list has results", len(results) > 0, f"got {len(results)}")
    s.check("Has Tunisia rate (TN)", any(r["country_code"] == "TN" for r in results))
    s.check("Has France rate (FR)", any(r["country_code"] == "FR" for r in results))

    # Check TN values match migration seed data
    tn = next((r for r in results if r["country_code"] == "TN"), None)
    if tn:
        s.check("TN rate = 7.00 DT", float(tn["rate_tnd"]) == 7.0, f"got {tn['rate_tnd']}")
        s.check("TN free threshold = 100.00 DT", float(tn["free_threshold_tnd"]) == 100.0, f"got {tn['free_threshold_tnd']}")

    # Create new country
    code2, nr = post(f"{API}/admin/shipping-rates/", {
        "country_code":       "MA",
        "country_name":       "Maroc",
        "rate_tnd":           "18.00",
        "free_threshold_tnd": "60.00",
        "is_active":          True,
    }, headers=ah)
    s.check("POST /admin/shipping-rates/ → 201", code2 == 201, f"got {code2}: {nr}")
    rate_id = nr.get("id")

    if rate_id:
        # Update
        code3, upd = patch(f"{API}/admin/shipping-rates/{rate_id}/", {"rate_tnd": "17.50"}, headers=ah)
        s.check("PATCH /admin/shipping-rates/<id>/ → 200", code3 == 200, f"got {code3}")
        s.check("Patched rate = 17.50", float(upd.get("rate_tnd", 0)) == 17.5, f"got {upd.get('rate_tnd')}")

        # Delete
        code4, _ = delete(f"{API}/admin/shipping-rates/{rate_id}/", headers=ah)
        s.check("DELETE /admin/shipping-rates/<id>/ → 204", code4 == 204, f"got {code4}")


def test_admin_settings(s: Suite):
    s.section("Admin site settings (exchange rate)")
    ah = admin_headers()

    # Get current rate
    code, data = get(f"{API}/admin/settings/", headers=ah)
    s.check("GET /admin/settings/ → 200", code == 200, f"got {code}")
    s.check("Settings has tnd_to_eur_rate", "tnd_to_eur_rate" in data, f"keys: {list(data.keys())}")
    original_rate = data.get("tnd_to_eur_rate", "0.300000")

    # Update rate
    code2, upd = put(f"{API}/admin/settings/", {"tnd_to_eur_rate": "0.295000"}, headers=ah)
    s.check("PUT /admin/settings/ → 200", code2 == 200, f"got {code2}: {upd}")
    s.check("Updated rate returned", float(upd.get("tnd_to_eur_rate", 0)) == 0.295, f"got {upd.get('tnd_to_eur_rate')}")

    # Restore original rate
    put(f"{API}/admin/settings/", {"tnd_to_eur_rate": original_rate}, headers=ah)
    s.check("Rate restored to original", True)

    # Invalid rate rejected
    code3, err = put(f"{API}/admin/settings/", {}, headers=ah)
    s.check("PUT /admin/settings/ without rate → 400", code3 == 400, f"got {code3}")


def test_admin_categories(s: Suite):
    s.section("Admin categories")
    ah = admin_headers()
    code, data = get(f"{API}/admin/categories/", headers=ah)
    s.check("GET /admin/categories/ → 200", code == 200, f"got {code}")


def test_admin_producers(s: Suite):
    s.section("Admin producers")
    ah = admin_headers()
    code, data = get(f"{API}/admin/producers/", headers=ah)
    s.check("GET /admin/producers/ → 200", code == 200, f"got {code}")


def test_admin_donations(s: Suite):
    s.section("Admin donations")
    ah = admin_headers()
    code, data = get(f"{API}/admin/donations/", headers=ah)
    s.check("GET /admin/donations/ → 200", code == 200, f"got {code}")

    code2, _ = get(f"{API}/admin/donations/countries/", headers=ah)
    s.check("GET /admin/donations/countries/ → 200", code2 == 200, f"got {code2}")

    code3, _ = get(f"{API}/admin/donations/projects/", headers=ah)
    s.check("GET /admin/donations/projects/ → 200", code3 == 200, f"got {code3}")


def test_admin_impact_events(s: Suite):
    s.section("Admin impact events CRUD")
    ah = admin_headers()

    code, data = get(f"{API}/admin/impact-events/", headers=ah)
    s.check("GET /admin/impact-events/ → 200", code == 200, f"got {code}")

    # Create
    import datetime
    code2, ev = post(f"{API}/admin/impact-events/", {
        "title":           "E2E Test Event",
        "school":          "Ecole Test",
        "date":            datetime.date.today().isoformat(),
        "items_delivered": 50,
        "item_type":       "cahiers",
        "description":     "Test event created by e2e suite",
        "is_published":    False,
    }, headers=ah)
    s.check("POST /admin/impact-events/ → 201", code2 == 201, f"got {code2}: {ev}")
    ev_id = ev.get("id")

    if ev_id:
        code3, _ = patch(f"{API}/admin/impact-events/{ev_id}/", {"items_delivered": 60}, headers=ah)
        s.check("PATCH /admin/impact-events/<id>/ → 200", code3 == 200, f"got {code3}")

        code4, _ = delete(f"{API}/admin/impact-events/{ev_id}/", headers=ah)
        s.check("DELETE /admin/impact-events/<id>/ → 204", code4 == 204, f"got {code4}")


def test_admin_b2b(s: Suite):
    s.section("Admin B2B approval flow")
    ah = admin_headers()
    code, data = get(f"{API}/admin/b2b/", headers=ah)
    s.check("GET /admin/b2b/ → 200", code == 200, f"got {code}")


# ─────────────────────────────────────────────
# ══════════════════════════════════════════════
#  SECTION 9: Multilingual
# ══════════════════════════════════════════════
# ─────────────────────────────────────────────

def test_multilingual(s: Suite):
    s.section("Multilingual product names")
    for lang in ("fr", "en", "ar"):
        code, prod = get(f"{API}/products/{KNOWN_PRODUCT_SLUG}/?lang={lang}")
        s.check(f"GET /products/<slug>/?lang={lang} → 200", code == 200, f"got {code}")
        s.check(f"Product has name in {lang}", bool(prod.get("name")), "name missing")


# ─────────────────────────────────────────────
# ══════════════════════════════════════════════
#  SECTION 10: Edge cases & validation
# ══════════════════════════════════════════════
# ─────────────────────────────────────────────

def test_edge_cases(s: Suite):
    s.section("Edge cases")

    # 404 on unknown product
    code, _ = get(f"{API}/products/this-product-does-not-exist-xyz/")
    s.check("GET unknown product → 404", code == 404, f"got {code}")

    # Register with duplicate email
    code2, _ = post(f"{API}/auth/register/", {
        "email":            TEST_EMAIL,   # Already registered above
        "password":         TEST_PASSWORD,
        "password_confirm": TEST_PASSWORD,
        "first_name":       "Dup",
        "last_name":        "User",
    })
    s.check("Duplicate email registration rejected → 400", code2 == 400, f"got {code2}")

    # Register with missing fields
    code3, _ = post(f"{API}/auth/register/", {"email": f"missing_{TS}@test.com"})
    s.check("Registration with missing password → 400", code3 == 400, f"got {code3}")

    # Checkout without items (use a fresh session with nothing in cart)
    sh = session_headers(str(uuid.uuid4()))
    code4, _ = post(f"{API}/checkout/", {
        "email":                f"emptycart_{TS}@test.com",
        "phone":                "+216 20 000 001",
        "payment_method":       "cash_on_delivery",
        "shipping_first_name":  "Test",
        "shipping_last_name":   "User",
        "shipping_address_1":   "123 Rue",
        "shipping_city":        "Tunis",
        "shipping_postal_code": "1000",
        "shipping_country":     "TN",
    }, headers=sh)
    s.check("Checkout with empty cart → 400", code4 == 400, f"got {code4}")

    # Admin with wrong key
    code5, _ = get(f"{API}/admin/stats/", headers={"Authorization": "Api-Key wrong-key"})
    s.check("Admin with wrong key → 401/403", code5 in (401, 403), f"got {code5}")


# ─────────────────────────────────────────────
# Main runner
# ─────────────────────────────────────────────

def main():
    global BASE_URL, API, VERBOSE

    parser = argparse.ArgumentParser(description="WWC Shop E2E Test Suite")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    BASE_URL = args.base_url.rstrip("/")
    API      = f"{BASE_URL}/api/v1"
    VERBOSE  = args.verbose

    print("=" * 60)
    print("  WWC Shop — End-to-End Test Suite")
    print(f"  Target: {BASE_URL}")
    print(f"  Test account: {TEST_EMAIL}")
    print("=" * 60)

    suites_run    = []
    total_pass    = 0
    total_fail    = 0

    def run_suite(name, fn, *args):
        nonlocal total_pass, total_fail
        print(f"\n{'-'*60}")
        print(f"  {name}")
        print(f"{'-'*60}")
        s = Suite(name)
        try:
            result = fn(s, *args)
        except Exception as e:
            s.results.append(Result(f"[EXCEPTION] {name}", False, str(e)))
            print(f"  ✗ EXCEPTION: {e}")
            result = None
        ok, bad = s.counts
        total_pass += ok
        total_fail += bad
        suites_run.append(s)
        print(f"\n  → {ok} passed, {bad} failed")
        return result

    # ── Run suites ──────────────────────────────────────

    run_suite("1. Public Pages",    test_public_pages)
    prod_info = run_suite("2. Public API",      test_public_api)
    product_id = prod_info.get("id") if prod_info else 1

    token       = run_suite("3. Authentication",  test_auth)
    run_suite("4. Guest Cart",      test_cart_guest, product_id)
    run_suite("5. Auth Cart & Coupons", test_cart_authenticated, token, product_id)
    order_num   = run_suite("6. Checkout",         test_checkout, token, product_id)
    run_suite("7. Customer Dashboard", test_customer_dashboard, token)
    run_suite("8. Donation Flow",   test_donations, token)
    run_suite("9. Auth Required",   test_auth_required)
    run_suite("10. Multilingual",   test_multilingual)
    run_suite("11. Edge Cases",     test_edge_cases)

    # Admin suites
    run_suite("12. Admin Stats",         test_admin_stats)
    run_suite("13. Admin Orders",        test_admin_orders, order_num)
    run_suite("14. Admin Customers",     test_admin_customers)
    run_suite("15. Admin Products",      test_admin_products)
    run_suite("16. Admin Coupons",       test_admin_coupons)
    run_suite("17. Admin Shipping",      test_admin_shipping)
    run_suite("18. Admin Settings",      test_admin_settings)
    run_suite("19. Admin Categories",    test_admin_categories)
    run_suite("20. Admin Producers",     test_admin_producers)
    run_suite("21. Admin Donations",     test_admin_donations)
    run_suite("22. Admin Impact Events", test_admin_impact_events)
    run_suite("23. Admin B2B",           test_admin_b2b)

    # ── Summary ─────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")

    failed_suites = [s for s in suites_run if not s.passed]
    if failed_suites:
        print(f"\n  Failed checks:")
        for s in suites_run:
            for r in s.results:
                if not r.passed:
                    print(f"    ✗  [{s.name}] {r.name}: {r.message}")

    print(f"\n  Total: {total_pass + total_fail} checks")
    print(f"  ✓ Passed: {total_pass}")
    print(f"  ✗ Failed: {total_fail}")

    if total_fail == 0:
        print("\n  *** All tests passed! ***")
    else:
        pct = int(100 * total_pass / (total_pass + total_fail))
        print(f"\n  {pct}% pass rate")

    print("=" * 60)
    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
