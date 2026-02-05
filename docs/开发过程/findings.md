# 黄金交易 Agent - 研究发现

## 技术调研结果

### 前端框架选择
**选择：Vue 3 + TypeScript + Tailwind CSS**
- **理由**：Vue 3 生态成熟，组件化开发效率高
- **参考**：FastAPI + Vue3 是本地部署的热门组合
- **数据来源**：[代码搜索结果](https://github.com/Tomansion/Vue3-FastAPI-WebApp-template)

### 后端框架选择
**选择：FastAPI + Uvicorn**
- **理由**：Python 生态丰富（yfinance, pandas-ta），FastAPI 性能优秀，自动 API 文档
- **部署**：使用 `uvicorn main:app --reload` 开发模式
- **数据来源**：[FastAPI 官方文档](https://fastapi.tiangolo.com/)

### 图表库选择
**选择：Apache ECharts**
- **理由**：功能强大，支持 K 线图、趋势线、标注等金融图表需求
- **Vue 集成**：使用 `echarts` 和 `vue-echarts` 组件
- **数据来源**：[ECharts K 线图教程](https://blog.csdn.net/Myqijiahai/article/details/145846048)

### 技术指标库选择
**选择：pandas-ta**
- **理由**：纯 Python 实现，150+ 技术指标，与 pandas 无缝集成
- **替代方案**：TA-Lib（需要编译安装）
- **数据来源**：[pandas-ta 官方文档](https://pandas-ta.dev/)

### 定时任务库选择
**选择：APScheduler**
- **理由**：功能强大，支持 Cron 表达式，适合生产环境
- **用途**：每日 14:00 自动更新数据
- **数据来源**：[APScheduler 文档](https://apscheduler.readthedocs.io/)

## 数据源方案

### 价格数据源
**选择：yfinance（Yahoo Finance）**
- **黄金期货代码**：`GC=F`
- **美元指数代码**：`DXY`
- **优点**：免费、无需 API Key、历史数据丰富
- **数据来源**：[yfinance GitHub](https://github.com/ranaroussi/yfinance)

### 宏观数据源
**选择：AKShare**
- **美联储利率**：`macro_bank_usa_interest_rate_decision`
- **实际利率**：需从名义利率减去通胀率计算
- **数据来源**：[AKShare 利率数据文档](https://akshare.akfamily.xyz/data/interest_rate/interest_rate.html)

### 新闻数据源
**待实现**：可使用新闻 API 或手动录入重大事件

## 项目目录结构

```
黄金交易/
├── backend/                # 后端代码
│   ├── api/               # API 路由
│   ├── core/              # 配置文件
│   ├── models/            # 数据模型
│   ├── services/          # 业务逻辑
│   │   ├── data_provider.py    # 数据获取
│   │   ├── indicators.py        # 指标计算
│   │   ├── strategy.py          # 策略引擎
│   │   └── scheduler.py         # 定时任务
│   └── main.py            # FastAPI 入口
├── frontend/              # 前端代码
│   ├── src/
│   │   ├── components/    # Vue 组件
│   │   ├── views/         # 页面
│   │   ├── api/           # API 调用
│   │   └── styles/        # 样式
│   └── package.json
├── data/                  # 数据存储
│   ├── cache/             # 缓存数据
│   └── database/          # SQLite 数据库
├── design-system/         # UI 设计系统
├── logs/                  # 日志文件
└── requirements.txt       # Python 依赖
```

## 核心依赖清单

### Python 后端
```
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0

# 数据处理
pandas>=2.0.0
numpy>=1.24.0
pandas-ta>=0.3.14

# 数据源
yfinance>=0.2.36
akshare>=1.12.0

# 定时任务
apscheduler>=3.10.0

# 数据库
sqlalchemy>=2.0.0
sqlite3  # Python 内置
```

### 前端
```
vue@^3.4.0
typescript@^5.0.0
vue-router@^4.0.0
pinia@^2.0.0
axios@^1.6.0
echarts@^5.5.0
vue-echarts@^6.6.0
tailwindcss@^3.4.0
```

## 实现方案研究

### 市场状态识别算法
基于设计文档 01 的逻辑描述：
- **趋势模式**：均线多头排列 + 价格在均线上方
- **震荡模式**：价格在区间内反复，无明显趋势
- **不清晰**：趋势和震荡信号冲突

### 趋势判定算法
使用 pandas-ta：
```python
import pandas_ta as ta

# 计算均线
df.ta.sma(length=20, append=True)  # 短期均线
df.ta.sma(length=60, append=True)  # 中期均线

# 趋势判断
trend_up = df['SMA_20'] > df['SMA_60']  # 短期在中期之上
```

### 支撑/阻力位识别算法
基于局部极值点：
- 计算一定窗口内的最高点和最低点
- 通过聚类识别关键价位
- 参考多次触及的结构位

### ATR 波动指标
```python
df.ta.atr(length=14, append=True)
```

## 参考资源

- [yfinance 黄金价格数据](https://github.com/ranaroussi/yfinance)
- [pandas-ta 技术指标库](https://pandas-ta.dev/)
- [APScheduler 定时任务](https://apscheduler.readthedocs.io/)
- [FastAPI + Vue3 模板项目](https://github.com/Tomansion/Vue3-FastAPI-WebApp-template)
- [Vue3 ECharts K 线图教程](https://blog.csdn.net/Myqijiahai/article/details/145846048)
- [AKShare 宏观数据](https://akshare.akfamily.xyz/data/interest_rate/interest_rate.html)

---

## LLM 集成调研 (阶段 15)

### 技术选型

**LLM 服务提供商**: OpenRouter
- **理由**: 统一接口支持多模型,价格透明,按使用付费
- **官网**: https://openrouter.ai/
- **文档**: https://openrouter.ai/docs/quick-start

**模型选择**: Anthropic Claude 3.5 Sonnet (通过 OpenRouter)
- **模型 ID**: `anthropic/claude-3.5-sonnet`
- **理由**: 优秀的推理能力和安全性,适合金融领域,成本适中
- **价格**: $3/M input tokens, $15/M output tokens
- **上下文**: 200K tokens

### HTTP Client 库选择
**选择**: `httpx` (已存在于依赖中)
- **理由**: 异步支持、超时控制、重试机制、与 FastAPI 集成好
- **替代方案**: `requests` (同步,缺少原生异步支持)

### OpenRouter API 使用方式

**端点**: `POST https://openrouter.ai/api/v1/chat/completions`

**请求格式**:
```python
import httpx

response = httpx.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": "anthropic/claude-3.5-sonnet",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        "max_tokens": 1000,
        "temperature": 0.7,
    },
    timeout=30.0,
)
```

**响应格式**:
```json
{
  "id": "gen-xxx",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "响应内容"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### 当前代码结构分析

**策略引擎** (`backend/services/strategy.py`):
- `_generate_explanation()`: 生成规则模板解释
- 输出格式: Markdown 格式的结构化文本
- 包含: 市场状态、趋势、关键位、信号、宏观、新闻、风险、仓位

**Chat 接口** (`backend/api/routes.py`):
- 基于关键词匹配的规则问答
- 支持问题类型: 信号解释、关键位、操作建议、宏观事件、新闻情绪
- 限制: 只能回答预定义的问题类型

**数据提供者** (`backend/services/data_provider.py`):
- `get_news_sentiment()`: 基于关键词的情绪分析
- 简单规则: "rate cut" → 利多, "rate hike" → 利空
- 限制: 无法识别否定和反转语义

### LLM 增强点识别

**1. 解释生成优化** (`strategy.py`):
- **当前**: 规则模板生成的解释较为生硬
- **增强**: LLM 生成更自然、教学性的解释
- **回退**: LLM 失败时使用规则模板

**2. 新闻情绪语义分析** (`data_provider.py`):
- **当前**: 关键词规则,容易误判
- **增强**: LLM 理解语义,识别否定/反转
- **回退**: LLM 失败时使用关键词规则

**3. Chat 开放式问答** (`routes.py`):
- **当前**: 只能回答预定义问题类型
- **增强**: LLM 理解用户意图,灵活回答
- **回退**: LLM 失败时使用规则问答

### 成本控制策略

**调用频率限制**:
- 自动更新: 每天 14:00 最多 1 次
- 手动刷新: 每天最多 3 次
- Chat 问答: 不计限制,但建议缓存

**Token 使用估算**:
- 解释生成: ~800 tokens/request
- 新闻分析: ~600 tokens/request
- Chat 问答: ~500 tokens/request
- **总计**: ~18K tokens/day ≈ $0.05-0.10/day

**软限制实现**:
- 超过限制时记录警告日志,但不阻止调用
- 用户可选择继续或等待
- 提供统计 API 查看使用情况

### 错误处理与回退

**静默回退原则**:
- LLM 调用失败不应影响主流程
- 用户无感知,系统自动切换到规则模板
- 所有失败记录到日志文件

**失败场景处理**:
| 场景 | HTTP 状态码 | 处理方式 |
|------|------------|----------|
| API Key 未配置 | N/A | 跳过 LLM 调用 |
| 网络超时 | Timeout | 重试 2 次,仍失败则回退 |
| 速率限制 | 429 | 记录警告,回退到规则 |
| API 错误 | 4xx/5xx | 记录日志,回退到规则 |
| 解析失败 | N/A | 记录日志,回退到规则 |

### 日志与监控

**日志文件**: `logs/llm_calls.log`

**记录内容**:
```json
{
  "timestamp": "2026-02-03T14:00:00",
  "endpoint": "generate_explanation",
  "model": "anthropic/claude-3.5-sonnet",
  "prompt_tokens": 500,
  "completion_tokens": 300,
  "total_tokens": 800,
  "duration_ms": 1500,
  "status": "success",
  "error": null
}
```

**统计指标**:
- 每日调用次数
- 每日 token 使用量
- 每日成本估算
- 成功率/失败率
- 平均响应时间

### 用户偏好确认(通过 AskUserQuestion)

1. **LLM 模型选择**: Anthropic Claude 3.5 Sonnet
   - 理由: 优秀的推理能力,适合金融领域

2. **频率控制策略**: 适中控制(软限制)
   - 理由: 平衡成本控制和用户体验

3. **解释质量评估**: 规则解释有待改进
   - 理由: 当前模板解释较为生硬,LLM 增强是重点

### 参考资源

- [OpenRouter 官方文档](https://openrouter.ai/docs)
- [Claude 3.5 Sonnet 模型卡](https://docs.anthropic.com/en/docs/about-claude/models)
- [httpx 文档](https://www.python-httpx.org/)
- [FastAPI 异步编程](https://fastapi.tiangolo.com/async/)
