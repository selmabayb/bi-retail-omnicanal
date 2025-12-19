import os
import math
import random
from datetime import date, timedelta
import csv

# =========================
# CONFIG (tu peux modifier)
# =========================
SEED = 42
START_DATE = date(2022, 1, 1)
END_DATE   = date(2024, 12, 31)

N_CUSTOMERS = 8000
N_PRODUCTS  = 450
N_STORES    = 35

# Objectif de volume (approx). Si tu veux + gros: 120000 par ex.
TARGET_SALES_ROWS = 50000

OUT_DIR = os.path.join("data", "raw")

random.seed(SEED)

REGIONS = [
    "Île-de-France", "Auvergne-Rhône-Alpes", "Nouvelle-Aquitaine", "Occitanie",
    "Hauts-de-France", "Provence-Alpes-Côte d’Azur", "Grand Est", "Bretagne",
    "Pays de la Loire", "Normandie", "Bourgogne-Franche-Comté", "Centre-Val de Loire"
]

CATEGORIES = {
    "Vêtements": ["T-shirts", "Jeans", "Robes", "Manteaux", "Pulls", "Chemises"],
    "Chaussures": ["Sneakers", "Bottes", "Sandales", "Ville"],
    "Accessoires": ["Sacs", "Ceintures", "Casquettes", "Bijoux"],
    "Beauté": ["Parfum", "Skincare", "Makeup"],
    "Maison": ["Déco", "Textile", "Cuisine"]
}

SEGMENTS = ["Budget", "Mainstream", "Premium"]

CHANNELS = [
    (1, "Online"),
    (2, "Store"),
]

# =========================
# Helpers
# =========================
def daterange(d1, d2):
    d = d1
    while d <= d2:
        yield d
        d += timedelta(days=1)

def yyyymmdd(d: date) -> int:
    return d.year * 10000 + d.month * 100 + d.day

def month_name(m):
    names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return names[m-1]

def week_of_year(d: date) -> int:
    return int(d.isocalendar().week)

def dow(d: date) -> int:
    return int(d.isoweekday())  # 1=Mon ... 7=Sun

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

# Saison + événements (simple mais efficace pour des graphes crédibles)
def season_multiplier(d: date) -> float:
    # base sinus annual
    day_of_year = d.timetuple().tm_yday
    base = 1.0 + 0.15 * math.sin(2 * math.pi * (day_of_year / 365.0))

    # pics fin d'année
    if d.month in (11, 12):
        base *= 1.20

    # soldes (janvier, juin)
    if d.month in (1, 6):
        base *= 1.10

    # weekends = plus de ventes
    if dow(d) in (6, 7):
        base *= 1.08

    return base

def online_share(d: date) -> float:
    # Online progresse de 35% (2022) -> 55% (2024)
    # linéaire sur le temps
    total_days = (END_DATE - START_DATE).days
    t = (d - START_DATE).days / total_days
    return 0.35 + t * (0.55 - 0.35)

def weighted_choice(items, weights):
    r = random.random() * sum(weights)
    s = 0.0
    for it, w in zip(items, weights):
        s += w
        if r <= s:
            return it
    return items[-1]

# =========================
# Generate dimensions
# =========================
def gen_dim_date():
    rows = []
    for d in daterange(START_DATE, END_DATE):
        rows.append({
            "date_id": yyyymmdd(d),
            "date": d.isoformat(),
            "year": d.year,
            "month": d.month,
            "month_name": month_name(d.month),
            "quarter": (d.month - 1)//3 + 1,
            "week": week_of_year(d),
            "day_of_week": dow(d)
        })
    return rows

def gen_dim_channel():
    return [{"channel_id": cid, "channel_name": name} for cid, name in CHANNELS]

def gen_dim_stores():
    rows = []
    for i in range(1, N_STORES + 1):
        region = random.choice(REGIONS)
        city = f"City_{i:02d}"
        rows.append({
            "store_id": i,
            "store_name": f"Store_{i:02d}",
            "city": city,
            "region": region,
            "country": "France",
            "is_active": 1
        })
    return rows

def gen_dim_products():
    rows = []
    prod_id = 1
    for _ in range(N_PRODUCTS):
        cat = random.choice(list(CATEGORIES.keys()))
        sub = random.choice(CATEGORIES[cat])
        brand = random.choice(["OmniBasics", "UrbanLine", "Maison+","BelleVie","SportyCo"])
        # prix selon catégorie
        if cat == "Vêtements":
            base_price = random.uniform(15, 120)
        elif cat == "Chaussures":
            base_price = random.uniform(35, 180)
        elif cat == "Accessoires":
            base_price = random.uniform(10, 150)
        elif cat == "Beauté":
            base_price = random.uniform(8, 110)
        else:
            base_price = random.uniform(12, 200)

        rows.append({
            "product_id": f"P{prod_id:05d}",
            "product_name": f"{sub} {brand} {prod_id:05d}",
            "category": cat,
            "subcategory": sub,
            "brand": brand,
            "list_price": round(base_price, 2)
        })
        prod_id += 1
    return rows

def gen_dim_customers():
    rows = []
    for i in range(1, N_CUSTOMERS + 1):
        region = random.choice(REGIONS)
        segment = weighted_choice(SEGMENTS, [0.30, 0.55, 0.15])
        rows.append({
            "customer_id": f"C{i:06d}",
            "customer_name": f"Customer_{i:06d}",
            "segment": segment,
            "city": f"CityC_{random.randint(1,200):03d}",
            "region": region,
            "country": "France"
        })
    return rows

