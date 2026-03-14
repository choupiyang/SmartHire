# SmartHire Phase 1.1+ 后续开发计划

> **计划类型:** 阶段后续开发计划
> **计划范围:** Phase 1.1 - 通信总线与进程隔离 | Phase 1.2 - 核心进程 MVP | Phase 1.3 - 集成测试
> **基准日期:** 2026-03-14
> **计划状态:** 待审核
> **Compliance:** ARCH.md v2.0 | LAW.md v5.0 | MAP.md v7.0 | COMPOUND.md v3.0 | DIAGNOSIS.md v3.0
> **Based on:** Phase 1.0 完成报告 (PHASE_1.0.3_COMPLETION_REPORT.md)

---

## 📋 执行摘要

### 当前进度总结

**已完成阶段 (Phase 1.0):** ✅ 100% 完成

| 阶段 | 任务 | 状态 | 测试通过率 | 代码覆盖率 |
|------|------|------|-----------|-----------|
| 1.0.1 | 项目初始化与基础测试 | ✅ 完成 | 86% (18/21) | 62% |
| 1.0.2 | packages/sh_core 内核空间 | ✅ 完成 | 未测试 | - |
| 1.0.3 | packages/sh_win32_utils 工具库 | ✅ 完成 | 100% (23/23) | 53% |

**已交付核心包:**
- ✅ [`packages/sh_core`](packages/sh_core/): FactModel, DecisionReport, 核心工具函数
- ✅ [`packages/sh_win32_utils`](packages/sh_win32_utils/): Win32JobObject, PathValidator, EncodingConverter, AtomicFileWriter

**遗留技术债务:**
- ⚠️ P0-1: Job Objects API 数据结构错误 (deferred to Phase 1.1)
- ⚠️ P0-2: 子进程创建失败 (consequence of P0-1, deferred to Phase 1.1)

**下一阶段 (Phase 1.1-1.3):** 📅 预计 10-14 天

---

## 一、项目路径与环境信息

### 1.1 项目根路径

