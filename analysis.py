# analyze sales data from csv file and calculate total sales, category-wise sales, top product and region-wise distribution

import csv
import sys
from collections import defaultdict

SEP = "=" * 40
DASH = "-" * 40


# --- File reading logic ---

def load_sales_data(filepath):
    required_cols = {"OrderID", "Date", "Customer", "Product", "Category", "Region", "Quantity", "Price"}
    records = []

    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            missing = required_cols - set(reader.fieldnames or [])
            if missing:
                print("Error: missing columns in CSV: {}".format(", ".join(sorted(missing))))
                sys.exit(1)

            for i, row in enumerate(reader, start=2):
                try:
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
                except ValueError as e:
                    print("Warning: skipping row {} - {}".format(i, e))

    except FileNotFoundError:
        print("Error: file not found: {}".format(filepath))
        sys.exit(1)
    except PermissionError:
        print("Error: permission denied: {}".format(filepath))
        sys.exit(1)

    if not records:
        print("Error: no valid records found in {}".format(filepath))
        sys.exit(1)

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
        "num_orders":     len(records),
    }


# --- Output formatting ---

def print_report(results):
    print("\n" + SEP)
    print("       SALES ANALYSIS REPORT")
    print(SEP)
    print("  Total Orders : {}".format(results["num_orders"]))
    print("  Total Sales  : ${:,.2f}".format(results["total_sales"]))
    print(DASH)

    print("\n  Category-wise Sales:")
    for cat, amount in sorted(results["category_sales"].items(), key=lambda x: -x[1]):
        bar = "#" * int(amount / 50)
        print("  {:<15} ${:>8,.2f}  {}".format(cat, amount, bar))

    product, amount = results["top_product"]
    print("\n  Top Product  : {} (${:,.2f})".format(product, amount))

    print("\n  Region-wise Distribution:")
    total = results["total_sales"]
    for region, amount in sorted(results["region_sales"].items(), key=lambda x: -x[1]):
        pct = (amount / total * 100) if total else 0
        bar = "#" * int(pct / 2)
        print("  {:<10} ${:>8,.2f}  {:>5.1f}%  {}".format(region, amount, pct, bar))

    print("\n" + SEP)


# --- High-value orders ---

def print_high_value_orders(records, threshold=200):
    high_orders = [r for r in records if r["quantity"] * r["price"] > threshold]

    print("\n" + SEP)
    print("  ORDERS ABOVE ${} ({} found)".format(threshold, len(high_orders)))
    print(SEP)

    if not high_orders:
        print("  None found.")
    else:
        cols = ("ID", "Date", "Customer", "Product", "Qty", "Price", "Total")
        header = "  {:<8} {:<12} {:<14} {:<12} {:>4} {:>7} {:>8}".format(*cols)
        print(header)
        print("  " + "-" * (len(header) - 2))
        for r in sorted(high_orders, key=lambda x: -(x["quantity"] * x["price"])):
            total = r["quantity"] * r["price"]
            print("  {:<8} {:<12} {:<14} {:<12} {:>4} {:>7.2f} {:>8.2f}".format(
                r["order_id"], r["date"], r["customer"], r["product"],
                r["quantity"], r["price"], total,
            ))

    print(SEP)


# --- Entry point ---

if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "sales_data.csv"
    data = load_sales_data(filepath)
    results = analyze(data)
    print_report(results)
    print_high_value_orders(data)
