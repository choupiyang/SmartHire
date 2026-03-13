COMPOUND.md - 动态避坑与复利知识压缩协议

Version: 3.0.0 (The Distilled Pentagon Edition)

Status: Active / Distilled

Limit: Strictly Max 5000 Tokens

Role: The Judiciary / Precedents & Pitfalls

Ecosystem: Enforces LAW.md, Guides MAP.md, Aligned with DIAGNOSIS.md and ARCH.md

0. 治理五权分立互操作协议

作为“五权分立”中的司法判例库，本文件仅记录在 Windows 单租户环境下，具有架构破坏性、调试非直观性、物理机特有性的失效模式。它是系统的“负向知识库”，与另外四份核心文档保持以下动态关系：

To MAP.md (向行政输出): 每一个 Case 转化为防御性代码。若更新成本过高，允许在 MAP 中记录“文档债务”，延后更新。

To LAW.md (向立法反哺): 频次 > 3 的 Case 必须提炼为铁律，并从此处删除（晋升）。

To ARCH.md (向蓝图反馈): 架构设计导致的重复 Bug 需升级 ARCH.md。

To DIAGNOSIS.md (向免疫反哺): 记录不当 Debug 导致的次生灾害。

1. 记录准则 (Entry & Compaction Criteria)

为了防止文档熵增，所有进入本手册的条目必须经过以下审计：

准入标准： 单次调试耗时 > 4h；现象与根因严重背离；或直接导致违反 LAW/ARCH 的系统级崩溃。

禁止标准： 严禁记录语法错误、基础业务 Bug 或第三方库官方文档已涵盖的内容。

修剪与分层协议 (Layering)： * 摘要层： 此文件。当接近 5000 tokens 时，必须启动“知识蒸馏”，将同类项合并为通用的设计模式，并删除已通过底层框架彻底免疫的旧记录。

详情层： docs/debug/YYYY-MM-DD_case_x.md。仅高频或极其复杂的 Case 才建立详情层链接以存放完整 Stack Trace。

2. 核心知识库预设 (Core Knowledge Base Presets)

2.1 [ENV] Windows 物理环境失效模式

ID模式名称失效场景 (Context)致命根因 (Root Cause)结构性规避 (Resolution)ENV-01路径深度溢出向量库索引、多级缓存嵌套或长文件操作。Windows MAX_PATH (260字符) 物理限制。强制执行根路径锚定；目录嵌套深度严禁超过 5 层。ENV-02NTFS 写锁冲突多进程竞争写入同一个 SQLite 文件或日志文件。Windows 强制文件锁（Mandatory Locking）。引入指数退避（Backoff）重试；核心写权限收拢至单一进程。ENV-03GBK 僵尸输出通过 subprocess 调用本地工具获取报错信息。Windows 默认 OEM 代码页与 Python UTF-8 冲突。管道调用显式声明 encoding='65001' (UTF-8) 或执行字节流强制转换。ENV-04孤儿进程泄露主进程异常崩溃，EXECUTE 启动的物理脚本残留。Windows 进程树缺乏自动回收机制。利用 Win32 Job Objects 将子进程与主进程生命周期绑定。

2.2 [IPC] 跨进程通信与同步失效模式

ID模式名称失效场景 (Context)致命根因 (Root Cause)结构性规避 (Resolution)IPC-01指令时序倒挂高频发送任务指令，且网络/IO 存在波动。Redis 队列读取顺序与物理发起时间不一致。封包强制携带全局自增 sequence_id，接收端自动丢弃过期指令。IPC-02消息积压崩溃PLAN 拆解任务速度远快于 EXECUTE 执行物理动作。缺乏背压（Backpressure）负反馈机制。PLAN 下发前主动监测队列长度，超过阈值则由 MESSAGE 触发限流响应。IPC-03IPC 性能地狱简单对话响应延迟 > 2s，Windows 管道偶尔僵死。强制所有技能走 Subprocess 模式，进程启动开销巨大。实施弹性集成。高频/核心技能切至 Embedded，仅边缘重度应用保留 Subprocess。IPC-04边界契约违反工具执行成功但系统突发崩溃。跨层传递时返回 Dict 而非 String，违反了强类型通信契约。严守 L4→L2 边界验证，使用 Pydantic 并在入口实施防御性类型提取。IPC-05事件循环污染集成飞书/钉钉等 IM 平台的官方 SDK 时，SDK 提供的 `start()` 方法是同步阻塞调用，内部使用 `loop.run_until_complete()`，与 Shasha 的纯 asyncio 架构冲突。Python 的 `asyncio.run()` 和 `loop.run_until_complete()` 会检测当前线程是否已有运行中的事件循环。即使使用 `threading.Thread()` 在后台线程运行，SDK 内部仍可能检测到主线程的事件循环。1. 物理隔离: 将 SDK 运行在独立进程中 (不共享事件循环) 2. IPC 桥接: 使用 Redis Pub/Sub (已部署的基础设施) 跨进程传递消息 3. 避免使用 `multiprocessing.Queue` (序列化开销、无原生支持) 4. 保持核心进程 (MESSAGE/PLAN/EXECUTE/WATCHDOG) 的纯 asyncio 环境IPC-06Pydantic 字段名不匹配在跨进程通信中使用 Pydantic 模型时，代码中使用的字段名与模型定义不一致，导致运行时 ValidationError。未在开发过程中进行 Pydantic 模型实例化验证；依赖静态类型检查 (mypy) 未发现运行时字段名错误；测试未覆盖实际的对象创建代码路径。1. 开发阶段: 创建简单的验证脚本，测试 Pydantic 模型实例化 2. 测试阶段: 添加"模型字段匹配性"测试用例 3. CI/CD: 集成 Pydantic 模型验证检查 4. 代码审查: 重点检查 Pydantic 模型的字段名使用

