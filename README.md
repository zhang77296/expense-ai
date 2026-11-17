# 记账 AI 助手（expense-ai）

2026 GDUF 人工智能工作室二轮考核 · 方向一（AI 应用）· 选题 A：个人记账与消费分析 AI 助手。

一句话记账 → 自动分类统计 → 自然语言查账，全部走本地 FastAPI + SQLite，大模型只负责「抽取字段」，不接触数据库。

## 目录结构

```
expense-ai/
├── main.py            FastAPI 入口，7 个接口都在这里
├── db.py              存储层，所有 SQL 集中于此（白名单模板 + 参数占位符）
├── parser.py          一句话记账解析（本地规则优先，可选大模型补字段）
├── validator.py       数据契约校验（金额 / 类别白名单 / 日期格式）
├── query_engine.py    自然语言查账（意图抽参 → 后端拼 SQL）
├── load_demo.py       导入示例数据
├── demo/bills.csv     示例账单（7 个类别、近 3 个月）
├── static/index.html  网页前端（一句话输入 / 统计 / 查账 / 账单列表）
├── tests/test_basic.py 最小测试集（边界值）
├── requirements.txt
├── .env.example       环境变量样例（真实 .env 不进仓库）
├── Dockerfile
└── docker-compose.yml
```

## 接口清单

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health` | 健康检查 |
| POST | `/record/parse` | `{text, session_id}` → 草稿或追问 |
| POST | `/record/add` | 直接录入一条 |
| POST | `/record/confirm` | `{draft_id, 修正后字段}` → 入库 |
| GET | `/stats?month=&category=` | 分类统计 |
| POST | `/query/ask` | `{question}` → 自然语言查账 |
| GET | `/records?month=` | 账单列表 |

数据契约：`amount / category / time / remark`；`time` 为 `YYYY-MM-DD`；
类别白名单 `餐饮/交通/购物/娱乐/住房/医疗/其他`。

## 环境步骤

1. 安装 Python 3.11（勾选 Add python.exe to PATH），`python --version` 应显示 3.11.x。
2. 用 VS Code 打开本项目文件夹。
3. 在项目目录建虚拟环境并激活：

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass   # 仅本窗口有效，可跳过
.\.venv\Scripts\Activate.ps1
```

4. 安装依赖：

```powershell
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 运行命令

```powershell
python load_demo.py                 # 导入示例账单（会先清空旧数据）
uvicorn main:app --reload           # 启动服务
```

浏览器打开 <http://127.0.0.1:8000/> 即可使用；接口文档在 <http://127.0.0.1:8000/docs>。

跑测试：

```powershell
python tests/test_basic.py
```

Docker 方式：

```bash
docker compose up --build
```

## 已验证功能

- 一句话记账：`昨天午饭花了 25 块` → `{amount:25, category:餐饮, time:昨天}`，中文金额「二十块」也能识别
- 缺字段追问：`昨天和朋友吃饭` → 追问「这笔花了多少钱？」，补齐后自动成草稿（多轮澄清）
- 数据校验：负数金额、非法类别、非 `YYYY-MM-DD` 日期一律拒绝入库
- 分类统计：按类别、按日汇总，前端柱状条展示
- 自然语言查账：`这个月吃饭花了多少` / `上个月最贵的一笔` / `这个月几笔` 均返回中文结论
- 查账安全：大模型只抽 `{time_range, category, target}`，SQL 全部后端白名单拼接 + 占位符，模型不接触数据库
- 密钥管理：`.env` 已加入 `.gitignore`，仓库只放 `.env.example`

## 已知问题

- 金额解析是规则匹配，遇到「三百五」「一百二」这类口语省略说法可能识别成 102 而不是 120，需要后续补规则。
- OCR 小票识别接口（`/record/ocr`）尚未接入，前端也没有上传入口，属待办。
- 查账的意图识别目前是关键词匹配，复杂问句（如「上个月吃饭和交通一共多少」）只能答出主要类别。
- 草稿存在内存里，服务重启后未确认的草稿会丢失。
