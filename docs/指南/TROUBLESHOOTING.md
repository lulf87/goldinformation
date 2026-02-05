# 🚀 快速启动指南

## 启动前端应用

```bash
# 1. 进入前端目录
cd /Users/lulingfeng/Documents/工作/开发/黄金交易/frontend

# 2. 启动开发服务器
npm run dev

# 3. 在浏览器中访问
# 主页: http://localhost:5173/
# 深度分析: http://localhost:5173/analysis
# AI 助手: http://localhost:5173/chat
```

---

## 🔍 常见问题排查

### 问题 1: 应用无法启动

**可能原因**: 依赖未安装

**解决方案**:
```bash
cd frontend
npm install
```

---

### 问题 2: 白屏或页面空白

**可能原因**: JavaScript 错误

**解决方案**:
1. 打开浏览器开发者工具 (F12)
2. 查看 Console 标签页的错误信息
3. 查看错误堆栈找到问题文件

---

### 问题 3: 样式未生效

**可能原因**: 设计系统 CSS 未加载

**解决方案**:
- 确认 `frontend/src/main.ts` 包含以下导入：
```typescript
import './styles/design-system.css'
```

---

### 问题 4: 路由 404

**可能原因**: 路由配置错误

**解决方案**:
- 检查 `frontend/src/router/index.ts` 配置
- 确认所有路由指向的组件文件存在

---

### 问题 5: 组件导入错误

**可能原因**: 组件路径错误

**解决方案**:
- 确认所有导入路径使用 `@/` 别名
- 例如: `import MarketDepth from '@/components/MarketDepth.vue'`

---

## 📋 验证清单

启动前确认：

- [ ] Node.js 已安装 (v16+)
- [ ] 依赖已安装 (`npm install`)
- [ ] 后端服务运行在 http://127.0.0.1:8000
- [ ] 前端配置了正确的 API 代理

---

## 🎯 访问新页面

优化后新增的页面：

| 路由 | 页面 | 说明 |
|------|------|------|
| `/` | 主仪表板 | 市场分析和价格概览 |
| `/analysis` | 深度分析 | 技术指标和趋势分析 |
| `/chat` | AI 助手 | 智能问答 |

---

## 💡 提示

如果遇到问题：

1. **清除浏览器缓存**
   - Chrome: Cmd+Shift+R (Mac) 或 Ctrl+Shift+R (Windows)
   - 或者在开发者工具中右键刷新按钮选择"清空缓存并硬性重新加载"

2. **查看控制台错误**
   - 打开开发者工具 (F12)
   - 查看 Console 和 Network 标签页

3. **重启开发服务器**
   ```bash
   # 停止服务器 (Ctrl+C)
   # 重新启动
   npm run dev
   ```

4. **检查端口占用**
   ```bash
   # 查看 5173 端口是否被占用
   lsof -i :5173
   ```

---

## 📞 需要帮助？

如果问题仍未解决，请提供：

1. 完整的错误信息截图
2. 浏览器控制台的错误堆栈
3. 你尝试访问的 URL
4. 使用的操作系统和浏览器版本

---

**最后更新**: 2026-02-05