2.3 [AI] 逻辑演化与反思失效模式

ID模式名称失效场景 (Context)致命根因 (Root Cause)结构性规避 (Resolution)AI-01反思逻辑坍塌系统连续针对同一个错误尝试自愈失败。提示词权重被原有错误上下文深度污染（幻觉叠加）。引入反思阈值熔断；第二次重试强制切换“极端批判/对比” Prompt 模板。AI-02硬约束偏移长对话或复杂任务导致系统偏离 LAW 核心准则。Token 窗口滑动导致 System Prompt 权重被业务信息稀释。将核心红线指令采用 System 角色强注入，并配合 OutputGuard 拦截器。AI-03高熵截断幻觉工具执行后，进入下一轮对话时 JSON 解析无故断裂。Base64 等高熵、无语义字符严重干扰 LLM 注意力，诱发截断输出。Prompt 降噪：拦截并移除高熵参数，替换为人类可读的明文摘要，同时在 SDK 层做 try-catch 兜底。AI-04认知启动阻塞应用启动卡死，网络握手迟迟无法建立。初始化时同步触发了耗时的 SOUL 压缩或远程 LLM 交互。严格执行异步初始化，将非关键的认知压缩/总结推入后台 Daemon 线程（只读模式）。

3. 动态维护记录 (Incidents Log)

开发者自检： 新问题是否符合准入标准？是否已进行信息熵压缩？

[2026.02.16-02.22 蒸馏归档]

已将 [Ar-05]、[Ar-06]、[Ar-12] 等关于 AST 静态解析、f-string 污染的底层代码 Bug 修复至框架底座，从本宏观架构避坑指南中移除。

将 [Ar-08] 蒸馏为 IPC-04 边界契约违反；将 [Ar-11] 蒸馏为 AI-03 高熵截断幻觉。

[2026.02.23-001]

现象： Windows Defender 实时扫描导致 SQLite 随机出现 database is locked。

避坑逻辑： 部署脚本必须自动将项目根目录下的 ./data/ 文件夹加入 Defender 排除项。

[2026.02.25-001]

失效模式： sys.path 配置不一致导致测试失败

失效场景：测试脚本的 sys.path 只包含 `packages/`，缺少 `packages/*/src`，导致 pi_mono.core 等模块无法导入。

致命根因： ARCH.md 的物理拓扑设计中，每个包有独立的 `src/` 子目录（如 `packages/pi_mono_core/src/pi_mono/core/`）。测试脚本未添加这些路径到 sys.path。

结构性规避：统一使用 glob 动态添加所有 `packages/*/src` 到 sys.path：`for pkg_src_dir in project_root.glob("packages/*/src"): sys.path.insert(0, str(pkg_src_dir))`。

---

[2026.02.25-002]

失效模式： 相对导入与脚本启动方式不兼容

失效场景：使用 `python main.py` 直接运行脚本时，相对导入（`from .xxx import`）失败，报错 "ImportError: attempted relative import with no known parent package"。

致命根因：相对导入只在模块作为包的一部分运行时有效。直接运行脚本时，Python 不知道该模块的父包，导致相对导入失败。

结构性规避：
1. 方案 A（推荐）：在 main.py 开头动态添加 apps/ 到 sys.path，使用绝对导入：
   ```python
   apps_root = Path(__file__).resolve().parent.parent
   if str(apps_root) not in sys.path:
       sys.path.insert(0, str(apps_root))
   from apps.shasha_xxx.yyy import Zzz
   ```
2. 方案 B：使用 `python -m apps.shasha_xxx.main` 启动（需修改 ss.py）
3. 方案 C：创建 `apps/shasha_xxx/__main__.py`（需要多个文件）

失效场景 (Context): 测试脚本和生产环境使用不同的 sys.path 配置模式，导致 `No module named 'pi_mono.core'` 导入错误。

致命根因 (Root Cause): 测试脚本硬编码添加 `packages/` 而非 `packages/*/src`，无法找到 Monorepo 包的实际源代码位置。生产环境 (ss.py) 使用正确的 glob 模式 `packages/*/src`。

结构性规避 (Resolution):
1. 强制所有脚本使用统一的 sys.path 配置模式：
    ```python
    for pkg_src_dir in project_root.glob("packages/*/src"):
        sys.path.insert(0, str(pkg_src_dir))
    ```
2. 在 COMPOUND.md 记录此模式作为最佳实践
3. 建议在未来版本中通过 `anchor_root()` 统一管理所有 sys.path 配置

---

[2026.02.25-003]

失效模式： WATCHDOG 启动竞态条件

失效场景：WATCHDOG 启动进程后立即检查心跳，但进程还在初始化阶段（需要 2-5 秒），导致进程被误判为无心跳而持续重启。

致命根因：监控循环设计缺陷。启动进程后立即进入监控循环，第一次循环立即检查心跳，而此时进程还未进入主循环发送第一次心跳。

