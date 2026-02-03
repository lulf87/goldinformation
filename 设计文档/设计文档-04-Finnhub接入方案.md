# 设计文档 04：Finnhub 接入方案（V1）

本文档用于指导开发接入新闻接口，满足“新闻事件解读”的需求。

## 1. 接口清单（V1）

所有接口均需带对应的 API Key

### 1.1 新闻
- 接口：`/news`
- 参数：`category=general`
- 用途：获取市场新闻（V1 使用）

## 2. 字段对照表（API -> 统一字段）

### 2.1 新闻（Finnhub News）
| Finnhub 字段 | 统一字段 | 说明 |
|---|---|---|
| `datetime` | `news_time` | 时间 |
| `headline` | `title` | 标题 |
| `summary` | `content` | 具体内容 |
| `source` | `source` | 来源媒体 |
| `url` | `url` | 原文链接 |
| `sentiment`（无） | `sentiment` | 用关键词规则生成 |

## 3. 最小实施步骤（V1）

### 阶段 1：环境配置
1) `.env` 增加 `FINNHUB_API_KEY`（新闻）
2) 后端配置读取并暴露该值

### 阶段 2：新闻接入
1) 调用 `/news?category=general`
2) 获取最近 7-10 条
3) 按关键词规则生成情绪倾向

### 阶段 4：分析融合
1) `MarketAnalysis` 新增字段：
   - `news_items`
2) 在 `explanation` 中增加新闻提示（基于具体内容）

### 阶段 5：前端展示
1) Dashboard 增加“新闻事件”板块（具体内容）

## 4. 情绪规则（最小版）
- 关键词包含：`rate cut`, `inflation`, `risk-off` -> 偏多
- 包含：`rate hike`, `strong dollar` -> 偏空
- 其他 -> 中性

## 4.1 情绪规则（LLM 增强，可选）
- 允许使用大模型对新闻与事件进行语义理解
- 输出字段可包含：`llm_sentiment_reason`，用于解释情绪来源
- 若 LLM 不可用，则回退到关键词规则

## 5. 验收清单（勾选版）
- [ ] `.env` 中存在 `FINNHUB_API_KEY`
- [ ] `/analysis` 返回 `news_items` 列表（>=3 条）
- [ ] `explanation` 中出现“新闻事件提示”
- [ ] Dashboard 有“新闻事件”模块（具体内容）
- [ ] Chat 支持“新闻事件”问答
- [ ] LLM 未接入时，仍可正常输出（回退规则生效）
