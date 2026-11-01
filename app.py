import os
import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

load_dotenv(override=True)
app = Flask(__name__)


def get_db():
    """The ONE database connection function."""
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return psycopg2.connect(
            database_url,
            cursor_factory=psycopg2.extras.RealDictCursor
        )

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "blinkitapp_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def run(sql, params=(), fetch=False, one=False):
    """Run one parameterized SQL query. Commits on success, rolls back on error."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)          # %s placeholders prevent SQL injection
            data = None
            if fetch:
                data = cur.fetchone() if one else cur.fetchall()
        conn.commit()
        return data
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.errorhandler(Exception)
def handle_error(e):
    print("ERROR:", e)
    return jsonify({"error": "Database or server error. Check the Flask terminal."}), 500


# ---------- Pages ----------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/cart")
def cart_page():
    return render_template("cart.html")

@app.route("/wishlist")
def wishlist_page():
    return render_template("wishlist.html")

@app.route("/admin/database")
def database_viewer():
    # Fresh data is fetched from PostgreSQL every time the page loads.
    products = run("SELECT * FROM products ORDER BY product_id", fetch=True)
    cart = run("""SELECT c.cart_id, c.product_id, p.name, p.price, c.quantity, c.created_at
                  FROM cart_items c JOIN products p ON p.product_id = c.product_id
                  ORDER BY c.cart_id""", fetch=True)
    wish = run("""SELECT w.wishlist_id, w.product_id, p.name, p.price, w.created_at
                  FROM wishlist_items w JOIN products p ON p.product_id = w.product_id
                  ORDER BY w.wishlist_id""", fetch=True)
    return render_template("database.html", products=products, cart=cart, wishlist=wish)


# ---------- Products ----------
@app.route("/api/products")
def get_products():
    rows = run("SELECT * FROM products ORDER BY product_id", fetch=True)
    for r in rows:
        r["price"] = float(r["price"])
    return jsonify(rows)


# ---------- Cart ----------
@app.route("/api/cart")
def get_cart():
    rows = run("""SELECT c.cart_id, c.product_id, c.quantity, p.name, p.price, p.image_url, p.quantity AS pack
                  FROM cart_items c JOIN products p ON p.product_id = c.product_id
                  ORDER BY c.cart_id""", fetch=True)
    total = 0
    for r in rows:
        r["price"] = float(r["price"])
        r["subtotal"] = r["price"] * r["quantity"]
        total += r["subtotal"]
    return jsonify({"items": rows, "total": total, "count": sum(r["quantity"] for r in rows)})


@app.route("/api/cart/add", methods=["POST"])
def add_to_cart():
    pid = request.get_json().get("product_id")
    existing = run("SELECT cart_id FROM cart_items WHERE product_id = %s", (pid,), fetch=True, one=True)
    if existing:   # already in cart -> UPDATE quantity, no duplicate row
        run("UPDATE cart_items SET quantity = quantity + 1 WHERE product_id = %s", (pid,))
    else:
        run("INSERT INTO cart_items (product_id, quantity) VALUES (%s, 1)", (pid,))
    return jsonify({"message": "Added to cart"})


@app.route("/api/cart/update", methods=["POST"])
def update_cart():
    data = request.get_json()
    pid, qty = data.get("product_id"), int(data.get("quantity", 1))
    if qty <= 0:
        run("DELETE FROM cart_items WHERE product_id = %s", (pid,))
    else:
        run("UPDATE cart_items SET quantity = %s WHERE product_id = %s", (qty, pid))
    return jsonify({"message": "Cart updated"})


@app.route("/api/cart/remove", methods=["POST"])
def remove_from_cart():
    run("DELETE FROM cart_items WHERE product_id = %s", (request.get_json().get("product_id"),))
    return jsonify({"message": "Removed from cart"})


# ---------- Wishlist ----------
@app.route("/api/wishlist")
def get_wishlist():
    rows = run("""SELECT w.wishlist_id, w.product_id, p.name, p.price, p.quantity, p.image_url
                  FROM wishlist_items w JOIN products p ON p.product_id = w.product_id
                  ORDER BY w.wishlist_id""", fetch=True)
    for r in rows:
        r["price"] = float(r["price"])
    return jsonify({"items": rows, "count": len(rows)})


@app.route("/api/wishlist/add", methods=["POST"])
def add_to_wishlist():
    run("INSERT INTO wishlist_items (product_id) VALUES (%s) ON CONFLICT (product_id) DO NOTHING",
        (request.get_json().get("product_id"),))
    return jsonify({"message": "Added to wishlist"})


@app.route("/api/wishlist/remove", methods=["POST"])
def remove_from_wishlist():
    run("DELETE FROM wishlist_items WHERE product_id = %s", (request.get_json().get("product_id"),))
    return jsonify({"message": "Removed from wishlist"})


if __name__ == "__main__":
    app.run(debug=True)
