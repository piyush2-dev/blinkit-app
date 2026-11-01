# Blinkit – Basic Grocery Website (Flask + PostgreSQL)

## 1. Install
- Python 3.9+  and  PostgreSQL (remember the `postgres` user password)

## 2. Create the database
Open **psql** (or SQL Shell) and run:
    CREATE DATABASE blinkit_db;
Then load tables + 15 products:
    psql -U postgres -d blinkit_db -f schema.sql
(Or in pgAdmin: open blinkit_db > Query Tool > open schema.sql > Run.)

## 3. Configure
Edit `.env` and put your real PostgreSQL password in DB_PASSWORD.

## 4. Run in VS Code
    python -m venv venv
    venv\Scripts\activate          (Mac/Linux: source venv/bin/activate)
    pip install -r requirements.txt
    python app.py
Open http://127.0.0.1:5000  and  http://127.0.0.1:5000/admin/database

## 5. Verify stored data (psql)
    SELECT * FROM products;
    SELECT c.cart_id, p.name, c.quantity, c.created_at FROM cart_items c JOIN products p USING (product_id);
    SELECT w.wishlist_id, p.name, w.created_at FROM wishlist_items w JOIN products p USING (product_id);
    SELECT SUM(p.price * c.quantity) AS cart_total FROM cart_items c JOIN products p USING (product_id);
