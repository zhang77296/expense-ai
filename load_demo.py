import csv
import sqlite3
from pathlib import Path

DB_PATH = "expense.db"
CSV_PATH = "demo_bills.csv"

def load_demo_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute("""
                INSERT INTO expenses (date, category, amount, note)
                VALUES (?, ?, ?, ?)
            """, (row["date"], row["category"], float(row["amount"]), row["remark"]))

    conn.commit()
    conn.close()
    print("✅ 样例账单导入成功！")

if __name__ == "__main__":
    if not Path(CSV_PATH).exists():
        print("❌ 找不到 demo_bills.csv")
    else:
        load_demo_data()