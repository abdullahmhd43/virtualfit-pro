-- VirtualFit Pro — Supabase Database Setup
-- Go to: Supabase Dashboard → SQL Editor → Paste this → Run

-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,
    phone       VARCHAR(20),
    gender      VARCHAR(20) DEFAULT 'men',
    role        VARCHAR(20) DEFAULT 'customer',
    is_active   BOOLEAN DEFAULT true,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login  TIMESTAMP WITH TIME ZONE
);

-- PRODUCTS TABLE
CREATE TABLE IF NOT EXISTS products (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    brand       VARCHAR(100),
    gender      VARCHAR(20) NOT NULL,
    cat         VARCHAR(50) NOT NULL,
    price       INTEGER NOT NULL,
    old_price   INTEGER,
    img         TEXT,
    badge       VARCHAR(20),
    sizes       VARCHAR(200) DEFAULT 'S,M,L,XL',
    description TEXT,
    rating      DECIMAL(3,1) DEFAULT 4.5,
    reviews     INTEGER DEFAULT 0,
    stock       INTEGER DEFAULT 100,
    is_active   BOOLEAN DEFAULT true,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ORDERS TABLE
CREATE TABLE IF NOT EXISTS orders (
    id              BIGSERIAL PRIMARY KEY,
    order_number    VARCHAR(20) UNIQUE NOT NULL,
    user_id         BIGINT REFERENCES users(id) ON DELETE SET NULL,
    customer_name   VARCHAR(100) NOT NULL,
    customer_email  VARCHAR(150) NOT NULL,
    customer_phone  VARCHAR(20),
    address         TEXT,
    city            VARCHAR(100),
    total_amount    INTEGER NOT NULL,
    shipping_fee    INTEGER DEFAULT 350,
    discount        INTEGER DEFAULT 0,
    payment_method  VARCHAR(50) DEFAULT 'cod',
    payment_status  VARCHAR(20) DEFAULT 'pending',
    order_status    VARCHAR(20) DEFAULT 'pending',
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ORDER ITEMS TABLE
CREATE TABLE IF NOT EXISTS order_items (
    id           BIGSERIAL PRIMARY KEY,
    order_id     BIGINT REFERENCES orders(id) ON DELETE CASCADE,
    product_id   BIGINT REFERENCES products(id) ON DELETE SET NULL,
    product_name VARCHAR(200) NOT NULL,
    product_img  TEXT,
    size         VARCHAR(20),
    quantity     INTEGER DEFAULT 1,
    price        INTEGER NOT NULL,
    subtotal     INTEGER NOT NULL
);

-- ANALYTICS TABLE
CREATE TABLE IF NOT EXISTS analytics (
    id          BIGSERIAL PRIMARY KEY,
    event_type  VARCHAR(50) NOT NULL,
    page        VARCHAR(100),
    product_id  BIGINT,
    user_id     BIGINT,
    device      VARCHAR(50),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- TRYON HISTORY TABLE
CREATE TABLE IF NOT EXISTS tryon_history (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT REFERENCES users(id) ON DELETE SET NULL,
    product_id  BIGINT REFERENCES products(id) ON DELETE SET NULL,
    result_url  TEXT,
    provider    VARCHAR(50) DEFAULT 'fashn',
    gender      VARCHAR(20),
    category    VARCHAR(50),
    status      VARCHAR(20) DEFAULT 'success',
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- WISHLIST TABLE
CREATE TABLE IF NOT EXISTS wishlist (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT REFERENCES users(id) ON DELETE CASCADE,
    product_id  BIGINT REFERENCES products(id) ON DELETE CASCADE,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- PROMO CODES TABLE
CREATE TABLE IF NOT EXISTS promo_codes (
    id              BIGSERIAL PRIMARY KEY,
    code            VARCHAR(50) UNIQUE NOT NULL,
    discount_type   VARCHAR(20) DEFAULT 'percent',
    discount_value  INTEGER NOT NULL,
    min_order       INTEGER DEFAULT 0,
    max_uses        INTEGER DEFAULT 100,
    used_count      INTEGER DEFAULT 0,
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- DEFAULT PROMO CODES
INSERT INTO promo_codes (code, discount_type, discount_value, min_order) VALUES
('SAVE10',    'percent', 10, 1000),
('FREESHIP',  'fixed',   350, 0),
('WELCOME20', 'percent', 20, 2000),
('VF50',      'fixed',   500, 5000)
ON CONFLICT (code) DO NOTHING;

-- Enable Row Level Security (RLS) - important for security!
ALTER TABLE users         ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders        ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items   ENABLE ROW LEVEL SECURITY;
ALTER TABLE tryon_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE wishlist      ENABLE ROW LEVEL SECURITY;

-- Allow public read for products
CREATE POLICY "Products are viewable by everyone" ON products FOR SELECT USING (true);
CREATE POLICY "Analytics insert allowed" ON analytics FOR INSERT WITH CHECK (true);

SELECT 'VirtualFit Pro Database Ready! ✅' AS status;

-- ================================================
--  PRODUCT SIZE STOCK TABLE
--  Each size has its own stock count
-- ================================================
CREATE TABLE IF NOT EXISTS product_sizes (
    id          BIGSERIAL PRIMARY KEY,
    product_id  BIGINT REFERENCES products(id) ON DELETE CASCADE,
    size        VARCHAR(20) NOT NULL,
    stock       INTEGER DEFAULT 0,
    sold        INTEGER DEFAULT 0,
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(product_id, size)
);

-- Auto-update timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_size_stock_timestamp
BEFORE UPDATE ON product_sizes
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

SELECT 'Size stock table created! ✅' AS status;

-- ================================================
--  ADD TRACKING COLUMNS TO USERS TABLE
--  Run this if users table already exists
-- ================================================
ALTER TABLE users ADD COLUMN IF NOT EXISTS city VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS device_type VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS browser VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS signup_source VARCHAR(50) DEFAULT 'website';
ALTER TABLE users ADD COLUMN IF NOT EXISTS ip_country VARCHAR(10) DEFAULT 'LK';

SELECT 'User tracking columns added! ✅' AS status;
