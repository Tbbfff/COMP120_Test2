# analyze sales data from csv file and calculate total sales, category-wise sales, top product and region-wise distribution

import csv
from collections import defaultdict

SEP = "=" * 40


# --- File reading logic ---

def load_sales_data(filepath):
    records = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                "order_id": row["OrderID"],
                "date":     row["Date"],
                "customer": row["Customer"],
                "product":  row["Product"],
                "category": row["Category"],
                "region":   row["Region"],
                "quantity": int(row["Quantity"]),
                "price":    float(row["Price"]),
            })
    return records


# --- Calculations ---

def analyze(records):
    total_sales = 0.0
    category_sales = defaultdict(float)
    product_sales = defaultdict(float)
    region_sales = defaultdict(float)

    for r in records:
        revenue = r["quantity"] * r["price"]
        total_sales += revenue
        category_sales[r["category"]] += revenue
        product_sales[r["product"]] += revenue
        region_sales[r["region"]] += revenue

    top_product = max(product_sales, key=product_sales.get)

    return {
        "total_sales":    total_sales,
        "category_sales": dict(category_sales),
        "top_product":    (top_product, product_sales[top_product]),
        "region_sales":   dict(region_sales),
    }


# --- Output formatting ---

def print_report(results):
    print(SEP)
    print("  SALES ANALYSIS REPORT")
    print(SEP)

    print("\nTotal Sales: ${:,.2f}".format(results["total_sales"]))

    print("\nCategory-wise Sales:")
    for cat, amount in sorted(results["category_sales"].items(), key=lambda x: -x[1]):
        print("  {:<20} ${:,.2f}".format(cat, amount))

    product, amount = results["top_product"]
    print("\nTop Product: {} (${:,.2f})".format(product, amount))

    print("\nRegion-wise Distribution:")
    total = results["total_sales"]
    for region, amount in sorted(results["region_sales"].items(), key=lambda x: -x[1]):
        pct = (amount / total * 100) if total else 0
        print("  {:<20} ${:,.2f}  ({:.1f}%)".format(region, amount, pct))

    print("\n" + SEP)


# --- High-value orders ---

def print_high_value_orders(records, threshold=200):
    high_orders = [r for r in records if r["quantity"] * r["price"] > threshold]

    print("\n" + SEP)
    print("  ORDERS ABOVE ${}".format(threshold))
    print(SEP)

    if not high_orders:
        print("  None found.")
    else:
        cols = ("ID", "Date", "Customer", "Product", "Qty", "Price", "Total")
        header = "  {:<8} {:<12} {:<14} {:<12} {:>4} {:>7} {:>8}".format(*cols)
        print(header)
        print("  " + "-" * (len(header) - 2))
        for r in high_orders:
            total = r["quantity"] * r["price"]
            print("  {:<8} {:<12} {:<14} {:<12} {:>4} {:>7.2f} {:>8.2f}".format(
                r["order_id"], r["date"], r["customer"], r["product"],
                r["quantity"], r["price"], total,
            ))

    print(SEP)


# --- Entry point ---

if __name__ == "__main__":
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else "sales_data.csv"
    data = load_sales_data(filepath)
    results = analyze(data)
    print_report(results)
    print_high_value_orders(data)