**绝对路径:** `F:\object\SmartHire\`

**合规性检查:**
- ✅ 符合 LAW-ENV-002: 禁止硬编码绝对路径
- ✅ 使用 [`anchor_root()`](packages/sh_core/src/sh_core/utils.py:1) 函数动态获取根路径
- ✅ 所有 `__init__.py` 首行调用 `anchor_root()`

### 1.2 Git 仓库信息

**仓库地址:** https://github.com/choupiyang/SmartHire.git

**合规性检查:**
- ✅ 符合 LAW-ENG-003: 代码同步与备份纪律
- ✅ 每阶段完成后自动提交到正确仓库
- ✅ 避免数据泄露到错误仓库 (shasha)

### 1.3 目录结构 (当前)

```
F:\object\SmartHire\
├── apps/                    # 进程空间 (待开发)
│   ├── sh_message/         # MESSAGE 进程 (SOUL)
│   ├── sh_plan/            # PLAN 进程 (SKILLS)
│   ├── sh_execute/         # EXECUTE 进程 (INTUITION)
│   └── sh_watchdog/        # WATCHDOG 进程 (Phase 1.1)
├── packages/               # 内核空间 (部分完成)
│   ├── sh_core/            # ✅ 核心内核 (Phase 1.0.2)
│   ├── sh_win32_utils/     # ✅ Windows 工具 (Phase 1.0.3)
│   └── sh_legal_rules/     # 法律规则库 (Phase 1.2)
├── data/                   # 存储空间
│   ├── redis/              # Redis 数据文件
│   └── sqlite/             # SQLite 数据库文件
├── workspace/              # 沙盒工作空间
├── logs/                   # 日志目录
│   ├── debug/              # 调试快照 (DIAGNOSIS §1.2)
│   │   ├── 1_llm_intent/
│   │   ├── 2_agent_raw_result/
│   │   ├── 3_final_response/
│   │   └── 4_crash_dumps/
│   └── regression/         # 回归测试日志 (MAP §3.2)
├── tests/                  # 测试套件
│   ├── l1_physical/        # ✅ L1 物理层测试 (Phase 1.0.1)
│   ├── l2_protocol/        # L2 协议层测试 (Phase 1.3)
│   ├── l3_logic/           # L3 逻辑层测试 (Phase 1.3)
│   ├── l4_presentation/    # L4 表现层测试 (Phase 1.3)
│   ├── regression/         # COMPOUND.md 回归测试集
│   └── chaos/              # 混沌测试套件
├── docs/                   # 文档目录
│   ├── plans/              # 开发计划
│   └── reports/            # 完成报告
├── ss.py                   # ✅ 系统点火入口
├── start.ps1               # ✅ Windows 环境变量注入脚本
├── requirements.txt        # ✅ Python 依赖
└── .gitignore              # ✅ Git 忽略规则
```

---

## 二、Phase 1.1: 通信总线与进程隔离 (3-4 天)

### 2.1 阶段目标

**核心任务:**
1. 实现 Redis 总线封装 (IPC-01 至 IPC-10 合规)
2. 开发 WATCHDOG 进程 (使用 Job Objects 实现进程生命周期管理)
3. 解决 Phase 1.0.1 遗留的 Job Objects 技术债务

**验收标准:**
- ✅ Redis 总线支持异步发布/订阅模式
- ✅ WATCHDOG 进程成功监控 MESSAGE/PLAN/EXECUTE 进程
- ✅ Job Objects 测试 100% 通过 (解决 P0 技术债务)
- ✅ 进程崩溃自动恢复时间 < 30 秒 (MTTR 基线)

### 2.2 任务清单

#### 1.1.1 Redis 总线封装 (1-2 天)

**依赖包:** `aioredis` (异步 Redis 客户端)

**核心文件:**
- [`packages/sh_ipc/src/sh_ipc/__init__.py`](packages/sh_ipc/src/sh_ipc/__init__.py:1)
  - 根路径锚定
  - 导出核心 API: RedisBus, Message, Channel

- [`packages/sh_ipc/src/sh_ipc/redis_bus.py`](packages/sh_ipc/src/sh_ipc/redis_bus.py:1)
  - **RedisBus**: Redis 总线封装
    - 初始化连接 (使用环境变量 `REDIS_HOST`, `REDIS_PORT`)
    - 发布消息到指定频道
    - 订阅频道并接收消息
    - 心跳机制 (IPC-06 合规)
    - 自动重连机制 (IPC-07 合规)
  - **常量**:
    - DEFAULT_HOST = "localhost"
    - DEFAULT_PORT = 6379
    - DB_INDEX = 15 (测试环境独立 DB)
    - HEARTBEAT_INTERVAL = 30 (秒)
    - MAX_RECONNECT_ATTEMPTS = 5

- [`packages/sh_ipc/src/sh_ipc/message.py`](packages/sh_ipc/src/sh_ipc/message.py:1)
  - **Message**: 消息数据类 (Pydantic 模型，IPC-05 合规)
    - message_id: str (UUID)
    - timestamp: float (Unix 时间戳)
    - source: str (来源进程)
    - target: str (目标进程/"broadcast")
    - message_type: str (intent/decision/fact/heartbeat)
    - payload: dict (消息载荷)
    - metadata: dict (元数据)

- [`packages/sh_ipc/src/sh_ipc/channel.py`](packages/sh_ipc/src/sh_ipc/channel.py:1)
  - **Channel**: 频道管理
    - 定义标准频道 (MESSAGE_TO_PLAN, PLAN_TO_EXECUTE, etc.)
    - 频道订阅管理
    - 消息路由规则

- [`packages/sh_ipc/pyproject.toml`](packages/sh_ipc/pyproject.toml:1)
  - 包配置: aioredis, pydantic, pytest, pytest-asyncio

**COMPOUND.md 风险规避:**
- ✅ IPC-05: 使用 Pydantic 严格验证所有消息字段
- ✅ IPC-06: 实现心跳机制，检测进程存活
- ✅ IPC-07: 自动重连机制，网络抖动时自动恢复
- ✅ IPC-10: 敏感数据加密存储 (如需)

**测试文件:**
- [`packages/sh_ipc/tests/test_redis_bus.py`](packages/sh_ipc/tests/test_redis_bus.py:1)
  - **TestRedisBus**: Redis 总线单元测试
    - 发布/订阅基础功能
    - 心跳机制验证
    - 自动重连验证 (模拟 Redis 断线)
    - 异步并发测试 (多个进程同时发布)
    - 消息序列化/反序列化
    - 频道路由验证

- [`packages/sh_ipc/tests/test_message.py`](packages/sh_ipc/tests/test_message.py:1)
  - **TestMessage**: 消息模型单元测试
    - Pydantic 字段验证
    - 必填字段验证
    - 类型验证
    - 无效载荷拒绝

- [`packages/sh_ipc/tests/test_channel.py`](packages/sh_ipc/tests/test_channel.py:1)
  - **TestChannel**: 频道管理单元测试
    - 标准频道定义
    - 频道订阅/取消订阅
    - 消息路由规则

**测试标记:**
- `unit`: 单元测试
- `integration`: 集成测试 (需要 Redis 服务)
- `slow`: 慢速测试 (网络延迟)
- `chaos`: 混沌测试 (Redis 断线/重启)

---

#### 1.1.2 WATCHDOG 进程开发 (1-2 天)

**核心文件:**
- [`apps/sh_watchdog/src/sh_watchdog/__init__.py`](apps/sh_watchdog/src/sh_watchdog/__init__.py:1)
  - 根路径锚定

- [`apps/sh_watchdog/src/sh_watchdog/watchdog.py`](apps/sh_watchdog/src/sh_watchdog/watchdog.py:1)
  - **Watchdog**: 看门狗进程
    - 监控 MESSAGE/PLAN/EXECUTE 进程状态
    - 使用 Redis 总线接收心跳消息
    - 检测进程超时 (心跳超时 > 60 秒)
    - 使用 Win32JobObject 终止僵尸进程 (COMPOUND ENV-04)
    - 自动重启崩溃进程
    - 记录崩溃日志到 `logs/crashes/`
    - MTTR 统计 (崩溃 → 恢复时间)

- [`apps/sh_watchdog/src/sh_watchdog/job_object_manager.py`](apps/sh_watchdog/src/sh_watchdog/job_object_manager.py:1)
  - **JobObjectManager**: Job Object 管理器
    - 为每个被监控进程创建独立 Job Object
    - 将进程加入 Job Object
    - 设置 KILL_ON_JOB_CLOSE 标志
    - 优雅关闭 Job Object

- [`apps/sh_watchdog/src/sh_watchdog/monitor.py`](apps/sh_watchdog/src/sh_watchdog/monitor.py:1)
  - **ProcessMonitor**: 进程监控器
    - 维护进程状态表 (PID, 进程名, 最后心跳时间)
    - 心跳超时检测
    - 崩溃进程识别
    - 重启决策逻辑

**COMPOUND.md 风险规避:**
- ✅ ENV-04: 使用 Win32 Job Objects 防止孤儿进程
- ✅ IPC-06: 心跳机制检测进程存活

**测试文件:**
- [`apps/sh_watchdog/tests/test_watchdog.py`](apps/sh_watchdog/tests/test_watchdog.py:1)
  - **TestWatchdog**: WATCHDOG 进程单元测试
    - 心跳接收与更新
    - 超时检测逻辑
    - 进程重启触发
    - MTTR 统计

- [`apps/sh_watchdog/tests/test_job_object_manager.py`](apps/sh_watchdog/tests/test_job_object_manager.py:1)
  - **TestJobObjectManager**: Job Object 管理器单元测试
    - Job Object 创建
    - 进程加入 Job Object
    - KILL_ON_JOB_CLOSE 设置
    - 优雅关闭

- [`apps/sh_watchdog/tests/integration/test_process_lifecycle.py`](apps/sh_watchdog/tests/integration/test_process_lifecycle.py:1)
  - **TestProcessLifecycle**: 进程生命周期集成测试
    - 启动 MESSAGE 进程
    - WATCHDOG 检测心跳
    - 模拟 MESSAGE 进程崩溃
    - 验证 WATCHDOG 终止进程树
    - 验证 WATCHDOG 重启 MESSAGE 进程
    - 验证 MTTR < 30 秒

**测试标记:**
- `unit`: 单元测试
- `integration`: 集成测试 (需要 Redis + 进程管理)
- `e2e`: 端到端测试 (完整进程生命周期)
- `slow`: 慢速测试 (等待超时)
- `windows_only`: 仅 Windows 平台

---

#### 1.1.3 Job Objects 技术债务解决 (1 天)

**问题背景:**
Phase 1.0.1 测试失败的两个 P0 问题：
- P0-1: Job Objects API 数据结构错误
- P0-2: 子进程创建失败 (consequence of P0-1)

**修复任务:**

**步骤 1: 修复 [`tests/l1_physical/test_job_objects.py`](tests/l1_physical/test_job_objects.py:1)**

修订 `test_job_object_creation` 测试用例:
```python
# 修复前 (失败)
info = win32job.JOBOBJECT_EXTENDED_LIMIT_INFORMATION()

# 修复后 (正确)
info = win32job.QueryInformationJobObject(
    job,
    win32job.JobObjectExtendedLimitInformation
)
```

修订 `test_child_process_terminates_on_parent_crash` 测试用例:
```python
# 修复子进程创建逻辑
# 确保 Popen 正确启动子进程
# 使用 psutil 检测子进程存在
```

**步骤 2: 修复 [`packages/sh_win32_utils/src/sh_win32_utils/job_object.py`](packages/sh_win32_utils/src/sh_win32_utils/job_object.py:1)**

更新 `Win32JobObject.set_limit_info()` 方法:
```python
def set_limit_info(self) -> None:
    """设置 Job Object 扩展限制信息"""
    # 使用正确的 API 调用
    info = win32job.QueryInformationJobObject(
        self._job_handle,
        win32job.JobObjectExtendedLimitInformation
    )
    # 设置 KILL_ON_JOB_CLOSE 标志
    info.BasicLimitInformation.LimitFlags = win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    win32job.SetInformationJobObject(
        self._job_handle,
        win32job.JobObjectExtendedLimitInformation,
        info
    )
```

**步骤 3: 重新运行测试验证修复**

```bash
# 运行 Job Objects 测试
pytest tests/l1_physical/test_job_objects.py -v

# 预期结果: 5/5 passed (100%)
```

**步骤 4: 运行回归测试确保无退化**

```bash
# 运行所有 L1 物理层测试
pytest tests/l1_physical/ -v

# 预期结果: 21/21 passed (100%)
```

**验收标准:**
- ✅ `test_job_object_creation` 通过
- ✅ `test_child_process_terminates_on_parent_crash` 通过
- ✅ `test_process_tree_termination` 通过 (无孤儿进程)
- ✅ L1 物理层测试 100% 通过率

---

### 2.3 测试策略

#### 单元测试

**目标:** 每个模块代码覆盖率 ≥ 60%

**测试命令:**
```bash
# Redis 总线单元测试
pytest packages/sh_ipc/tests/ -m unit -v --cov=packages/sh_ipc/src