# =========================
# Generate fact_sales
# =========================
def gen_fact_sales(dim_products, dim_customers, dim_stores):
    products = dim_products
    customers = dim_customers
    stores = dim_stores

    # Pour rendre le truc réaliste: certains clients achètent plus souvent
    customer_weights = []
    for c in customers:
        # Zipf-like: quelques gros acheteurs
        idx = int(c["customer_id"][1:])
        w = 1.0 / (1 + (idx ** 0.35))
        # segment influence
        if c["segment"] == "Premium":
            w *= 1.4
        elif c["segment"] == "Budget":
            w *= 0.9
        customer_weights.append(w)

    # produits populaires
    product_weights = []
    for p in products:
        cat = p["category"]
        w = 1.0
        if cat in ("Vêtements", "Chaussures"):
            w *= 1.25
        if "Sneakers" in p["subcategory"]:
            w *= 1.15
        product_weights.append(w * random.uniform(0.7, 1.3))

    all_dates = list(daterange(START_DATE, END_DATE))

    rows = []
    order_counter = 1

    # On répartit TARGET_SALES_ROWS sur les jours avec saisonnalité
    base_per_day = TARGET_SALES_ROWS / len(all_dates)

    for d in all_dates:
        mult = season_multiplier(d)
        day_target = max(1, int(base_per_day * mult))

        # bruit
        day_target = int(day_target * random.uniform(0.75, 1.35))

        for _ in range(day_target):
            order_id = f"ORD{order_counter:09d}"
            order_counter += 1

            channel_is_online = random.random() < online_share(d)
            channel_id = 1 if channel_is_online else 2
            channel_name = "Online" if channel_is_online else "Store"

            # store only if Store
            if channel_name == "Store":
                st = random.choice(stores)
                store_id = st["store_id"]
                region = st["region"]
                store_name = st["store_name"]
            else:
                store_id = ""
                store_name = ""
                # région côté online: on la met selon client (plus logique)
                region = ""

            cust = weighted_choice(customers, customer_weights)
            customer_id = cust["customer_id"]
            if channel_name == "Online":
                region = cust["region"]

            prod = weighted_choice(products, product_weights)
            product_id = prod["product_id"]
            category = prod["category"]

            # quantité
            qty = 1
            if category in ("Vêtements", "Beauté"):
                qty = weighted_choice([1,2,3], [0.70,0.22,0.08])
            else:
                qty = weighted_choice([1,2], [0.82,0.18])

            # prix & discount réaliste
            price = prod["list_price"]
            # stores ont parfois un panier plus élevé
            if channel_name == "Store":
                price *= random.uniform(0.98, 1.08)
            else:
                price *= random.uniform(0.95, 1.05)

            # discount (soldes + promos online)
            disc_rate = 0.0
            if d.month in (1, 6):  # soldes
                disc_rate = random.uniform(0.05, 0.35)
            elif channel_name == "Online":
                disc_rate = random.uniform(0.00, 0.20)
            else:
                disc_rate = random.uniform(0.00, 0.12)

            revenue = qty * price * (1 - disc_rate)

            rows.append({
                "order_id": order_id,
                "order_date": d.isoformat(),
                "date_id": yyyymmdd(d),
                "customer_id": customer_id,
                "product_id": product_id,
                "channel_id": channel_id,
                "channel": channel_name,
                "store_id": store_id,
                "store": store_name,
                "region": region,
                "quantity": qty,
                "list_price": round(price, 2),
                "discount_rate": round(disc_rate, 4),
                "revenue": round(revenue, 2)
            })

    # Si on a généré un peu plus/moins que TARGET (normal), on ajuste en coupant
    if len(rows) > TARGET_SALES_ROWS:
        rows = rows[:TARGET_SALES_ROWS]

    return rows

# =========================
# Write CSV
# =========================
def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def main():
    ensure_dir(OUT_DIR)

    dim_date = gen_dim_date()
    dim_channel = gen_dim_channel()
    dim_stores = gen_dim_stores()
    dim_products = gen_dim_products()
    dim_customers = gen_dim_customers()

    fact_sales = gen_fact_sales(dim_products, dim_customers, dim_stores)

    write_csv(os.path.join(OUT_DIR, "dim_date.csv"), dim_date,
              ["date_id","date","year","month","month_name","quarter","week","day_of_week"])
    write_csv(os.path.join(OUT_DIR, "dim_channel.csv"), dim_channel,
              ["channel_id","channel_name"])
    write_csv(os.path.join(OUT_DIR, "dim_stores.csv"), dim_stores,
              ["store_id","store_name","city","region","country","is_active"])
    write_csv(os.path.join(OUT_DIR, "dim_products.csv"), dim_products,
              ["product_id","product_name","category","subcategory","brand","list_price"])
    write_csv(os.path.join(OUT_DIR, "dim_customers.csv"), dim_customers,
              ["customer_id","customer_name","segment","city","region","country"])
    write_csv(os.path.join(OUT_DIR, "fact_sales.csv"), fact_sales,
              ["order_id","order_date","date_id","customer_id","product_id","channel_id","channel",
               "store_id","store","region","quantity","list_price","discount_rate","revenue"])

    print("✅ Dataset generated in:", OUT_DIR)
    print(" - fact_sales.csv:", len(fact_sales), "rows")
    print(" - dim_products.csv:", len(dim_products))
    print(" - dim_customers.csv:", len(dim_customers))
    print(" - dim_stores.csv:", len(dim_stores))
    print(" - dim_date.csv:", len(dim_date))
    print(" - dim_channel.csv:", len(dim_channel))

if __name__ == "__main__":
    main()