结构性规避：
1. 方案 A：启动进程后添加 10 秒缓冲期（兜底保护）
2. 方案 B：在 ProcessManager 中跟踪进程启动时间，使用 `time.monotonic()` 保证时间单调性，缓冲期内跳过心跳检查（避免误报）
3. 混合方案：同时实施 A 和 B，提供双重保护

验证结果：✅ 修复成功。2026.02.26 测试通过，所有进程正常启动，无持续重启问题。

---

[IPC-05]

失效模式：第三方同步 SDK 与 asyncio 环境冲突

失效场景 (Context): 集成飞书/钉钉等 IM 平台的官方 SDK 时，SDK 提供的 `start()` 方法是同步阻塞调用，内部使用 `loop.run_until_complete()`，与 Shasha 的纯 asyncio 架构冲突。

致命根因 (Root Cause): Python 的 `asyncio.run()` 和 `loop.run_until_complete()` 会检测当前线程是否已有运行中的事件循环。即使使用 `threading.Thread()` 在后台线程运行，SDK 内部仍可能检测到主线程的事件循环。

结构性规避 (Resolution):
1. 物理隔离: 将 SDK 运行在独立进程中 (不共享事件循环)
2. IPC 桥接: 使用 Redis Pub/Sub (已部署的基础设施) 跨进程传递消息
3. 避免使用 `multiprocessing.Queue` (序列化开销、无原生支持)
4. 保持核心进程 (MESSAGE/PLAN/EXECUTE/WATCHDOG) 的纯 asyncio 环境

关联修复计划: docs/PLAN_FEISHU_GATEWAY_REDIS_FIX.md

验证结果: ✅ 修复成功。2026.02.26 测试通过，Gateway 进程独立运行，核心进程保持纯 asyncio 环境。

---

[DINGTALK-001]

失效模式：钉钉 Stream SDK 数据结构假设错误

失效场景：代码错误假设钉钉 Stream SDK 使用嵌套数据结构（如 `message.sender.sender_id`），而实际 SDK 使用扁平结构（如 `message.sender_id`）。

致命根因：L2 协议层缺陷。代码直接访问嵌套属性（`obj.sub_obj.attr`），导致 `AttributeError`。实际 SDK 使用扁平结构和字典扩展字段。

结构性规避：
1. 实施统一的 `extract_message_content()` 工具函数，提供双重回退策略（extensions 字典优先）
2. 对所有第三方 SDK 数据结构进行前置验证（Phase 0 前置验证）
3. 使用单例模式封装数据访问逻辑，避免重复的错误模式
4. 遵循 DIAGNOSIS v3.0 四层定损模型进行测试

关联修复计划：docs/DINGTALK_STREAM_ATTR_BUG_FIX_PLAN.md

验证结果：✅ 修复成功。2026.02.26 测试通过，所有数据访问逻辑已修复。

---

[IPC-05-A]

失效模式：Gateway 进程心跳缺失导致 WATCHDOG 误判重启

失效场景 (Context): Gateway 进程（Feishu WebSocket 客户端）成功建立连接后，不发送心跳信号到 WATCHDOG，导致 WATCHDOG 每 10-15 秒重启 Gateway 进程。

致命根因 (Root Cause):
1. Gateway 进程缺少心跳发送机制（L1 物理层缺陷）
2. WATCHDOG 期望 MESSAGE 进程发送心跳，但 Gateway 不发送任何心跳（L2 协议层缺陷）
3. Feishu SDK 的 `client.start()` 是同步阻塞调用，阻塞主线程无法执行后台任务（L1 物理层缺陷）
4. Gateway 使用同步 Redis 客户端，与异步 `publish_heartbeat()` 函数不兼容（L2 协议层缺陷）

结构性规避 (Resolution):
1. 实现 `publish_heartbeat_sync()` 同步心跳发送函数（bus.py）
2. 在 Gateway 进程中使用后台守护线程定期发送心跳（每 5 秒）
3. 使用 `ProcessName.message` + `metadata["component": "feishu_gateway"]` 标识 Gateway（ADR-001）
4. 修改 WATCHDOG 心跳检查逻辑，正确识别 Gateway 心跳

架构决策 (ADR-001): Gateway 心跳使用 `ProcessName.message` + `metadata["component"]` 识别：
- 符合 ARCH.md v2.6 四进程架构（Gateway 是 MESSAGE 的物理隔离层）
- 不修改 `ProcessName` 枚举，保持架构一致性
- 允许 WATCHDOG 监控 Gateway 而不增加新进程类型

关键修改:
1. `packages/pi_mono_core/src/pi_mono/core/bus.py`: 添加 `publish_heartbeat_sync()` 函数
2. `apps/shasha_message/gateway.py`: 添加心跳工作线程
3. `apps/shasha_watchdog/main.py`: 修改心跳检查逻辑（第 420-427 行）

关联修复计划: docs/GATEWAY_HEARTBEAT_FIX_PLAN.md

验证结果: ✅ 修复成功。2026.02.26 测试通过，Gateway 进程正常发送心跳，WATCHDOG 正确识别。

---

[IPC-06]

失效模式：Pydantic 模型字段名不匹配导致运行时崩溃

失效场景 (Context): 在跨进程通信中使用 Pydantic 模型时，代码中使用的字段名与模型定义不一致，导致 ValidationError。

致命根因 (Root Cause):
1. 未在开发过程中进行 Pydantic 模型实例化验证
2. 依赖静态类型检查 (mypy) 未发现运行时字段名错误
3. 测试未覆盖实际的对象创建代码路径

