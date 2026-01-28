# Wallah We Can E-Commerce Shop

E-commerce platform for GreenSchool products with transparent social impact tracking.

## Project Overview

This project provides a complete e-commerce solution for Wallah We Can's GreenSchool initiative, where parents of students work on farms producing various goods. Every purchase directly supports students and producers with complete transparency on impact.

**Core Value Proposition**: "Thanks to your purchase of product X, 6 energy bars will be provided to students at Sidi Mechreg"

## Architecture

The project consists of two main components:

### 1. Django REST API Backend (`/backend`)

A standalone Django REST API that handles:
- Product catalog management
- Shopping cart operations
- Order processing
- Payment integration (Stripe)
- Customer accounts (B2C and B2B)
- Social impact tracking

### 2. WordPress Plugin (`/wordpress-plugin/wwc-shop`)

A WordPress plugin that integrates with the existing WordPress site:
- Preserves 100% of existing site structure
- Adds shop functionality via shortcodes
- AJAX-powered cart operations
- Responsive design matching the UI specifications

## Features

- **Multi-currency support**: TND (Tunisia) and EUR (France)
- **Multi-language support**: French, English, Arabic
- **B2C and B2B pricing**: Different prices for individual vs corporate customers
- **Impact tracking**: Every product shows its social impact
- **Composable boxes**: "COMPOSER MA BOX" feature for custom gift boxes
- **Customer dashboard**: Track cumulative impact from purchases

## Installation

### Django Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### WordPress Plugin

1. Copy the `wordpress-plugin/wwc-shop` folder to `/wp-content/plugins/`
2. Activate the plugin in WordPress admin
3. Go to **WWC Shop > Settings** and configure:
   - API URL (your Django backend URL)
   - Stripe keys
   - Default currency

## Configuration

### Django Settings

Key environment variables in `.env`:

```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=api.wallahwecan.org

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=wwc_shop
DB_USER=wwc_user
DB_PASSWORD=your-password
DB_HOST=localhost

# Stripe
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### WordPress Plugin

Configure in **WWC Shop > Settings**:

- **API URL**: `https://api.wallahwecan.org`
- **Default Currency**: TND or EUR
- **Stripe Keys**: For client-side payment integration

## API Endpoints

### Products
- `GET /api/v1/products/` - List products
- `GET /api/v1/products/{slug}/` - Product detail
- `GET /api/v1/products/featured/` - Featured products
- `GET /api/v1/categories/` - List categories

### Cart
- `GET /api/v1/cart/` - Get cart
- `POST /api/v1/cart/add/` - Add item
- `PATCH /api/v1/cart/update/{id}/` - Update item
- `DELETE /api/v1/cart/remove/{id}/` - Remove item

### Checkout
- `POST /api/v1/checkout/` - Create order
- `POST /api/v1/payments/create-session/` - Create Stripe session

### Customer
- `GET /api/v1/customer/dashboard/` - Customer dashboard with impact
- `GET /api/v1/orders/` - Order history

## Shortcodes

Use these shortcodes in WordPress pages:

```
[wwc_products]                         - Product grid
[wwc_products category="soins"]        - Products by category
[wwc_products featured="true"]         - Featured products
[wwc_product slug="roll-on-calme"]     - Single product
[wwc_categories]                       - Category navigation
[wwc_cart]                             - Cart page
[wwc_checkout]                         - Checkout page
[wwc_customer_dashboard]               - Customer dashboard
[wwc_impact]                           - Impact events
```

## Product Categories

Based on UI design:
- SOINS (Care/Wellness)
- NUTRITION (Nutrition)
- BIEN-ÊTRE (Well-being)
- MAISON (Home)
- COFFRETS (Gift Sets)
- CADEAUX D'ENTREPRISE (Corporate Gifts)
- COMPOSER MA BOX (Create Your Box)

## Social Impact Model

Each product has:
- `impact_quantity`: Number of items provided (e.g., 6)
- `impact_item`: Type of item (e.g., "energy bars")
- `impact_school`: Beneficiary school (e.g., "Sidi Mechreg")

Impact is tracked at:
- Product level (displayed on product page)
- Cart level (total impact preview)
- Order level (captured at purchase time)
- Customer level (cumulative impact in dashboard)

## Development

### Running Tests

```bash
# Django tests
cd backend
python manage.py test

# With pytest
pytest
```

### Code Style

- Django: Follow PEP 8
- PHP: WordPress coding standards
- JavaScript: ES6+

## Deployment

### Django Backend

1. Set up PostgreSQL database
2. Configure environment variables
3. Run migrations
4. Collect static files: `python manage.py collectstatic`
5. Set up Gunicorn and Nginx
6. Configure SSL certificate
7. Set up Stripe webhooks

### WordPress Plugin

1. Upload plugin to production WordPress
2. Activate and configure settings
3. Create necessary pages with shortcodes
4. Test checkout flow

## License

Copyright 2024 Wallah We Can. All rights reserved.

## Support

For issues and questions:
- GitHub Issues: [Report a bug](https://github.com/wallahwecan/wwc-shop/issues)
- Email: tech@wallahwecan.org
