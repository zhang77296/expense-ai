from datetime import date, timedelta

from stats_service import daily_total


def parse_question(question):
    if "今天" in question:
        day = date.today()
    elif "昨天" in question:
        day = date.today() - timedelta(days=1)
    else:
        raise ValueError("请在问题里写上“今天”或“昨天”。")

    if not any(word in question for word in ("吃饭", "餐饮", "午饭", "晚饭")):
        raise ValueError("目前可以查餐饮支出，例如“今天吃饭花了多少”。")

    return day.isoformat(), "餐饮"


def answer_question(question):
    try:
        day, category = parse_question(question)
        total = daily_total(day, category)
        return f"{day} 的{category}支出合计是 {total:.2f} 元。"
    except Exception as error:
        return "暂时不支持该类型查询，目前仅支持餐饮账单查询"


if __name__ == "__main__":
    question = input("想查什么？")
    try:
        print(answer_question(question))
    except ValueError as error:
        print(error)