结构性规避 (Resolution):
1. 开发阶段: 创建简单的验证脚本，测试 Pydantic 模型实例化
2. 测试阶段: 添加"模型字段匹配性"测试用例
3. CI/CD: 集成 Pydantic 模型验证检查
4. 代码审查: 重点检查 Pydantic 模型的字段名使用

示例代码 (验证脚本):
```python
# 在完成 Gateway 实现后运行此验证
from pi_mono.core.models import PlatformContext
try:
    ctx = PlatformContext(
        msg_id='test',  # 错误字段名
    )
except ValidationError as e:
    print(f"字段名错误: {e}")
```

修复详情:
1. PlatformContext 字段更正: `msg_id` → `message_id`, `raw_data` → `raw_webhook`, 移除 `timestamp`
2. TaskRequest 字段更正: 添加 `sequence_id`, 修正 `priority` (NORMAL → P1)
3. 添加 `_get_next_sequence_id()` 方法，使用 Redis INCR 原子操作获取序列号

关联修复计划: docs/PLAN_FEISHU_GATEWAY_REDIS_FIX.md

验证结果: ✅ 修复成功。2026.02.26 测试通过，Gateway 进程正常启动，Pydantic 模型验证通过。

---

[L2-03]

失效模式：IM协议解析不完整

失效场景 (Context): Gateway进程直接返回飞书的JSON字符串 `'{"text":"hi"}'`，未解析提取纯文本，导致IntentRouter关键字匹配失败。

致命根因 (Root Cause):
1. **L2协议层缺陷**: Gateway未完成协议脱水（ARCH v2.6 §2）
2. **代码重复**: 协议解析逻辑散布在Gateway和Webhook两处
3. **缺乏统一接口**: 无共享的协议适配层

失效表现:
- 用户发送"hi" → `IntentType.UNKNOWN`
- 关键词匹配失败: `"hi" in '{"text":"hi"}'` = False
- 影响范围: 100%飞书Gateway模式消息

结构性规避 (Resolution):
1. **创建统一协议适配层**: 在`pi_mono/core/protocols.py`定义`IProtocolParser`接口
2. **提取解析逻辑到共享库**: 将`feishu.py:115-131`的解析逻辑重构为`FeishuProtocolParser`
3. **实现优雅降级**: 所有解析器实现异常捕获，返回安全默认值`"[消息解析失败]"`
4. **灰度发布**: 使用影子运行机制验证新解析器
5. **金牌测试集**: 定义10个金牌测试用例防止逻辑退化

关联修复计划: docs/PLAN_PROTOCOL_PARSER_ARCHITECTURE.md

验证结果: ✅ 修复成功。2026.02.27 测试通过，飞书消息正确解析为纯文本。

经验教训:
- 协议解析必须在Gateway完成（LAW 5.1: 跨进程通信契约）
- 代码重复是技术债的信号（ARCH v2.6: 使用共享库）
- 测试必须覆盖真实SDK数据（DIAGNOSIS §2.1: 基线验证）

---

[L2-04]

失效模式：协议解析器数据契约不一致

失效场景 (Context): Gateway提取`event.event`后传给Protocols，但Protocols期望收到完整的`event`对象，导致`hasattr(event_data, 'event')`检查失败。

致命根因 (Root Cause):
1. **数据结构假设不一致**: Gateway和Protocols对数据格式有不同的假设
2. **缺少明确的数据契约**: 接口文档未说明支持的数据格式
3. **测试覆盖不足**: 单元测试使用字典格式，未覆盖Gateway模式的SDK对象

失效表现:
- 飞书发送"hello" → 新解析器返回`[消息解析失败]`
- 影子运行显示解析结果差异
- 意图识别失败（`IntentType.UNKNOWN`）
- 影响100%飞书Gateway模式消息

结构性规避 (Resolution):
1. **兼容多种数据格式**: 修改`_extract_raw_content`、`extract_message_id`、`validate_event`支持：
   - 提取后的event对象（Gateway模式）: `event_data.message.content`
   - 完整的event对象: `event_data.event.message.content`
   - 字典格式（Webhook模式）: `event_data['event']['message']['content']`
2. **明确数据契约**: 在文档字符串中说明支持的数据格式
3. **增强测试覆盖**: 添加模拟SDK对象的集成测试（12个测试用例）
4. **优先Gateway模式**: 调整路径检查顺序，优先检查`event_data.message`

关键修改:
1. `packages/pi_mono_core/src/pi_mono/core/protocols.py:159-189`: 修改`_extract_raw_content`方法
2. `packages/pi_mono_core/src/pi_mono/core/protocols.py:232-259`: 修改`extract_message_id`方法
3. `packages/pi_mono_core/src/pi_mono/core/protocols.py:275-301`: 修改`validate_event`方法
4. `tests/unit/test_protocol_parsers.py`: 添加4个Gateway模式测试用例
5. `tests/integration/test_protocol_parser_gateway.py`: 新建集成测试文件（12个测试用例）

关联修复计划: docs/PLAN_PROTOCOL_PARSER_DATA_CONTRACT_FIX.md

验证结果: ✅ 修复成功。2026.02.27 测试通过（19个单元测试 + 12个集成测试 + 10个金牌测试 = 41个测试全部通过）

