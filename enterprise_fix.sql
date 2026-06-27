-- ============================================================
--  VirtualFit Pro — Enterprise Final Fix SQL
--  Run this ONCE in Supabase SQL Editor
-- ============================================================

-- ── 1. Disable RLS on all tables ──────────────────────────
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE orders DISABLE ROW LEVEL SECURITY;
ALTER TABLE order_items DISABLE ROW LEVEL SECURITY;
ALTER TABLE analytics DISABLE ROW LEVEL SECURITY;
ALTER TABLE products DISABLE ROW LEVEL SECURITY;
ALTER TABLE tryon_history DISABLE ROW LEVEL SECURITY;
ALTER TABLE wishlist DISABLE ROW LEVEL SECURITY;
ALTER TABLE promo_codes DISABLE ROW LEVEL SECURITY;

-- ── 2. Grant full access ───────────────────────────────────
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO anon;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO anon, authenticated;

-- ── 3. Create missing tables ───────────────────────────────
CREATE TABLE IF NOT EXISTS product_sizes (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id) ON DELETE CASCADE,
    size VARCHAR(10) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    sold INT NOT NULL DEFAULT 0,
    UNIQUE(product_id, size)
);
ALTER TABLE product_sizes DISABLE ROW LEVEL SECURITY;
GRANT ALL ON product_sizes TO anon, authenticated;
GRANT ALL ON SEQUENCE product_sizes_id_seq TO anon, authenticated;

-- ── 4. Add missing columns ─────────────────────────────────
ALTER TABLE users ADD COLUMN IF NOT EXISTS city VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS device_type VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS browser VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS signup_source VARCHAR(50) DEFAULT 'website';
ALTER TABLE users ADD COLUMN IF NOT EXISTS ip_country VARCHAR(10) DEFAULT 'LK';
ALTER TABLE orders ADD COLUMN IF NOT EXISTS payhere_payment_id VARCHAR(100);
ALTER TABLE orders ADD COLUMN IF NOT EXISTS notes TEXT;

-- ── 5. Ensure admin user exists with bcrypt password ──────
-- Password: VirtualFit@2026
UPDATE users 
SET password = '$2b$12$Ij4MkYc/5sVXlY08q4C/3.BV67c/P8VVai6SlkO9uXREnRzv7SIJS',
    role = 'admin',
    is_active = TRUE
WHERE email = 'admin@virtualfit.com';

INSERT INTO users (name, email, password, role, is_active, gender)
SELECT 'Admin', 'admin@virtualfit.com',
       '$2b$12$Ij4MkYc/5sVXlY08q4C/3.BV67c/P8VVai6SlkO9uXREnRzv7SIJS',
       'admin', TRUE, 'men'
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE email = 'admin@virtualfit.com'
);

-- ── 6. Add useful indexes ──────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_orders_email ON orders(customer_email);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_products_gender ON products(gender);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);

-- ── 7. Verify ─────────────────────────────────────────────
SELECT '✅ Enterprise Fix Complete!' AS status;
SELECT COUNT(*) as total_users FROM users;
SELECT COUNT(*) as total_orders FROM orders;
SELECT COUNT(*) as total_products FROM products;
SELECT email, role, is_active FROM users WHERE role = 'admin';
