"""
WebSocket 服务器
用于实时推送黄金交易数据

功能:
- 实时价格推送
- 订单簿更新
- 市场深度推送
- 成交记录推送
- 心跳保持连接
"""

from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import List, Dict, Set
import json
import asyncio
from datetime import datetime
import random

router = APIRouter()


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 存储所有活跃的 WebSocket 连接
        self.active_connections: List[WebSocket] = []
        # 存储订阅的符号
        self.subscriptions: Dict[WebSocket, Set[str]] = {}

    async def connect(self, websocket: WebSocket, symbols: List[str] = None):
        """接受新的 WebSocket 连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = set(symbols or ['AU9999', 'XAU/USD'])
        print(f"[WebSocket] 新连接建立. 当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        print(f"[WebSocket] 连接断开. 当前连接数: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送消息给特定连接"""
        try:
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
        except Exception as e:
            print(f"[WebSocket] 发送消息失败: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: dict, symbol: str = None):
        """广播消息给所有订阅了该符号的连接"""
        disconnected = []
        for connection in self.active_connections:
            # 检查是否订阅了该符号
            if symbol and symbol not in self.subscriptions.get(connection, set()):
                continue

            try:
                await connection.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                print(f"[WebSocket] 广播消息失败: {e}")
                disconnected.append(connection)

        # 清理断开的连接
        for conn in disconnected:
            self.disconnect(conn)

    def get_subscriptions(self, websocket: WebSocket) -> Set[str]:
        """获取连接的订阅列表"""
        return self.subscriptions.get(websocket, set())

    def update_subscriptions(self, websocket: WebSocket, symbols: List[str]):
        """更新连接的订阅"""
        self.subscriptions[websocket] = set(symbols)
        print(f"[WebSocket] 更新订阅: {symbols}")


# 全局连接管理器
manager = ConnectionManager()


async def generate_price_data(symbol: str) -> dict:
    """生成模拟价格数据"""
    # 基准价格
    base_prices = {
        'AU9999': 580.50,
        'XAU/USD': 2350.00,
    }

    base_price = base_prices.get(symbol, 500.0)
    change = round(random.uniform(-2.0, 2.0), 2)
    change_percent = round((change / base_price) * 100, 2)

    return {
        'symbol': symbol,
        'price': round(base_price + change, 2),
        'change': change,
        'changePercent': change_percent,
        'volume': random.randint(1000, 10000),
        'timestamp': int(datetime.now().timestamp() * 1000)
    }


async def generate_orderbook_data(symbol: str) -> dict:
    """生成模拟订单簿数据"""
    base_price = 580.50 if symbol == 'AU9999' else 2350.00

    # 生成买单 (从高到低)
    bids = []
    for i in range(10):
        price = round(base_price - (i + 1) * 0.5, 2)
        volume = random.randint(100, 1000)
        total = volume + sum(b['amount'] for b in bids)
        bids.append({
            'price': price,
            'amount': volume,
            'total': total
        })

    # 生成卖单 (从低到高)
    asks = []
    for i in range(10):
        price = round(base_price + (i + 1) * 0.5, 2)
        volume = random.randint(100, 1000)
        total = volume + sum(a['amount'] for a in asks)
        asks.append({
            'price': price,
            'amount': volume,
            'total': total
        })

    return {
        'symbol': symbol,
        'bids': bids,
        'asks': asks,
        'timestamp': int(datetime.now().timestamp() * 1000)
    }


async def generate_market_depth_data(symbol: str) -> dict:
    """生成模拟市场深度数据"""
    base_price = 580.50 if symbol == 'AU9999' else 2350.00

    depth_data = []
    for i in range(50):
        price = round(base_price + (i - 25) * 0.5, 2)
        bid_volume = random.randint(0, 500) if i < 25 else 0
        ask_volume = random.randint(0, 500) if i >= 25 else 0
        depth_data.append({
            'price': price,
            'bidVolume': bid_volume,
            'askVolume': ask_volume
        })

    return {
        'symbol': symbol,
        'data': depth_data,
        'timestamp': int(datetime.now().timestamp() * 1000)
    }


async def generate_trade_data(symbol: str) -> dict:
    """生成模拟成交数据"""
    base_price = 580.50 if symbol == 'AU9999' else 2350.00

    return {
        'symbol': symbol,
        'price': round(base_price + random.uniform(-1.0, 1.0), 2),
        'amount': random.randint(10, 500),
        'type': random.choice(['buy', 'sell']),
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }


async def price_update_task():
    """价格更新任务 - 每2秒推送一次"""
    while True:
        for symbol in ['AU9999', 'XAU/USD']:
            price_data = await generate_price_data(symbol)
            message = {
                'type': 'price',
                'data': price_data,
                'timestamp': int(datetime.now().timestamp() * 1000)
            }
            await manager.broadcast(message, symbol)
        await asyncio.sleep(2)


async def orderbook_update_task():
    """订单簿更新任务 - 每5秒推送一次"""
    while True:
        for symbol in ['AU9999', 'XAU/USD']:
            orderbook_data = await generate_orderbook_data(symbol)
            message = {
                'type': 'orderbook',
                'data': orderbook_data,
                'timestamp': int(datetime.now().timestamp() * 1000)
            }
            await manager.broadcast(message, symbol)
        await asyncio.sleep(5)


async def market_depth_update_task():
    """市场深度更新任务 - 每10秒推送一次"""
    while True:
        for symbol in ['AU9999', 'XAU/USD']:
            depth_data = await generate_market_depth_data(symbol)
            message = {
                'type': 'market_depth',
                'data': depth_data,
                'timestamp': int(datetime.now().timestamp() * 1000)
            }
            await manager.broadcast(message, symbol)
        await asyncio.sleep(10)


async def trade_update_task():
    """成交记录更新任务 - 随机推送"""
    while True:
        symbol = random.choice(['AU9999', 'XAU/USD'])
        trade_data = await generate_trade_data(symbol)
        message = {
            'type': 'trade',
            'data': trade_data,
            'timestamp': int(datetime.now().timestamp() * 1000)
        }
        await manager.broadcast(message, symbol)
        await asyncio.sleep(random.uniform(1, 3))


async def heartbeat_task():
    """心跳任务 - 每30秒发送一次"""
    while True:
        message = {
            'type': 'heartbeat',
            'data': {'ping': int(datetime.now().timestamp() * 1000)},
            'timestamp': int(datetime.now().timestamp() * 1000)
        }
        await manager.broadcast(message)
        await asyncio.sleep(30)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点"""
    # 等待客户端发送订阅请求
    try:
        await manager.connect(websocket)

        # 发送欢迎消息
        welcome_message = {
            'type': 'news',
            'data': {
                'title': '连接成功',
                'message': f'已连接到黄金交易 WebSocket 服务. 当前时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            },
            'timestamp': int(datetime.now().timestamp() * 1000)
        }
        await manager.send_personal_message(welcome_message, websocket)

        # 处理客户端消息
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # 处理不同类型的消息
            if message.get('type') == 'subscribe':
                # 订阅符号
                symbols = message.get('data', {}).get('symbols', ['AU9999'])
                manager.update_subscriptions(websocket, symbols)

                # 发送确认
                confirm_message = {
                    'type': 'news',
                    'data': {
                        'title': '订阅成功',
                        'message': f'已订阅: {", ".join(symbols)}'
                    },
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }
                await manager.send_personal_message(confirm_message, websocket)

            elif message.get('type') == 'unsubscribe':
                # 取消订阅
                symbols = message.get('data', {}).get('symbols', [])
                current_subs = manager.get_subscriptions(websocket)
                new_subs = current_subs - set(symbols)
                manager.update_subscriptions(websocket, list(new_subs))

                # 发送确认
                confirm_message = {
                    'type': 'news',
                    'data': {
                        'title': '取消订阅',
                        'message': f'已取消订阅: {", ".join(symbols)}'
                    },
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }
                await manager.send_personal_message(confirm_message, websocket)

            elif message.get('type') == 'ping':
                # 响应心跳
                pong_message = {
                    'type': 'heartbeat',
                    'data': {'pong': int(datetime.now().timestamp() * 1000)},
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }
                await manager.send_personal_message(pong_message, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"[WebSocket] 客户端主动断开连接")
    except Exception as e:
        print(f"[WebSocket] 错误: {e}")
        manager.disconnect(websocket)


# 启动后台任务的函数
def start_background_tasks():
    """启动所有后台推送任务"""
    import asyncio

    async def run_tasks():
        await asyncio.gather(
            price_update_task(),
            orderbook_update_task(),
            market_depth_update_task(),
            trade_update_task(),
            heartbeat_task()
        )

    # 在应用启动时调用
    return run_tasks


# 使用示例:
# 在 main.py 中:
#
# from websocket_server import router, start_background_tasks
# from fastapi import FastAPI
# import asyncio
#
# app = FastAPI()
#
# # 注册 WebSocket 路由
# app.include_router(router)
#
# # 启动后台任务
# @app.on_event("startup")
# async def startup_event():
#     asyncio.create_task(start_background_tasks())
