# 黄金交易 Agent

本地运行的黄金交易决策辅助系统，提供可解释的中线交易信号。

## 项目特点

- **稳健策略**: 优先防守，确认后出手
- **市场状态识别**: 自动判断趋势/震荡/不清晰
- **教学型解释**: 每条信号都有详细说明
- **LLM 增强**: 可选的大语言模型增强,提升解释质量
- **新闻事件**: 展示具体新闻内容与来源
- **本地部署**: 无需云服务，数据隐私安全
- **实时更新**: 金价每 10s 自动刷新
- **风险降级**: 重大新闻触发信号降级与仓位降低
- **止损约束**: 止损区自动遵守最大回撤 15%

## 技术栈

### 后端
- Python 3.10+
- FastAPI (Web 框架)
- pandas + pandas-ta (技术指标计算)
- yfinance (黄金价格数据)
- Finnhub API (新闻数据)
- OpenRouter (可选 LLM 接入)
- APScheduler (定时任务)

### 前端
- Vue 3 + TypeScript
- Tailwind CSS
- Apache ECharts (图表)
- Pinia (状态管理)

## 项目结构

```
黄金交易/
├── backend/              # 后端代码
│   ├── api/             # API 路由
│   ├── core/            # 配置文件
│   ├── models/          # 数据模型
│   └── services/        # 业务逻辑
├── frontend/            # 前端代码
│   └── src/
│       ├── components/  # Vue 组件
│       ├── views/       # 页面
│       ├── api/         # API 调用
│       └── stores/      # Pinia stores
├── data/                # 数据存储
│   ├── cache/          # 缓存数据
│   └── database/       # SQLite 数据库
├── design-system/      # UI 设计系统
├── 设计文档/            # 设计文档
├── logs/               # 日志文件
└── requirements.txt    # Python 依赖
```

## 快速开始

### 1. 安装依赖

**后端:**
```bash
# 创建虚拟环境 (推荐)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

**前端:**
```bash
cd frontend
npm install
```

### 2. 配置环境

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑 .env 文件
```

**环境变量说明**:

| 变量 | 说明 | 默认值 | 必需 |
|------|------|--------|------|
| `HOST` | 后端服务地址 | 127.0.0.1 | 否 |
| `PORT` | 后端服务端口 | 8000 | 否 |
| `GOLD_SYMBOL` | 黄金期货代码 | GC=F | 否 |
| `FINNHUB_API_KEY` | Finnhub API Key (新闻) | - | 推荐 |
| `FINNHUB_PLAN` | Finnhub 账号级别(free/premium) | free | 否 |
| `FRED_API_KEY` | FRED API Key (实际利率数据) | - | 可选 |
| `OPENROUTER_API_KEY` | OpenRouter API Key (LLM增强) | - | 可选 |
| `LLM_ENABLED` | 是否启用LLM增强 | false | 否 |

**获取 API Keys**:
- Finnhub: https://finnhub.io/register (免费层可用新闻)
- FRED: https://fred.stlouisfed.org/docs/api/api_key.html (免费，推荐用于实际利率数据)
- OpenRouter: https://openrouter.ai/ (支持 Claude、GPT-4 等模型)

### 3. 启动服务

