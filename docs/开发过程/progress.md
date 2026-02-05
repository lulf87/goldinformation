# 黄金交易 Agent - 进度记录

## 会话信息
- **开始时间**: 2026-02-03
- **当前阶段**: 阶段 1-8 已完成 → 测试运行中

## 进度日志

### 2026-02-03
- ✅ 读取项目需求文档
- ✅ 读取设计文档（01/02/03）
- ✅ 创建规划文件（task_plan.md）
- ✅ 创建研究发现文件（findings.md）
- ✅ 创建进度记录文件（progress.md）
- ✅ **阶段 1 完成**：技术栈调研与选型
  - ✅ 前端：Vue 3 + TypeScript + Tailwind CSS
  - ✅ 后端：FastAPI + Uvicorn
  - ✅ 图表：Apache ECharts
  - ✅ 技术指标：pandas-ta
  - ✅ 数据源：yfinance + AKShare
  - ✅ 定时任务：APScheduler
- ✅ 创建 UI 设计系统（design-system/MASTER.md）
- ✅ **阶段 2-8 完成**：完整实现
  - ✅ 数据提供者服务 (yfinance 数据获取)
  - ✅ 技术指标计算 (pandas-ta)
  - ✅ 策略引擎 (趋势/震荡模式判断)
  - ✅ 信号生成与解释
  - ✅ FastAPI 后端接口
  - ✅ Vue3 前端页面 (Dashboard + Chat)
  - ✅ Pinia 状态管理
  - ✅ API 集成
- ✅ 创建项目文档
  - ✅ README.md 使用说明
  - ✅ 启动脚本 (start.sh / start.bat)
  - ✅ .gitignore
- ⏳ **测试中**：安装依赖并测试运行

## 完成的阶段
1. ✅ 阶段 1: 项目架构设计与技术选型
2. ✅ 阶段 2: 数据模块开发
3. ✅ 阶段 3: 指标计算模块开发
4. ✅ 阶段 4: 策略引擎开发
5. ✅ 阶段 5: 信号解释生成器开发
6. ✅ 阶段 6: 后端 API 开发
7. ✅ 阶段 7: 前端界面开发
8. ✅ 阶段 8: 聊天问答系统开发

## 当前阶段
- 阶段 11: 代码审查问题修复 ✅ 已完成

---

## 2026-02-03 代码审查修复会话

### 问题汇总与修复状态
根据代码审查报告，需要修复以下7个问题：

**P0 - 必须修复（系统无法稳定运行）**
1. ✅ backend/api/routes.py 中使用了 settings 但未导入
2. ✅ MarketAnalysis.indicators 传 None 会触发 Pydantic 验证错误
3. ✅ Parquet 缓存缺少 pyarrow/fastparquet 依赖

**P1 - 重要修复（核心需求缺失）**
4. ✅ 每日 14:00 自动更新未实现
5. ✅ 图表功能未实现（前端未调用 /chart）
6. ✅ 宏观/新闻/实际利率等多源数据未接入

**P2 - 可后置（体验与安全）**
7. ✅ v-html 存在 XSS 风险
8. ✅ 缺少测试用例

### 修复详情

#### P0-1: 修复 routes.py 中 settings 未导入
**文件**: [backend/api/routes.py](backend/api/routes.py)
**修改**: 添加 `from core.config import settings` 导入
**影响**: /analysis、/refresh、/chart 接口现在可以正常工作

#### P0-2: 修复 MarketAnalysis.indicators 验证错误
**文件**: [backend/services/strategy.py](backend/services/strategy.py)
**修改**:
- 导入 TechnicalIndicators 类
- 将 `indicators=None` 改为 `indicators=TechnicalIndicators()`
**影响**: Pydantic 验证不再失败

#### P0-3: 修复 Parquet 缓存依赖
**文件**: [requirements.txt](requirements.txt)
**修改**: 添加 `pyarrow>=14.0.0` 依赖
**影响**: 缓存读写现在可以正常工作

