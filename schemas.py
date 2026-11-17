from pydantic import BaseModel, field_validator

# 类别白名单：全队唯一来源，谁都不许另写一份
CATEGORIES = ["餐饮", "交通", "购物", "娱乐", "住房", "医疗", "教育", "其他"]

SOURCE_TYPES = ["text", "ocr"]


class Expense(BaseModel):
    """一条账单：入库前的形态。注意没有 id，id 由数据库生成"""
    amount: float
    category: str
    date: str
    merchant: str = ""
    note: str = ""
    source: str = "text"

    @field_validator("amount")
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("金额必须是正数")
        return v

    @field_validator("category")
    def category_in_whitelist(cls, v):
        if v not in CATEGORIES:
            raise ValueError(f"类别必须是 {CATEGORIES} 之一")
        return v

    @field_validator("source")
    def source_valid(cls, v):
        if v not in SOURCE_TYPES:
            raise ValueError("source 只能是 text 或 ocr")
        return v


class ExpenseDraft(BaseModel):
    """解析出来的草稿：还没入库，等用户确认"""
    draft_id: str
    data: Expense
    confidence: float = 1.0
    missing_fields: list[str] = []


class ExpenseOut(Expense):
    """从数据库读出来的账单：多了 id，给 /records 返回用"""
    id: int


def normalize_category(value: str) -> str:
    """模型给的类别不在白名单时，统一归到「其他」，不让脏数据进库"""
    return value if value in CATEGORIES else "其他"