经验教训:
- 跨模块调用需要明确数据契约（LAW 5.1）
- 测试必须覆盖真实使用场景（DIAGNOSIS §2.1）
- 影子运行机制有效发现兼容性问题
- 同步修改所有相关方法（_extract_raw_content、extract_message_id、validate_event）保持一致性

---

[L2-05]

失效模式：ModelFactory 配置硬编码导致环境变量失效

失效场景 (Context): ModelFactory 在初始化时硬编码为使用 `anthropic` 作为默认模型提供商，即使设置了 `DEFAULT_MODEL_PROVIDER=openai` 和 `OPENAI_API_KEY`，系统仍然使用 Anthropic API。

致命根因 (Root Cause):
1. **L2 协议层缺陷**: ModelFactory.__init__() 未读取 DEFAULT_MODEL_PROVIDER 环境变量
2. **配置耦合**: 模型配置在模块加载时创建（module-level），此时环境变量可能未设置
3. **API Key 读取优先级错误**: clients.py 未正确实现环境变量回退机制
4. **缺少配置验证**: 没有运行时验证默认提供商配置是否正确

失效表现:
- 设置 `DEFAULT_MODEL_PROVIDER=openai` + `OPENAI_API_KEY` → 系统仍使用 Anthropic
- IntentRouter 超时（Anthropic API 不可用或网络问题）
- 用户意图识别失败 → 所有消息路由到 PLAN（不正确）
- 影响范围: 100% 需要 OpenAI 替代的场景

结构性规避 (Resolution):
1. **环境变量支持**: 在 ModelFactory.__init__() 中读取 DEFAULT_MODEL_PROVIDER
2. **向后兼容**: 保留默认值 "anthropic"（不设置环境变量时行为不变）
3. **API Key 回退**: 修改 clients.py 实现环境变量回退：`config.api_key if config.api_key else os.getenv("OPENAI_API_KEY")`
4. **配置验证**: 添加单元测试验证环境变量正确生效
5. **文档更新**: 在 .env.example 中添加配置说明和推荐值

关键修改:
1. `packages/pi_mono_ai/src/pi_mono/ai/factory.py:53-59`: 添加 DEFAULT_MODEL_PROVIDER 环境变量支持
2. `packages/pi_mono_ai/src/pi_mono/ai/clients.py:127,171`: 修改 API Key 读取逻辑
3. `.env.example:39-42`: 添加 DEFAULT_MODEL_PROVIDER 配置
4. `tests/unit/test_model_factory_provider.py`: 新建单元测试（11 个测试用例）
5. `tests/integration/test_intent_router_model_provider.py`: 新建集成测试（12 个测试用例）

验证结果: ✅ 修复成功。2026.02.28 测试通过（23 个测试全部通过）

经验教训:
- 环境变量是配置的正确来源，不应硬编码（LAW v4.0: 环境主权）
- 向后兼容是架构升级的核心原则（ARCH v2.6: 渐进式演进）
- 模块级配置对象应在首次使用时而非加载时创建
- API Key 等敏感信息应优先从环境变量读取

---

[L3-01]

失效模式：IntentRouter LLM 分类超时导致规则匹配失效

失效场景 (Context): 用户发送"哇"等简单表情/感叹词，IntentRouter 规则匹配成功但置信度 < 0.9，继续调用 LLM 分类导致超时，最终返回 UNKNOWN，路由到 PLAN（不正确）。

致命根因 (Root Cause):
1. **L3 逻辑层缺陷**: 规则匹配置信度阈值过高（0.9），简单消息无法直接返回
2. **性能问题**: LLM 分类耗时 300ms，对于高频关键词匹配场景不必要
3. **关键词缺失**: "哇"、"哇哦"、"wow" 等常见表情未加入 CHITCHAT_KEYWORDS
4. **缺乏优化策略**: 未实施"规则优先、LLM 回退"的性能优化策略

失效表现:
- 用户发送"哇" → 规则匹配置信度 0.8 < 0.9 → LLM 调用 → 超时 → UNKNOWN → PLAN
- 响应延迟: 300ms（LLM 调用）+ 超时处理
- 影响范围: 所有不满足 0.9 阈值的简单聊天消息
- 用户体验: 简单消息响应慢、路由错误

结构性规避 (Resolution):
1. **规则匹配优先策略**: 规则匹配置信度 >= 0.8 直接返回（不调用 LLM）
2. **扩展关键词**: 添加"哇"、"哇哦"、"wow"到 CHITCHAT_KEYWORDS
3. **LLM 延迟初始化**: 实现 _ensure_llm_client() 方法，仅在需要时初始化 LLM 客户端
4. **客户端缓存**: 使用 _llm_model 缓存已初始化的客户端，避免重复创建
5. **性能监控**: 添加性能基准测试，监控响应时间改进

关键修改:
1. `apps/shasha_message/intent_router.py:47-53`: 添加 LLM 客户端缓存字段
2. `apps/shasha_message/intent_router.py:62-94`: 实现 _ensure_llm_client() 延迟初始化方法
3. `apps/shasha_message/intent_router.py:184-226`: 修改 classify() 方法（规则匹配优先 + 置信度阈值 0.8）
4. `apps/shasha_message/intent_router.py:28-29`: 扩展 CHITCHAT_KEYWORDS
5. `tests/unit/test_intent_router_llm_cache.py`: 新建单元测试（6 个测试用例）
6. `tests/integration/test_intent_router_rule_priority.py`: 新建集成测试（9 个测试用例）
7. `tests/performance/test_intent_router_performance.py`: 新建性能测试（8 个测试用例）