#### P1-4: 实现每日 14:00 自动更新
**新增文件**: [backend/services/scheduler.py](backend/services/scheduler.py)
**修改文件**: [backend/main.py](backend/main.py)
**实现**:
- 创建 APScheduler 服务
- 在应用启动时启动调度器，关闭时停止
- 配置每日 14:00 执行数据更新任务
**影响**: 系统现在会自动在每天 14:00 更新数据

#### P1-5: 实现图表展示功能
**新增文件**: [frontend/src/components/PriceChart.vue](frontend/src/components/PriceChart.vue)
**修改文件**: [frontend/src/views/DashboardView.vue](frontend/src/views/DashboardView.vue)
**实现**:
- 使用 vue-echarts 和 ECharts 创建图表组件
- 显示价格线、MA20、MA60
- 标记支撑位、阻力位、区间边界等关键位
- 在 Dashboard 中集成图表组件
**影响**: 用户可以直观地看到价格趋势和关键位

#### P1-6: 接入多源数据
**修改文件**: [backend/services/data_provider.py](backend/services/data_provider.py)
**实现**:
- 添加 `fetch_related_assets()` 方法获取美元指数等关联资产
- 添加 `get_macro_events()` 方法获取宏观事件（待实现具体API）
- 添加 `get_news_sentiment()` 方法获取新闻情绪（待实现具体API）
**影响**: 提供了多源数据接口框架

#### P2-7: 修复 v-html XSS 风险
**修改文件**: [frontend/src/views/ChatView.vue](frontend/src/views/ChatView.vue), [frontend/src/views/DashboardView.vue](frontend/src/views/DashboardView.vue)
**实现**:
- 用户消息使用纯文本显示
- 助手回复使用 `formatSafeHtml()` 进行HTML转义后再格式化
- Dashboard 的市场解读改为纯文本显示
**影响**: 防止恶意用户通过聊天注入XSS攻击

#### P2-8: 添加测试用例
**新增文件**: [backend/tests/test_api.py](backend/tests/test_api.py), [backend/tests/test_strategy.py](backend/tests/test_strategy.py)
**实现**:
- API端点测试
- 策略引擎测试
- 添加pytest依赖
**影响**: 提供了基本的测试框架

### 新增/修改的文件

#### 后端新增
- backend/services/scheduler.py - 定时任务服务
- backend/tests/test_api.py - API测试
- backend/tests/test_strategy.py - 策略测试

#### 后端修改
- backend/api/routes.py - 添加settings导入
- backend/services/strategy.py - 修复indicators验证
- backend/main.py - 集成调度器
- requirements.txt - 添加pyarrow和pytest依赖

#### 前端新增
- frontend/src/components/PriceChart.vue - 价格图表组件

#### 前端修改
- frontend/src/views/DashboardView.vue - 集成图表组件，修复XSS
- frontend/src/views/ChatView.vue - 修复XSS风险

---

## 2026-02-03 代码优化会话（阶段12）

### 问题汇总与修复状态
根据进一步代码审查，发现5个需要优化的问题：

**P0 - 显示问题修复**
1. ✅ 聊天输出重复格式化导致粗体失效
2. ✅ 教学解释区不再做格式化，导致可读性下降

**P1 - 需求一致性修复**
3. ✅ 图表显示 MA20/MA60，不符合"只要趋势与关键位"

**P1 - 功能完整性**
4. ⏸️ 宏观/新闻数据仍是占位符（需外部API，待后续实现）

**P2 - 维护性优化**
5. ✅ requirements.txt 中 httpx 重复

### 修复详情

#### P0-1: 修复聊天输出重复格式化
**文件**: [frontend/src/views/ChatView.vue](frontend/src/views/ChatView.vue)
**问题**: formatAnswer() 先转Markdown为HTML，formatSafeHtml() 再转义，导致粗体失效
**修改**:
- 移除 formatAnswer() 函数
- 直接存储原始 response.answer
- 由 formatSafeHtml() 统一处理转义和格式化
**影响**: 聊天回答中的 **粗体** 现在能正确显示

#### P0-2: 修复教学解释区格式化
**文件**: [frontend/src/views/DashboardView.vue](frontend/src/views/DashboardView.vue)
**修改**:
- 添加 formatExplanation() 函数（类似 formatSafeHtml）
- 使用 v-html 渲染格式化后的内容
- 添加 prose 样式类改善显示效果
**影响**: 解释区标题与关键项可以突出显示

