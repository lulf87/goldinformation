# LLM 集成实施计划 (阶段 15)

## 项目概述
在黄金交易 Agent 中集成 LLM 作为可选增强层,提升教学型解释的自然语言质量,并增强新闻/宏观语义理解能力。

### 核心目标
- 提升解释文本的自然度和教学性
- 增强新闻情绪分析的准确性(超越关键词规则)
- 支持 Chat 接口的更自然问答
- **关键**: LLM 不可用时,系统仍能正常工作(回退到规则模板)

### 用户偏好(已确认)
- **LLM 提供商**: OpenRouter
- **模型选择**: Anthropic Claude 3.5 Sonnet
- **频率控制**: 适中控制(软限制) - 超过限制时显示警告但仍允许手动触发
- **优先级**: 规则解释有待改进,LLM 增强是重点

---

## 实施阶段

### 阶段 1: 配置与开关
**状态**: `completed`
**目标**: 添加 LLM 相关配置,实现功能开关

**任务清单**:
- [x] 在 `backend/core/config.py` 添加配置项:
  - `OPENROUTER_API_KEY: Optional[str]` - OpenRouter API Key
  - `OPENROUTER_BASE_URL: str` - 固定为 https://openrouter.ai/api/v1
  - `LLM_MODEL: str` - 模型名称,默认 "anthropic/claude-3.5-sonnet"
  - `LLM_ENABLED: bool` - LLM 功能开关,默认 False
  - `LLM_TIMEOUT: int` - 请求超时时间(秒),默认 30
  - `LLM_MAX_RETRIES: int` - 最大重试次数,默认 2
- [x] 在 `.env.example` 添加配置示例
- [x] 验收: ✅ 配置加载正常,默认关闭 LLM

**涉及文件**:
- `backend/core/config.py`
- `.env.example`

---

### 阶段 2: LLM 服务层
**状态**: `completed`
**目标**: 创建统一的 LLM 客户端服务

**任务清单**:
- [x] 创建 `backend/services/llm_client.py`:
  - 实现 `LLMClient` 类
  - `generate_explanation()` - 生成教学型解释
  - `analyze_news_sentiment()` - 分析新闻情绪
  - `answer_chat_question()` - 回答聊天问题
  - 超时处理、错误重试、回退机制
  - 请求日志记录(耗时、成功/失败、token 使用)
- [x] 实现频率限制器:
  - 每日自动更新调用计数
  - 手动刷新调用计数(最多 3 次/天)
  - Chat 调用不计入限制
  - 超过限制时记录警告日志
- [x] 验收:
  - ✅ LLM 不可用时自动回退,不抛出异常
  - ✅ 超时自动重试,最多重试 N 次
  - ✅ 调用日志正确记录

**涉及文件**:
- `backend/services/llm_client.py` (新增)

---

### 阶段 3: 数据模型扩展
**状态**: `completed`
**目标**: 扩展数据模型以支持 LLM 字段

**任务清单**:
- [x] 在 `backend/models/schemas.py` 扩展 `MarketAnalysis`:
  - `llm_explanation: Optional[str]` - LLM 生成的教学型解释
  - `llm_news_summary: Optional[str]` - LLM 生成的新闻情绪摘要
- [x] 验收: ✅ 新字段为可选,不影响现有 API

**涉及文件**:
- `backend/models/schemas.py`

---

### 阶段 4: 解释生成接入 LLM
**状态**: `completed`
**目标**: 在策略引擎中接入 LLM 生成解释

**任务清单**:
- [x] 修改 `backend/services/strategy.py`:
  - 在 `StrategyEngine.__init__()` 中初始化 `LLMClient`
  - 在 `analyze()` 方法中:
    - 规则生成基础解释(保持现有逻辑)
    - 如果 `LLM_ENABLED=True`,调用 LLM 生成 `llm_explanation`
    - LLM 失败时自动回退到规则解释
  - 在 `_generate_explanation()` 中保持规则模板逻辑
- [x] 设计 LLM Prompt:
  - 输入: 市场状态、信号、关键位、宏观/新闻摘要
  - 要求: 语气稳健、避免强烈承诺、面向交易新手
  - 输出: 结构化的教学型解释
- [x] 验收:
  - ✅ LLM 关闭时,使用规则解释
  - ✅ LLM 开启时,优先显示 LLM 解释
  - ✅ LLM 失败时,自动回退到规则解释
  - ✅ 解释内容与规则信号一致

**涉及文件**:
- `backend/services/strategy.py`

---

### 阶段 5: 新闻情绪语义增强
**状态**: `completed`
**目标**: 使用 LLM 增强新闻情绪分析准确性

