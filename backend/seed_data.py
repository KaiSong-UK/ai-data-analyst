"""
AI Data Analyst - Demo seed data
Creates e-commerce dataset: customers, products, orders, order_items
"""
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from core.database import get_db_session

REGIONS = ["North", "South", "East", "West"]
TIERS = ["premium", "standard"]
STATUSES = ["completed", "completed", "completed", "completed", "completed", "cancelled"]
CATEGORIES = ["Software", "SaaS"]

PRODUCTS_DATA = [
    ("DataQGuard Pro", "Software", 299.00),
    ("AI Analyst License", "Software", 199.00),
    ("ETL Toolkit Enterprise", "Software", 399.00),
    ("CloudSync Basic", "SaaS", 49.00),
    ("CloudSync Pro", "SaaS", 99.00),
    ("DataPipeline Starter", "Software", 79.00),
    ("Analytics Dashboard", "Software", 149.00),
    ("ML Toolkit", "Software", 249.00),
    ("API Gateway", "SaaS", 129.00),
    ("Data Warehouse Connector", "Software", 179.00),
    ("Report Builder", "Software", 89.00),
    ("Real-time Monitor", "SaaS", 199.00),
    ("Audit Logger", "SaaS", 59.00),
    ("Schema Explorer", "Software", 39.00),
    ("Query Optimizer", "Software", 159.00),
    ("Data Catalog", "SaaS", 119.00),
    ("Batch Processor", "Software", 89.00),
    ("Stream Analytics", "SaaS", 299.00),
    ("Metadata Manager", "Software", 69.00),
    ("Data Lineage Tracker", "SaaS", 149.00),
]

CUSTOMER_NAMES = [
    ("Alice Johnson", "alice.j@example.com"),
    ("Bob Chen", "bob.chen@example.com"),
    ("Carol Davis", "carol.d@example.com"),
    ("David Kim", "david.kim@example.com"),
    ("Emma Wilson", "emma.w@example.com"),
    ("Frank Lee", "frank.lee@example.com"),
    ("Grace Liu", "grace.liu@example.com"),
    ("Henry Patel", "henry.p@example.com"),
    ("Ivy Zhang", "ivy.z@example.com"),
    ("Jack Ma", "jack.ma@example.com"),
]


def seed():
    print("Seeding demo data...")

    with get_db_session() as db:
        # Check if already seeded
        result = db.execute(text("SELECT COUNT(*) FROM customers"))
        if result.scalar() > 0:
            print(f"Already seeded ({result.scalar()} customers). Skipping.")
            return

        # --- Customers ---
        for i, (name, email) in enumerate(CUSTOMER_NAMES, 1):
            days_ago = random.randint(30, 500)
            signup = datetime.now(timezone.utc) - timedelta(days=days_ago)
            tier = random.choice(TIERS)
            region = REGIONS[i % len(REGIONS)]
            db.execute(text("""
                INSERT INTO customers (name, email, region, signup_date, tier)
                VALUES (:name, :email, :region, :signup, :tier)
            """), {"name": name, "email": email, "region": region,
                   "signup": signup, "tier": tier})
        print(f"  {len(CUSTOMER_NAMES)} customers inserted")

        # --- Products ---
        for name, category, price in PRODUCTS_DATA:
            db.execute(text("""
                INSERT INTO products (name, category, price, stock)
                VALUES (:name, :category, :price, 9999)
            """), {"name": name, "category": category, "price": price})
        print(f"  {len(PRODUCTS_DATA)} products inserted")

        # --- Orders (500 orders over last 90 days) ---
        now = datetime.now(timezone.utc)
        order_ids = []
        for _ in range(500):
            days_ago = random.uniform(0, 90)
            created = now - timedelta(days=days_ago)
            customer_id = random.randint(1, len(CUSTOMER_NAMES))
            status = random.choice(STATUSES)
            result = db.execute(text("""
                INSERT INTO orders (customer_id, created_at, status, total_amount)
                VALUES (:cid, :created, :status, 0) RETURNING id
            """), {"cid": customer_id, "created": created, "status": status})
            order_ids.append(result.scalar())
        print(f"  {len(order_ids)} orders inserted")

        # --- Order Items (1-4 items per order) ---
        total_items = 0
        for order_id in order_ids:
            num_items = random.randint(1, 4)
            order_total = 0.0
            for _ in range(num_items):
                product_id = random.randint(1, len(PRODUCTS_DATA))
                quantity = random.randint(1, 4)
                unit_price = PRODUCTS_DATA[product_id - 1][2]
                subtotal = round(quantity * unit_price, 2)
                order_total += subtotal
                db.execute(text("""
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
                    VALUES (:oid, :pid, :qty, :price, :sub)
                """), {"oid": order_id, "pid": product_id, "qty": quantity,
                       "price": unit_price, "sub": subtotal})
                total_items += 1

            # Update order total
            db.execute(text("""
                UPDATE orders SET total_amount = :total WHERE id = :oid
            """), {"total": round(order_total, 2), "oid": order_id})
        print(f"  {total_items} order items inserted")

        # --- Indexes ---
        for idx_sql in [
            "CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id)",
            "CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id)",
        ]:
            db.execute(text(idx_sql))

        db.commit()
        print("Demo data seeded successfully!")


if __name__ == "__main__":
    seed()