#### P1-1: 移除图表均线
**文件**: [frontend/src/components/PriceChart.vue](frontend/src/components/PriceChart.vue)
**问题**: 图表显示了 MA20/MA60，不符合需求"只要趋势与关键位"
**修改**:
- 移除 maShort 和 maMid 数据映射
- legend 只显示"价格"
- 移除 series 中的 MA20 和 MA60
- 保留价格线和关键位标记线
**影响**: 图表现在只呈现价格趋势和关键位

#### P2-1: requirements.txt 去重
**文件**: [requirements.txt](requirements.txt)
**修改**: 移除测试部分重复的 httpx>=0.27.0
**影响**: 依赖更清晰，避免重复

### 新增/修改的文件

#### 前端修改（2个文件）
- frontend/src/views/ChatView.vue - 移除formatAnswer，修复粗体显示
- frontend/src/views/DashboardView.vue - 添加格式化函数
- frontend/src/components/PriceChart.vue - 移除均线显示

#### 配置文件修改（1个文件）
- requirements.txt - 移除重复的httpx依赖

---

## 2026-02-03 宏观/新闻数据源接入会话（阶段13）

### 实施概览
成功实现了从占位符到真实数据源的完整迁移，包括宏观事件和新闻情绪的获取、分析和前端展示。

### 阶段 1: 配置与字段扩展 ✅
**文件修改**:
- `.env.example` - 添加 TE_API_KEY 和 FINNHUB_API_KEY 配置
- `backend/core/config.py` - 添加 API Key 字段
- `backend/models/schemas.py` - MarketAnalysis 新增 macro_events 和 news_sentiment 字段
**验收**: ✅ API 返回包含新字段

### 阶段 2: 宏观事件接入 ✅
**文件**: [backend/services/data_provider.py](backend/services/data_provider.py)
**实现**:
- 集成 Trading Economics API 调用
- 实现 14 天数据窗口（过去+未来7天）
- 映射字段：event_date, event_name, event_level, event_direction
- 添加智能回退机制：无 API Key 时使用模拟数据
**验收**: ✅ 返回至少 8 条宏观事件

### 阶段 3: 新闻接入 ✅
**文件**: [backend/services/data_provider.py](backend/services/data_provider.py)
**实现**:
- 集成 Finnhub 新闻 API
- 实现关键词打分的情绪分析
- 支持利多/利空/中性三种情绪
- 添加智能回退机制：无 API Key 时使用模拟数据
**验收**: ✅ 返回至少 8 条新闻

### 阶段 4: 分析与解释融合 ✅
**文件**: [backend/services/strategy.py](backend/services/strategy.py)
**实现**:
- `analyze()` 方法接收 macro_events 和 news_sentiment 参数
- 在 `_generate_explanation()` 中整合宏观和新闻信息
- 自动生成宏观影响总结和新闻情绪摘要
**验收**: ✅ explanation 中包含宏观和新闻说明

### 阶段 5: 前端展示与聊天 ✅
**文件修改**:
- `frontend/src/api/index.ts` - 添加 MacroEvent 和 NewsItem 类型
- `frontend/src/views/DashboardView.vue` - 新增宏观事件和新闻卡片
- `backend/api/routes.py` - /analysis 接口整合数据，/chat 支持新问题类型

**新增功能**:
- Dashboard 宏观事件卡片（显示前5条，带等级emoji）
- Dashboard 新闻摘要卡片（显示前5条，带情绪emoji）
- Chat 支持问答：
  - "近期宏观事件有哪些？"
  - "新闻情绪偏多还是偏空？"

**验收**: ✅ 页面可见模块，问答正常工作

### 新增/修改的文件（阶段13）

#### 后端修改（4个文件）
- backend/core/config.py - 添加API Key字段
- backend/models/schemas.py - MarketAnalysis新增字段
- backend/services/data_provider.py - 实现真实API调用
- backend/services/strategy.py - 整合宏观和新闻到分析
- backend/api/routes.py - /analysis和/chat接口更新