性能改进:
- 规则匹配响应时间: < 5ms（原来是 300ms+）
- "哇"等简单表情响应时间: < 5ms（原来是 300ms+）
- LLM 客户端初始化: 仅在首次调用时执行一次（之前每次调用都初始化）

验证结果: ✅ 修复成功。2026.02.28 测试通过（23 个测试全部通过）

经验教训:
- 性能优化应优先考虑"快速路径"（规则匹配）而非优化慢速路径（LLM）
- 延迟初始化是减少启动开销的有效模式（AI-04: 认知启动阻塞）
- 客户端缓存可显著降低重复创建开销
- 规则匹配阈值应根据实际使用场景调整（0.8 vs 0.9）

---

[IPC-07]

失效模式：sequence_id 类型假设错误

失效场景 (Context): MESSAGE 进程在创建 TaskRequest 时，错误地将 message_id 强制转换为 sequence_id，导致飞书消息处理失败。

致命根因 (Root Cause):
1. **L2 协议层缺陷**: main.py 错误地将 `sequence_id=int(platform_msg.platform_ctx.get("message_id", 0))`
2. **类型假设错误**: 假设所有平台的 message_id 都是 int 类型
3. **未考虑平台差异**: 飞书的 message_id 是字符串格式 (`'om_x100b551e4b4f6880b356f2ae17cdbd9'`)
4. **违反 IPC-01 机制**: sequence_id 应该通过 `get_next_sequence_id()` 获取，而非 message_id

失效表现:
- 飞书发送"哈哈哈" → ValueError: `int('om_x100b551e4b4f6880b356f2ae17cdbd9')` → 进程崩溃
- 影响范围: 100% 飞书平台消息
- 钉钉可能可用（如果 message_id 是纯数字）
- 未来平台高风险（任何非数字 message_id 都会失败）

结构性规避 (Resolution):
1. **正确的 sequence_id 获取**: 使用 `await get_next_sequence_id()` 获取全局自增序列号（int 类型）
2. **message_id 独立存储**: 将 message_id 保留在 platform_ctx 中（str 类型），用于幂等性拦截
3. **职责分离**: sequence_id 用于 IPC-01 指令时序倒挂防护，message_id 用于消息去重
4. **增强测试覆盖**: 添加飞书、钉钉、空 message_id 格式的测试用例

关键修改:
1. `apps/shasha_message/main.py:69-75`: 添加 `get_next_sequence_id` 导入
2. `apps/shasha_message/main.py:309`: 修改为 `sequence_id=await get_next_sequence_id()`
3. `tests/unit/test_task_request_sequence_id.py`: 新建单元测试（8 个测试用例）
4. `tests/integration/test_platform_message_id.py`: 新建集成测试（5 个测试用例）

关联修复计划: docs/PLAN_SEQUENCE_ID_TYPE_FIX.md

验证结果: ✅ 修复成功。2026.02.28 测试通过（8 个单元测试 + 5 个集成测试 = 13 个测试全部通过）

经验教训:
- 平台数据类型不可假设，必须验证（ARCH v2.6 §2: 平台无关性）
- sequence_id 和 message_id 职责不同，不能混用（IPC-01 vs 幂等性）
- 测试必须覆盖所有平台的数据格式（DIAGNOSIS §2.1: 基线验证）
- IPC-01 指令时序防护依赖 sequence_id 的 int 类型和单调递增性

---

[IPC-08]

失效模式：对象属性访问错误

失效场景 (Context): IntentRouter 在构建 LLM 提示词和进行关键词匹配时，错误地将 SkillMetadata Pydantic 模型当作字典，使用 `.get()` 方法访问属性。

致命根因 (Root Cause):
1. **L3 逻辑层缺陷**: 代码假设 SkillMetadata 是字典类型，使用 `meta.get('description', 'N/A')`
2. **类型验证缺失**: 未验证数据类型就使用特定访问方式
3. **Pydantic 特性不熟悉**: Pydantic BaseModel 使用属性访问而非字典方法

失效表现:
- IntentRouter 分类失败: `AttributeError: 'SkillMetadata' object has no attribute 'get'`
- LLM 分类不可用
- 规则匹配也不可用（关键词匹配中也使用 `.get()`）
- 影响范围: 100% 使用 SkillMetadata 的场景

结构性规避 (Resolution):
1. **正确的属性访问**: 将 `meta.get('description', 'N/A')` 改为 `meta.description`
2. **全面的代码审查**: 检查所有使用 SkillMetadata 的地方
3. **增强测试覆盖**: 添加单元测试验证正确的访问方式
4. **防御性编程**: 避免假设数据类型

关键修改:
1. `apps/shasha_message/intent_router.py:293`: 修改 LLM 提示词构建
2. `apps/shasha_message/intent_router.py:197-198`: 修改关键词匹配
3. `tests/unit/test_intent_router_fix.py`: 新建单元测试（7 个测试用例）

关联修复计划: docs/PLAN_DUAL_BUG_FIX.md

验证结果: ✅ 修复成功。2026.02.28 测试通过（7 个单元测试 + 7 个集成测试 = 14 个测试全部通过）

经验教训:
- Pydantic 模型使用属性访问而非字典方法
- 数据类型不可假设，必须验证（LAW v4.1: 防御性防御）
- 测试必须验证正确的访问方式

---

[IPC-09]

失效模式：类型契约违反

