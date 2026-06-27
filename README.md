# VirtualFit Pro 👗✨

> AI-powered virtual try-on fashion platform built for Sri Lanka — shop smarter, try before you buy.

![VirtualFit Pro](https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1200&q=80)

---

## 🚀 Features

- 👗 **Virtual Try-On** — AI-powered clothing try-on using FAL & Gemini
- 🛍️ **Full E-Commerce** — Browse, cart, checkout with COD & PayHere payment
- 👤 **Customer Accounts** — Register, login, order history, measurements
- 🔐 **Secure Auth** — JWT tokens, bcrypt passwords, brute-force protection
- 📦 **Order Management** — Real-time status tracking, cancel orders
- 🛠️ **Admin Dashboard** — Orders, users, analytics, stock management
- 📊 **Analytics** — Sales reports, revenue tracking
- 📱 **Responsive** — Mobile-friendly dark UI

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML, CSS, Vanilla JS |
| **Backend** | Python Flask |
| **Database** | Supabase (PostgreSQL) |
| **AI Try-On** | FAL AI, Gemini API |
| **Payment** | PayHere (Sri Lanka) |
| **Auth** | JWT + bcrypt |

---

## ⚡ Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/virtualfit-pro.git
cd virtualfit-pro
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup environment variables
```bash
cp .env.example .env
```
Edit `.env` with your credentials:
```env
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

FAL_API_KEY=your_fal_key
GEMINI_API_KEY=your_gemini_key

PAYHERE_MERCHANT_ID=your_merchant_id
PAYHERE_SECRET=your_payhere_secret
PAYHERE_SANDBOX=true
```

### 4. Setup Supabase Database
- Go to [Supabase Dashboard](https://supabase.com/dashboard)
- Open **SQL Editor**
- Run `MASTER_FIX.sql` (included in repo)

### 5. Run the app
```bash
python app.py
```

Open `http://localhost:5000` 🎉

---

## 📁 Project Structure

```
virtualfit-pro/
├── app.py                  # Flask entry point
├── requirements.txt
├── MASTER_FIX.sql          # Supabase database setup
├── .env.example
│
├── frontend/               # Static HTML/CSS/JS
│   ├── index.html
│   ├── gallery.html        # Shop page
│   ├── product.html        # Product detail
│   ├── cart.html
│   ├── checkout.html
│   ├── profile.html        # Customer profile & orders
│   ├── tryon.html          # AI Virtual Try-On
│   ├── admin.html          # Admin dashboard
│   ├── css/main.css
│   └── js/data.js
│
└── backend/
    ├── routes/
    │   ├── auth_routes.py  # Register, Login, JWT
    │   ├── core_routes.py  # Orders, Products, Stock
    │   └── ai_routes.py    # Try-On AI endpoints
    ├── database/
    │   └── connection.py   # Supabase client
    ├── auth/
    │   └── jwt_manager.py  # JWT & bcrypt
    ├── middleware/
    │   └── security.py     # Rate limiting, headers
    └── validators/
        └── input_validators.py
```

---

## 🔐 Default Admin

```
URL:      http://localhost:5000/admin.html
Email:    admin@virtualfit.com
Password: VirtualFit@2026
```

> ⚠️ Change the admin password before deploying to production!

---

## 🗃️ Database Setup

Run `MASTER_FIX.sql` in Supabase SQL Editor. This will:

- ✅ Create all tables (users, orders, products, order_items, etc.)
- ✅ Disable RLS for backend access
- ✅ Grant permissions to anon role
- ✅ Create admin user
- ✅ Add default promo codes (SAVE10, FREESHIP, WELCOME20, VF50)
- ✅ Add performance indexes

---

## 💳 Payment

Supports **PayHere** (Sri Lanka payment gateway):
- Visa / Mastercard / AMEX
- Internet Banking
- Cash on Delivery (COD)
- Bank Transfer

Set `PAYHERE_SANDBOX=true` for testing.

---

## 🤖 AI Virtual Try-On

Powered by **FAL AI** and **Google Gemini**:
1. Upload your photo
2. Select a clothing item
3. AI generates try-on result in seconds

---

## 📦 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Customer register |
| POST | `/api/auth/login` | Login → JWT token |
| GET | `/api/db/orders/my` | Customer's own orders |
| POST | `/api/db/orders` | Place new order |
| GET | `/api/db/products` | Product listing |
| GET | `/api/stock/:id` | Stock by size |
| POST | `/api/payment/initiate` | PayHere payment |
| GET | `/api/db/analytics/dashboard` | Admin dashboard |

---

## ⚙️ Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Flask secret key |
| `JWT_SECRET_KEY` | JWT signing key |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase anon key |
| `FAL_API_KEY` | FAL AI key for try-on |
| `GEMINI_API_KEY` | Google Gemini API key |
| `PAYHERE_MERCHANT_ID` | PayHere merchant ID |
| `PAYHERE_SECRET` | PayHere secret |
| `PAYHERE_SANDBOX` | `true` for testing |

---

## 🚀 Deployment

### Deploy to Railway / Render:
1. Push code to GitHub
2. Connect repo to Railway or Render
3. Add environment variables
4. Deploy!

### Important before production:
- [ ] Set `FLASK_ENV=production`
- [ ] Set `PAYHERE_SANDBOX=false`
- [ ] Change admin password
- [ ] Add strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Enable Supabase RLS with proper policies

---

## 📄 License

MIT License — free to use and modify.

---

## 🙏 Built With

- [Flask](https://flask.palletsprojects.com/)
- [Supabase](https://supabase.com/)
- [FAL AI](https://fal.ai/)
- [Google Gemini](https://ai.google.dev/)
- [PayHere](https://www.payhere.lk/)
- [Font Awesome](https://fontawesome.com/)

---

<p align="center">Made with ❤️ for Sri Lanka 🇱🇰</p>
