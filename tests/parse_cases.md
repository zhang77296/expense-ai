# 成员2 解析测试样例 v0.1

> 日期基准：今天 = 运行测试当天；“今天-1天”表示昨天。
> category 枚举以成员1最终确认为准。

| 编号 | 输入 | 类型 | 期望要点 | 期望 JSON（关键字段） |
|---|---|---|---|---|
| C01 | 昨天中午吃饭花了36 | 正常 | 餐饮/36/昨天/不入库前 ok=true | {"ok":true,"amount":36,"category":"餐饮","date":"今天-1天","aa_flag":false} |
| C02 | 打车回家28.5 | 正常 | 交通/28.5/今天 | {"ok":true,"amount":28.5,"category":"交通","date":"今天"} |
| C03 | 淘宝买衣服199，两人AA | 正常 | 购物/199/aa_flag=true | {"ok":true,"amount":199,"category":"购物","aa_flag":true} |
| C04 | 今天没花钱 | 失败 | 缺金额，ok=false，不入库 | {"ok":false,"error":"缺少金额"} |
| C05 | 前天买咖啡18 | 正常 | 餐饮/18/今天-2天/merchant可能为null | {"ok":true,"amount":18,"category":"餐饮","date":"今天-2天"} |
| C06 | 星巴克咖啡32 | 正常 | 餐饮/32/merchant=星巴克 | {"ok":true,"amount":32,"category":"餐饮","merchant":"星巴克"} |
| C07 | 美团外卖45 | 正常 | 餐饮/45 | {"ok":true,"amount":45,"category":"餐饮"} |
| C08 | 爱奇艺会员25 | 正常 | 娱乐/25 | {"ok":true,"amount":25,"category":"娱乐"} |
| C09 | 房租3500 | 正常 | 居住/3500 | {"ok":true,"amount":3500,"category":"居住"} |
| C10 | 药店买药56 | 正常 | 医疗/56 | {"ok":true,"amount":56,"category":"医疗"} |
| C11 | 买书《Python编程》89 | 正常 | 教育/89 | {"ok":true,"amount":89,"category":"教育"} |
| C12 | 地铁4块 | 正常 | 交通/4 | {"ok":true,"amount":4,"category":"交通"} |
| C13 | 午饭 | 失败/边界 | 缺金额，ok=false | {"ok":false,"error":"缺少金额"} |
| C14 | 花了50 | 边界 | 金额50，类别=其他 | {"ok":true,"amount":50,"category":"其他"} |
| C15 | 餐饮预算1000，已花1100 | 预算 | over_budget=true，remaining=-100 | {"over_budget":true,"remaining":-100} |
| B01 | 餐饮预算1000，已花800 | 预算 | has_budget=true，remaining=200，over_budget=false | {"has_budget":true,"remaining":200,"over_budget":false} |
| B02 | 未设置预算，已花300 | 预算 | has_budget=false | {"has_budget":false,"message":"未设置预算"} |

## 验收标准

- 15 条解析样例中，至少 12 条 ok=true 且关键字段正确。
- C04、C13 必须 ok=false，且不能入库。
- C03 的 aa_flag 必须为 true。
- C15/B01/B02 预算状态字段必须正确。
- 无 Key 时规则兜底也要让 C01/C02/C12 通过。