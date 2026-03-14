# LLM Integration 环境配置一致性修复

**修复日期**: 2026-03-14
**修复类型**: 代码一致性修复
**严重程度**: P0 (代码不一致)

---

## 问题发现

在审核 `.env.example` 配置文件时，发现代码与环境配置不一致：

1. **`.env.example`** 包含 Anthropic 配置
2. **`client.py`** 包含 Anthropic 配置加载逻辑
3. **`providers.py`** 已移除 `AnthropicProvider` 类
4. **`ModelProvider` 枚举** 已移除 `ANTHROPIC`

这导致：
- 用户可能配置 Anthropic 但无法使用
- 代码逻辑不一致
- 违反 LAW-ENG-001 (职责物理隔离)

---

## 修复内容

### 1. 修复 client.py

**问题**: `client.py:_load_config_from_env()` 中有 Anthropic 配置加载逻辑

**修复**:
```python
# 删除以下代码
- elif provider == ModelProvider.ANTHROPIC:
-     config.update({
-         "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
-         "model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
-     })

# 添加错误处理
else:
    raise ValueError(
        f"不支持的提供商: {provider.value}。"
        f"支持的提供商: openai, zhipu"
    )
```

### 2. 更新 .env.example

**问题**: 包含 Anthropic 配置但代码不支持

**修复**:
```diff
# =============================================================================
# LLM Configuration (LAW-ENV-003: 模型接入标准化)
# =============================================================================
- # Default model provider: openai, anthropic, or zhipu
+ # 默认模型提供商: openai 或 zhipu
  DEFAULT_MODEL_PROVIDER=openai

  # OpenAI API
  OPENAI_API_KEY=your_openai_api_key_here
  ...

- # Anthropic Claude API (Alternative)
- ANTHROPIC_API_KEY=your_anthropic_api_key_here
- ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
- ANTHROPIC_MAX_TOKENS=4096
- ANTHROPIC_TEMPERATURE=0.7
-
  # 智谱 AI API (GLM Models)
  ZHIPU_API_KEY=your_zhipu_api_key_here
  ...

+ # 注意: Anthropic Claude 暂未实现
+ # 如需使用 Anthropic,请参考 packages/sh_llm/README.md 实现适配器
```

---

## 修改文件清单

1. **packages/sh_llm/src/sh_llm/client.py**
   - 移除 Anthropic 配置加载
   - 添加不支持提供商的错误提示

2. **.env.example**
   - 移除 Anthropic 配置项
   - 添加说明注释
   - 更新提供商列表

---

## 验证结果

### 代码一致性检查

| 文件 | Anthropic 引用 | 状态 |
|------|---------------|------|
| `providers.py` | ❌ 无引用 | ✅ 正确 |
| `client.py` | ❌ 无引用 | ✅ 已修复 |
| `__init__.py` | ❌ 无引用 | ✅ 正确 |
| `.env.example` | ❌ 无配置 | ✅ 已修复 |
| `test_providers.py` | ✅ 测试不存在 | ✅ 正确 |

### 功能验证

1. **OpenAI 提供商**: ✅ 正常工作
2. **Zhipu 提供商**: ✅ 正常工作
3. **Anthropic 提供商**: ✅ 正确抛出 `ValueError`

### 合规性验证

- **LAW-ENG-001**: ✅ 职责物理隔离（代码一致）
- **LAW-ENV-003**: ✅ 模型接入标准化（清晰的提供商列表）
- **ARCH.md**: ✅ 代码与文档一致

---

## 影响评估

### 用户影响

- ✅ **正面**: 消除混淆，用户不会配置无法使用的功能
- ⚠️ **破坏性**: 如果用户已配置 Anthropic，需要迁移到 OpenAI 或 Zhipu

### 迁移指南

如果用户需要使用类似 Claude 的功能：

1. **使用 OpenAI**: 更换 `DEFAULT_MODEL_PROVIDER=openai`
2. **使用智谱 AI**: 更换 `DEFAULT_MODEL_PROVIDER=zhipu`
3. **实现 Anthropic**: 参考 `packages/sh_llm/README.md` 实现适配器

---

## 总结

### 修复前问题

- ❌ 代码不一致（client.py 与 providers.py）
- ❌ 配置误导（.env.example 包含无效配置）
- ❌ 违反 LAW-ENG-001

### 修复后状态

- ✅ 代码完全一致
- ✅ 配置清晰准确
- ✅ 符合所有 LAW 规范

### 相关文档

- [P0 修复报告](LLM_INTEGRATION_P0_FIX_REPORT.md)
- [自我审核报告](SELF_AUDIT_LLM_INTEGRATION.md)
- [使用文档](../../../packages/sh_llm/README.md)

---

**修复人员**: Claude Sonnet 4.6
**审核时间**: 2026-03-14
**审核结果**: ✅ **一致性修复完成**