**任务清单**:
- [x] 修改 `backend/services/data_provider.py`:
  - 在 `get_news_sentiment()` 后增加可选 LLM 判断
  - 输入: 新闻标题+摘要(前 10 条)
  - 输出: 更准确的情绪判断 + 简短解释
  - LLM 不可用时,继续使用关键词规则
- [x] 设计 LLM Prompt:
  - 输入: 新闻标题列表
  - 要求: 识别否定/反转语义,避免关键词误判
  - 输出: 每条新闻的情绪 + 整体情绪摘要
- [x] 验收:
  - ✅ LLM 关闭时,使用关键词规则
  - ✅ LLM 开启时,提供更准确的情绪分析
  - ✅ 能正确识别"如无意外"等否定语义

**涉及文件**:
- `backend/services/data_provider.py`

---

### 阶段 6: Chat 接入 LLM
**状态**: `completed`
**目标**: 在 Chat 接口中优先使用 LLM

**任务清单**:
- [x] 修改 `backend/api/routes.py` 的 `/chat` 接口:
  - 优先尝试 LLM(带当前分析上下文)
  - LLM 失败或关闭时,回退到现有规则问答
  - 为 LLM 提供足够的上下文:当前分析、信号、关键位、宏观/新闻
- [x] 设计 LLM Prompt:
  - 角色: 黄金交易教学助手
  - 约束: 回答不超出系统信号范围,保持一致性
  - 输入: 用户问题 + 当前分析上下文
- [x] 验收:
  - ✅ LLM 关闭时,使用规则问答
  - ✅ LLM 开启时,提供更自然的对话体验
  - ✅ LLM 回答与当前分析一致,不冲突

**涉及文件**:
- `backend/api/routes.py`

---

### 阶段 7: 前端适配
**状态**: `completed`
**目标**: 前端支持显示 LLM 增强字段

**任务清单**:
- [x] 修改 `frontend/src/api/index.ts`:
  - 扩展 `MarketAnalysis` 类型,添加 `llm_explanation` 和 `llm_news_summary`
- [x] 修改 `frontend/src/views/DashboardView.vue`:
  - 优先显示 `llm_explanation`,如果存在
  - 如果不存在,显示规则 `explanation`
  - 在新闻卡片中显示 `llm_news_summary`,如果存在
- [x] 验收:
  - ✅ LLM 解释优先显示
  - ✅ 无 LLM 解释时,规则解释正常显示
  - ✅ UI 不因 LLM 字段缺失而损坏

**涉及文件**:
- `frontend/src/api/index.ts`
- `frontend/src/views/DashboardView.vue`

---

### 阶段 8: 日志与成本控制
**状态**: `completed`
**目标**: 完善日志记录和成本控制

**任务清单**:
- [x] 实现 LLM 调用日志:
  - 记录每次 LLM 调用的:时间、耗时、成功/失败、token 使用
  - 日志文件: `logs/llm_calls.log`
- [x] 实现调用频率限制:
  - 每日自动更新:记录调用次数,超过时警告
  - 手动刷新限制:记录手动刷新次数,超过 3 次时警告
  - Chat 调用:不计入限制,但记录日志
- [x] 添加管理端点(可选):
  - `GET /api/v1/llm/stats` - 查看调用统计
  - `POST /api/v1/llm/reset-counters` - 重置计数器
- [x] 验收:
  - ✅ 所有 LLM 调用都有日志记录
  - ✅ 超过频率限制时记录警告
  - ✅ 可通过 API 查看使用统计

**涉及文件**:
- `backend/services/llm_client.py`
- `backend/api/routes.py` (可选,添加管理端点)

---

### 阶段 9: 测试与验收
**状态**: `completed`
**目标**: 端到端测试,确保功能正常

**任务清单**:
- [x] 单元测试:
  - `backend/tests/test_llm_client.py` - LLM 客户端测试
  - 测试回退机制、重试逻辑、错误处理
- [x] 集成测试:
  - 测试 LLM 开启/关闭两种场景
  - 测试各接入点的功能正常
  - 测试频率限制和日志记录
- [x] 手动测试:
  - LLM 关闭时,系统正常工作
  - LLM 开启时,解释更自然
  - LLM 失败时,自动回退
- [x] 性能测试:
  - LLM 调用不影响响应时间太多(目标: <5 秒)
  - 超时和重试机制正常工作

