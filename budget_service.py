# budget_service.py
from datetime import date
import json

def _parse_month(month: str = None):
    """解析月份格式，如果没传就默认当前月"""
    if month:
        y, m = map(int, month.split("-"))
        return y, m, f"{y:04d}-{m:02d}"
    t = date.today()
    return t.year, t.month, f"{t.year:04d}-{t.month:02d}"

def month_range(month: str = None):
    """获取某个月的起止日期"""
    y, m, mstr = _parse_month(month)
    start = date(y, m, 1)
    end = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
    return start, end, mstr

def get_budget_status(db, category: str = None, month: str = None):
    """
    获取预算状态。
    db: 数据库对象（包含 get_budget 和 sum_expenses 方法）
    category: 类别，None 表示总预算
    month: 'YYYY-MM' 格式
    """
    start, end, mstr = month_range(month)
    
    # 1. 查这个类别的预算上限 (实际联调时解开注释)
    # limit = db.get_budget(category=category, month=mstr)
    limit = 1000.0 # 测试用的假数据
    
    # 2. 查这个月已经花了多少 (实际联调时解开注释)
    # spent = db.sum_expenses(start=start, end=end, category=category)
    spent = 1100.0 # 测试用的假数据

    if limit is None:
        return {
            "month": mstr,
            "category": category,
            "has_budget": False,
            "spent": spent,
            "message": "未设置预算",
        }

    remaining = limit - spent
    over = remaining < 0
    label = category or "总"
    
    return {
        "month": mstr,
        "category": category,
        "has_budget": True,
        "monthly_limit": limit,
        "spent": spent,
        "remaining": remaining,
        "over_budget": over,
        "message": f"{label}预算已超支{abs(remaining):.2f}元" if over else f"{label}预算剩余{remaining:.2f}元",
    }

# ========== 本地测试代码 ==========
if __name__ == "__main__":
    print("--- 开始测试预算 ---")
    # 这里传 None 作为假 db，因为我们目前只是测逻辑
    result = get_budget_status(db=None, category="餐饮", month="2026-11")
    print(json.dumps(result, ensure_ascii=False, indent=2))