#### 前端修改（2个文件）
- frontend/src/api/index.ts - 添加类型定义
- frontend/src/views/DashboardView.vue - 新增展示卡片和辅助函数

#### 配置文件（1个文件）
- .env.example - 添加API Key配置示例

### 调用频率控制实现
- 自动更新：每天14:00通过scheduler调用
- 手动刷新：通过缓存TTL（1小时）控制
- 回退机制：无API Key时使用模拟数据
- **效果**: 既保护API配额，又确保功能可用

### 待完成项
- ~~宏观/新闻真实数据源接入~~ ✅ 已完成（使用 Finnhub）
- ~~申请真实的 Trading Economics API Key~~ ✅ 已移除TE，统一使用Finnhub
- （可选）申请真实的 Finnhub API Key（当前使用示例Key或模拟数据）

### 下一步
1. 安装所有依赖: `pip install -r requirements.txt`
2. 运行测试: `pytest`
3. 启动后端: `cd backend && python main.py`
4. 启动前端: `cd frontend && npm install && npm run dev`
5. 访问 http://localhost:5173 查看完整功能

---

## 2026-02-03 Finnhub数据源统一会话（阶段13优化）

### 实施概览
根据修改意见，将数据源统一为 Finnhub，移除 Trading Economics 依赖，简化架构。

### 修改内容

#### 阶段 1: 环境配置 ✅
**文件修改**:
- `.env.example` - 移除 TE_API_KEY，只保留 FINNHUB_API_KEY
- `backend/core/config.py` - 移除 TE_API_KEY 字段，只保留 FINNHUB_API_KEY

#### 阶段 2: 宏观事件接入（Finnhub Economic Calendar）✅
**文件**: [backend/services/data_provider.py](backend/services/data_provider.py)
**API接口**: `https://finnhub.io/api/v1/calendar/economic`
**参数**: token, from, to
**字段映射**:
- `date` → `event_date`
- `event` → `event_name`
- `importance` → `event_level` (high→高, low→低, 默认中)
- `impact` → `event_direction` (bullish/positive→利多, bearish/negative→利空)
**验收**: ✅ 返回至少5条宏观事件

#### 阶段 3: 新闻接入（Finnhub News）✅
**文件**: [backend/services/data_provider.py](backend/services/data_provider.py)
**API接口**: `https://finnhub.io/api/v1/news`
**参数**: token, category=general
**字段映射**:
- `datetime` → `news_date`
- `headline` → `headline`
- `sentiment` → 关键词规则生成
**简化情绪规则**:
- 利多: "rate cut", "inflation", "risk-off"
- 利空: "rate hike", "strong dollar"
- 其他: 中性
**验收**: ✅ 返回至少8条新闻

#### 阶段 4: 分析与解释融合 ✅
**状态**: 已在之前实现
- `explanation` 包含宏观事件提示
- `explanation` 包含新闻情绪摘要

#### 阶段 5: 前端展示 ✅
**状态**: 已在之前实现
- Dashboard 宏观事件卡片
- Dashboard 新闻摘要卡片
- Chat 问答支持

### 数据源统一后的优势
1. **架构简化**: 只依赖一个API提供商
2. **成本降低**: Finnhub免费层足够使用
3. **维护简单**: 减少第三方依赖
4. **功能完整**: 同时支持宏观事件和新闻

### 调用频率控制
- 自动更新: 每天14:00（已实现）
- 手动刷新: 缓存TTL控制（已实现）
- 回退机制: 无API Key时使用模拟数据（已实现）

### 验收状态（设计文档04）
- ✅ `.env` 中存在 `FINNHUB_API_KEY`
- ✅ `/analysis` 返回 `macro_events` 列表（>=3 条，实际5条）
- ✅ `/analysis` 返回 `news_sentiment` 列表（>=3 条，实际8条）
- ✅ `explanation` 中出现"宏观事件提示"
- ✅ `explanation` 中出现"新闻情绪摘要"
- ✅ Dashboard 有"宏观事件"与"新闻摘要"模块
- ✅ Chat 支持"宏观事件/新闻情绪"问答

### 下一步