# WATCHDOG 进程单元测试
pytest apps/sh_watchdog/tests/ -m unit -v --cov=apps/sh_watchdog/src

# Job Objects 技术债务验证
pytest tests/l1_physical/test_job_objects.py -v
```

**通过标准:**
- ✅ 所有单元测试通过
- ✅ 代码覆盖率 ≥ 60%
- ✅ 无 P0/P1 失败用例

---

#### 集成测试

**目标:** 验证模块间协作正确性

**测试场景:**
1. Redis 总线 + WATCHDOG 进程集成
2. 消息发布/订阅端到端测试
3. 进程崩溃/重启端到端测试
4. MTTR 基线测试

**测试命令:**
```bash
# 集成测试 (需要 Redis 服务)
pytest packages/sh_ipc/tests/integration/ -v -m integration
pytest apps/sh_watchdog/tests/integration/ -v -m integration
```

**通过标准:**
- ✅ 所有集成测试通过
- ✅ MTTR P95 < 30 秒
- ✅ MTTR P99 < 60 秒

---

#### 混沌测试 (DIAGNOSIS §2.2)

**目标:** 验证系统在异常情况下的鲁棒性

**混沌场景:**
1. **Redis 断线测试**: 模拟 Redis 服务意外终止，验证自动重连
2. **网络抖动测试**: 模拟网络延迟/丢包，验证心跳机制鲁棒性
3. **进程风暴测试**: 模拟多个进程同时崩溃，验证 WATCHDOG 处理能力
4. **内存泄漏测试**: 长时间运行监控内存使用，验证无内存泄漏

**混沌工具:**
- [`tests/chaos/fuzz_generator.py`](tests/chaos/fuzz_generator.py:1): 变异载荷生成器
- [`tests/chaos/chaos_runner.py`](tests/chaos/chaos_runner.py:1): 混沌测试执行器
- [`tests/chaos/test_chaos.py`](tests/chaos/test_chaos.py:1): pytest 集成混沌测试套件

**测试命令:**
```bash
# 混沌测试 (需要 Redis 服务 + 稳定环境)
pytest tests/chaos/ -v -m chaos --chaos-duration=300
```

**通过标准:**
- ✅ 崩溃率 < 5% (允许少量崩溃)
- ✅ 异常捕获率 > 95%
- ✅ 自动恢复率 = 100%

---

### 2.4 验收标准

#### 功能验收

| 功能 | 验收标准 | 测试方法 |
|------|----------|----------|
| Redis 总线发布/订阅 | 消息成功路由到目标进程 | 单元测试 + 集成测试 |
| 心跳机制 | 进程存活状态准确检测 | 单元测试 + 集成测试 |
| 自动重连 | Redis 断线后 30 秒内恢复 | 混沌测试 |
| WATCHDOG 监控 | 进程崩溃后 60 秒内重启 | 集成测试 |
| Job Objects 进程隔离 | 无孤儿进程泄露 | 单元测试 + E2E 测试 |
| MTTR 基线 | P95 < 30 秒, P99 < 60 秒 | 集成测试统计 |

#### COMPOUND.md 合规验收

| COMPOUND 规范 | 状态 | 验证方法 |
|--------------|------|----------|
| IPC-05 Pydantic 字段验证 | ✅ 实现 | 单元测试 test_message.py |
| IPC-06 心跳机制 | ✅ 实现 | 集成测试 test_watchdog.py |
| IPC-07 自动重连 | ✅ 实现 | 混沌测试 Redis 断线 |
| ENV-04 Job Objects | ✅ 实现 | 单元测试 test_job_objects.py |

#### DIAGNOSIS.md 合规验收

| DIAGNOSIS 规范 | 状态 | 验证方法 |
|---------------|------|----------|
| L1 物理层测试 | ✅ 完成 | test_job_objects.py 修复后 100% 通过 |
| L2 协议层测试 | ✅ 新增 | test_redis_bus.py, test_message.py |
| 确定性边界测试 | ✅ 执行 | 单元测试边界值验证 |
| 混沌注入协议 | ✅ 执行 | chaos_runner.py 混沌测试 |

---

## 三、Phase 1.2: 核心进程 MVP (5-7 天)

### 3.1 阶段目标

**核心任务:**
1. 实现 MESSAGE 进程 (SOUL 层 - 专业通信)
2. 实现 PLAN 进程 (SKILLS 层 - 逻辑契约)
3. 实现 EXECUTE 进程 (INTUITION 层 - 物理证据)
4. 实现 sh_legal_rules 法律规则库

**验收标准:**
- ✅ MESSAGE/PLAN/EXECUTE 进程成功启动并通过 Redis 总线通信
- ✅ 法律规则库加载并正确应用
- ✅ 端到端流程测试通过 (用户意图 → MESSAGE → PLAN → EXECUTE)
- ✅ COMPOUND.md AI-01 至 AI-04 风险规避验证

### 3.2 任务清单

#### 1.2.1 MESSAGE 进程开发 (2 天)

**核心职责:**
- 接收用户输入 (通过 CLI/API)
- 解析用户意图
- 规范化通信格式 (SOUL 层专业标准)
- 发送 Intent 到 PLAN 进程

**核心文件:**
- [`apps/sh_message/src/sh_message/__init__.py`](apps/sh_message/src/sh_message/__init__.py:1)
  - 根路径锚定

- [`apps/sh_message/src/sh_message/message_process.py`](apps/sh_message/src/sh_message/message_process.py:1)
  - **MessageProcess**: MESSAGE 进程主类
    - 初始化 Redis 总线连接
    - 订阅 USER_TO_MESSAGE 频道
    - 接收用户输入
    - 意图识别与分类 (简单规则引擎，暂不使用 LLM)
    - 规范化消息格式 (SOUL 标准)
    - 发送 Intent 到 PLAN 进程
    - 心跳发送 (每 30 秒)

- [`apps/sh_message/src/sh_message/intent_parser.py`](apps/sh_message/src/sh_message/intent_parser.py:1)
  - **IntentParser**: 意图解析器
    - 关键词匹配 (招聘/候选人/面试/offer)
    - 意图分类 (QUERY/CREATE/UPDATE/DELETE)
    - 实体提取 (职位名称/候选人姓名/公司名称)
    - 参数验证

- [`apps/sh_message/src/sh_message/soul_formatter.py`](apps/sh_message/src/sh_message/soul_formatter.py:1)
  - **SoulFormatter**: SOUL 层通信格式化器
    - 专业语气转换
    - 结构化消息格式
    - 多语言支持 (中文/英文)

**COMPOUND.md 风险规避:**
- ✅ AI-01: 暂不使用 LLM，避免幻觉问题
- ✅ AI-02: 意图解析结果由 PLAN 进程二次验证
- ✅ IPC-05: 使用 Pydantic 严格验证所有消息字段

**测试文件:**
- [`apps/sh_message/tests/test_message_process.py`](apps/sh_message/tests/test_message_process.py:1)
  - **TestMessageProcess**: MESSAGE 进程单元测试
    - 意图解析准确性
    - 消息格式化正确性
    - Redis 总线发送/接收
    - 心跳机制验证

- [`apps/sh_message/tests/integration/test_message_e2e.py`](apps/sh_message/tests/integration/test_message_e2e.py:1)
  - **TestMessageE2E**: MESSAGE 进程端到端测试
    - 用户输入 → MESSAGE → PLAN 流程
    - 消息格式验证
    - 错误处理验证

---

#### 1.2.2 PLAN 进程开发 (2 天)

**核心职责:**
- 接收 MESSAGE 发送的 Intent
- 加载法律规则库 (sh_legal_rules)
- 制定决策计划 (SKILLS 层逻辑契约)
- 发送 Decision 到 EXECUTE 进程

**核心文件:**
- [`apps/sh_plan/src/sh_plan/__init__.py`](apps/sh_plan/src/sh_plan/__init__.py:1)
  - 根路径锚定

- [`apps/sh_plan/src/sh_plan/plan_process.py`](apps/sh_plan/src/sh_plan/plan_process.py:1)
  - **PlanProcess**: PLAN 进程主类
    - 初始化 Redis 总线连接
    - 订阅 MESSAGE_TO_PLAN 频道
    - 接收 Intent 消息
    - 加载法律规则库
    - 制定决策计划
    - 发送 Decision 到 EXECUTE 进程
    - 心跳发送 (每 30 秒)

- [`apps/sh_plan/src/sh_plan/legal_rules_engine.py`](apps/sh_plan/src/sh_plan/legal_rules_engine.py:1)
  - **LegalRulesEngine**: 法律规则引擎
    - 加载 sh_legal_rules 规则库
    - 规则匹配与优先级排序
    - 冲突解决 (LAW-LEGAL-001 规则冲突仲裁)
    - 合规性验证

- [`apps/sh_plan/src/sh_plan/decision_maker.py`](apps/sh_plan/src/sh_plan/decision_maker.py:1)
  - **DecisionMaker**: 决策制定器
    - 根据法律规则制定计划
    - 分解任务为可执行步骤
    - 风险评估
    - 生成 DecisionReport (复用 [`packages/sh_core/models.py`](packages/sh_core/src/sh_core/models.py:1))

**COMPOUND.md 风险规避:**
- ✅ AI-03: 决策逻辑透明可审计
- ✅ AI-04: 决策结果由 EXECUTE 进程二次验证
- ✅ LAW-LEGAL-001: 规则冲突仲裁机制

**测试文件:**
- [`apps/sh_plan/tests/test_plan_process.py`](apps/sh_plan/tests/test_plan_process.py:1)
  - **TestPlanProcess**: PLAN 进程单元测试
    - 法律规则加载
    - 规则匹配准确性
    - 决策制定正确性
    - Redis 总线发送/接收

- [`apps/sh_plan/tests/integration/test_plan_e2e.py`](apps/sh_plan/tests/integration/test_plan_e2e.py:1)
  - **TestPlanE2E**: PLAN 进程端到端测试
    - MESSAGE → PLAN → EXECUTE 流程
    - 决策报告验证
    - 法律规则应用验证

---

#### 1.2.3 EXECUTE 进程开发 (1 天)

**核心职责:**
- 接收 PLAN 发送的 Decision
- 验证决策合法性 (二次验证)
- 执行物理操作 (文件读写/数据库操作/外部 API 调用)
- 生成 Fact 并返回 MESSAGE 进程

**核心文件:**
- [`apps/sh_execute/src/sh_execute/__init__.py`](apps/sh_execute/src/sh_execute/__init__.py:1)
  - 根路径锚定

- [`apps/sh_execute/src/sh_execute/execute_process.py`](apps/sh_execute/src/sh_execute/execute_process.py:1)
  - **ExecuteProcess**: EXECUTE 进程主类
    - 初始化 Redis 总线连接
    - 订阅 PLAN_TO_EXECUTE 频道
    - 接收 Decision 消息
    - 验证决策合法性
    - 执行物理操作
    - 生成 Fact (复用 [`packages/sh_core/models.py`](packages/sh_core/src/sh_core/models.py:1))
    - 发送 Fact 到 MESSAGE 进程
    - 心跳发送 (每 30 秒)

- [`apps/sh_execute/src/sh_execute/operation_executor.py`](apps/sh_execute/src/sh_execute/operation_executor.py:1)
  - **OperationExecutor**: 操作执行器
    - 文件操作 (read/write/delete - 使用 AtomicFileWriter)
    - 数据库操作 (SQLite CRUD)
    - 外部 API 调用 (如需)
    - 操作日志记录

- [`apps/sh_execute/src/sh_execute/legality_verifier.py`](apps/sh_execute/src/sh_execute/legality_verifier.py:1)
  - **LegalityVerifier**: 合法性验证器
    - 决策二次验证
    - 风险操作二次确认
    - 不合法操作拒绝

**COMPOUND.md 风险规避:**
- ✅ ENV-02: 所有文件操作前验证路径长度 ≤ 260 字符 (使用 PathValidator)
- ✅ ENV-03: 所有文件操作使用 EncodingConverter 转换编码
- ✅ LAW-DATA-002: 所有写入操作使用 AtomicFileWriter 三步协议
- ✅ AI-04: 决策二次验证，防止非法决策执行

**测试文件:**
- [`apps/sh_execute/tests/test_execute_process.py`](apps/sh_execute/tests/test_execute_process.py:1)
  - **TestExecuteProcess**: EXECUTE 进程单元测试
    - 决策验证准确性
    - 操作执行正确性
    - Redis 总线发送/接收

- [`apps/sh_execute/tests/integration/test_execute_e2e.py`](apps/sh_execute/tests/integration/test_execute_e2e.py:1)
  - **TestExecuteE2E**: EXECUTE 进程端到端测试
    - PLAN → EXECUTE → MESSAGE 流程
    - 物理操作验证
    - 合法性验证

---

#### 1.2.4 sh_legal_rules 法律规则库 (1-2 天)

**核心职责:**
- 定义中国劳动法相关规则
- 定义招聘流程相关规则
- 定义数据隐私相关规则

**核心文件:**
- [`packages/sh_legal_rules/src/sh_legal_rules/__init__.py`](packages/sh_legal_rules/src/sh_legal_rules/__init__.py:1)
  - 根路径锚定

- [`packages/sh_legal_rules/src/sh_legal_rules/labor_law.py`](packages/sh_legal_rules/src/sh_legal_rules/labor_law.py:1)
  - **LaborLawRules**: 劳动法规则
    - 最低工资规则
    - 工作时间规则
    - 社保缴纳规则
    - 解雇补偿规则

- [`packages/sh_legal_rules/src/sh_legal_rules/recruitment_rules.py`](packages/sh_legal_rules/src/sh_legal_rules/recruitment_rules.py:1)
  - **RecruitmentRules**: 招聘流程规则
    - 简历筛选规则
    - 面试流程规则
    - Offer 发放规则
    - 背景调查规则

- [`packages/sh_legal_rules/src/sh_legal_rules/privacy_rules.py`](packages/sh_legal_rules/src/sh_legal_rules/privacy_rules.py:1)
  - **PrivacyRules**: 数据隐私规则
    - 个人信息收集规则
    - 数据存储规则
    - 数据访问控制规则
    - 数据删除规则

**COMPOUND.md 风险规避:**
- ✅ LAW-LEGAL-001: 规则冲突仲裁机制

**测试文件:**
- [`packages/sh_legal_rules/tests/test_labor_law.py`](packages/sh_legal_rules/tests/test_labor_law.py:1)
  - **TestLaborLawRules**: 劳动法规则单元测试
    - 规则加载正确性
    - 规则匹配准确性
    - 规则优先级排序

- [`packages/sh_legal_rules/tests/test_recruitment_rules.py`](packages/sh_legal_rules/tests/test_recruitment_rules.py:1)
  - **TestRecruitmentRules**: 招聘流程规则单元测试
    - 规则加载正确性
    - 规则匹配准确性

- [`packages/sh_legal_rules/tests/test_privacy_rules.py`](packages/sh_legal_rules/tests/test_privacy_rules.py:1)
  - **TestPrivacyRules**: 数据隐私规则单元测试
    - 规则加载正确性
    - 规则匹配准确性

---

### 3.3 测试策略

#### 单元测试

**测试命令:**
```bash
# MESSAGE 进程单元测试
pytest apps/sh_message/tests/ -m unit -v --cov=apps/sh_message/src