失效场景 (Context): FeishuPlatform 在创建 PlatformMessage 时，可能将 UserId 对象直接作为 user_id 存储，违反了 PlatformMessage.user_id 的类型契约（str）。

致命根因 (Root Cause):
1. **L2 协议层缺陷**: PlatformMessage.user_id 定义为 str，但实际可能存储对象
2. **缺少类型检查**: 没有运行时验证 user_id 是否为字符串
3. **Gateway 模式差异**: 不同模式（Gateway/Webhook/Stream）传递的 user_id 类型可能不同

失效表现:
- 飞书 API 调用失败: HTTP 400 错误（receive_id 必须是字符串）
- 影响范围: 所有 Gateway 模式或 Stream 模式传递 UserId 对象的场景
- 潜在风险：任何传递对象而非字符串的 user_id 都会失败

结构性规避 (Resolution):
1. **提取 open_id 字符串**: 检测 UserId 对象，提取 `user_id.open_id`
2. **类型检查**: 在 `send_message()` 中添加运行时类型检查
3. **防御性编程**: 处理多种可能的 user_id 类型（字符串、UserId 对象、其他）
4. **增强测试覆盖**: 添加各种 user_id 类型的测试用例

关键修改:
1. `apps/shasha_message/platforms/feishu_platform.py:114-126`: 添加 user_id 类型转换逻辑
2. `apps/shasha_message/platforms/feishu_platform.py:154-162`: 添加类型检查
3. `tests/unit/test_user_id_type_fix.py`: 新建单元测试（9 个测试用例）
4. `tests/integration/test_dual_bug_fix.py`: 添加集成测试（7 个测试用例）

关联修复计划: docs/PLAN_DUAL_BUG_FIX.md

验证结果: ✅ 修复成功。2026.02.28 测试通过（9 个单元测试 + 7 个集成测试 = 16 个测试全部通过）

经验教训:
- 类型契约必须严格执行（LAW v4.1: 防御性防御）
- Gateway/Webhook/Stream 模式的数据类型可能不同，需要兼容处理
- 测试必须覆盖所有可能的类型

---

[IPC-10]

失效模式：Gateway user_id 提取不完整

失效场景 (Context): Gateway._extract_sender_id() 使用 `str(sender_id)` 而非提取 `sender_id.open_id`，导致所有飞书消息回复失败，返回 HTTP 400 错误。

致命根因 (Root Cause):
1. **L2 协议层缺陷**: Gateway._extract_sender_id() 未正确处理飞书 SDK 的 UserId 对象
2. **类型假设错误**: 假设 sender_id 是普通对象，直接转换为字符串
3. **缺少防御性检查**: main.py 未验证 user_id 类型就传递给 send_message()
4. **测试覆盖不足**: 单元测试使用模拟数据，未覆盖真实 SDK 对象

失效表现:
- 飞书发送任何消息 → HTTP 400 错误: "receive_id_type is required"
- 调试信息显示 receive_id = "{'open_id': 'ou_xxx'}"（字符串而非 "ou_xxx"）
- 影响范围: 100% 飞书 Gateway 模式消息
- 其他平台可能正常（钉钉使用直接字符串）

结构性规避 (Resolution):
1. **提取 open_id 属性**: 修改 _extract_sender_id() 检测 UserId 对象，提取 `sender_id.open_id`
2. **多层防御性检查**: 在 main.py 添加第二层类型检查（提取 open_id）
3. **增强测试覆盖**: 添加模拟 SDK UserId 对象的单元测试和集成测试
4. **文档记录**: 在 COMPOUND.md 记录此失效模式

关键修改:
1. `apps/shasha_message/gateway.py:342-362`: 修改 _extract_sender_id() 提取 UserId.open_id
2. `apps/shasha_message/main.py:329-345`: 添加防御性 user_id 类型检查
3. `tests/unit/test_gateway_user_id_extraction.py`: 新建单元测试（15 个测试用例）
4. `tests/integration/test_gateway_user_id_integration.py`: 新建集成测试（10 个测试用例）

关联修复计划: docs/PLAN_GATEWAY_USER_ID_EXTRACTION_FIX.md

验证结果: ✅ 修复成功。2026.02.28 测试通过（25 个测试全部通过）

经验教训:
- 第三方 SDK 对象必须了解其内部结构，不可盲目转换为字符串
- 多层防御性检查可提高系统鲁棒性（Gateway + main.py）
- 测试必须使用真实 SDK 对象模拟，避免测试与生产环境差异
- SDK 文档应仔细阅读（飞书 UserId 有 open_id 属性）

---

[L2-06]

失效模式：飞书API content字段二次JSON编码

失效场景 (Context): FeishuPlatform.send_message() 在构建API请求payload时，错误地使用 `json.dumps()` 手动序列化content字段，导致content字段从dict对象变成转义的JSON字符串。配合aiohttp的自动序列化（`json=payload`），造成二次JSON编码。

致命根因 (Root Cause):
1. **L2 协议层缺陷**: 不理解aiohttp的 `json` 参数会自动调用 `json.dumps(payload)`
2. **API契约违反**: 飞书API期望content字段是dict对象，不是JSON字符串
3. **缺少类型验证**: 未在发送前验证payload数据结构
4. **双重序列化陷阱**: 手动序列化 + aiohttp自动序列化

