-- Run this inside the blinkit_db database
DROP TABLE IF EXISTS cart_items;
DROP TABLE IF EXISTS wishlist_items;
DROP TABLE IF EXISTS products;

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    price      NUMERIC(8,2) NOT NULL,
    quantity   VARCHAR(50)  NOT NULL,   -- pack size, e.g. "500 ml"
    image_url  VARCHAR(255) NOT NULL
);

CREATE TABLE cart_items (
    cart_id    SERIAL PRIMARY KEY,
    product_id INT NOT NULL UNIQUE REFERENCES products(product_id) ON DELETE CASCADE,
    quantity   INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE wishlist_items (
    wishlist_id SERIAL PRIMARY KEY,
    product_id  INT NOT NULL UNIQUE REFERENCES products(product_id) ON DELETE CASCADE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO products (name, price, quantity, image_url) VALUES
('Amul Milk',   33,  '500 ml', '/static/images/milk.svg'),
('Bread',       45,  '400 g',  '/static/images/bread.svg'),
('Eggs',        84,  '12 pcs', '/static/images/eggs.svg'),
('Bananas',     59,  '1 kg',   '/static/images/bananas.svg'),
('Apples',      180, '1 kg',   '/static/images/apples.svg'),
('Potatoes',    35,  '1 kg',   '/static/images/potatoes.svg'),
('Tomatoes',    40,  '1 kg',   '/static/images/tomatoes.svg'),
('Onions',      38,  '1 kg',   '/static/images/onions.svg'),
('Rice',        120, '1 kg',   '/static/images/rice.svg'),
('Atta',        265, '5 kg',   '/static/images/atta.svg'),
('Maggi',       14,  '70 g',   '/static/images/maggi.svg'),
('Biscuits',    30,  '120 g',  '/static/images/biscuits.svg'),
('Cooking Oil', 155, '1 L',    '/static/images/oil.svg'),
('Sugar',       52,  '1 kg',   '/static/images/sugar.svg'),
('Tea',         140, '250 g',  '/static/images/tea.svg');