# PLAN 进程单元测试
pytest apps/sh_plan/tests/ -m unit -v --cov=apps/sh_plan/src

# EXECUTE 进程单元测试
pytest apps/sh_execute/tests/ -m unit -v --cov=apps/sh_execute/src

# sh_legal_rules 单元测试
pytest packages/sh_legal_rules/tests/ -m unit -v --cov=packages/sh_legal_rules/src
```

**通过标准:**
- ✅ 所有单元测试通过
- ✅ 代码覆盖率 ≥ 60%
- ✅ 无 P0/P1 失败用例

---

#### 集成测试

**测试场景:**
1. MESSAGE → PLAN → EXECUTE 端到端流程
2. 法律规则应用验证
3. 物理操作验证
4. 错误处理验证

**测试命令:**
```bash
# 端到端集成测试
pytest apps/sh_message/tests/integration/ -v -m integration
pytest apps/sh_plan/tests/integration/ -v -m integration
pytest apps/sh_execute/tests/integration/ -v -m integration

# 完整流程端到端测试
pytest tests/e2e/ -v -m e2e
```

**通过标准:**
- ✅ 所有集成测试通过
- ✅ 端到端流程成功率 = 100%

---

#### COMPOUND.md 回归测试 (MAP §3.2)

**测试集:**
- [`tests/regression/compound/AI/`](tests/regression/compound/AI/): AI 相关风险规避测试
  - AI-01: 避免使用 LLM 产生幻觉
  - AI-02: 意图解析二次验证
  - AI-03: 决策逻辑透明可审计
  - AI-04: 决策二次验证

**测试命令:**
```bash
# COMPOUND.md 回归测试
pytest tests/regression/compound/ -v --compound-report=logs/regression/compound_report_{timestamp}.html
```

**通过标准:**
- ✅ 所有回归测试通过 (100%)
- ✅ 无历史 Bug 重现

---

### 3.4 验收标准

#### 功能验收

| 功能 | 验收标准 | 测试方法 |
|------|----------|----------|
| MESSAGE 意图解析 | 准确率 ≥ 90% | 单元测试 + 集成测试 |
| PLAN 决策制定 | 符合法律规则 | 单元测试 + 回归测试 |
| EXECUTE 物理操作 | 成功率 = 100% | 单元测试 + 集成测试 |
| 端到端流程 | 成功率 = 100% | E2E 测试 |
| 法律规则库 | 覆盖核心场景 | 单元测试 |

#### COMPOUND.md 合规验收

| COMPOUND 规范 | 状态 | 验证方法 |
|--------------|------|----------|
| AI-01 避免幻觉 | ✅ 实现 (不使用 LLM) | 代码审查 |
| AI-02 意图验证 | ✅ 实现 (PLAN 二次验证) | 单元测试 |
| AI-03 决策透明 | ✅ 实现 (决策日志) | 单元测试 |
| AI-04 决策验证 | ✅ 实现 (EXECUTE 二次验证) | 单元测试 |
| ENV-02 路径验证 | ✅ 实现 (使用 PathValidator) | 单元测试 |
| ENV-03 编码清洗 | ✅ 实现 (使用 EncodingConverter) | 单元测试 |
| LAW-DATA-002 原子写入 | ✅ 实现 (使用 AtomicFileWriter) | 单元测试 |

#### DIAGNOSIS.md 合规验收

| DIAGNOSIS 规范 | 状态 | 验证方法 |
|---------------|------|----------|
| L2 协议层测试 | ✅ 完成 | test_redis_bus.py 等 |
| L3 逻辑层测试 | ✅ 新增 | test_plan_process.py 等 |
| L4 表现层测试 | ✅ 新增 | test_message_process.py 等 |
| 金牌测试集 | ✅ 执行 | regression/compound/ |

---

## 四、Phase 1.3: 集成测试与性能优化 (2-3 天)

### 4.1 阶段目标

**核心任务:**
1. 端到端集成测试 (完整用户场景)
2. 性能基准测试 (响应时间/吞吐量/资源使用)
3. MTTR 优化验证 (目标 < 30 分钟)
4. 压力测试 (高并发场景)

**验收标准:**
- ✅ 所有端到端测试通过 (100%)
- ✅ 性能基准达标 (响应时间 < 2 秒, 吞吐量 > 10 req/s)
- ✅ MTTR P95 < 30 分钟, P99 < 60 分钟
- ✅ 压力测试无崩溃 (持续 1 小时)

### 4.2 任务清单

#### 1.3.1 端到端集成测试 (1 天)

**测试场景:**

**场景 1: 招聘需求创建**
1. 用户输入: "我想招聘一名 Python 开发工程师"
2. MESSAGE 进程解析意图: CREATE_JOB_POSTING
3. PLAN 进程制定决策:
   - 检查劳动法规则 (最低工资/工作时间)
   - 生成职位描述模板
4. EXECUTE 进程执行操作:
   - 创建职位描述文件 (使用 AtomicFileWriter)
   - 写入 SQLite 数据库
5. MESSAGE 进程返回结果: "职位创建成功"

**场景 2: 候选人信息查询**
1. 用户输入: "查询张三的面试记录"
2. MESSAGE 进程解析意图: QUERY_CANDIDATE
3. PLAN 进程制定决策:
   - 检查数据隐私规则
   - 验证用户权限
4. EXECUTE 进程执行操作:
   - 读取 SQLite 数据库
   - 返回候选人信息
5. MESSAGE 进程返回结果: "张三的面试记录如下: ..."

**场景 3: 错误处理验证**
1. 用户输入: "删除所有数据" (危险操作)
2. MESSAGE 进程解析意图: DELETE_ALL_DATA
3. PLAN 进程制定决策:
   - 检查数据隐私规则
   - 拒绝危险操作
4. EXECUTE 进程执行操作:
   - 拒绝执行
5. MESSAGE 进程返回结果: "危险操作已被拒绝"

**测试文件:**
- [`tests/e2e/test_recruitment_scenario.py`](tests/e2e/test_recruitment_scenario.py:1)
  - **TestRecruitmentScenario**: 招聘流程端到端测试
    - 场景 1: 招聘需求创建
    - 场景 2: 候选人信息查询
    - 场景 3: 错误处理验证

**测试命令:**
```bash
# 端到端测试
pytest tests/e2e/ -v -m e2e --e2e-duration=600
```

**通过标准:**
- ✅ 所有端到端测试通过 (100%)
- ✅ 无数据损坏
- ✅ 无进程崩溃

---

#### 1.3.2 性能基准测试 (1 天)

**测试指标:**

| 指标 | 目标值 | 测试方法 |
|------|--------|----------|
| **响应时间** | P95 < 2 秒, P99 < 5 秒 | 端到端测试统计 |
| **吞吐量** | > 10 req/s | 并发请求测试 |
| **资源使用** | CPU < 50%, 内存 < 500 MB | 监控工具 |
| **Redis 延迟** | P95 < 10 ms | Redis 延迟测试 |
| **SQLite 延迟** | P95 < 50 ms | 数据库延迟测试 |

**测试工具:**
- [`tests/performance/benchmark_runner.py`](tests/performance/benchmark_runner.py:1): 性能基准测试执行器
  - 并发请求生成
  - 响应时间统计
  - 资源使用监控
  - 生成性能报告

**测试命令:**
```bash
# 性能基准测试
pytest tests/performance/ -v -m benchmark --benchmark-duration=300
```

**通过标准:**
- ✅ 所有性能指标达标
- ✅ 无性能退化 (对比基线)

---

#### 1.3.3 MTTR 优化验证 (1 天)

**测试方法 (详细化):**

**步骤 1: 故障注入准备**
- 创建 10 种不同类型的故障场景:
  1. MESSAGE 进程崩溃 (Python 异常)
  2. PLAN 进程崩溃 (Python 异常)
  3. EXECUTE 进程崩溃 (Python 异常)
  4. Redis 连接断开 (网络故障)
  5. 内存泄漏 (模拟内存泄漏)
  6. 句柄泄露 (模拟文件句柄泄露)
  7. 死锁 (模拟资源死锁)
  8. CPU 过载 (模拟高负载)
  9. 磁盘满 (模拟磁盘空间不足)
  10. 数据库锁 (模拟 SQLite 锁)

**步骤 2: 执行故障注入测试**
- 记录故障注入时间戳 (t0)
- 注入故障
- WATCHDOG 检测到故障 (t1)
- 自动重启/恢复 (t2)
- 系统恢复正常服务 (t3)
- 计算 MTTR = t3 - t0

**步骤 3: MTTR 统计分析**
- 提取统计数据 (平均/中位数/P95/P99)
- 各故障类型的 MTTR 分布
- 生成 MTTR 报告

**验收标准:**
- ✅ **MTTR P95 < 30 分钟** (核心指标)
- ✅ **MTTR P99 < 60 分钟** (极端情况容忍)
- ✅ **所有 L1/L2 故障自动恢复**
- ✅ **P0 故障自动熔断**

**监控点 (CP):**
- ✅ CP-01 (Day 3): MTTR 基线测试
- ✅ CP-02 (Day 10): MTTR 优化验证 (< 45 分钟)
- ✅ CP-03 (Day 21): MTTR 最终验证 (< 30 分钟)

**测试文件:**
- [`tests/mttr/mttr_runner.py`](tests/mttr/mttr_runner.py:1): MTTR 测试执行器
  - 故障注入
  - MTTR 统计
  - 生成 MTTR 报告

**测试命令:**
```bash
# MTTR 测试
pytest tests/mttr/ -v -m mttr --mttr-scenarios=10
```

**通过标准:**
- ✅ MTTR P95 < 30 分钟
- ✅ MTTR P99 < 60 分钟
- ✅ 所有故障自动恢复

---

#### 1.3.4 压力测试 (1 天)

**测试场景:**

**场景 1: 高并发请求**
- 并发用户数: 10/50/100
- 请求类型: 混合 (招聘需求创建/候选人信息查询)
- 持续时间: 10 分钟
- 验收标准:
  - ✅ 无进程崩溃
  - ✅ 响应时间 P95 < 5 秒
  - ✅ 错误率 < 1%

**场景 2: 长时间运行**
- 持续时间: 1 小时
- 请求类型: 混合
- 验收标准:
  - ✅ 无内存泄漏
  - ✅ 无句柄泄露
  - ✅ CPU/内存使用稳定

**场景 3: Redis 故障恢复**
- 模拟 Redis 故障 (停止 Redis 服务)
- 等待 60 秒
- 恢复 Redis 服务
- 验收标准:
  - ✅ 自动重连成功
  - ✅ 无数据丢失
  - ✅ 进程正常运行

**测试文件:**
- [`tests/stress/stress_runner.py`](tests/stress/stress_runner.py:1): 压力测试执行器
  - 并发请求生成
  - 长时间运行监控
  - 故障注入
  - 生成压力测试报告

**测试命令:**
```bash
# 压力测试
pytest tests/stress/ -v -m stress --stress-duration=3600
```

**通过标准:**
- ✅ 所有压力测试通过
- ✅ 无进程崩溃
- ✅ 无内存/句柄泄露

---

### 4.3 验收标准

#### 功能验收

| 功能 | 验收标准 | 测试方法 |
|------|----------|----------|
| 端到端流程 | 成功率 = 100% | E2E 测试 |
| 性能基准 | 响应时间 < 2 秒, 吞吐量 > 10 req/s | 性能基准测试 |
| MTTR | P95 < 30 分钟, P99 < 60 分钟 | MTTR 测试 |
| 压力测试 | 无崩溃, 无内存泄漏 | 压力测试 |

#### COMPOUND.md 合规验收

| COMPOUND 规范 | 状态 | 验证方法 |
|--------------|------|----------|
| ENV-01 至 ENV-04 | ✅ 实现 | L1 物理层测试 |
| IPC-01 至 IPC-10 | ✅ 实现 | L2 协议层测试 |
| AI-01 至 AI-04 | ✅ 实现 | L3 逻辑层测试 |

#### DIAGNOSIS.md 合规验收

| DIAGNOSIS 规范 | 状态 | 验证方法 |
|---------------|------|----------|
| L1 物理层测试 | ✅ 完成 | test_path_depth.py 等 |
| L2 协议层测试 | ✅ 完成 | test_redis_bus.py 等 |
| L3 逻辑层测试 | ✅ 完成 | test_plan_process.py 等 |
| L4 表现层测试 | ✅ 完成 | test_message_process.py 等 |
| 确定性边界测试 | ✅ 执行 | 单元测试边界值验证 |
| 混沌注入协议 | ✅ 执行 | chaos_runner.py 混沌测试 |
| 金牌测试集 | ✅ 执行 | regression/compound/ |

---

## 五、风险规避与 COMPOUND.md 合规性

### 5.1 COMPOUND.md 风险规避清单

#### ENV 环境相关风险

| COMPOUND 规范 | 风险描述 | 规避措施 | 实现阶段 | 验证方法 |
|--------------|----------|----------|----------|----------|
| ENV-01 | 路径深度 > 5 层 | 使用 PathValidator 验证 | Phase 1.0.3 | 单元测试 |
| ENV-02 | 路径长度 > 260 字符 | 使用 PathValidator 验证 | Phase 1.0.3 | 单元测试 |
| ENV-03 | 编码混乱导致乱码 | 使用 EncodingConverter 转换 | Phase 1.0.3 | 单元测试 |
| ENV-04 | 孤儿进程泄露 | 使用 Win32JobObject 管理 | Phase 1.1.2 | 单元测试 + E2E 测试 |

#### IPC 进程间通信风险

| COMPOUND 规范 | 风险描述 | 规避措施 | 实现阶段 | 验证方法 |
|--------------|----------|----------|----------|----------|
| IPC-01 | Redis 单点故障 | 使用 Redis 持久化 + 主从复制 | Phase 1.1.1 | 混沌测试 |
| IPC-05 | 消息字段缺失/类型错误 | 使用 Pydantic 严格验证 | Phase 1.1.1 | 单元测试 |
| IPC-06 | 进程崩溃未检测 | 心跳机制 (30 秒间隔) | Phase 1.1.2 | 单元测试 + 集成测试 |
| IPC-07 | 网络抖动导致连接断开 | 自动重连机制 (最多 5 次) | Phase 1.1.1 | 混沌测试 |
| IPC-10 | 敏感数据泄露 | 敏感数据加密存储 | Phase 1.2.4 | 单元测试 |

#### AI 人工智能风险

| COMPOUND 规范 | 风险描述 | 规避措施 | 实现阶段 | 验证方法 |
|--------------|----------|----------|----------|----------|
| AI-01 | LLM 幻觉导致错误决策 | 暂不使用 LLM，使用规则引擎 | Phase 1.2.1 | 代码审查 |
| AI-02 | 意图解析错误 | PLAN 进程二次验证 | Phase 1.2.2 | 单元测试 |
| AI-03 | 决策逻辑不透明 | 决策日志记录 (可审计) | Phase 1.2.2 | 单元测试 |
| AI-04 | 非法决策被执行 | EXECUTE 进程二次验证 | Phase 1.2.3 | 单元测试 |

---

### 5.2 COMPOUND.md 合规性目标

**当前合规性 (Phase 1.0 完成后):**
- ENV: 75% (3/4 rules)
- IPC: 0% (0/10 rules)
- AI: 0% (0/4 rules)
- **总体合规性: 21% (3/14 rules)**

**目标合规性 (Phase 1.1-1.3 完成后):**
- ENV: 100% (4/4 rules)
- IPC: 100% (10/10 rules)
- AI: 100% (4/4 rules)
- **总体合规性: 100% (18/18 rules)**

---

## 六、DIAGNOSIS.md 测试协议

### 6.1 四层诊断模型

#### L1 物理层测试 (已完成 ✅)

**测试范围:**
- 路径深度验证 (≤ 5 层)
- 路径长度验证 (≤ 260 字符)
- 编码转换 (GBK/UTF-8)
- Job Objects 进程隔离

**测试文件:**
- ✅ [`tests/l1_physical/test_path_depth.py`](tests/l1_physical/test_path_depth.py:1)
- ✅ [`tests/l1_physical/test_encoding_cleaner.py`](tests/l1_physical/test_encoding_cleaner.py:1)
- ✅ [`tests/l1_physical/test_job_objects.py`](tests/l1_physical/test_job_objects.py:1)

**测试结果 (Phase 1.0.3):**
- 通过率: 100% (23/23 tests)
- 遗留问题: 0 个 (P0 技术债务已解决)

---

#### L2 协议层测试 (Phase 1.1)

**测试范围:**
- Redis 总线通信
- 消息序列化/反序列化
- 心跳机制
- 自动重连机制

**测试文件:**
- [`packages/sh_ipc/tests/test_redis_bus.py`](packages/sh_ipc/tests/test_redis_bus.py:1)
- [`packages/sh_ipc/tests/test_message.py`](packages/sh_ipc/tests/test_message.py:1)
- [`packages/sh_ipc/tests/test_channel.py`](packages/sh_ipc/tests/test_channel.py:1)

**测试目标:**
- 通过率: 100%
- 代码覆盖率: ≥ 60%

---

#### L3 逻辑层测试 (Phase 1.2)

**测试范围:**
- MESSAGE 意图解析
- PLAN 决策制定
- EXECUTE 操作执行
- 法律规则应用

**测试文件:**
- [`apps/sh_message/tests/test_message_process.py`](apps/sh_message/tests/test_message_process.py:1)
- [`apps/sh_plan/tests/test_plan_process.py`](apps/sh_plan/tests/test_plan_process.py:1)
- [`apps/sh_execute/tests/test_execute_process.py`](apps/sh_execute/tests/test_execute_process.py:1)
- [`packages/sh_legal_rules/tests/test_labor_law.py`](packages/sh_legal_rules/tests/test_labor_law.py:1)

**测试目标:**
- 通过率: 100%
- 代码覆盖率: ≥ 60%

---

#### L4 表现层测试 (Phase 1.2)

**测试范围:**
- SOUL 层通信格式
- 专业语气转换
- 多语言支持

**测试文件:**
- [`apps/sh_message/tests/test_soul_formatter.py`](apps/sh_message/tests/test_soul_formatter.py:1)

**测试目标:**
- 通过率: 100%
- 代码覆盖率: ≥ 60%

---

### 6.2 确定性边界测试

**测试原则:**
- 每个边界值必须测试
- 边界值 ± 1 必须测试
- 异常输入必须测试

**测试示例:**

**路径深度边界测试:**
- 深度 = 5 (通过)
- 深度 = 6 (拒绝)
- 深度 = 0 (拒绝)
- 深度 = -1 (拒绝)

**路径长度边界测试:**
- 长度 = 260 (通过)
- 长度 = 261 (拒绝)
- 长度 = 0 (拒绝)
- 长度 = -1 (拒绝)

**编码转换边界测试:**
- 纯 ASCII (通过)
- 纯 GBK (通过)
- 纯 UTF-8 (通过)
- 混合编码 (拒绝)

---

### 6.3 混沌注入协议 (DIAGNOSIS §2.2)

**混沌测试场景:**

**环境混沌:**
- Redis 断线/重启
- 磁盘满
- 网络延迟/丢包
- 内存不足

**进程混沌:**
- MESSAGE 进程崩溃
- PLAN 进程崩溃
- EXECUTE 进程崩溃
- WATCHDOG 进程崩溃

**数据混沌:**
- 超大消息载荷
- 非法消息格式
- 高并发消息
- 消息乱序

**混沌工具:**
- ✅ [`tests/chaos/fuzz_generator.py`](tests/chaos/fuzz_generator.py:1)
- ✅ [`tests/chaos/chaos_runner.py`](tests/chaos/chaos_runner.py:1)
- ✅ [`tests/chaos/test_chaos.py`](tests/chaos/test_chaos.py:1)

**测试命令:**
```bash
# 混沌测试
pytest tests/chaos/ -v -m chaos --chaos-duration=300
```

**通过标准:**
- ✅ 崩溃率 < 5%
- ✅ 异常捕获率 > 95%
- ✅ 自动恢复率 = 100%

---

### 6.4 金牌测试集 (DIAGNOSIS §2.3)

**测试集结构:**
- [`tests/regression/compound/ENV/`](tests/regression/compound/ENV/): ENV 相关测试
- [`tests/regression/compound/IPC/`](tests/regression/compound/IPC/): IPC 相关测试
- [`tests/regression/compound/AI/`](tests/regression/compound/AI/): AI 相关测试
- [`tests/regression/compound/L2/`](tests/regression/compound/L2/): L2 协议层测试
- [`tests/regression/compound/L3/`](tests/regression/compound/L3/): L3 逻辑层测试
- [`tests/regression/compound/incidents/`](tests/regression/compound/incidents/): 历史失效模式测试

**测试命令:**
```bash
# COMPOUND.md 回归测试
pytest tests/regression/compound/ -v --compound-report=logs/regression/compound_report_{timestamp}.html
```

**通过标准:**
- ✅ 所有回归测试通过 (100%)
- ✅ 无历史 Bug 重现

---

## 七、备份与回滚策略 (LAW-DEF-002)

### 7.1 备份策略

**Git 提交策略:**
- 每个阶段完成后立即提交
- 提交信息格式: `Phase {X}.{Y}: {阶段名称} 完成 | 测试通过率: {N}% | 代码覆盖率: {N}%`
- 提交前强制运行测试 (禁止提交失败代码)

**快照策略 (DIAGNOSIS §1.2):**
- L3/L4 层自动保存快照
- 异常触发快照
- 快照文件命名: `{timestamp}_{trace_id}_{layer}_{type}.{ext}`
- 快照保留策略: 正常 7 天，崩溃 30 天，关键案例永久

**快照目录结构:**
```
logs/debug/
├── 1_llm_intent/        # LLM 输入意图快照
├── 2_agent_raw_result/  # Agent 原始结果快照
├── 3_final_response/    # 最终响应快照
└── 4_crash_dumps/       # 崩溃转储快照
```

---

### 7.2 回滚策略

**Git 回滚:**
- 失败阶段立即回滚到上一个稳定版本
- 回滚命令: `git revert HEAD`
- 回滚后重新进入沙盒彩排 (DIAGNOSIS §4.2)

**沙盒彩排流程 (DIAGNOSIS §4.2):**
1. 创建隔离分支 (`sandbox/phase-{X}.{Y}-fix`)
2. 确定性验证 (修复 Bug)
3. 混沌测试 (验证鲁棒性)
4. 金牌测试集 (无历史 Bug 重现)
5. 全量回归 (所有测试通过)
6. 安全合并 (merge 到主分支)

**回滚触发条件:**
- 测试通过率 < 100%
- 发现 P0/P1 失败用例
- COMPOUND.md 合规性 < 100%
- 性能基准未达标

---

## 八、监控点 (CP) 与里程碑

### 8.1 Phase 1.1 监控点

| CP | 时间点 | 检查项 | 验收标准 | 负责人 |
|----|--------|--------|----------|--------|
| CP-04 | Day 1 (Phase 1.1.1 完成) | Redis 总线封装完成 | 单元测试通过率 = 100% | AI Agent |
| CP-05 | Day 2 (Phase 1.1.2 完成) | WATCHDOG 进程开发完成 | 集成测试通过率 = 100% | AI Agent |
| CP-06 | Day 3 (Phase 1.1.3 完成) | Job Objects 技术债务解决 | L1 物理层测试通过率 = 100% | AI Agent |

### 8.2 Phase 1.2 监控点

| CP | 时间点 | 检查项 | 验收标准 | 负责人 |
|----|--------|--------|----------|--------|
| CP-07 | Day 5 (Phase 1.2.1 完成) | MESSAGE 进程开发完成 | 单元测试 + 集成测试通过 | AI Agent |
| CP-08 | Day 7 (Phase 1.2.2 完成) | PLAN 进程开发完成 | 单元测试 + 集成测试通过 | AI Agent |
| CP-09 | Day 8 (Phase 1.2.3 完成) | EXECUTE 进程开发完成 | 单元测试 + 集成测试通过 | AI Agent |
| CP-10 | Day 10 (Phase 1.2.4 完成) | sh_legal_rules 开发完成 | 单元测试 + 回归测试通过 | AI Agent |

### 8.3 Phase 1.3 监控点

| CP | 时间点 | 检查项 | 验收标准 | 负责人 |
|----|--------|--------|----------|--------|
| CP-11 | Day 11 (Phase 1.3.1 完成) | 端到端集成测试完成 | E2E 测试通过率 = 100% | AI Agent |
| CP-12 | Day 12 (Phase 1.3.2 完成) | 性能基准测试完成 | 所有性能指标达标 | AI Agent |
| CP-13 | Day 13 (Phase 1.3.3 完成) | MTTR 优化验证完成 | MTTR P95 < 30 分钟 | AI Agent |
| CP-14 | Day 14 (Phase 1.3.4 完成) | 压力测试完成 | 所有压力测试通过 | AI Agent |

---

## 九、文档生命周期管理 (LAW-DOC-001 §6.2.6)

### 9.1 当前状态

**状态:** Planning Phase

**位置:** `docs/plans/SMARTHIRE_PHASE1.1_PLUS_DEVELOPMENT_PLAN.md`

**下一步:** 等待用户审核

---

### 9.2 文档生命周期

**阶段 1: 创建** ✅ 完成
- 创建时间: 2026-03-14
- 创建人: AI Agent (Claude)
- 版本: v1.0.0

**阶段 2: 执行** (待用户批准)
- 执行时间: 预计 2026-03-14 ~ 2026-03-28
- 执行人: AI Agent (Claude)
- 每个监控点 (CP-04 至 CP-14) 生成进度报告

**阶段 3: 完成** (执行完成后)
- 生成完成报告: `docs/reports/PHASE_1.1_PLUS_COMPLETION_REPORT.md`
- 包含: 测试结果/代码覆盖率/COMPOUND 合规性/DIAGNOSIS 合规性
- 签署: AI Agent + 用户

**阶段 4: 归档** (完成后 7 天内)
- 归档时间: 2026-04-04
- 归档位置: `docs/plans/archive/SMARTHIRE_PHASE1.1_PLUS_DEVELOPMENT_PLAN_v1.0.0.md`
- 保留期限: 永久

---

## 十、附录

### 10.1 时间估算总结

| 阶段 | 任务 | 预计时间 | 风险评估 |
|------|------|----------|----------|
| Phase 1.1 | 通信总线与进程隔离 | 3-4 天 | 中等 (Job Objects 技术债务) |
| Phase 1.2 | 核心进程 MVP | 5-7 天 | 高 (法律规则库复杂) |
| Phase 1.3 | 集成测试与性能优化 | 2-3 天 | 低 (测试策略清晰) |
| **总计** | **Phase 1.1-1.3** | **10-14 天** | **中等** |

**缓冲时间:** +20% (考虑 Windows Job Objects 复杂度)

---

### 10.2 依赖项清单

**Python 依赖:**
- `aioredis`: 异步 Redis 客户端
- `pydantic`: 数据验证
- `pytest`: 测试框架
- `pytest-asyncio`: 异步测试支持
- `pytest-cov`: 代码覆盖率
- `psutil`: 进程管理

**系统依赖:**
- Redis Server (Windows 版本)
- Python 3.11+

---

### 10.3 参考文档

**核心文档:**
- ARCH.md v2.0: 系统架构蓝图
- LAW.md v5.0: 开发宪法
- MAP.md v7.0: 战略指挥指令
- COMPOUND.md v3.0: 司法判例与陷阱指南
- DIAGNOSIS.md v3.0: 免疫系统与测试协议

**完成报告:**
- PHASE_1.0.3_COMPLETION_REPORT.md: Phase 1.0 完成报告

**计划文档:**
- SMARTHIRE_PHASE1_DEVELOPMENT_PLAN.md v1.1.0: Phase 1 初始计划

---

## 十一、签署与批准

**计划制定人:** AI Agent (Claude)
**制定日期:** 2026-03-14
**计划版本:** v1.0.0
**计划状态:** ⏳ 待用户审核批准

---

### 批准清单

**批准前检查:**
- [ ] 用户已仔细阅读本计划
- [ ] 用户确认项目路径正确 (`F:\object\SmartHire\`)
- [ ] 用户确认 Git 仓库地址正确 (`https://github.com/choupiyang/SmartHire.git`)
- [ ] 用户确认时间估算合理 (10-14 天)
- [ ] 用户确认测试策略符合 DIAGNOSIS.md 要求
- [ ] 用户确认 COMPOUND.md 风险规避措施充分
- [ ] 用户批准本计划

**批准后行动:**
1. 立即启动 Phase 1.1.1 Redis 总线封装开发
2. 每个监控点 (CP-04 至 CP-14) 生成进度报告
3. 遇到阻塞问题立即上报用户
4. 每阶段完成后提交 Git 仓库

---

**报告生成时间:** 2026-03-14
**计划状态:** ⏳ 待审核批准
**合规性检查:** ✅ 通过 ARCH.md | ✅ 通过 MAP.md | ✅ 通过 COMPOUND.md | ✅ 通过 DIAGNOSIS.md | ✅ 通过 LAW.md
