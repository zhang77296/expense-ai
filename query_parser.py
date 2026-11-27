from datetime import date, timedelta

from stats_service import daily_total, monthly_total, category_summary

FOOD_WORDS = ("吃饭", "餐饮", "午饭", "晚饭")


def parse_question(question):
    day = date.today()
    if "今天" in question:
        pass
    elif "昨天" in question:
        day -= timedelta(days=1)
    else:
        raise ValueError("请在问题里写上“今天”“昨天”“这个月”或“上个月”。")

    if not any(word in question for word in FOOD_WORDS):
        raise ValueError("目前可以查询餐饮支出。")

    return day.isoformat(), "餐饮"


def answer_question(question):
    if "这个月" in question and "哪类" in question and "最多" in question:
        start = date.today().replace(day=1)
        end = (start + timedelta(days=31)).replace(day=1)
        summary = category_summary(start.isoformat(), end.isoformat())

        if not summary:
            return "这个月还没有支出记录。"

        category, amount, percent = summary[0]
        return f"这个月花得最多的是{category}，共 {amount:.2f} 元，占总支出的 {percent:.2f}%。"
    if "这个月" in question and "占比" in question:
        start = date.today().replace(day=1)
        end = (start + timedelta(days=31)).replace(day=1)
        summary = category_summary(start.isoformat(), end.isoformat())

        if not summary:
            return "这个月还没有支出记录。"

        parts = [
            f"{category} {amount:.2f} 元，占 {percent:.2f}%"
            for category, amount, percent in summary
        ]
        return " 这个月的分类支出为：" + "；".join(parts) + "。"
    if "这个月" in question or "上个月" in question:
        if not any(word in question for word in FOOD_WORDS):
            return "目前可以查询餐饮支出。"

        month = date.today().replace(day=1)
        if "上个月" in question:
            month -= timedelta(days=1)

        total = monthly_total(month.year, month.month, "餐饮")
        return f"{month.year}年{month.month}月的餐饮支出合计是 {total:.2f} 元。"

    try:
        day, category = parse_question(question)
    except ValueError as error:
        return str(error)

    total = daily_total(day, category)
    return f"{day} 的{category}支出合计是 {total:.2f} 元。"


if __name__ == "__main__":
    question = input("想查什么？")
    print(answer_question(question))
