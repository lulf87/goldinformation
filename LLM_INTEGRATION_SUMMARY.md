# LLM 集成测试指南

## 测试前准备

### 1. 测试 LLM 关闭时的系统运行(默认状态)

系统应该正常工作,使用规则生成的解释。

**测试步骤**:
1. 确保 `.env` 中 `LLM_ENABLED=false` 或未设置
2. 启动后端: `cd backend && python main.py`
3. 启动前端: `cd frontend && npm run dev`
4. 访问 http://localhost:5173

**预期结果**:
- ✅ Dashboard 显示规则生成的市场解读
- ✅ Chat 可以使用规则问答
- ✅ 无 "AI 增强" 标签
- ✅ 无错误日志

### 2. 测试 LLM 开启时(需要 API Key)

#### 配置 OpenRouter API Key

1. 访问 https://openrouter.ai/ 注册账号
2. 获取 API Key
3. 在 `.env` 中配置:
```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxx
LLM_ENABLED=true
```

#### 测试增强功能

**测试 A: 增强解释生成**
1. 刷新 Dashboard
2. 查看市场解读部分
3. **预期**:
   - ✅ 显示 "AI 增强" 标签
   - ✅ 解释更自然、更具教学性
   - ✅ 包含 Markdown 格式

**测试 B: Chat 问答**
1. 进入 Chat 页面
2. 提问: "为什么给出该信号?"
3. **预期**:
   - ✅ 回答更自然、更详细
   - ✅ 与当前分析一致

**测试 C: 频率限制**
1. 多次刷新 Dashboard(超过 3 次)
2. **预期**:
   - ✅ 后台日志显示警告
   - ✅ 仍可继续使用(软限制)

**测试 D: 回退机制**
1. 临时禁用网络或使用错误的 API Key
2. 刷新 Dashboard
3. **预期**:
   - ✅ 系统自动回退到规则解释
   - ✅ 无崩溃,用户体验正常
   - ✅ 日志记录失败信息

### 3. 测试 LLM 统计端点

**测试步骤**:
```bash
curl http://localhost:8000/api/v1/llm/stats
```

**预期返回**:
```json
{
  "enabled": true,
  "model": "anthropic/claude-3.5-sonnet",
  "today_date": "2026-02-03",
  "today_calls": 2,
  "daily_limit": 3,
  "chat_calls": 5,
  "remaining_calls": 1
}
```

### 4. 查看日志

```bash
tail -f logs/llm_calls.log
```

**预期日志格式**:
```json
{"timestamp": "2026-02-03T14:00:00", "call_type": "explanation", "model": "anthropic/claude-3.5-sonnet", "prompt_tokens": 500, "completion_tokens": 300, "total_tokens": 800, "duration_ms": 1500.5, "status": "success", "error": null}
```

## 验收清单

### 功能性验收

- [ ] **LLM 关闭时**: 系统正常工作,使用规则解释
- [ ] **LLM 开启时**: 解释质量明显提升
- [ ] **LLM 失败时**: 自动回退到规则,无崩溃
- [ ] **Chat 问答**: LLM 回答与当前分析一致
- [ ] **频率限制**: 超过限制时记录警告
- [ ] **日志记录**: 所有调用都有日志

### 性能验收

- [ ] **响应时间**: LLM 调用 < 5 秒
- [ ] **超时处理**: 30 秒超时正常工作
- [ ] **重试机制**: 失败后自动重试最多 2 次

### 用户体验验收

- [ ] **UI 标识**: LLM 增强内容有 "AI 增强" 标签
- [ ] **无感回退**: 用户无感知 LLM 失败
- [ ] **一致性**: LLM 输出与规则信号不冲突

### 成本控制验收

- [ ] **每日限制**: 自动更新不超过 1 次
- [ ] **手动限制**: 手动刷新不超过 3 次/天
- [ ] **Chat 不限制**: Chat 可以正常使用

## 常见问题排查

### 问题 1: LLM 不工作
**检查**:
1. `.env` 中 `LLM_ENABLED=true`
2. `OPENROUTER_API_KEY` 已设置且有效
3. 查看后端日志: `tail -f logs/app.log`

### 问题 2: 回退到规则解释
**可能原因**:
- API Key 无效
- 网络问题
- API 速率限制
- 模型不可用

**解决方案**:
1. 检查 `logs/llm_calls.log` 查看错误信息
2. 验证 API Key
3. 检查网络连接

### 问题 3: 响应慢
**原因**: LLM API 调用通常需要 1-3 秒
**优化**:
- 调整 `LLM_TIMEOUT` 配置
- 减少 max_tokens 参数
- 检查网络延迟

## 下一步优化(可选)

1. **缓存 LLM 结果**: 相同输入使用缓存
2. **流式输出**: 实现流式响应提升体验
3. **模型选择**: 支持用户自定义模型
4. **成本监控**: 添加每日成本统计
5. **A/B 测试**: 对比规则和 LLM 效果
