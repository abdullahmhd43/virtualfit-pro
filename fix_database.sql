-- ============================================================
--  VirtualFit Pro — Fix Script
--  Run this in Supabase SQL Editor
-- ============================================================

-- 1. Disable RLS on all tables
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE orders DISABLE ROW LEVEL SECURITY;
ALTER TABLE order_items DISABLE ROW LEVEL SECURITY;
ALTER TABLE analytics DISABLE ROW LEVEL SECURITY;
ALTER TABLE products DISABLE ROW LEVEL SECURITY;
ALTER TABLE tryon_history DISABLE ROW LEVEL SECURITY;
ALTER TABLE wishlist DISABLE ROW LEVEL SECURITY;
ALTER TABLE promo_codes DISABLE ROW LEVEL SECURITY;

-- 2. Grant full access to anon role
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon;
GRANT USAGE ON SCHEMA public TO anon;

-- 3. Create product_sizes table if missing
CREATE TABLE IF NOT EXISTS product_sizes (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id) ON DELETE CASCADE,
    size VARCHAR(10) NOT NULL,
    stock INT DEFAULT 0,
    sold INT DEFAULT 0,
    UNIQUE(product_id, size)
);
ALTER TABLE product_sizes DISABLE ROW LEVEL SECURITY;
GRANT ALL ON product_sizes TO anon;

-- 4. Add missing columns to users
ALTER TABLE users ADD COLUMN IF NOT EXISTS city VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS device_type VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS browser VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS signup_source VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS ip_country VARCHAR(10);

-- 5. Add missing columns to orders
ALTER TABLE orders ADD COLUMN IF NOT EXISTS payhere_payment_id VARCHAR(100);

-- 6. Make sure admin user exists with bcrypt password
-- Password: VirtualFit@2026
UPDATE users 
SET password = '$2b$12$Ij4MkYc/5sVXlY08q4C/3.BV67c/P8VVai6SlkO9uXREnRzv7SIJS',
    role = 'admin',
    is_active = TRUE
WHERE email = 'admin@virtualfit.com';

-- If admin doesn't exist, insert
INSERT INTO users (name, email, password, role, is_active, gender)
SELECT 'Admin', 'admin@virtualfit.com', 
       '$2b$12$Ij4MkYc/5sVXlY08q4C/3.BV67c/P8VVai6SlkO9uXREnRzv7SIJS',
       'admin', TRUE, 'men'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@virtualfit.com');

SELECT '✅ Fix complete!' AS status;
SELECT COUNT(*) as total_users FROM users;
SELECT COUNT(*) as total_orders FROM orders;
SELECT COUNT(*) as total_products FROM products;
