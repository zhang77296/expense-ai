# llm_parser.py
from dotenv import load_dotenv
load_dotenv() # 这行代码会自动把 .env 里的变量加载到环境里
import json
import os
import re
from datetime import date, timedelta
from category_service import normalize_category

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "expense_parse.txt")

def _extract_json(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^```(?:json)?|```$", "", s, flags=re.M).strip()
    i, j = s.find("{"), s.rfind("}")
    if i < 0 or j < i:
        raise ValueError("模型未返回 JSON")
    return s[i:j + 1]

def _rule_based(text: str, today: date) -> dict:
    amount = None
    m = re.search(r"(?:花了|消费|付了|用了|共|合计)\s*(\d+(?:\.\d+)?)\s*(?:元|块|rmb|¥)?", text, re.I)
    if m:
        amount = float(m.group(1))
    else:
        m2 = re.search(r"(\d+(?:\.\d+)?)\s*(?:元|块|rmb|¥)", text, re.I)
        if m2:
            amount = float(m2.group(1))
        else:
            nums = re.findall(r"\d+(?:\.\d+)?", text)
            if nums:
                amount = float(nums[-1])

    d = today
    if "前天" in text:
        d = today - timedelta(days=2)
    elif "昨天" in text:
        d = today - timedelta(days=1)

    return {
        "amount": amount,
        "date": d.isoformat(),
        "category": normalize_category(None, None, None, text),
        "merchant": None,
        "note": text,
        "confidence": 0.5,
        "missing_fields": [] if amount else ["amount"],
    }

def _call_llm(text: str, today: date):
    # 按规范改成 LLM_API_KEY
    api_key = os.getenv("LLM_API_KEY")
    if not api_key or OpenAI is None:
        return _rule_based(text, today)

    kwargs = {"api_key": api_key}
    if os.getenv("LLM_BASE_URL"):
        kwargs["base_url"] = os.getenv("LLM_BASE_URL")

    client = OpenAI(**kwargs)
    
    with open(PROMPT_PATH, encoding="utf-8") as f:
        prompt = f.read()

    resp = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"今天是{today.isoformat()}。输入：{text}"},
        ],
    )
    return resp.choices[0].message.content

# 按规范：函数名必须叫 parse_text
def parse_text(text: str, today: date = None) -> dict:
    """主解析入口：返回规范要求的 dict 结构"""
    today = today or date.today()
    if not text or not text.strip():
        return {"error": "输入为空"}

    try:
        raw = _call_llm(text.strip(), today)
        obj = raw if isinstance(raw, dict) else json.loads(_extract_json(raw))

        obj["date"] = obj.get("date") or today.isoformat()
        obj["category"] = normalize_category(
            obj.get("category"), obj.get("merchant"), obj.get("note"), text
        )
        obj.setdefault("confidence", 0.8)

        if obj.get("amount") in (None, 0, ""):
            obj["missing_fields"] = ["amount"]
        else:
            obj["missing_fields"] = obj.get("missing_fields", [])

        return obj  # 直接返回字典，不包外壳
    except Exception as e:
        return {"error": f"解析失败：{e}"}

# ========== 本地测试代码 ==========
if __name__ == "__main__":
    print("--- 开始测试 ---")
    test_inputs = ["昨天中午吃饭花了36", "打车回家28.5", "今天没花钱"]
    for t in test_inputs:
        result = parse_text(t)
        print(f"输入：{t} -> 结果：{result}")