**启动后端:**
```bash
# 方式一：直接运行
cd backend
python main.py

# 方式二：使用 uvicorn
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

后端将在 http://127.0.0.1:8000 启动

**启动前端:**
```bash
cd frontend
npm run dev
```

前端将在 http://localhost:5173 启动

### 4. 访问应用

打开浏览器访问: http://localhost:5173

- **Dashboard**: 查看市场分析和交易信号
- **Chat**: 智能问答界面
- **API 文档**: http://localhost:8000/docs

## 使用说明

### Dashboard 页面

1. **交易信号卡片**: 显示当前信号等级 (强买/买/观望/卖/强卖)
2. **行情概览**: 当前价格、涨跌幅
3. **市场状态**: 趋势/震荡/不清晰
4. **关键价位**: 支撑位、阻力位、区间边界（随周期联动）
5. **操作建议**: 入场区、止损区、目标区
6. **仓位建议**: 根据信号强度给出仓位建议
7. **新闻事件**: 具体新闻内容列表(含来源/链接)
8. **关联市场指标**: 美元指数(DXY)、实际利率(与黄金相关性分析)

### Chat 问答

支持以下问题类型：
- "为什么给出该信号？"
- "当前关键位是什么？"
- "下一步建议如何操作？"
- "近期重要新闻有哪些？"
- "美元指数对黄金有什么影响？"

**LLM 增强**: 启用 LLM 后,可支持更自然的开放式问答。

### 数据刷新

- **自动更新**: 金价每 10s 自动刷新(仅金价)
- **刷新时间**: 页面显示金价刷新时间
 - **趋势线**: 图表显示 MA20/MA60 趋势线与关键位
 - **周期联动**: 切换分/日/周/月/年时，同步刷新信号与关键位

## 设计文档

- [设计文档 01: 策略规则设计](设计文档/设计文档-01-策略规则设计.md)
- [设计文档 02: 数据字段与指标规范](设计文档/设计文档-02-数据字段与指标规范.md)
- [设计文档 03: 页面与交互原型说明](设计文档/设计文档-03-页面与交互原型说明.md)
- [设计文档 04: Finnhub 接入方案](设计文档/设计文档-04-Finnhub接入方案.md)
- [设计文档 05: LLM 接入方案](设计文档/设计文档-05-LLM接入方案.md)

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/analysis` | GET | 获取市场分析(含新闻/DXY，支持 period/interval) |
| `/api/v1/price` | GET | 获取金价(10s 自动刷新) |
| `/api/v1/refresh` | POST | 刷新数据 |
| `/api/v1/chart` | GET | 获取图表数据(分/日/周/月/年) |
| `/api/v1/chat` | POST | 聊天问答(支持 LLM) |
| `/api/v1/llm/stats` | GET | LLM 使用统计(需启用 LLM) |

## 功能特性

### 已实现功能 (v1.1.0)

- ✅ 市场状态识别(趋势/震荡/不清晰)
- ✅ 交易信号生成(5级信号:强买/买/观望/卖/强卖)
- ✅ 关键位识别(支撑/阻力/区间边界)
- ✅ 教学型解释(规则生成 + 可选 LLM 增强)
- ✅ 新闻事件展示(Finnhub News)
- ✅ 美元指数关联分析(DXY 价格与变化)
- ✅ 图表展示(价格趋势 + MA20/MA60 + 关键位标注)
- ✅ Chat 智能问答(规则模板 + 可选 LLM 对话)
- ✅ 金价每 10s 自动刷新

### LLM 增强功能(可选)

- ✅ 教学型解释生成(更自然、更详细)
- ✅ 新闻情绪语义分析(识别否定/反转语义)
- ✅ Chat 开放式问答(支持自由提问)
- ✅ 优雅降级(LLM 失败时自动使用规则模板)

**注意**: LLM 功能为可选增强,默认关闭。配置 OpenRouter API Key 并设置 `LLM_ENABLED=true` 即可启用。

## 注意事项

1. **数据来源**: 本项目使用 yfinance 从 Yahoo Finance 获取免费数据
2. **延迟**: 免费数据可能有 15-20 分钟延迟
3. **风险提示**: 本系统仅供参考，不构成投资建议
4. **本地时间**: 系统时间影响刷新显示

## 开发

### 添加新的技术指标

编辑 `backend/services/indicators.py`:

```python
def custom_indicator(self, df: pd.DataFrame) -> pd.DataFrame:
    # 计算自定义指标
    df['custom'] = ...
    return df
```

### 修改交易策略

编辑 `backend/services/strategy.py`:

```python
def _generate_signal(self, df, market_state):
    # 自定义信号生成逻辑
    ...
```

## 许可证

MIT License

## 更新日志

### v1.1.0 (2026-02-03)
- ✅ 新增 LLM 增强功能(可选)
  - LLM 生成教学型解释
  - LLM 新闻情绪语义分析
  - LLM Chat 开放式问答
  - 静默回退机制(LLM 失败时使用规则模板)
- ✅ 新闻事件与关联指标展示
  - 接入 Finnhub 新闻数据
  - 新增美元指数(DXY)关联分析
- ✅ 金价 10s 自动刷新与刷新时间展示
- ✅ 图表支持分/日/周/月/年切换
 - ✅ 重大新闻事件触发信号降级与风险提示
 - ✅ 止损区自动遵守最大回撤 15%

### v1.0.0 (2026-02-03)
- ✅ 初始版本发布
- ✅ 实现核心功能：市场分析、信号生成、智能问答
- ✅ 支持手动刷新和定时更新