失效表现:
- 飞书发送任何消息 → HTTP 400 错误: "field validation failed" + "receive_id_type is required"
- 实际发送的JSON: `content: "{\"text\": \"hi\"}"` (转义的JSON字符串)
- 飞书API期望格式: `content: {"text": "hi"}` (dict对象)
- 影响范围: 100% 飞书消息回复失败（纯文本 + 富文本卡片）
- 系统完全不可用：所有回复都返回 HTTP 400

结构性规避 (Resolution):
1. **移除手动序列化**: 直接传递dict对象作为content字段
2. **依赖aiohttp自动序列化**: 使用 `json=payload` 让aiohttp处理
3. **添加单元测试**: 验证payload数据结构（content必须是dict）
4. **API契约验证**: 测试实际发送的JSON格式
5. **反例测试**: 证明手动json.dumps()会导致二次编码

关键修改:
1. `apps/shasha_message/platforms/feishu_platform.py:225`: 移除 `json.dumps({"text": content})`，改为 `{"text": content}`
2. `apps/shasha_message/platforms/feishu_platform.py:217`: 移除 `json.dumps(post_content)`，改为 `post_content`
3. `tests/unit/test_feishu_payload_format.py`: 新建payload格式验证测试（7个测试用例）
4. `tests/unit/test_feishu_payload_edge_cases.py`: 新建边界情况测试（10个测试用例）
5. `tests/integration/test_feishu_api_e2e.py`: 新建集成测试（需要真实飞书API凭证）

关联修复计划: docs/PLAN_FEISHU_API_CONTENT_FIELD_FIX.md

验证结果: ✅ 修复成功。2026.02.28 测试通过（17个单元测试全部通过）

经验教训:
- 使用第三方HTTP库时，必须理解其参数行为（aiohttp的json参数会自动序列化）
- API契约必须严格遵守（飞书API要求content是dict）
- 双重序列化是常见陷阱，需要通过单元测试验证
- DEBUG日志对发现问题至关重要
- 测试反例（错误做法）有助于理解问题的严重性

---

[L3-02]

失效模式：SOP 库不完整导致任务执行失败

失效场景 (Context): 用户发送天气查询任务（如"了解https://wttr.in/ 如何查询天气"），PLAN 进程的 Orchestrator 无法找到对应的 SOP，导致任务失败。

致命根因 (Root Cause):
1. **L3 逻辑层缺陷**: SOP 库完整性仅 57.1% (4/7)，缺失三个关键 SOP
2. **L2 协议层缺陷**: Gateway 返回 JSON 格式 content（如 `{"text":"..."}`），导致 IntentRouter 关键词匹配失败
3. **L3 逻辑层缺陷**: 缺少 SOP 降级机制，当检索失败时无兜底策略

失效表现:
- 用户发送"了解https://wttr.in/ 如何查询天气" → 错误匹配到 SHELL_POWERSHELL（"ps" in "https"）
- 提示"未找到合适的 SOP: IntentType.SHELL_POWERSHELL"
- 任务执行失败，无法完成 curl 查询
- 影响范围: 42.9% 的 IntentType (3/7) 无法执行
- 系统功能严重受限

结构性规避 (Resolution):
1. **修复协议污染**:
   - 默认使用新解析器（FeishuProtocolParser），返回纯文本而非 JSON 字符串
   - main.py 添加防御性 JSON 格式检测并**实际提取纯文本**（修复 RC1 P0）
2. **完善 SOP 库**:
   - 添加 FILE_DELETE SOP（文件删除操作）
   - 添加 SHELL_POWERSHELL SOP（PowerShell 专用脚本执行）
   - 添加 WEB_POST SOP（HTTP POST 请求）
   - SOP 库完整性达到 100% (7/7)
3. **实现降级机制**:
   - 添加相似 IntentType 降级映射（SHELL_POWERSHELL ↔ SHELL_EXEC）
   - _retrieve_sop() 实现降级逻辑
   - 提供兜底策略，避免任务直接失败

关键修改:
1. `apps/shasha_message/gateway.py:76`: 修改默认解析器为 `true`
2. `apps/shasha_message/main.py:428-452`: 添加防御性 JSON 格式检测**并实际提取纯文本**
3. `apps/shasha_plan/orchestrator.py:185-263`: 添加三个缺失的 SOP
4. `apps/shasha_plan/orchestrator.py:314-340`: 实现降级机制
5. `tests/diagnosis/test_sop_completeness_verification.py`: 新建完整性验证测试（5 个测试用例）

关联修复计划:
- DIAGNOSIS_SOP_COMPLETE_VERIFICATION_WITH_SOLUTIONS.md
- PLAN_SOP_COMPLETION_AND_LLM_UPGRADE.md

验证结果: ✅ 修复成功。2026.03.01 测试通过
- SOP 库完整性: 4/7 → 7/7 (100%)
- 降级机制测试: 2 个测试用例通过
- 结构有效性测试: 3 个测试用例通过
- 协议污染修复: ✅ main.py 实际提取纯文本（不只是日志记录）

经验教训:
- SOP 完整性是 PLAN 层的基础（MAP v2.0 §1.1: SOP 完整性原则）
- 协议污染会导致下游组件失效（LAW 5.1: 跨进程通信契约）
- 防御性代码必须实际修复问题，不只是日志记录（LAW v4.1: 防御性防御）
- 降级机制是提高系统鲁棒性的关键（LAW v4.1: 防御性防御）
- 测试必须验证系统完整性，而非单点功能（DIAGNOSIS §2.1: 基线验证）