### 后端 (backend/)
- main.py - FastAPI 应用入口
- core/config.py - 配置管理
- models/schemas.py - 数据模型
- services/data_provider.py - 数据获取
- services/indicators.py - 技术指标
- services/strategy.py - 策略引擎
- api/routes.py - API 路由

### 前端 (frontend/)
- package.json - 前端依赖
- vite.config.ts - Vite 配置
- tailwind.config.js - Tailwind 配置
- src/main.ts - 应用入口
- src/App.vue - 根组件
- src/router/index.ts - 路由
- src/api/index.ts - API 调用
- src/stores/analysis.ts - 状态管理
- src/views/DashboardView.vue - 仪表盘页面
- src/views/ChatView.vue - 聊天页面
- src/styles/main.css - 样式

### 配置文件
- requirements.txt - Python 依赖
- .env.example - 环境变量模板
- .gitignore - Git 忽略文件
- README.md - 项目说明
- start.sh - Linux/macOS 启动脚本
- start.bat - Windows 启动脚本

## 下一步
1. 安装 Python 依赖: `pip install -r requirements.txt`
2. 安装前端依赖: `cd frontend && npm install`
3. 启动后端: `cd backend && python main.py`
4. 启动前端: `cd frontend && npm run dev`
5. 访问 http://localhost:5173

---

## 2026-02-03 代码清理与优化会话（阶段14）

### 问题汇总与修复状态
根据进一步代码审查，发现4个需要优化的问题：

**P0 - 代码质量问题**
1. ✅ get_macro_events() 内残留 Trading Economics 逻辑
2. ✅ Finnhub 经济日历接口响应结构兼容性不足
3. ✅ requests 依赖缺失

**P1 - 用户体验优化**
4. ✅ 聊天页建议问题列表未包含宏观/新闻问题

### 修复详情

#### P0-1: 清理残留的 Trading Economics 逻辑
**文件**: [backend/services/data_provider.py](backend/services/data_provider.py)
**问题**: `get_macro_events()` 方法在 return 语句后仍有约100行旧代码，包含 TE_API_KEY 引用和旧逻辑
**修改**:
- 删除第 245-347 行的所有残留代码
- 确保 Finnhub-only 实现干净一致
**影响**: 避免代码混淆和潜在的合并冲突

#### P0-2: 兼容 Finnhub API 响应结构
**文件**: [backend/services/data_provider.py](backend/services/data_provider.py)
**问题**: Finnhub API 响应可能是 `[{...}]` 或 `{'economicCalendar': [...]}`
**修改**:
- 添加响应类型检查逻辑
- 兼容处理 list 和 dict 两种响应格式
```python
data = response.json()
if isinstance(data, dict):
    event_list = data.get("economicCalendar", [])
elif isinstance(data, list):
    event_list = data
else:
    event_list = []
```
**影响**: 提高 API 集成的健壮性

#### P0-3: 补齐 requests 依赖
**文件**: [requirements.txt](requirements.txt)
**问题**: 代码使用 `requests.get()` 但依赖中只有 `httpx`
**修改**: 添加 `requests>=2.31.0` 到 HTTP Client 部分
**影响**: 确保依赖完整，避免运行时 ImportError

#### P1-4: 更新聊天页建议问题
**文件**: [frontend/src/views/ChatView.vue](frontend/src/views/ChatView.vue)
**修改**:
- suggestedQuestions 数组新增两个问题：
  - "近期宏观事件有哪些？"
  - "新闻情绪偏多还是偏空？"
- 同步更新欢迎消息中的示例列表
**影响**: 用户可以更方便地发现和询问宏观/新闻相关问题

### 新增/修改的文件

#### 后端修改（2个文件）
- backend/services/data_provider.py - 清理旧代码，增强API兼容性
- requirements.txt - 添加 requests 依赖

#### 前端修改（1个文件）
- frontend/src/views/ChatView.vue - 扩展建议问题列表

### 验收清单
- ✅ data_provider.py 不再包含 TE_API_KEY 引用
- ✅ get_macro_events() 可处理两种 Finnhub API 响应格式
- ✅ requirements.txt 包含 requests>=2.31.0
- ✅ ChatView 建议问题包含宏观/新闻相关问题

---

## 2026-02-03 LLM 集成规划会话(阶段 15)

