# 集成使用指南

本文档说明如何启动和使用完整的黄金交易系统,包括前端、后端 API 和 WebSocket 实时推送。

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                     前端 (Vue 3)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  API Client  │  │   WebSocket  │  │  Pinia Store │  │
│  │   (Axios)    │  │   (原生 WS)   │  │  (状态管理)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│           │                  │                  │        │
│           └──────────────────┴──────────────────┘        │
│                           │                               │
└───────────────────────────┼───────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   后端 (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ REST API     │  │   WebSocket  │  │  数据服务     │  │
│  │  /api/v1/*   │  │     /ws      │  │  (价格/行情)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 文件结构

### 前端文件
```
frontend/src/
├── api/
│   └── index.ts                      # REST API 客户端
├── services/
│   └── websocket.ts                  # WebSocket 服务
├── stores/
│   ├── trading/
│   │   └── tradingStore.ts           # 交易数据状态管理
│   └── websocket/
│       └── websocketStore.ts         # WebSocket 连接管理
├── components/
│   ├── ui/                           # 基础 UI 组件
│   └── trading/                      # 交易组件
├── views/
│   └── IntegratedTrading.vue         # 集成交易页面
└── router/
    └── index.ts                      # 路由配置
```

### 后端文件
```
backend/
├── main.py                           # FastAPI 应用入口
├── websocket_server.py               # WebSocket 服务器
└── api/
    └── analysis.py                   # 价格分析 API
```

## 快速开始

### 1. 启动后端服务

#### 安装依赖
```bash
cd backend
pip install fastapi uvicorn websockets
```

#### 创建 `main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from websocket_server import router, start_background_tasks
import asyncio

app = FastAPI(title="黄金交易 API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api/v1", tags=["分析"])
app.include_router(router.websocket("/ws"), tags=["WebSocket"])

# 启动 WebSocket 后台任务
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_background_tasks())

@app.get("/")
async def root():
    return {"message": "黄金交易 API 服务正在运行"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 启动服务器
```bash
python main.py
```

服务器将在 `http://localhost:8000` 启动。

### 2. 启动前端服务

#### 配置环境变量
创建 `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

#### 安装依赖
```bash
cd frontend
npm install
```

#### 启动开发服务器
```bash
npm run dev
```

前端将在 `http://localhost:5173` 启动。

### 3. 访问集成页面

在浏览器中打开:
```
http://localhost:5173/trading
```

## 功能说明

### REST API 接口

#### 获取当前价格
```http
GET /api/v1/price/current
```

响应:
```json
{
  "current_price": 580.50,
  "price_change": 2.30,
  "price_change_pct": 0.40
}
```

#### 获取市场深度
```http
GET /api/v1/market/depth
```

响应:
```json
{
  "bids": [
    {"price": 580.00, "volume": 100},
    {"price": 579.50, "volume": 200}
  ],
  "asks": [
    {"price": 581.00, "volume": 150},
    {"price": 581.50, "volume": 180}
  ]
}
```

#### 提交订单
```http
POST /api/v1/orders
```

请求体:
```json
{
  "symbol": "AU9999",
  "type": "buy",
  "order_type": "market",
  "amount": 100,
  "leverage": 1
}
```

### WebSocket 消息格式

#### 客户端发送的消息

**订阅符号**
```json
{
  "type": "subscribe",
  "data": {
    "symbols": ["AU9999", "XAU/USD"]
  },
  "timestamp": 1704000000000
}
```

**取消订阅**
```json
{
  "type": "unsubscribe",
  "data": {
    "symbols": ["XAU/USD"]
  },
  "timestamp": 1704000000000
}
```

**心跳**
```json
{
  "type": "ping",
  "data": {},
  "timestamp": 1704000000000
}
```

#### 服务器推送的消息

**价格更新**
```json
{
  "type": "price",
  "data": {
    "symbol": "AU9999",
    "price": 580.50,
    "change": 2.30,
    "changePercent": 0.40,
    "volume": 5000
  },
  "timestamp": 1704000000000
}
```

**订单簿更新**
```json
{
  "type": "orderbook",
  "data": {
    "symbol": "AU9999",
    "bids": [
      {"price": 580.00, "amount": 100, "total": 100},
      {"price": 579.50, "amount": 200, "total": 300}
    ],
    "asks": [
      {"price": 581.00, "amount": 150, "total": 150},
      {"price": 581.50, "amount": 180, "total": 330}
    ]
  },
  "timestamp": 1704000000000
}
```

**市场深度更新**
```json
{
  "type": "market_depth",
  "data": {
    "symbol": "AU9999",
    "data": [
      {"price": 580.00, "bidVolume": 100, "askVolume": 0},
      {"price": 581.00, "bidVolume": 0, "askVolume": 150}
    ]
  },
  "timestamp": 1704000000000
}
```

**成交记录**
```json
{
  "type": "trade",
  "data": {
    "symbol": "AU9999",
    "price": 580.50,
    "amount": 100,
    "type": "buy",
    "timestamp": "14:30:25"
  },
  "timestamp": 1704000000000
}
```

**心跳响应**
```json
{
  "type": "heartbeat",
  "data": {
    "pong": 1704000000000
  },
  "timestamp": 1704000000000
}
```

## 前端使用示例

### 在组件中使用 Store

```vue
<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useTradingStore } from '@/stores/trading/tradingStore'
import { useWebSocketStore } from '@/stores/websocket/websocketStore'

const tradingStore = useTradingStore()
const wsStore = useWebSocketStore()

onMounted(async () => {
  // 初始化 WebSocket 连接
  wsStore.initialize()

  // 订阅符号
  wsStore.subscribe(['AU9999', 'XAU/USD'])

  // 获取初始数据
  await tradingStore.refreshAllData()
})

onUnmounted(() => {
  // 清理 WebSocket 连接
  wsStore.cleanup()
})
</script>

<template>
  <div>
    <!-- WebSocket 连接状态 -->
    <div class="connection-status">
      状态: {{ wsStore.connectionState }}
    </div>

    <!-- 当前价格 -->
    <div class="price">
      ¥{{ tradingStore.currentPrice }}
      <span :class="tradingStore.priceChange >= 0 ? 'text-green' : 'text-red'">
        {{ tradingStore.priceChangePercent }}%
      </span>
    </div>
  </div>
</template>
```

### 监听 WebSocket 消息

```typescript
// 在组件中监听实时价格
watch(
  () => wsStore.realtimePrices.get('AU9999'),
  (priceData) => {
    if (priceData) {
      console.log('新价格:', priceData.price)
      // 更新 UI 或执行其他操作
    }
  }
)
```

## 数据推送频率

| 数据类型 | 推送频率 | 说明 |
|---------|---------|-----|
| 价格更新 | 2秒 | 实时价格推送 |
| 订单簿 | 5秒 | 买卖盘口数据 |
| 市场深度 | 10秒 | 深度图表数据 |
| 成交记录 | 1-3秒(随机) | 最新成交 |
| 心跳 | 30秒 | 保持连接 |

## 测试 WebSocket 连接

### 使用浏览器控制台

打开浏览器控制台 (F12),执行以下代码:

```javascript
// 连接 WebSocket
const ws = new WebSocket('ws://localhost:8000/ws')

// 监听连接打开
ws.onopen = () => {
  console.log('WebSocket 已连接')

  // 订阅符号
  ws.send(JSON.stringify({
    type: 'subscribe',
    data: { symbols: ['AU9999'] },
    timestamp: Date.now()
  }))
}

// 监听消息
ws.onmessage = (event) => {
  const message = JSON.parse(event.data)
  console.log('收到消息:', message)
}

// 监听错误
ws.onerror = (error) => {
  console.error('WebSocket 错误:', error)
}

// 监听关闭
ws.onclose = () => {
  console.log('WebSocket 已断开')
}
```

### 使用 wscat 命令行工具

安装 wscat:
```bash
npm install -g wscat
```

连接到 WebSocket:
```bash
wscat -c ws://localhost:8000/ws
```

发送订阅请求:
```json
{"type":"subscribe","data":{"symbols":["AU9999"]},"timestamp":1704000000000}
```

## 故障排查

### WebSocket 无法连接

1. 检查后端服务是否启动
   ```bash
   curl http://localhost:8000/
   ```

2. 检查 WebSocket 端点是否可访问
   ```bash
   curl --include \
     --no-buffer \
     --header "Connection: Upgrade" \
     --header "Upgrade: websocket" \
     --header "Host: localhost:8000" \
     --header "Origin: http://localhost:5173" \
     http://localhost:8000/ws
   ```

3. 检查浏览器控制台错误信息

### 收不到实时数据

1. 确认已成功订阅符号
2. 检查 WebSocket 连接状态
3. 查看后端日志是否有错误
4. 确认防火墙没有阻止 WebSocket 连接

### CORS 错误

确保后端配置了正确的 CORS 设置:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 生产环境部署

### 后端部署

1. 使用 Gunicorn + Uvicorn workers:
   ```bash
   pip install gunicorn
   gunicorn main:app \
     --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000
   ```

2. 使用 Nginx 作为反向代理:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /ws {
           proxy_pass http://127.0.0.1:8000/ws;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_read_timeout 86400;
       }
   }
   ```

### 前端部署

1. 构建生产版本:
   ```bash
   npm run build
   ```

2. 部署到静态服务器 (Nginx, Apache, Vercel 等)

3. 更新环境变量为生产地址

## 性能优化

### 后端优化

1. 使用 Redis 缓存价格数据
2. 使用消息队列 (RabbitMQ, Kafka) 处理订单
3. 数据库索引优化
4. WebSocket 连接池管理

### 前端优化

1. 使用虚拟滚动处理大量订单簿数据
2. 防抖处理高频 WebSocket 消息
3. 使用 Web Worker 处理复杂计算
4. 实现数据分页和懒加载

## 安全建议

1. **认证**: 实现 JWT 认证保护 API 和 WebSocket
2. **限流**: 防止 API 滥用和 DDoS 攻击
3. **输入验证**: 验证所有用户输入
4. **HTTPS**: 生产环境使用加密连接
5. **CORS**: 严格配置允许的域名
6. **敏感数据**: 不在日志中记录敏感信息

## 下一步

- [ ] 实现用户认证和授权
- [ ] 添加订单历史查询
- [ ] 实现持仓管理
- [ ] 添加价格预警功能
- [ ] 实现交易统计和报表
- [ ] 添加风险控制模块
- [ ] 实现模拟交易模式
- [ ] 添加移动端适配

## 参考文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Vue 3 官方文档](https://vuejs.org/)
- [Pinia 官方文档](https://pinia.vuejs.org/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [设计系统文档](../design-system/gold-trading/MASTER.md)