**验收清单(最终)**:
- [x] LLM 不可用时,系统正常输出信号和解释
- [x] LLM 开启时,解释质量明显提升
- [x] 新闻情绪分析更准确,能识别语义
- [x] Chat 体验更自然,回答一致
- [x] 所有关键点都有日志记录
- [x] 频率限制正常工作,成本可控

---

## 错误处理策略

### LLM 调用失败场景
| 场景 | 处理方式 | 用户体验 |
|------|----------|----------|
| API Key 未配置 | 跳过 LLM,使用规则 | 正常,无提示 |
| 网络超时 | 重试 2 次,仍失败则回退 | 稍慢,但正常 |
| API 错误(4xx/5xx) | 记录日志,回退到规则 | 正常,后台记录错误 |
| 速率限制 | 记录警告,回退到规则 | 正常,日志警告 |
| 输出解析失败 | 记录日志,回退到规则 | 正常,后台记录错误 |

### 回退机制设计原则
1. **静默回退**: 用户无感知,系统自动切换到规则模板
2. **日志记录**: 所有失败都记录到 `logs/llm_calls.log`
3. **不阻塞流程**: LLM 调用失败不应影响主要功能
4. **保留信号**: 规则生成的信号不受 LLM 影响

---

## Prompt 设计指南

### 解释生成 Prompt
```
角色: 你是一位黄金交易教学助手,面向刚入门的交易者。

任务: 根据以下技术分析结果,生成一段教学型解释。

输入信息:
- 市场状态: {market_state}
- 趋势方向: {trend_dir}
- 当前价格: {current_price}
- 支撑位: {support}
- 阻力位: {resistance}
- 交易信号: {signal}
- 信号原因: {signal_reason}
- 宏观事件: {macro_events}
- 新闻情绪: {news_sentiment}

要求:
1. 语气稳健,避免强烈承诺,使用"可能"、"建议"等词汇
2. 面向新手,用通俗语言解释技术概念
3. 说明当前市场的关键特征和风险点
4. 解释为什么给出该信号
5. 提示需要注意的事项

输出格式:
- 分段清晰,使用粗体标注关键点
- 长度控制在 200-300 字
```

### 新闻情绪分析 Prompt
```
任务: 分析以下黄金相关新闻的情绪倾向。

新闻列表:
{news_list}

要求:
1. 判断每条新闻的情绪:利多/利空/中性
2. 注意识别否定和反转语义(如"如无意外"、"除非"等)
3. 生成整体情绪摘要(100 字以内)

输出格式(JSON):
{
  "items": [
    {"headline": "...", "sentiment": "利多/利空/中性", "reason": "..."}
  ],
  "summary": "整体情绪偏多,主要因为..."
}
```

### Chat 问答 Prompt
```
角色: 你是一位黄金交易教学助手。

当前市场分析:
{current_analysis}

用户问题: {question}

要求:
1. 基于当前分析回答,不要超出分析范围
2. 面向新手,用通俗语言解释
3. 如果问题超出范围,礼貌说明无法回答
4. 使用 Markdown 格式,重点内容加粗
```

---

## 成本估算

### API 调用频率(预估)
- 自动更新: 1 次/天
- 手动刷新: 最多 3 次/天
- Chat: 按需,预估 5-10 次/天

### Token 使用估算(Claude 3.5 Sonnet)
- 解释生成: ~800 tokens/次
- 新闻分析: ~600 tokens/次
- Chat 问答: ~500 tokens/次

### 日成本(假设)
- 总调用: ~9 次/天 × 2000 tokens = 18K tokens/天
- OpenRouter 价格(Claude 3.5 Sonnet): $3/M input, $15/M output
- 预估成本: ~$0.05-0.10/天

**注**: 实际成本取决于使用频率和输出长度。

---

## 关键决策记录

| 决策点 | 选择 | 原因 | 日期 |
|--------|------|------|------|
| LLM 提供商 | OpenRouter | 统一接口,支持多模型,价格透明 | 2026-02-03 |
| 模型选择 | Claude 3.5 Sonnet | 优秀的推理能力,适合金融领域 | 2026-02-03 |
| 频率控制 | 软限制 | 平衡成本控制和用户体验 | 2026-02-03 |
| 回退策略 | 静默回退 | 不影响基础功能可用性 | 2026-02-03 |

---

## 下一步行动

1. ✅ 完成头脑风暴和需求理解
2. ⏳ 创建详细实施计划(本文档)
3. ⏳ 开始实施阶段 1: 配置与开关
4. ⏳ 按顺序完成各阶段开发
5. ⏳ 最终测试与验收

---

**计划创建时间**: 2026-02-03
**预计完成时间**: 待定
**当前状态**: 准备开始实施
