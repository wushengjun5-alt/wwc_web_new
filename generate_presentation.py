"""
WWC Shop - Presentation Generator
Generates a PowerPoint presentation for Wallah We Can
covering: what has been built, user guide, and next steps for a third party.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy

# ─── Brand colours ───────────────────────────────────────────────────────────
WWC_ORANGE   = RGBColor(0xE0, 0x44, 0x03)   # #e04403
WWC_NAVY     = RGBColor(0x1C, 0x34, 0x5E)   # #1c345e
WWC_WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
WWC_LIGHT    = RGBColor(0xF5, 0xF5, 0xF5)
WWC_DARK     = RGBColor(0x19, 0x19, 0x19)
WWC_GREY     = RGBColor(0x40, 0x40, 0x40)
WWC_GREEN    = RGBColor(0x28, 0xA7, 0x45)
WWC_AMBER    = RGBColor(0xFF, 0xC1, 0x07)

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

blank_layout = prs.slide_layouts[6]  # completely blank

# ─── Helper utilities ─────────────────────────────────────────────────────────

def add_rect(slide, x, y, w, h, fill_rgb=None, line_rgb=None, line_width_pt=0):
    shape = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.line.fill.background()
    if fill_rgb:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_rgb
    else:
        shape.fill.background()
    if line_rgb:
        shape.line.color.rgb = line_rgb
        shape.line.width = Pt(line_width_pt)
    else:
        shape.line.fill.background()
    return shape

def add_text(slide, text, x, y, w, h,
             font_size=18, bold=False, color=WWC_DARK,
             align=PP_ALIGN.LEFT, italic=False, wrap=True):
    txBox = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    txBox.word_wrap = wrap
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txBox

def add_text_para(tf, text, font_size=14, bold=False, color=WWC_GREY,
                  align=PP_ALIGN.LEFT, space_before=0, indent=False):
    p = tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    if indent:
        p.level = 1
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    return p

def header_band(slide, title, subtitle=None):
    """Navy top band with orange accent bar."""
    add_rect(slide, 0, 0, 13.33, 1.4, fill_rgb=WWC_NAVY)
    add_rect(slide, 0, 1.4, 13.33, 0.08, fill_rgb=WWC_ORANGE)
    add_text(slide, title, 0.4, 0.1, 12, 0.75,
             font_size=32, bold=True, color=WWC_WHITE, align=PP_ALIGN.LEFT)
    if subtitle:
        add_text(slide, subtitle, 0.4, 0.82, 12, 0.5,
                 font_size=15, bold=False, color=RGBColor(0xCC, 0xCC, 0xCC),
                 align=PP_ALIGN.LEFT)

def footer(slide, page_num, total=20):
    add_rect(slide, 0, 7.15, 13.33, 0.35, fill_rgb=WWC_NAVY)
    add_text(slide, "Wallah We Can – GreenSchool E-Commerce Platform  |  Confidential",
             0.3, 7.17, 10, 0.3, font_size=9, color=RGBColor(0xAA, 0xAA, 0xAA))
    add_text(slide, f"{page_num} / {total}",
             12.5, 7.17, 0.8, 0.3, font_size=9, color=RGBColor(0xAA, 0xAA, 0xAA),
             align=PP_ALIGN.RIGHT)

def bullet_box(slide, items, x, y, w, h,
               font_size=13, color=WWC_GREY, title=None, title_color=WWC_NAVY,
               bg=None, border=None, bullet="●"):
    if bg:
        add_rect(slide, x, y, w, h, fill_rgb=bg, line_rgb=border, line_width_pt=1)
    txBox = slide.shapes.add_textbox(Inches(x+0.15), Inches(y+0.12), Inches(w-0.3), Inches(h-0.2))
    txBox.word_wrap = True
    tf = txBox.text_frame
    tf.word_wrap = True
    if title:
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = title
        run.font.size = Pt(font_size + 2)
        run.font.bold = True
        run.font.color.rgb = title_color
    for i, item in enumerate(items):
        p = tf.add_paragraph() if (title or i > 0) else tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = f"{bullet}  {item}"
        run.font.size = Pt(font_size)
        run.font.color.rgb = color
    return txBox

def status_badge(slide, x, y, text, done=True):
    col = WWC_GREEN if done else WWC_AMBER
    add_rect(slide, x, y, 1.1, 0.28, fill_rgb=col)
    add_text(slide, text, x+0.05, y+0.02, 1.0, 0.26,
             font_size=10, bold=True, color=WWC_WHITE, align=PP_ALIGN.CENTER)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — COVER
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)

# Full navy background
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_NAVY)
# Orange accent strip
add_rect(slide, 0, 5.6, 13.33, 0.12, fill_rgb=WWC_ORANGE)
# Decorative circle
add_rect(slide, 10.5, -0.5, 4, 4, fill_rgb=RGBColor(0x22, 0x3E, 0x70))

add_text(slide, "🌿", 0.5, 0.6, 1.2, 1.0, font_size=48, color=WWC_WHITE)
add_text(slide, "Wallah We Can", 0.5, 1.5, 12, 0.9,
         font_size=42, bold=True, color=WWC_WHITE)
add_text(slide, "GreenSchool E-Commerce Platform", 0.5, 2.35, 12, 0.7,
         font_size=26, bold=False, color=WWC_ORANGE)
add_text(slide,
         "Project Status · User Guide · Roadmap for Completion",
         0.5, 3.1, 12, 0.5, font_size=16, color=RGBColor(0xCC, 0xCC, 0xCC))
add_text(slide, "March 2026  |  Confidential", 0.5, 5.9, 8, 0.4,
         font_size=12, color=RGBColor(0x88, 0x88, 0x88))

footer(slide, 1)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — AGENDA / TABLE OF CONTENTS
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "Agenda", "What we will cover in this presentation")

sections = [
    ("01", "The Mission & Platform Overview",    "What WWC is building and why"),
    ("02", "What Has Been Built",                "Complete feature inventory — backend, frontend, admin"),
    ("03", "Customer Journey — User Guide",      "Step-by-step walkthrough for shop visitors"),
    ("04", "Admin & Operations Guide",           "How the WWC team manages the shop"),
    ("05", "What Is Still Missing",             "Honest gap analysis — critical, high, medium priority"),
    ("06", "Roadmap for a Third-Party Developer","Phase 3 & 4 tasks with effort estimates"),
    ("07", "Technical Handover Notes",           "Architecture, credentials, key decisions"),
    ("08", "Recommended Next Steps",             "Immediate actions & partner criteria"),
]

for i, (num, title, sub) in enumerate(sections):
    row = i % 4
    col = i // 4
    x = 0.4 + col * 6.5
    y = 1.7 + row * 1.3

    add_rect(slide, x, y, 6.1, 1.1,
             fill_rgb=WWC_WHITE,
             line_rgb=RGBColor(0xE0, 0xE0, 0xE0), line_width_pt=1)
    add_rect(slide, x, y, 0.55, 1.1, fill_rgb=WWC_ORANGE)
    add_text(slide, num, x+0.04, y+0.28, 0.5, 0.5,
             font_size=16, bold=True, color=WWC_WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, title, x+0.65, y+0.1, 5.3, 0.4,
             font_size=13, bold=True, color=WWC_NAVY)
    add_text(slide, sub, x+0.65, y+0.52, 5.3, 0.4,
             font_size=11, color=WWC_GREY)

footer(slide, 2)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — MISSION & OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "The Mission", "Why this platform exists")

# Quote box
add_rect(slide, 0.4, 1.65, 12.5, 1.1, fill_rgb=WWC_NAVY)
add_rect(slide, 0.4, 1.65, 0.12, 1.1, fill_rgb=WWC_ORANGE)
add_text(slide,
         '"Thanks to your purchase, 6 energy bars will be provided to students at Sidi Mechreg."',
         0.65, 1.75, 12.1, 0.9,
         font_size=18, bold=True, italic=True, color=WWC_WHITE)

# Three pillars
pillars = [
    ("🌱", "GreenSchool Initiative",
     "Parents of students grow and handcraft products on farms. Every sale directly funds school supplies, meals, and energy bars for their children."),
    ("🛒", "The Shop",
     "A full e-commerce platform integrated into the WWC WordPress website. Customers browse, add to cart, and check out — all impact is tracked transparently."),
    ("📊", "Impact Transparency",
     "Every order generates a real impact record: which school benefited, how many items, funded by which purchase. Customers see their personal impact dashboard."),
]
for i, (icon, title, desc) in enumerate(pillars):
    x = 0.4 + i * 4.3
    add_rect(slide, x, 2.95, 4.0, 3.8,
             fill_rgb=WWC_WHITE,
             line_rgb=RGBColor(0xE0, 0xE0, 0xE0), line_width_pt=1)
    add_rect(slide, x, 2.95, 4.0, 0.08, fill_rgb=WWC_ORANGE)
    add_text(slide, icon,  x+1.6, 3.1,  0.8, 0.6, font_size=28, align=PP_ALIGN.CENTER)
    add_text(slide, title, x+0.2, 3.75, 3.6, 0.4,
             font_size=14, bold=True, color=WWC_NAVY, align=PP_ALIGN.CENTER)
    add_text(slide, desc,  x+0.2, 4.25, 3.6, 2.3,
             font_size=12, color=WWC_GREY, align=PP_ALIGN.CENTER)

footer(slide, 3)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — WHAT HAS BEEN BUILT: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "What Has Been Built", "Complete system overview — Phase 1 & 2 complete")

boxes = [
    ("🗄️ Backend API\n(Django 5)",
     ["14 database models with migrations",
      "60+ REST API endpoints",
      "JWT authentication",
      "Stripe payment integration",
      "Order email notifications",
      "Admin API (key-protected)",
      "Stock & impact tracking"],
     WWC_NAVY),
    ("🌐 Customer Frontend\n(Standalone HTML)",
     ["Product catalogue & search",
      "Product detail + reviews",
      "Shopping cart (guest & logged-in)",
      "Full checkout flow",
      "Order history & tracking",
      "Wishlist & account settings",
      "Impact dashboard"],
     WWC_ORANGE),
    ("⚙️ Admin Dashboard\n(Standalone HTML)",
     ["KPI overview (sales, orders, impact)",
      "Product CRUD + image upload",
      "Category & producer management",
      "Order status & tracking updates",
      "Customer list & details",
      "Donation management",
      "Coupon management (UI ready)"],
     RGBColor(0x6F, 0x42, 0xC1)),
    ("🔌 WordPress Plugin\n(PHP)",
     ["Shortcodes for all pages",
      "API client with 5-min cache",
      "Cart AJAX handlers",
      "Checkout & shipping logic",
      "Auth templates (login/register)",
      "Password reset flow",
      "Admin product editing in WP"],
     WWC_GREEN),
]

for i, (title, items, color) in enumerate(boxes):
    col = i % 2
    row = i // 2
    x = 0.3 + col * 6.5
    y = 1.65 + row * 2.75
    add_rect(slide, x, y, 6.2, 2.55,
             fill_rgb=WWC_WHITE,
             line_rgb=RGBColor(0xE0, 0xE0, 0xE0), line_width_pt=1)
    add_rect(slide, x, y, 6.2, 0.45, fill_rgb=color)
    add_text(slide, title, x+0.2, y+0.06, 5.8, 0.38,
             font_size=13, bold=True, color=WWC_WHITE)
    txBox = slide.shapes.add_textbox(Inches(x+0.2), Inches(y+0.55), Inches(5.8), Inches(1.85))
    txBox.word_wrap = True
    tf = txBox.text_frame
    tf.word_wrap = True
    for j, item in enumerate(items):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        run = p.add_run()
        run.text = f"✓  {item}"
        run.font.size = Pt(11)
        run.font.color.rgb = WWC_GREY

footer(slide, 4)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — WHAT HAS BEEN BUILT: DATA MODEL
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "Data Architecture", "14 database models — all production-ready with migrations")

groups = [
    ("Products", WWC_NAVY,
     ["Producer — farm producers with bio (FR/EN/AR)",
      "ProductCategory — 7 categories, hierarchical",
      "Product — multilingual, dual-currency (TND+EUR), badges, SEO",
      "ProductImage — multiple images per product",
      "ComposableBox — 'Build My Box' bundles",
      "Review — star ratings, moderated"]),
    ("Orders & Cart", WWC_ORANGE,
     ["Cart / CartItem — guest & logged-in, box support",
      "Order — full lifecycle: pending→paid→shipped→delivered",
      "OrderItem — snapshot of product+price at order time",
      "ImpactEvent — real-world events funded by orders",
      "PendingCheckout — Stripe pre-payment snapshot",
      "Coupon — discount codes (model + API ready)"]),
    ("Customers", WWC_GREEN,
     ["Customer — B2C & B2B profiles, impact stats",
      "CustomerAddress — multiple saved addresses",
      "Wishlist — per-customer product wishlist",
      "  ",
      "  ",
      "  "]),
]

for i, (group, color, items) in enumerate(groups):
    x = 0.3 + i * 4.35
    add_rect(slide, x, 1.65, 4.1, 5.35,
             fill_rgb=WWC_WHITE,
             line_rgb=RGBColor(0xE0, 0xE0, 0xE0), line_width_pt=1)
    add_rect(slide, x, 1.65, 4.1, 0.42, fill_rgb=color)
    add_text(slide, group, x+0.15, y+0.08 if (y:=1.65) else 0,
             3.8, 0.32, font_size=14, bold=True, color=WWC_WHITE)
    txBox = slide.shapes.add_textbox(Inches(x+0.15), Inches(2.18), Inches(3.8), Inches(4.6))
    txBox.word_wrap = True
    tf = txBox.text_frame
    tf.word_wrap = True
    for j, item in enumerate(items):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        p.space_before = Pt(4)
        run = p.add_run()
        run.text = item if item.strip() == "" else f"📋  {item}"
        run.font.size = Pt(11.5)
        run.font.color.rgb = WWC_GREY

footer(slide, 5)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — USER GUIDE: CUSTOMER JOURNEY MAP
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "Customer Journey", "The complete shopping experience — step by step")

steps = [
    ("1", "Browse",      "🛍️", "Visit shop\nExplore by\ncategory,\nsearch or\nfeatured"),
    ("2", "Product",     "📦", "View product\ndetails, images,\ningredients,\nimpact info,\nreviews"),
    ("3", "Cart",        "🛒", "Add to cart\nUpdate qty\nApply coupon\nSee live\nimpact total"),
    ("4", "Checkout",    "📝", "Enter address\n(saved or new)\nChoose payment\nCredit card\nor COD"),
    ("5", "Payment",     "💳", "Stripe secure\npayment (EUR)\nor cash on\ndelivery (TND)"),
    ("6", "Confirmation","✅", "Order email\nconfirmation\nOrder number\nTracking link"),
    ("7", "My Account",  "👤", "View orders\nTrack shipping\nSee my impact\nManage wishlist"),
]

arrow_col = RGBColor(0xCC, 0xCC, 0xCC)
step_w = 1.7
gap = 0.12
start_x = 0.25

for i, (num, label, icon, desc) in enumerate(steps):
    x = start_x + i * (step_w + gap)
    # Box
    add_rect(slide, x, 1.7, step_w, 4.9,
             fill_rgb=WWC_WHITE,
             line_rgb=RGBColor(0xDC, 0xDC, 0xDC), line_width_pt=1)
    add_rect(slide, x, 1.7, step_w, 0.38, fill_rgb=WWC_NAVY)
    # Step number
    add_text(slide, f"STEP {num}", x+0.05, 1.72, step_w-0.1, 0.34,
             font_size=11, bold=True, color=WWC_ORANGE, align=PP_ALIGN.CENTER)
    # Icon
    add_text(slide, icon, x+0.5, 2.2, 0.7, 0.6,
             font_size=24, align=PP_ALIGN.CENTER)
    # Label
    add_text(slide, label, x+0.05, 2.88, step_w-0.1, 0.38,
             font_size=13, bold=True, color=WWC_NAVY, align=PP_ALIGN.CENTER)
    # Description
    add_text(slide, desc, x+0.1, 3.35, step_w-0.2, 3.1,
             font_size=10.5, color=WWC_GREY, align=PP_ALIGN.CENTER)
    # Arrow (not after last)
    if i < len(steps) - 1:
        ax = x + step_w + 0.01
        add_text(slide, "›", ax, 3.5, 0.12, 0.4,
                 font_size=18, bold=True, color=arrow_col, align=PP_ALIGN.CENTER)

# Guest vs logged-in note
add_rect(slide, 0.25, 6.78, 12.8, 0.42,
         fill_rgb=RGBColor(0xE8, 0xF4, 0xEC),
         line_rgb=WWC_GREEN, line_width_pt=1)
add_text(slide,
         "✓  Guest checkout supported — no account required.  "
         "✓  Logged-in customers get saved addresses, order history & personal impact dashboard.",
         0.4, 6.8, 12.5, 0.38, font_size=10.5, color=WWC_GREEN)

footer(slide, 6)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — USER GUIDE: ACCOUNT & IMPACT DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "Customer Account", "Everything a registered customer can do in 'Mon Compte'")

left_features = [
    ("📊", "Impact Dashboard",
     "Personalised banner showing total purchases, total orders, and a breakdown of how many items were donated to which schools — updated after every order."),
    ("📦", "Order History",
     "Full list of all past orders with status badge (pending / paid / shipped / delivered). Click any order to see full details: items, prices, shipping address, billing address, and tracking number."),
    ("❤️", "Wishlist",
     "Save products to a personal wishlist directly from the product page. View and manage saved items in the account area."),
]

right_features = [
    ("⚙️", "Account Settings",
     "Update personal info (name, phone), default shipping address, change password, set preferred currency (TND / EUR) and language (FR / EN / AR), manage newsletter subscription."),
    ("🧾", "Billing Address",
     "B2B customers can save a separate billing address (company name, tax ID) that auto-fills at checkout — no need to re-type every order."),
    ("🔐", "Password Reset",
     "Full forgot-password flow via email link. Secure token-based reset — works independently of WordPress login."),
]

for i, (icon, title, desc) in enumerate(left_features):
    y = 1.7 + i * 1.75
    add_rect(slide, 0.3, y, 6.0, 1.55,
             fill_rgb=WWC_WHITE, line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
    add_rect(slide, 0.3, y, 0.08, 1.55, fill_rgb=WWC_ORANGE)
    add_text(slide, icon,  0.5, y+0.45, 0.65, 0.6, font_size=22)
    add_text(slide, title, 1.2, y+0.12, 5.0, 0.38, font_size=13, bold=True, color=WWC_NAVY)
    add_text(slide, desc,  1.2, y+0.55, 5.0, 0.9,  font_size=11, color=WWC_GREY)

for i, (icon, title, desc) in enumerate(right_features):
    y = 1.7 + i * 1.75
    add_rect(slide, 6.9, y, 6.1, 1.55,
             fill_rgb=WWC_WHITE, line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
    add_rect(slide, 6.9, y, 0.08, 1.55, fill_rgb=WWC_NAVY)
    add_text(slide, icon,  7.1, y+0.45, 0.65, 0.6, font_size=22)
    add_text(slide, title, 7.8, y+0.12, 5.0, 0.38, font_size=13, bold=True, color=WWC_NAVY)
    add_text(slide, desc,  7.8, y+0.55, 5.0, 0.9,  font_size=11, color=WWC_GREY)

footer(slide, 7)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — USER GUIDE: CHECKOUT DEEP DIVE
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "Checkout — In Detail", "Smart address management + dual payment method support")

# Left: address flow
add_rect(slide, 0.3, 1.65, 6.0, 5.35,
         fill_rgb=WWC_WHITE, line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
add_rect(slide, 0.3, 1.65, 6.0, 0.4, fill_rgb=WWC_NAVY)
add_text(slide, "📦 Address Management", 0.5, 1.68, 5.7, 0.36,
         font_size=13, bold=True, color=WWC_WHITE)

addr_points = [
    "Logged-in users with a saved address see it displayed instantly — no re-typing.",
    "Option tile 1: 'Use this address' — one click to confirm.",
    "Option tile 2: 'Use a different address' — expands an inline form.",
    "New address can be saved as default with a single checkbox tick.",
    "Guest users fill in the address form directly (no account needed).",
    "",
    "🧾  Billing Address Section:",
    "Option tile 1: 'Same as shipping' — default, zero friction.",
    "Option tile 2: 'Different billing address' — expands full billing form with company name field.",
    "B2B customers enter company name + address for proper invoicing.",
    "Billing address is saved to every order for later reference.",
]
txBox = slide.shapes.add_textbox(Inches(0.5), Inches(2.18), Inches(5.7), Inches(4.6))
txBox.word_wrap = True
tf = txBox.text_frame
tf.word_wrap = True
for j, pt in enumerate(addr_points):
    p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
    p.space_before = Pt(3)
    run = p.add_run()
    run.text = pt if (pt.startswith("🧾") or pt == "") else f"•  {pt}"
    run.font.size = Pt(11)
    run.font.bold = pt.startswith("🧾")
    run.font.color.rgb = WWC_NAVY if pt.startswith("🧾") else WWC_GREY

# Right: payment
add_rect(slide, 6.9, 1.65, 6.1, 5.35,
         fill_rgb=WWC_WHITE, line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
add_rect(slide, 6.9, 1.65, 6.1, 0.4, fill_rgb=WWC_ORANGE)
add_text(slide, "💳 Payment Methods", 7.1, 1.68, 5.7, 0.36,
         font_size=13, bold=True, color=WWC_WHITE)

pay_sections = [
    ("💳  Card Payment (Stripe)", WWC_NAVY,
     ["Secure hosted Stripe Checkout page.",
      "Supports Visa, Mastercard, Apple Pay.",
      "Payment in EUR (customers' banks handle TND conversion automatically).",
      "Order created only after webhook confirms payment — no risk of unpaid orders."]),
    ("💵  Cash on Delivery", WWC_GREEN,
     ["Available for Tunisian customers.",
      "Order placed immediately, payment at door.",
      "Order confirmation email sent at checkout.",
      "Status automatically set to 'Paid'."]),
    ("🎁  Gift Packaging", WWC_ORANGE,
     ["Optional add-on at checkout.",
      "+5 DT / +2 € — added to order total.",
      "Noted on order for packing team."]),
]
ty = 2.2
for (ptitle, pcolor, plist) in pay_sections:
    add_text(slide, ptitle, 7.1, ty, 5.7, 0.32, font_size=12, bold=True, color=pcolor)
    ty += 0.35
    for pt in plist:
        add_text(slide, f"•  {pt}", 7.3, ty, 5.5, 0.28, font_size=10.5, color=WWC_GREY)
        ty += 0.3
    ty += 0.1

footer(slide, 8)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — ADMIN GUIDE: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "Admin Dashboard — Overview", "Everything the WWC team can manage without touching code")

admin_modules = [
    ("📊", "Dashboard KPIs",
     ["Total revenue (TND & EUR)",
      "Orders today / this week / this month",
      "Items donated to students",
      "Top-selling products",
      "Low stock alerts",
      "API health status banner"]),
    ("📦", "Products",
     ["Add / edit / delete products",
      "Upload multiple product images",
      "Set price in TND and EUR",
      "Set B2B wholesale price",
      "Define social impact (school, qty, item)",
      "Manage stock levels",
      "Set badges: organic, handmade, vegan…"]),
    ("🏷️", "Categories",
     ["Create / rename / reorder categories",
      "7 default categories (SOINS, NUTRITION…)",
      "Hierarchical (parent / child)",
      "Multilingual labels (FR/EN/AR)"]),
    ("👨‍🌾", "Producers",
     ["Add / edit producer profiles",
      "Upload producer photo",
      "Write bio in French, English, Arabic",
      "Track total products sold & earnings"]),
    ("📋", "Orders",
     ["View all orders with status filter",
      "Search by order number or customer",
      "Update status: paid→processing→shipped",
      "Enter tracking number",
      "System sends shipping email automatically"]),
    ("👥", "Customers",
     ["View all registered customers",
      "See B2C vs B2B type",
      "View order history per customer",
      "See cumulative impact per customer"]),
]

for i, (icon, title, items) in enumerate(admin_modules):
    col = i % 3
    row = i // 3
    x = 0.3 + col * 4.35
    y = 1.65 + row * 2.75
    add_rect(slide, x, y, 4.1, 2.55,
             fill_rgb=WWC_WHITE, line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
    add_rect(slide, x, y, 4.1, 0.42, fill_rgb=WWC_NAVY)
    add_text(slide, f"{icon}  {title}", x+0.15, y+0.06, 3.8, 0.36,
             font_size=12, bold=True, color=WWC_WHITE)
    txBox = slide.shapes.add_textbox(Inches(x+0.15), Inches(y+0.55), Inches(3.8), Inches(1.85))
    txBox.word_wrap = True
    tf = txBox.text_frame
    tf.word_wrap = True
    for j, item in enumerate(items):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        run = p.add_run()
        run.text = f"✓  {item}"
        run.font.size = Pt(10.5)
        run.font.color.rgb = WWC_GREY

footer(slide, 9)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — ADMIN GUIDE: ORDER MANAGEMENT WORKFLOW
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "Order Management Workflow", "How a WWC team member processes an order from start to finish")

statuses = [
    ("PENDING",     WWC_AMBER,              "Order placed\n(bank transfer\nor stripe\nnot yet\nconfirmed)"),
    ("PAID",        WWC_GREEN,              "Payment\nconfirmed\n(Stripe webhook\nor COD\nmarked paid)"),
    ("PROCESSING",  RGBColor(0,123,255),    "Admin confirms\nstock, prepares\nshipment\n(set in admin\ndashboard)"),
    ("SHIPPED",     RGBColor(111,66,193),   "Admin enters\ntracking\nnumber —\nemail sent\nautomatically"),
    ("DELIVERED",   RGBColor(32,201,151),   "Customer\nconfirms\nreceipt\n(or admin\nmarks done)"),
    ("CANCELLED /\nREFUNDED",
                    RGBColor(220,53,69),    "Stock\nautomatically\nrestored —\nno manual\nadjustment"),
]

for i, (label, color, desc) in enumerate(statuses):
    x = 0.3 + i * 2.16
    add_rect(slide, x, 1.7, 2.0, 0.52, fill_rgb=color)
    add_text(slide, label, x+0.05, 1.74, 1.9, 0.44,
             font_size=10, bold=True, color=WWC_WHITE, align=PP_ALIGN.CENTER)
    add_rect(slide, x+0.95, 2.22, 0.1, 0.35, fill_rgb=RGBColor(0xCC,0xCC,0xCC))
    add_rect(slide, x, 2.57, 2.0, 4.05,
             fill_rgb=WWC_WHITE, line_rgb=color, line_width_pt=2)
    add_text(slide, desc, x+0.1, 2.7, 1.8, 3.8,
             font_size=11, color=WWC_GREY, align=PP_ALIGN.CENTER)

# Automation notes
add_rect(slide, 0.3, 6.8, 12.7, 0.45,
         fill_rgb=RGBColor(0xE8,0xF4,0xEC), line_rgb=WWC_GREEN, line_width_pt=1)
add_text(slide,
         "🤖  Automated:  Stripe webhook creates order on payment ·  Shipping email on status→Shipped  ·  Stock restored on Cancel/Refund",
         0.5, 6.82, 12.4, 0.38, font_size=10.5, color=WWC_GREEN)

footer(slide, 10)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — ADMIN GUIDE: IMPACT & DONATIONS
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "Impact & Donations", "The social transparency engine at the heart of WWC")

# Left: how impact works
add_rect(slide, 0.3, 1.65, 6.0, 5.35,
         fill_rgb=WWC_WHITE, line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
add_rect(slide, 0.3, 1.65, 6.0, 0.4, fill_rgb=WWC_NAVY)
add_text(slide, "How Impact Is Calculated", 0.5, 1.68, 5.7, 0.36,
         font_size=13, bold=True, color=WWC_WHITE)

impact_flow = [
    "1️⃣  Admin sets impact on each product:",
    "      → School name (e.g. Sidi Mechreg)",
    "      → Impact item (e.g. 'energy bars')",
    "      → Quantity per unit sold (e.g. 6)",
    "",
    "2️⃣  Customer buys 2 units of that product:",
    "      → 12 energy bars recorded for Sidi Mechreg",
    "",
    "3️⃣  Impact is captured at order time:",
    "      → Stored permanently on the Order record",
    "      → Cannot be changed retroactively",
    "",
    "4️⃣  Customer sees their personal total:",
    "      → 'You have donated 48 energy bars'",
    "      → Breakdown by school on their dashboard",
    "",
    "5️⃣  Admin can log real Impact Events:",
    "      → 'March 2026: 200 bars delivered to Sidi Mechreg'",
    "      → Visible on public Impact page",
]
txBox = slide.shapes.add_textbox(Inches(0.5), Inches(2.15), Inches(5.7), Inches(4.65))
txBox.word_wrap = True
tf = txBox.text_frame
tf.word_wrap = True
for j, pt in enumerate(impact_flow):
    p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
    p.space_before = Pt(2)
    run = p.add_run()
    run.text = pt
    run.font.size = Pt(11)
    run.font.bold = pt.startswith(("1️⃣","2️⃣","3️⃣","4️⃣","5️⃣"))
    run.font.color.rgb = WWC_NAVY if run.font.bold else WWC_GREY

# Right: donations module
add_rect(slide, 6.9, 1.65, 6.1, 5.35,
         fill_rgb=WWC_WHITE, line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
add_rect(slide, 6.9, 1.65, 6.1, 0.4, fill_rgb=WWC_ORANGE)
add_text(slide, "Donations Module", 7.1, 1.68, 5.7, 0.36,
         font_size=13, bold=True, color=WWC_WHITE)

don_points = [
    ("Separate donation flow", "Customers can make direct monetary donations to specific school projects — independent of purchases."),
    ("Country & project image", "Each donation project has a country flag, project description, and image shown on the donation page."),
    ("User attribution", "Logged-in donors are linked to their donation for history tracking."),
    ("Admin management", "Donation admin panel: view all donations, amounts, donors, dates, and project breakdown."),
    ("Public impact page", "A public-facing Impact page shows cumulative donations and real events — builds trust and transparency."),
]
dy = 2.2
for (dtitle, ddesc) in don_points:
    add_rect(slide, 7.05, dy, 5.75, 0.95,
             fill_rgb=RGBColor(0xFF,0xF8,0xF0), line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
    add_text(slide, dtitle, 7.2, dy+0.06, 5.4, 0.3, font_size=11, bold=True, color=WWC_NAVY)
    add_text(slide, ddesc, 7.2, dy+0.4, 5.4, 0.45, font_size=10.5, color=WWC_GREY)
    dy += 1.05

footer(slide, 11)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — WHAT IS STILL MISSING (GAP ANALYSIS)
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "Gap Analysis", "Honest assessment of what still needs to be built")

priorities = [
    ("🔴  PHASE 2 — Remaining", RGBColor(220,53,69), RGBColor(255,235,235), [
        "Composable Box builder UI  —  The 'Build My Box' feature: multi-step JS interface to assemble a custom box",
        "Email verification  —  Send verification email on registration; gate certain features behind verified status",
        "Cart count badge in WordPress header  —  Requires theme integration hook",
        "B2B billing address saved in account  —  Save default billing address for company customers",
    ]),
    ("🟡  PHASE 3 — Business Features", RGBColor(255,152,0), RGBColor(255,248,225), [
        "Multilingual UI switching  —  Language switcher widget; serve FR/EN/AR product content based on user preference",
        "B2B registration & approval  —  Dedicated company signup form + admin approval workflow",
        "Coupon system  —  Backend model is ready; need admin UI to create codes + frontend apply-coupon logic",
        "Live TND/EUR exchange rate  —  Currently hardcoded at 0.30; need daily fetch from exchange rate API",
        "SEO meta output  —  Output product meta title/description into WordPress <head>",
        "Google Analytics / Meta Pixel events  —  Track add_to_cart, purchase, view_item",
    ]),
    ("🔵  PHASE 4 — Production Hardening", RGBColor(0,123,255), RGBColor(232,244,255), [
        "PostgreSQL migration  —  Move from SQLite (dev) to PostgreSQL (production)",
        "Nginx + Gunicorn production config  —  Proper web server setup for api.wallahwecan.org",
        "SSL certificate  —  HTTPS for the API domain",
        "Media storage on S3 / Cloudflare R2  —  Product images currently on server disk",
        "Celery async email workers  —  Emails currently sent synchronously; move to background queue",
        "Error monitoring (Sentry)  —  Catch and alert on production errors",
        "Automated backups  —  Daily database + media file backups",
    ]),
]

y = 1.65
for (ptitle, pcolor, pbg, pitems) in priorities:
    h = 0.35 + len(pitems) * 0.42
    add_rect(slide, 0.3, y, 12.7, h,
             fill_rgb=pbg, line_rgb=pcolor, line_width_pt=1.5)
    add_text(slide, ptitle, 0.5, y+0.04, 12.2, 0.32,
             font_size=12, bold=True, color=pcolor)
    for j, item in enumerate(pitems):
        add_text(slide, f"•  {item}", 0.6, y+0.38+j*0.42, 12.1, 0.38,
                 font_size=10.5, color=WWC_DARK)
    y += h + 0.08

footer(slide, 12)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — ROADMAP: PHASE 3 EFFORT TABLE
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "Roadmap — Phase 3 & 4", "Work breakdown for a third-party developer")

# Table header
cols = [5.5, 1.4, 1.4, 1.4, 2.8]
col_x = [0.3, 5.85, 7.3, 8.75, 10.2]
headers = ["Task", "Component", "Effort", "Priority", "Notes"]

add_rect(slide, 0.3, 1.65, 12.7, 0.42, fill_rgb=WWC_NAVY)
for i, (hdr, cx, cw) in enumerate(zip(headers, col_x, cols)):
    add_text(slide, hdr, cx+0.05, 1.67, cw-0.1, 0.38,
             font_size=11, bold=True, color=WWC_WHITE, align=PP_ALIGN.CENTER)

rows = [
    # (task, component, effort, priority, notes)
    ("Multilingual UI switching",        "Frontend + WP",  "3 days",  "HIGH",   "FR/EN/AR toggle, store in cookie"),
    ("B2B registration + approval",      "Backend + WP",   "4 days",  "HIGH",   "Company form, admin approval email"),
    ("Coupon system — admin UI",         "Frontend",       "2 days",  "HIGH",   "Backend model already done"),
    ("Email verification on register",   "Backend",        "1 day",   "MED",    "Send token on signup, gate features"),
    ("Composable Box builder UI",        "Frontend + JS",  "5 days",  "HIGH",   "Multi-step selector, preview"),
    ("Live TND/EUR rate",                "Backend",        "0.5 day", "MED",    "Daily cron job, admin override"),
    ("SEO meta tags in WP head",         "WP Plugin",      "0.5 day", "MED",    "Output meta_title/description"),
    ("GA4 / Meta Pixel events",          "Frontend JS",    "2 days",  "MED",    "view_item, add_to_cart, purchase"),
    ("B2B billing address in account",   "Backend + FE",   "1.5 days","MED",    "CustomerAddress, settings page"),
    ("--- PHASE 4 ---",                  "",               "",        "",       ""),
    ("PostgreSQL migration",             "Backend",        "1 day",   "CRIT",   "Change DB engine, run migrations"),
    ("Nginx + Gunicorn + systemd",       "Infrastructure", "1 day",   "CRIT",   "Server config for production"),
    ("SSL certificate (Let's Encrypt)",  "Infrastructure", "0.5 day", "CRIT",   "Auto-renew with certbot"),
    ("S3 media storage",                 "Backend",        "1 day",   "CRIT",   "django-storages + Cloudflare R2"),
    ("Celery async email workers",       "Backend",        "1 day",   "HIGH",   "Redis already in requirements"),
    ("Sentry error monitoring",          "Backend + FE",   "0.5 day", "HIGH",   "Add DSN, test alerts"),
    ("Automated DB backups",             "Infrastructure", "0.5 day", "HIGH",   "Cron + S3 offsite backup"),
    ("Stripe webhook registration",      "Backend + Stripe","0.5 day","CRIT",   "Register endpoint in Stripe dashboard"),
]

effort_map = {"CRIT": RGBColor(220,53,69), "HIGH": WWC_ORANGE, "MED": WWC_GREEN}
ty = 2.07
for i, row in enumerate(rows):
    if row[0].startswith("---"):
        add_rect(slide, 0.3, ty, 12.7, 0.32, fill_rgb=RGBColor(0xE8,0xE8,0xE8))
        add_text(slide, "PHASE 4 — Production Hardening",
                 0.5, ty+0.04, 12.2, 0.28, font_size=11, bold=True, color=WWC_NAVY)
        ty += 0.32
        continue
    bg = WWC_WHITE if i % 2 == 0 else RGBColor(0xFA,0xFA,0xFA)
    add_rect(slide, 0.3, ty, 12.7, 0.38, fill_rgb=bg,
             line_rgb=RGBColor(0xEE,0xEE,0xEE), line_width_pt=0.5)
    task, comp, effort, prio, notes = row
    data = [task, comp, effort, prio, notes]
    for j, (val, cx, cw) in enumerate(zip(data, col_x, cols)):
        if j == 3 and val:
            pc = effort_map.get(val, WWC_GREY)
            add_rect(slide, cx+0.1, ty+0.06, cw-0.2, 0.26, fill_rgb=pc)
            add_text(slide, val, cx+0.1, ty+0.07, cw-0.2, 0.24,
                     font_size=9, bold=True, color=WWC_WHITE, align=PP_ALIGN.CENTER)
        else:
            add_text(slide, val, cx+0.05, ty+0.05, cw-0.1, 0.3,
                     font_size=10, color=WWC_DARK,
                     align=PP_ALIGN.CENTER if j in (1,2) else PP_ALIGN.LEFT)
    ty += 0.38

footer(slide, 13)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 14 — TECHNICAL HANDOVER: ARCHITECTURE
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "Technical Architecture", "What a new developer needs to understand on Day 1")

# Architecture diagram (text-based)
components = [
    # (label, sublabel, x, y, w, h, color)
    ("WordPress\n+ WWC Plugin", "wallahwecan.org\nPHP / WordPress CMS",
     0.3, 2.0, 2.9, 1.8, RGBColor(0,106,176)),
    ("Standalone Frontend", "HTML / Vanilla JS\nServed by Django at /shop/",
     0.3, 4.3, 2.9, 1.8, RGBColor(52,73,94)),
    ("Django REST API", "Python 3 / Django 5\napi.wallahwecan.org",
     5.2, 2.8, 3.0, 1.8, WWC_NAVY),
    ("SQLite → PostgreSQL", "Database\n(migrate for prod)",
     5.2, 5.1, 3.0, 1.4, RGBColor(52,73,94)),
    ("Stripe", "Payment processing\nEUR payments",
     9.5, 2.0, 2.5, 1.4, RGBColor(99,91,255)),
    ("Email (SMTP)", "Order confirmations\nPassword reset",
     9.5, 3.8, 2.5, 1.4, WWC_GREEN),
    ("Redis + Celery", "Async task queue\n(configured, ready)",
     9.5, 5.6, 2.5, 1.4, RGBColor(220,53,69)),
]

for (label, sub, cx, cy, cw, ch, col) in components:
    add_rect(slide, cx, cy, cw, ch, fill_rgb=col,
             line_rgb=RGBColor(0xFF,0xFF,0xFF), line_width_pt=2)
    add_text(slide, label, cx+0.1, cy+0.15, cw-0.2, ch*0.5,
             font_size=12, bold=True, color=WWC_WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, sub, cx+0.1, cy+ch*0.5, cw-0.2, ch*0.45,
             font_size=9.5, color=RGBColor(0xDD,0xDD,0xDD), align=PP_ALIGN.CENTER)

# Arrows (text)
add_text(slide, "REST API\n(JSON + JWT)", 3.35, 2.7, 1.75, 0.6,
         font_size=9, color=WWC_ORANGE, align=PP_ALIGN.CENTER, bold=True)
add_text(slide, "──────→", 3.3, 3.3, 1.8, 0.3, font_size=14, color=WWC_ORANGE, align=PP_ALIGN.CENTER)
add_text(slide, "Webhook\nPayment confirm", 8.35, 2.55, 1.1, 0.6,
         font_size=8.5, color=WWC_GREY, align=PP_ALIGN.CENTER)
add_text(slide, "←───→", 8.3, 3.1, 1.1, 0.3, font_size=14, color=WWC_GREY, align=PP_ALIGN.CENTER)

# Tech stack note
add_rect(slide, 0.3, 6.7, 12.7, 0.5,
         fill_rgb=RGBColor(0xE8,0xEE,0xF8), line_rgb=WWC_NAVY, line_width_pt=1)
add_text(slide,
         "Tech Stack:  Python 3 · Django 5 · Django REST Framework · SimpleJWT · Stripe SDK · "
         "PHP 8 · WordPress · Vanilla JS · HTML5 · CSS3",
         0.5, 6.72, 12.4, 0.45, font_size=10.5, color=WWC_NAVY)

footer(slide, 14)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 15 — TECHNICAL HANDOVER: KEY DECISIONS & FILES
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "Technical Handover Notes", "Key decisions made, files to know, and open questions")

# Left: key decisions
add_rect(slide, 0.3, 1.65, 6.0, 5.35,
         fill_rgb=WWC_WHITE, line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
add_rect(slide, 0.3, 1.65, 6.0, 0.4, fill_rgb=WWC_NAVY)
add_text(slide, "✅ Key Decisions Already Made", 0.5, 1.68, 5.7, 0.36,
         font_size=13, bold=True, color=WWC_WHITE)

decisions = [
    ("TND + Stripe:", "Stripe charges in EUR only. TND customers pay via Cash on Delivery. Customer's bank handles any conversion."),
    ("Auth strategy:", "Django JWT for shop accounts. WordPress users and Django users are separate systems. Login UI is included."),
    ("Cart sessions:", "Stable session key stored in localStorage (not PHP session) — survives page reloads and browser back."),
    ("Billing address:", "Captured per-order on the Order model. B2B default saved in CustomerAddress model."),
    ("Impact capture:", "Snapshot at order time — impact figures cannot be changed retroactively. Protects integrity."),
    ("Admin access:", "Admin frontend protected by API key auth — separate from customer JWT. Key configured in .env."),
]
dy = 2.18
for (dt, dd) in decisions:
    add_text(slide, dt, 0.5, dy, 5.6, 0.26, font_size=11, bold=True, color=WWC_NAVY)
    add_text(slide, dd, 0.5, dy+0.28, 5.6, 0.5, font_size=10.5, color=WWC_GREY)
    dy += 0.83

# Right: open questions + critical files
add_rect(slide, 6.9, 1.65, 6.1, 2.45,
         fill_rgb=WWC_WHITE, line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
add_rect(slide, 6.9, 1.65, 6.1, 0.4, fill_rgb=WWC_ORANGE)
add_text(slide, "❓ Open Questions for WWC", 7.1, 1.68, 5.7, 0.36,
         font_size=13, bold=True, color=WWC_WHITE)

questions = [
    "Hosting: VPS (Hetzner/DigitalOcean), PaaS (Railway/Render), or shared?",
    "Media: Store product images on S3/R2 or server disk?",
    "Email provider: SMTP credentials (Gmail, Mailgun, Brevo…)?",
    "Auth: Keep WP + Django separate, or sync logins?",
    "Stripe: Which account? Test mode → production switch needed.",
]
qy = 2.18
for q in questions:
    add_text(slide, f"•  {q}", 7.1, qy, 5.75, 0.32, font_size=10.5, color=WWC_DARK)
    qy += 0.36

add_rect(slide, 6.9, 4.2, 6.1, 2.8,
         fill_rgb=WWC_WHITE, line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
add_rect(slide, 6.9, 4.2, 6.1, 0.4, fill_rgb=WWC_NAVY)
add_text(slide, "📁 Critical Files to Know", 7.1, 4.23, 5.7, 0.36,
         font_size=13, bold=True, color=WWC_WHITE)

files = [
    ("backend/.env", "All secrets: DB, Stripe keys, email, API key"),
    ("backend/api/views.py", "All public API logic — checkout, orders, auth"),
    ("backend/api/payments.py", "Stripe webhook + order creation + emails"),
    ("frontend/checkout.html", "Checkout UX — address tiles, payment"),
    ("frontend/account.html", "Customer dashboard, orders, settings"),
    ("frontend/admin/index.html", "Admin dashboard entry point"),
    ("PLANNING.md", "Full project status & roadmap"),
]
fy = 4.72
for (fname, fdesc) in files:
    add_text(slide, fname, 7.1, fy, 2.8, 0.26, font_size=9.5, bold=True, color=WWC_ORANGE)
    add_text(slide, fdesc, 9.95, fy, 2.9, 0.26, font_size=9.5, color=WWC_GREY)
    fy += 0.3

footer(slide, 15)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 16 — EFFORT SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "Effort Summary", "Estimated developer days to complete the platform")

# Three big numbers
summary = [
    ("~27", "developer days", "to complete Phase 3 & 4\n(all remaining features +\nproduction hardening)",
     WWC_ORANGE, 0.4),
    ("~17", "developer days", "for Phase 3 alone\n(B2B, multilingual,\ncoupons, box builder)",
     WWC_NAVY, 4.85),
    ("~10", "developer days", "for Phase 4 alone\n(hosting, SSL, backups,\nmonitoring, PostgreSQL)",
     WWC_GREEN, 9.3),
]

for (num, unit, desc, col, x) in summary:
    add_rect(slide, x, 1.7, 3.6, 4.6, fill_rgb=WWC_WHITE,
             line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
    add_rect(slide, x, 1.7, 3.6, 0.1, fill_rgb=col)
    add_text(slide, num,  x+0.1, 2.0, 3.4, 1.4,
             font_size=72, bold=True, color=col, align=PP_ALIGN.CENTER)
    add_text(slide, unit, x+0.1, 3.45, 3.4, 0.4,
             font_size=16, color=WWC_GREY, align=PP_ALIGN.CENTER)
    add_text(slide, desc, x+0.1, 3.95, 3.4, 1.2,
             font_size=12, color=WWC_DARK, align=PP_ALIGN.CENTER)

# Assumptions note
add_rect(slide, 0.4, 6.5, 12.5, 0.65,
         fill_rgb=RGBColor(0xFF,0xF8,0xE1), line_rgb=WWC_AMBER, line_width_pt=1)
add_text(slide,
         "⚠️  Assumptions: Estimates assume a mid-level full-stack developer (Django + JS) with access to the codebase, "
         ".env secrets, and server credentials. Does not include time for QA / client review cycles. "
         "A senior developer could complete Phase 3 alone in 2–3 weeks.",
         0.6, 6.52, 12.1, 0.6, font_size=10.5, color=RGBColor(0x66,0x55,0x00))

footer(slide, 16)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 17 — PARTNER CRITERIA / HOW TO FIND A DEVELOPER
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "Finding a Developer Partner", "What to look for and what to share with candidates")

# Must-have skills
add_rect(slide, 0.3, 1.65, 6.0, 3.5,
         fill_rgb=WWC_WHITE, line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
add_rect(slide, 0.3, 1.65, 6.0, 0.4, fill_rgb=WWC_NAVY)
add_text(slide, "✅ Must-Have Skills", 0.5, 1.68, 5.7, 0.36,
         font_size=13, bold=True, color=WWC_WHITE)

must = [
    "Python / Django (REST API development)",
    "JavaScript (vanilla JS — no framework needed)",
    "HTML / CSS (responsive frontend)",
    "Git version control",
    "Basic Linux server administration (Nginx, systemd)",
    "Stripe integration experience",
    "Understanding of JWT authentication",
]
for i, m in enumerate(must):
    add_text(slide, f"✓  {m}", 0.5, 2.18+i*0.38, 5.6, 0.34, font_size=11, color=WWC_DARK)

# Nice to have
add_rect(slide, 0.3, 5.28, 6.0, 1.72,
         fill_rgb=WWC_WHITE, line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
add_rect(slide, 0.3, 5.28, 6.0, 0.4, fill_rgb=WWC_GREEN)
add_text(slide, "👍 Nice to Have", 0.5, 5.31, 5.7, 0.36,
         font_size=13, bold=True, color=WWC_WHITE)

nice = ["WordPress / PHP plugin development", "PostgreSQL", "Celery / Redis", "Multilingual web apps"]
for i, n in enumerate(nice):
    col = 0 if i < 2 else 1
    row = i % 2
    add_text(slide, f"○  {n}", 0.5+col*3.0, 5.78+row*0.38, 2.9, 0.34, font_size=11, color=WWC_DARK)

# Right: what to share
add_rect(slide, 6.9, 1.65, 6.1, 2.8,
         fill_rgb=WWC_WHITE, line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
add_rect(slide, 6.9, 1.65, 6.1, 0.4, fill_rgb=WWC_ORANGE)
add_text(slide, "📦 Share with Candidates", 7.1, 1.68, 5.7, 0.36,
         font_size=13, bold=True, color=WWC_WHITE)

share = [
    "This presentation",
    "PLANNING.md (full technical roadmap)",
    "GitHub repository access",
    "backend/.env.example (not the real .env)",
    "Access to staging server for testing",
    "Stripe test mode credentials",
]
for i, s in enumerate(share):
    add_text(slide, f"📄  {s}", 7.1, 2.18+i*0.36, 5.7, 0.32, font_size=11, color=WWC_DARK)

# Questions to ask
add_rect(slide, 6.9, 4.55, 6.1, 2.45,
         fill_rgb=WWC_WHITE, line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
add_rect(slide, 6.9, 4.55, 6.1, 0.4, fill_rgb=WWC_NAVY)
add_text(slide, "❓ Questions to Ask Candidates", 7.1, 4.58, 5.7, 0.36,
         font_size=13, bold=True, color=WWC_WHITE)

questions2 = [
    "Have you built Django REST APIs before? Share examples.",
    "How do you handle Stripe webhook security?",
    "Can you show a multilingual Django project?",
    "What is your approach to production deployment?",
    "Do you have experience with impact/social-sector projects?",
]
for i, q in enumerate(questions2):
    add_text(slide, f"?  {q}", 7.1, 5.06+i*0.37, 5.7, 0.32, font_size=10.5, color=WWC_DARK)

footer(slide, 17)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 18 — RECOMMENDED NEXT STEPS
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "Recommended Next Steps", "Immediate actions — in priority order")

steps_next = [
    ("🔴", "This Week", WWC_ORANGE, [
        "Decide on hosting provider (VPS recommendation: Hetzner CX22 ~€4/month or Railway.app for easier setup)",
        "Confirm SMTP email credentials for order notifications",
        "Confirm Stripe account — switch from test mode keys to live production keys in .env",
        "Register Stripe webhook endpoint once server is up (takes 10 minutes)",
    ]),
    ("🟡", "Before Go-Live (Phase 2 completion)", WWC_NAVY, [
        "Run the platform on a staging server and do a full end-to-end test: browse → cart → checkout → email",
        "Complete email verification flow (prevents spam accounts)",
        "Decide on Composable Box builder priority — is 'Build My Box' needed at launch or can it wait?",
        "Mobile responsiveness audit on checkout and product pages",
    ]),
    ("🟢", "After Go-Live (Phase 3)", WWC_GREEN, [
        "Multilingual UI — critical for reaching Arabic and English-speaking customers",
        "B2B registration flow — important for the corporate gifts (CADEAUX D'ENTREPRISE) category",
        "Coupon/promotional codes — useful for launch campaigns",
        "Google Analytics 4 setup — understand customer behaviour from day one",
    ]),
]

y = 1.65
for (emoji, label, color, items) in steps_next:
    h = 0.42 + len(items) * 0.48
    add_rect(slide, 0.3, y, 12.7, h,
             fill_rgb=WWC_WHITE, line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
    add_rect(slide, 0.3, y, 0.12, h, fill_rgb=color)
    add_text(slide, f"{emoji}  {label}", 0.55, y+0.07, 12.0, 0.34,
             font_size=13, bold=True, color=color)
    for j, item in enumerate(items):
        add_text(slide, f"▸  {item}", 0.6, y+0.45+j*0.48, 12.1, 0.42,
                 font_size=11, color=WWC_DARK)
    y += h + 0.1

footer(slide, 18)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 19 — WHAT WWC ALREADY HAS (ASSETS SUMMARY)
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_LIGHT)
header_band(slide, "What You Already Have", "A summary of assets ready to hand to a developer")

asset_cols = [
    ("Backend Assets", WWC_NAVY, [
        "Complete Django 5 project (production-grade structure)",
        "14 database models + all migrations written",
        "60+ API endpoints (products, orders, customers, payments, admin)",
        "JWT authentication system fully wired",
        "Stripe Checkout + webhook integration complete",
        "Order confirmation + shipping notification emails",
        "Stock management with automatic restore on cancellation",
        "Admin API with API key protection",
        "Sample data population commands for testing",
        ".env.example documenting every required variable",
    ]),
    ("Frontend Assets", WWC_ORANGE, [
        "Product catalogue page (search, filter, pagination)",
        "Product detail page (images, reviews, impact, add-to-cart)",
        "Shopping cart (guest + logged-in, live totals)",
        "Checkout (smart address tiles, billing, Stripe + COD)",
        "Order success + order detail pages",
        "Customer account (orders, wishlist, impact dashboard)",
        "Account settings (profile, address, password, preferences)",
        "Login + Register + Password Reset pages",
        "Admin dashboard (products, orders, customers, donations)",
        "Impact + Donate public pages",
    ]),
    ("Documentation", WWC_GREEN, [
        "PLANNING.md — complete technical roadmap",
        "This presentation — non-technical overview",
        "All code commented and structured",
        "API endpoint list in urls.py",
        "Inline code comments throughout",
        " ",
        "WordPress Plugin Assets",
        "Full WP plugin with all shortcodes",
        "API client class (caching, auth, all resources)",
        "Cart, checkout, auth PHP classes",
    ]),
]

for i, (title, color, items) in enumerate(asset_cols):
    x = 0.3 + i * 4.35
    add_rect(slide, x, 1.65, 4.1, 5.55,
             fill_rgb=WWC_WHITE, line_rgb=RGBColor(0xE0,0xE0,0xE0), line_width_pt=1)
    add_rect(slide, x, 1.65, 4.1, 0.42, fill_rgb=color)
    add_text(slide, title, x+0.15, y+0.07 if (y:=1.65) else 0,
             3.8, 0.32, font_size=13, bold=True, color=WWC_WHITE)
    txBox = slide.shapes.add_textbox(Inches(x+0.15), Inches(2.18), Inches(3.8), Inches(4.8))
    txBox.word_wrap = True
    tf = txBox.text_frame
    tf.word_wrap = True
    for j, item in enumerate(items):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        p.space_before = Pt(3)
        run = p.add_run()
        run.text = f"✓  {item}" if item.strip() and not item.startswith(" ") and not item == "WordPress Plugin Assets" else item
        run.font.size = Pt(10.5)
        run.font.bold = (item == "WordPress Plugin Assets")
        run.font.color.rgb = WWC_NAVY if run.font.bold else WWC_GREY

footer(slide, 19)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 20 — CLOSING SLIDE
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(blank_layout)
add_rect(slide, 0, 0, 13.33, 7.5, fill_rgb=WWC_NAVY)
add_rect(slide, 0, 3.6, 13.33, 0.12, fill_rgb=WWC_ORANGE)

add_text(slide, "🌿", 0.5, 0.5, 1.4, 1.2, font_size=56, color=WWC_WHITE)
add_text(slide, "Every purchase plants a seed.", 0.5, 1.6, 12.3, 0.8,
         font_size=36, bold=True, italic=True, color=WWC_ORANGE, align=PP_ALIGN.LEFT)
add_text(slide, "Every seed feeds a student.", 0.5, 2.35, 12.3, 0.7,
         font_size=36, bold=True, italic=True, color=WWC_WHITE, align=PP_ALIGN.LEFT)

add_text(slide, "The platform is ready. The mission continues.", 0.5, 3.9, 12.3, 0.55,
         font_size=20, color=RGBColor(0xCC,0xCC,0xCC), align=PP_ALIGN.LEFT)

contact_lines = [
    "Platform Repository:  GitHub — wwc_web_new",
    "Technical Documentation:  PLANNING.md",
    "Contact for handover:  [your contact here]",
]
for i, cl in enumerate(contact_lines):
    add_text(slide, cl, 0.5, 4.75+i*0.48, 12.3, 0.42,
             font_size=13, color=RGBColor(0x99,0x99,0x99), align=PP_ALIGN.LEFT)

add_text(slide, "Wallah We Can  ·  GreenSchool Initiative  ·  2026",
         0.5, 6.6, 12.3, 0.4, font_size=11,
         color=RGBColor(0x66,0x66,0x66), align=PP_ALIGN.LEFT)

footer(slide, 20)

# ─── Save ─────────────────────────────────────────────────────────────────────
output_path = "WWC_Shop_Presentation.pptx"
prs.save(output_path)
print(f"[OK]  Saved: {output_path}")
print(f"    Slides: {len(prs.slides)}")