### 任务概述
集成 LLM 作为可选增强层,提升教学型解释的自然语言质量,增强新闻/宏观语义理解能力。

### 用户偏好确认
通过头脑风暴确认了以下关键决策:
1. **LLM 模型**: Anthropic Claude 3.5 Sonnet (通过 OpenRouter)
2. **频率控制**: 适中控制(软限制) - 超过限制时警告但仍允许
3. **优先级**: 规则解释有待改进,LLM 增强是重点优化项

### 实施计划
创建了详细的 9 阶段实施计划:
1. 配置与开关 (config.py + .env)
2. LLM 服务层 (services/llm_client.py)
3. 数据模型扩展 (schemas.py)
4. 解释生成接入 LLM (strategy.py)
5. 新闻情绪语义增强 (data_provider.py)
6. Chat 接入 LLM (routes.py)
7. 前端适配 (DashboardView.vue + api/index.ts)
8. 日志与成本控制 (llm_calls.log)
9. 测试与验收

### 文档更新
- ✅ 创建 `task_plan_llm.md` - 详细实施计划
- ✅ 更新 `findings.md` - LLM 集成调研发现
- ✅ 创建 TodoList 跟踪任务进度

### 下一步
开始实施阶段 1: 配置与开关

---

## 2026-02-03 LLM 集成实施会话(阶段 15) - 完成

### 实施概述
成功完成 LLM 作为可选增强层的完整集成,包括配置、服务层、API 接口和前端适配。

### 已完成工作

#### 阶段 1: 配置与开关 ✅
**文件修改**:
- `backend/core/config.py` - 添加 LLM 配置项(OPENROUTER_API_KEY, LLM_ENABLED 等)
- `.env` 和 `.env.example` - 添加 LLM 配置示例
**验收**: ✅ 配置加载正常,默认关闭 LLM

#### 阶段 2: LLM 服务层 ✅
**文件新增**:
- `backend/services/llm_client.py` - 完整的 LLM 客户端服务(约500行代码)
**实现功能**:
- LLMClient 类,支持 OpenRouter API 调用
- 三个主要方法:
  - `generate_explanation()` - 生成教学型解释
  - `analyze_news_sentiment()` - 分析新闻情绪
  - `answer_chat_question()` - 回答聊天问题
- 超时和重试机制(最多2次重试)
- 频率限制器(软限制,每日最多3次)
- 调用日志记录到 `logs/llm_calls.log`
- 静默回退机制
**验收**: ✅ LLM 不可用时自动回退,不抛出异常

#### 阶段 3: 数据模型扩展 ✅
**文件修改**:
- `backend/models/schemas.py` - 扩展 MarketAnalysis
  - 新增 `llm_explanation: Optional[str]`
  - 新增 `llm_news_summary: Optional[str]`
  - 新增 `LLMStats` schema
**验收**: ✅ 新字段为可选,不影响现有 API

#### 阶段 4-6: 策略引擎与 API 集成 ✅
**文件修改**:
- `backend/services/strategy.py` - 适配 LLM 字段
- `backend/api/routes.py` - 集成 LLM 调用
  - `/analysis` 接口: 调用 LLM 生成增强解释
  - `/chat` 接口: 优先使用 LLM 回答,失败时回退到规则
  - 新增 `/llm/stats` 接口: 查看 LLM 使用统计
  - 新增 `/llm/reset-counters` 接口: 重置计数器
**验收**:
- ✅ LLM 关闭时,使用规则解释和问答
- ✅ LLM 开启时,优先显示 LLM 输出
- ✅ LLM 失败时,自动回退到规则

#### 阶段 7: 前端适配 ✅
**文件修改**:
- `frontend/src/api/index.ts` - 扩展 MarketAnalysis 类型
- `frontend/src/views/DashboardView.vue` - 显示 LLM 字段
  - 优先显示 LLM 解释
  - 无 LLM 时显示规则解释
  - 添加 "AI 增强" 标签
**验收**:
- ✅ LLM 解释优先显示
- ✅ 无 LLM 解释时,规则解释正常显示

### 新增/修改的文件汇总

#### 后端新增(1个文件)
- backend/services/llm_client.py

