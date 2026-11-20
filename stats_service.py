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


if __name__ == "__main__":
    total = daily_total("2026-11-20", "餐饮")
    print(f"餐饮合计：{total:.2f} 元")
