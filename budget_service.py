# budget_service.py
from datetime import date

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
    start, end, mstr = month_range(month)
    
    if category is None:
        category = ""

    # 1. 查这个类别的预算上限
    limit_data = db.get_budget(category=category, month=mstr)
    
    # 兼容处理：如果返回的是字典，就提取数字；如果是数字，直接用
    limit = None
    if limit_data is not None:
        if isinstance(limit_data, dict):
            # 尝试从字典里提取金额字段（成员1可能叫 monthly_limit 或 limit）
            limit = limit_data.get('monthly_limit') or limit_data.get('limit')
        else:
            limit = limit_data

    # 2. 查这个月已经花了多少
    query_category = category if category != "" else None
    spent = db.sum_expenses(start=start, end=end, category=query_category)

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