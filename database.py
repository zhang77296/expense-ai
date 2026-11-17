"""
database.py —— 所有 SQL 都在这个文件里，别的模块不许写 SQL。

设计原则（答辩要点）：
1. 大模型只负责抽字段，绝不生成 SQL；SQL 全部由本文件的函数执行。
2. 全部使用参数化查询（? 占位符），杜绝 SQL 注入。
3. 表结构固定，不按用户输入拼表名/列名。
"""

import csv
import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.getenv("EXPENSE_DB_PATH", "expense.db")


@contextmanager
def get_conn():
    """每次操作开连接、结束自动提交并关闭"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """建表：expenses / categories / budgets"""
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                amount   REAL    NOT NULL,
                category TEXT    NOT NULL,
                date     TEXT    NOT NULL,
                merchant TEXT    DEFAULT '',
                note     TEXT    DEFAULT '',
                source   TEXT    DEFAULT 'text'
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                name TEXT PRIMARY KEY
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                category      TEXT NOT NULL,
                monthly_limit REAL NOT NULL,
                month         TEXT NOT NULL,
                UNIQUE(category, month)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)")

        # 初始化类别白名单（与 schemas.CATEGORIES 保持一致）
        from schemas import CATEGORIES
        for name in CATEGORIES:
            conn.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (name,))


def create_expense(data: dict) -> int:
    """插入一条账单，返回新 id。
    data 需含 amount / category / date，可选 merchant / note / source。
    CSV 里带来的 id 一律忽略，由数据库自己发号。
    """
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO expenses (amount, category, date, merchant, note, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                float(data["amount"]),
                data["category"],
                data["date"],
                data.get("merchant", "") or "",
                data.get("note", "") or "",
                data.get("source", "text") or "text",
            ),
        )
        return cur.lastrowid


def list_expenses(start: str, end: str, category: str | None = None) -> list[dict]:
    """按日期区间查账单，start/end 为 'YYYY-MM-DD'，含端点。"""
    sql = (
        "SELECT id, amount, category, date, merchant, note, source "
        "FROM expenses WHERE date >= ? AND date <= ?"
    )
    params = [start, end]
    if category:
        sql += " AND category = ?"
        params.append(category)
    sql += " ORDER BY date DESC, id DESC"
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def sum_expenses(start: str, end: str, category: str | None = None) -> float:
    """区间求和（可限定类别）。"""
    sql = "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE date >= ? AND date <= ?"
    params = [start, end]
    if category:
        sql += " AND category = ?"
        params.append(category)
    with get_conn() as conn:
        return float(conn.execute(sql, params).fetchone()["total"])


def get_month_stats(month: str) -> dict:
    """month 形如 '2026-11'，返回 {total, count, by_category}"""
    start = f"{month}-01"
    end = f"{month}-31"
    with get_conn() as conn:
        total = float(
            conn.execute(
                "SELECT COALESCE(SUM(amount),0) AS t FROM expenses WHERE date >= ? AND date <= ?",
                (start, end),
            ).fetchone()["t"]
        )
        count = int(
            conn.execute(
                "SELECT COUNT(*) AS c FROM expenses WHERE date >= ? AND date <= ?",
                (start, end),
            ).fetchone()["c"]
        )
        rows = conn.execute(
            """
            SELECT category, SUM(amount) AS amt, COUNT(*) AS cnt
            FROM expenses WHERE date >= ? AND date <= ?
            GROUP BY category ORDER BY amt DESC
            """,
            (start, end),
        ).fetchall()
        by_category = [
            {"category": r["category"], "amount": float(r["amt"]), "count": int(r["cnt"])}
            for r in rows
        ]
    return {"month": month, "total": total, "count": count, "by_category": by_category}


def upsert_budget(category: str, monthly_limit: float, month: str) -> None:
    """设置某月某类别预算，已存在则更新。"""
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO budgets (category, monthly_limit, month) VALUES (?, ?, ?)
            ON CONFLICT(category, month) DO UPDATE SET monthly_limit = excluded.monthly_limit
            """,
            (category, float(monthly_limit), month),
        )


def get_budget(category: str, month: str) -> dict | None:
    """查某月某类别预算，没有返回 None。"""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT category, monthly_limit, month FROM budgets WHERE category = ? AND month = ?",
            (category, month),
        ).fetchone()
        return dict(row) if row else None


def budget_status(category: str, month: str) -> dict:
    """预算使用情况：预算 / 已花 / 剩余 / 是否超支"""
    budget = get_budget(category, month)
    spent = sum_expenses(f"{month}-01", f"{month}-31", category)
    limit = budget["monthly_limit"] if budget else 0.0
    return {
        "category": category,
        "month": month,
        "budget": limit,
        "spent": spent,
        "remaining": limit - spent,
        "over_budget": bool(budget) and spent > limit,
    }


def import_csv(path: str) -> int:
    """导入示例 CSV，返回导入条数。表头：id,amount,category,merchant,date,note,source 均可，缺列不报错。"""
    from schemas import Expense

    n = 0
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            payload = {
                "amount": float(row["amount"]),
                "category": row["category"].strip(),
                "date": row["date"].strip(),
                "merchant": (row.get("merchant") or "").strip(),
                "note": (row.get("note") or "").strip(),
                "source": (row.get("source") or "text").strip(),
            }
            Expense(**payload)  # 过一遍校验，脏数据直接抛错
            create_expense(payload)
            n += 1
    return n


def reset_db():
    """删掉数据库文件后用 init_db 重建（仅自测用）"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()


if __name__ == "__main__":
    reset_db()
    print("建表完成：", DB_PATH)

    create_expense({"amount": 25.0, "category": "餐饮", "date": "2026-11-17", "merchant": "食堂", "note": "午饭"})
    create_expense({"amount": 12.5, "category": "交通", "date": "2026-11-16", "note": "共享单车"})
    create_expense({"amount": 300.0, "category": "教育", "date": "2026-11-10", "merchant": "书店", "note": "教材"})
    print("已插入 3 条")

    print("区间求和（全部）：", sum_expenses("2026-11-01", "2026-11-30"))
    print("区间求和（餐饮）：", sum_expenses("2026-11-01", "2026-11-30", "餐饮"))
    print("账单列表：", len(list_expenses("2026-11-01", "2026-11-30")), "条")

    upsert_budget("餐饮", 600.0, "2026-11")
    upsert_budget("餐饮", 800.0, "2026-11")  # 覆盖测试
    print("预算：", get_budget("餐饮", "2026-11"))
    print("预算状态：", budget_status("餐饮", "2026-11"))

    stats = get_month_stats("2026-11")
    print("月度统计：", stats)
    assert stats["count"] == 3 and stats["total"] == 337.5
    print("全部自测通过")
