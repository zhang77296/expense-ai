from datetime import date, timedelta

import database


def daily_total(day, category):
    next_day = (date.fromisoformat(day) + timedelta(days=1)).isoformat()
    rows = database.list_expenses(day, next_day)

    return sum(
        row["amount"]
        for row in rows
        if row["date"] == day and row["category"] == category
    )
def monthly_total(year, month, category):
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)

    start_text = start.isoformat()
    end_text = end.isoformat()
    rows = database.list_expenses(start_text, end_text)

    return sum(
        row["amount"]
        for row in rows
        if start_text <= row["date"] < end_text
        and row["category"] == category
    )

if __name__ == "__main__":
    total = daily_total("2026-11-20", "餐饮")
    print(f"餐饮合计：{total:.2f} 元")
def category_summary(start, end):
    totals = {}

    for row in database.list_expenses(start, end):
        if start <= row["date"] < end:
            category = row["category"]
            totals[category] = totals.get(category, 0) + row["amount"]

    grand_total = sum(totals.values())
    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)

    return [
        (category, round(amount, 2),
         round(amount / grand_total * 100, 2) if grand_total else 0.0)
        for category, amount in ranked
    ]