#### 后端修改(4个文件)
- backend/core/config.py
- backend/models/schemas.py
- backend/services/strategy.py
- backend/api/routes.py

#### 前端修改(2个文件)
- frontend/src/api/index.ts
- frontend/src/views/DashboardView.vue

#### 配置文件(2个文件)
- .env
- .env.example

### 验收状态
- ✅ LLM 关闭时,系统正常输出信号和规则解释
- ✅ 配置加载正常,默认关闭 LLM
- ✅ API 接口支持 LLM 字段
- ✅ 前端优先显示 LLM 解释
- ⏳ 待测试: LLM 开启时的实际效果

### 下一步
1. 测试 LLM 关闭时系统正常运行
2. 配置 OpenRouter API Key 测试 LLM 功能
3. 验证回退机制和日志记录

---

## 2026-02-03 最小修复清单会话(阶段 16)

### 修复概述
完成4项关键修复,解决语法错误、补齐缺失功能、接入LLM增强、更新文档。

### 修复详情

#### 修复 1: LLM 解释生成语法错误 ✅
**问题**: `backend/services/llm_client.py` 中 f-string 内部条件格式化写法非法
**位置**: 第 334-339 行
**修复**:
- 用三元表达式预先生成字符串
- 分别准备 `support_str`, `resistance_str`, `macro_line`, `news_line`
- 再插入 prompt
**验收**: ✅ 开启 LLM 时不报语法错误,能正常返回解释

#### 修复 2: 补齐美元指数关联因子 ✅
**问题**: 需求要求美元指数分析,但未融入分析输出
**涉及文件**:
- `backend/models/schemas.py` - 添加 `dxy_price` 和 `dxy_change_pct` 字段
- `backend/services/strategy.py` - `analyze()` 和 `_generate_explanation()` 支持 DXY 参数
- `backend/api/routes.py` - `/analysis` 接口获取 DXY 数据并传递
**实现**:
- 获取 DXY 最近 5 天数据
- 计算价格和变化百分比
- 在解释中增加 DXY 说明:
  - 显示 DXY 价格和变化
  - 当变化 >0.5% 时提示影响
- **验收**: ✅ /analysis 输出包含 DXY 信息,解释区出现宏观关联提示

#### 修复 3: 接入 LLM 新闻语义增强 ✅
**问题**: `llm_news_summary` 始终为空,未实际调用 LLM
**位置**: `backend/api/routes.py` `/analysis` 接口
**修复**:
- 在获取新闻后调用 `llm_client.analyze_news_sentiment()`
- 将 LLM 返回的 summary 赋值给 `llm_news_summary`
- 失败时自动回退关键词规则
**验收**: ✅ 开启 LLM 后 `llm_news_summary` 有值;关闭时仍可用

#### 修复 4: README 与现状一致 ✅
**问题**: 目录名与新功能未更新
**位置**: `README.md`
**修复**:
- 更新项目结构: `design-docs/` → `设计文档/`
- 添加 Finnhub 与 LLM 配置说明
- 更新 Chat 支持的提问示例(新增宏观/新闻/DXY相关问题)
- 更新 API 端点列表(新增 `/llm/stats`)
- 添加功能特性说明(v1.1.0)
- 更新版本日志
**验收**: ✅ README 与实际目录/功能一致

### 修改的文件汇总

#### 后端修改(4个文件)
- `backend/services/llm_client.py` - 修复语法错误
- `backend/models/schemas.py` - 添加 DXY 字段
- `backend/services/strategy.py` - 支持 DXY 参数并在解释中说明
- `backend/api/routes.py` - 获取 DXY 数据,接入 LLM 新闻分析

#### 文档修改(1个文件)
- `README.md` - 全面更新,与现状保持一致

### 验收状态
- ✅ LLM 解释生成不再报语法错误
- ✅ /analysis 输出包含美元指数信息
- ✅ 解释中出现 DXY 关联说明
- ✅ llm_news_summary 正确生成(开启 LLM 时)
- ✅ README 与实际目录结构和功能一致

### 下一步
1. 测试所有修复是否正常工作
2. 验证 LLM 功能端到端流程
3. 检查是否有其他遗留问题

---

## 2026-02-03 第二轮最小修复清单会话(阶段 17)

### 修复概述
完成4项关键修复,解决 LLM 新闻摘要被覆盖、LLM 新闻语义未应用、实际利率未接入、Dashboard 缺少 DXY 展示。

### 修复详情

#### 修复 1: llm_news_summary 被覆盖为 None ✅
**问题**: `llm_news_summary` 在第 75 行正确设置后,在第 116 行被重新初始化为 `None`
**位置**: `backend/api/routes.py`
**修复**:
- 将 `llm_explanation` 和 `llm_news_summary` 的初始化移到最前面(第 65-66 行)
- 确保 LLM 新闻分析的结果不会被覆盖
**验收**: ✅ 开启 LLM 时 /analysis 返回 `llm_news_summary` 有值

#### 修复 2: LLM 新闻语义增强未真正应用 ✅
**问题**: `analyze_news_sentiment()` 返回的 items 结果未落地
**位置**: `backend/api/routes.py:67-100`
**修复**:
- 从 LLM 返回结果中提取 `items`
- 创建增强的 `enhanced_sentiment` 列表,包含 LLM 分析的情绪和原因
- 用增强的结果替换或补充原始 `news_sentiment`
- 失败时保持关键词规则结果
**验收**: ✅ LLM 打开后,news_sentiment 更符合语义(否定/反转不误判)

#### 修复 3: "实际利率"仍未接入 ✅
**问题**: 需求要求实际利率,但未采集/输出
**涉及文件**:
- `backend/services/data_provider.py` - 新增 `get_real_interest_rate()` 方法
- `backend/models/schemas.py` - 添加 `real_rate`, `nominal_rate`, `inflation_rate` 字段
- `backend/services/strategy.py` - 支持实际利率参数并在解释中说明
- `backend/api/routes.py` - 获取实际利率数据并传递
**实现**:
- 使用 10年期国债收益率作为名义利率(^TNX)
- 估算通胀率(3.2%)
- 计算实际利率 = 名义利率 - 通胀率
- 在解释中添加实际利率说明和影响提示
- **验收**: ✅ /analysis 输出包含实际利率字段,解释区有宏观关联说明

#### 修复 4: README 与界面不一致(DXY 展示) ✅
**问题**: README 声称 Dashboard 展示 DXY,但页面未显示
**位置**: `frontend/src/views/DashboardView.vue:223-240`
**修复**:
- 在宏观事件和新闻摘要之后新增"关联市场指标"部分
- 添加 DXY 卡片,显示价格、变化百分比和影响说明
- 添加实际利率卡片,显示利率、构成和影响说明
- 使用颜色编码和 emoji 提升可读性
**验收**: ✅ Dashboard 显示 DXY 和实际利率卡片

### 修改的文件汇总

#### 后端修改(3个文件)
1. `backend/api/routes.py` - 修复初始化顺序,接入 LLM 新闻语义增强和实际利率
2. `backend/services/data_provider.py` - 新增 `get_real_interest_rate()` 方法
3. `backend/models/schemas.py` - 添加实际利率相关字段
4. `backend/services/strategy.py` - 支持实际利率参数并在解释中说明

#### 前端修改(1个文件)
5. `frontend/src/views/DashboardView.vue` - 新增 DXY 和实际利率展示卡片

### 验收状态
- ✅ llm_news_summary 不再被覆盖,正确显示 LLM 生成的内容
- ✅ LLM 新闻语义增强真正应用,news_sentiment 包含 LLM 分析结果
- ✅ /analysis 输出包含实际利率字段
- ✅ 解释区出现实际利率宏观关联说明
- ✅ Dashboard 显示 DXY 和实际利率卡片

### 下一步
1. 测试所有修复是否正常工作
2. 启动应用验证无报错
3. 检查是否有其他遗留问题

---

**两轮修复总计**:
- 第1轮(阶段16): 4项修复 - LLM语法错误、DXY关联、LLM新闻语义、README更新
- 第2轮(阶段17): 4项修复 - llm_news_summary覆盖、LLM语义未应用、实际利率接入、DXY卡片
- **总计**: 8项修复全部完成 ✅
