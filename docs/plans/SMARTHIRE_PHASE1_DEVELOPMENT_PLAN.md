# SmartHire Phase 1 开发计划 - 回路验证与基础架构

> **Version:** 1.1.0 (修订版)
> **Status:** ⚠️ 条件性批准（需二次审核）
> **Date:** 2026-03-14
> **Author:** AI Agent (Claude)
> **Compliance:** ARCH v2.0 | LAW v5.0 | MAP v7.0 | DIAGNOSIS v3.0
> **审核报告:** docs/reports/SMARTHIRE_PHASE1_DEVELOPMENT_PLAN_AUDIT_REPORT.md

---

## 📋 执行摘要

### 任务目标
按照 ARCH.md 的物理拓扑设计，搭建智雇家系统的**Phase 1 基础设施**，建立"报错 → 捕获 → 反思 → 修正"的自愈循环，验证三层架构（MESSAGE/PLAN/EXECUTE）的物理隔离可行性。

### 状态
⚠️ **等待审核通过** - 审核通过前不做任何开发任务

### 核心指标 (MAP v2.0 Phase 1)
- **MTTR (平均修复时长):** < 30分钟
- **进程存活率:** > 99%
- **通信成功率:** > 95%
- **测试覆盖率:** > 80%

---

## 🏗️ 架构对齐分析

### ARCH.md §0 物理拓扑映射

```
F:\object\SmartHire\
├── ss.py                           # 系统点火入口
├── start.ps1                       # Windows 环境变量注入
│
├── /apps                           # 【进程空间】
│   ├── /sh_message                 # [进程 A] SOUL：职业管家渲染
│   │   ├── soul_renderer.py        # 职业话术渲染
│   │   ├── matrix_distributor.py   # 海报+风险书+面试提纲
│   │   └── ui_radar_adapter.py     # 五维雷达图适配器
│   │
│   ├── /sh_plan                    # [进程 B] SKILLS：契约认知层
│   │   ├── contract_orchestrator.py# 任务编排
│   │   ├── rubric_engine.py        # 1-5 分标准化量规
│   │   └── compliance_checker.py   # 避嫌算法控制
│   │
│   ├── /sh_execute                 # [进程 C] INTUITION：物理存证层
│   │   ├── multimodal_parser.py    # 语音/截图/简历解析
│   │   ├── evidence_vault.py       # 证据锚点管理器
│   │   └── conflict_detector.py    # 逻辑冲突点扫描
│   │
│   └── /sh_watchdog                # [进程 D] 免疫层：故障自愈与合规监控
│
├── /packages                       # 【内核空间】
│   ├── /sh_core                    # 统一模型：FactModel, DecisionReport
│   ├── /sh_legal_rules             # 行业法律法规库与屏蔽词库
│   └── /sh_win32_utils             # Windows 路径锚定与编码流清洗
│
├── /data                           # 【存储主权】
│   ├── /evidence/                  # trace_evidence.db (证据链)
│   └── /profiles/                  # employer_pref.db (雇主偏好)
│
└── /workspace                      # 物理写操作沙箱
```

### MAP v7.0 三维熵减法映射

| 维度 | 组件 | 设计原则 | 验证指标 |
|------|------|----------|----------|
| **逻辑决策** | PLAN 进程 | 逻辑声明化、SOP 知识库 | SOP 召回准确率 > 90% |
| **物理执行** | EXECUTE 进程 | 逻辑真空、幂等性 | IO 操作成功率 > 99% |
| **表现感知** | MESSAGE 进程 | 事信分离、职业管家 | 输出合规率 100% |

---

## 🎯 Phase 1 任务拆解 (MAP §1 三维熵减法)

### 阶段 1.0: 基础设施搭建 (6-8 天) ⚠️ 修订

> **修订说明 (P1-1):** 原估算 4-7 天过于乐观。考虑 Windows Job Objects 复杂度、编码清洗边界测试、COMPOUND.md 案例显示类似模块耗时 > 4h/Case，调整为 6-8 天，预留 20% 缓冲时间。

#### 1.0.1 项目初始化 [ENV-001/ENV-002 合规]

**目标:** 建立 Python Monorepo 物理拓扑

**任务清单:**
- [ ] 创建 `ss.py` 系统点火入口
- [ ] 创建 `start.ps1` Windows 环境变量脚本
- [ ] 创建 `/apps` 和 `/packages` 目录结构
- [ ] 创建 `/data/evidence` 和 `/data/profiles` 存储目录
- [ ] 创建 `/workspace` 沙箱目录
- [ ] 初始化 Git 仓库 (LAW-ENG-003)
- [ ] **⚠️ P0-2 修订:** 确认 Git 仓库地址为 `https://github.com/choupiyang/SmartHire.git`
- [ ] 创建 `.gitignore` 排除敏感信息

**COMPOUND.md 风险规避:**
- ✅ ENV-01: 根路径锚定，目录嵌套 ≤ 5 层
- ✅ ENV-02: SQLite 写锁隔离，核心写权限收拢
- ✅ ENV-03: GBK/UTF-8 编码双向清洗
- ✅ ENV-04: Win32 Job Objects 绑定子进程生命周期

**测试策略 (DIAGNOSIS §2):** ⚠️ P1-4 具体化修订
- [ ] **L1 物理层: 路径深度测试**
  - 创建 6 层目录，验证 >260 字符路径被拒绝
  - 创建 5 层目录，验证 <260 字符路径被接受
  - 验证路径深度检测在所有文件操作中生效
- [ ] **L1 物理层: 编码清洗测试**
  - 创建 GBK 编码文件名（如：`测试_中文.txt`）
  - 通过 subprocess 读取文件
  - 验证输出为 UTF-8 编码，无乱码
  - 测试混合编码场景（GBK 文件名 + UTF-8 内容）
- [ ] **L1 物理层: Job Objects 测试**
  - 启动子进程（通过 Win32 Job Object）
  - 强制杀死父进程（模拟崩溃）
  - 验证子进程自动终止（无孤儿进程）
  - 验证进程树完整性

**备份策略 (LAW-DEF-002):**
- [ ] 初始化前快照: 记录空目录状态
- [ ] 配置文件备份: `.env.example` 版本控制

---

#### 1.0.2 packages/sh_core 内核空间开发 (2-3 天)

**目标:** 建立统一数据模型和 Windows 工具库

**任务清单:**
- [ ] 创建 `FactModel` 统一事实模型
- [ ] 创建 `DecisionReport` 决策报告模型
- [ ] 实现 `anchor_root()` 根路径锚定函数
- [ ] 实现 `safe_write()` 原子写入协议 (Temp → Flush → Rename)
- [ ] 实现 `encoding_cleaner()` 编码流清洗
- [ ] 实现 `get_next_sequence_id()` 全局自增序列号 (IPC-01)
- [ ] **⚠️ P0-1 修订:** 强制所有 `__init__.py` 首行调用 `anchor_root()`
- [ ] **⚠️ P0-1 修订:** 所有文件操作前验证路径合规性（深度 ≤ 5 层，长度 ≤ 260 字符）

**COMPOUND.md 风险规避:**
- ✅ IPC-06: Pydantic 模型字段名验证测试
- ✅ IPC-04: L4→L2 边界验证，防御性类型提取

**测试策略 (DIAGNOSIS §2.1):**
- [ ] 基线验证: FactModel/DecisionReport 实例化测试
- [ ] 混沌注入: Pydantic 字段类型漂移测试
- [ ] 边界测试: 超长路径、特殊编码文件名测试

**备份策略:**
- [ ] 模型变更前自动 Git commit
- [ ] 测试数据快照保存到 `logs/debug/`

---

#### 1.0.3 packages/sh_win32_utils Windows 工具库 (1-2 天)

**目标:** 封装 Windows 特有的物理操作

**任务清单:**
- [ ] 实现 `Win32JobObject` 进程生命周期管理
- [ ] 实现 `PathValidator` MAX_PATH 检查
- [ ] 实现 `EncodingConverter` GBK/UTF-8 双向转换
- [ ] 实现 `AtomicFileWriter` 三步写入协议

**COMPOUND.md 风险规避:**
- ✅ ENV-01: 路径深度溢出检测和警告
- ✅ ENV-02: NTFS 写锁冲突指数退避重试
- ✅ ENV-03: subprocess 编码强制 UTF-8

**测试策略:** ⚠️ P1-4 具体化修订
- [ ] **L1 物理层: MAX_PATH 边界测试**
  - 测试 260 字符路径（Windows 限制，应拒绝）
  - 测试 259 字符路径（应接受）
  - 测试 32000 字符路径（启用长路径支持后应接受）
- [ ] **L1 物理层: 并发文件写入冲突测试**
  - 3 个进程同时写入同一 SQLite 文件
  - 验证指数退避重试机制生效
  - 验证写权限收拢至单进程
  - 验证无数据损坏
- [ ] **L1 物理层: subprocess 编码污染测试**
  - 创建 GBK 编码输出脚本
  - 通过 subprocess 调用并捕获输出
  - 验证自动转换为 UTF-8（encoding='utf-8'）
  - 验证无 "僵尸字符" 输出

---

### 阶段 1.1: 通信总线与进程隔离 (3-4 天)

#### 1.1.1 Redis 总线封装 (IPC-01 合规)

**目标:** 建立跨进程通信总线，支持指令时序防护

**任务清单:**
- [ ] 创建 `RedisBus` 通信总线封装
- [ ] 实现 `publish_task()` 携带全局自增 sequence_id
- [ ] 实现 `subscribe_task()` 支持过期指令丢弃
- [ ] 实现 `publish_heartbeat()` 心跳机制
- [ ] 实现 Redis 连接池和自动重连

**COMPOUND.md 风险规避:**
- ✅ IPC-01: 指令时序倒挂防护 (sequence_id 单调递增)
- ✅ IPC-02: 消息积压崩溃 (背压机制)
- ✅ IPC-06: Pydantic 模型序列化验证

**测试策略:**
- [ ] L2 协议层: sequence_id 单调性测试
- [ ] L2 协议层: 指令时序倒挂模拟测试
- [ ] L2 协议层: 背压机制测试 (队列长度阈值)
- [ ] 混沌测试: Redis 连接断开重连测试

**备份策略:**
- [ ] Redis 数据快照 (RDB) 定期备份
- [ ] 通信日志保存到 `logs/redis_bus.log`

---

#### 1.1.2 WATCHDOG 进程开发 (DIAGNOSIS §4 自愈机制)

**目标:** 实现进程监控、故障检测和自动重启

**任务清单:**
- [ ] 创建 `apps/sh_watchdog/main.py`
- [ ] 实现进程启动和心跳监控
- [ ] 实现 10 秒缓冲期启动保护 (COMPOUND [2026.02.25-003])
- [ ] 实现进程异常捕获和重启
- [ ] 实现 Redis 总线健康检查
- [ ] 实现崩溃报告生成 (Traceback 写入)

**COMPOUND.md 风险规避:**
- ✅ [2026.02.25-003]: 启动竞态条件，10 秒缓冲期保护
- ✅ AI-04: 认知启动阻塞，异步初始化
- ✅ ENV-04: 孤儿进程泄露，Job Objects 绑定

**测试策略 (DIAGNOSIS §4.1):**
- [ ] L1 物理层: 进程崩溃检测测试
- [ ] L1 物理层: 心跳丢失重启测试
- [ ] L1 物理层: Redis 总线故障测试
- [ ] L3 逻辑层: P0 级别熔断测试 (违反 LAW 核心禁令)

**备份策略:**
- [ ] 崩溃日志保存到 `logs/crash/`
- [ ] 进程状态快照保存到 `data/watchdog_state.db`

---

### 阶段 1.2: 核心进程 MVP (5-7 天)

#### 1.2.1 MESSAGE 进程 (SOUL 层)

**目标:** 实现职业管家渲染和事信分离

**任务清单:**
- [ ] 创建 `apps/sh_message/main.py`
- [ ] 实现 `SoulRenderer` 职业话术渲染
- [ ] 实现 `MatrixDistributor` 三位一体输出
- [ ] 实现 `UiRadarAdapter` 五维雷达图适配
- [ ] 实现防御性表达 (ARCH §2.1)
- [ ] 实现 Redis 总线订阅 (TASK_DONE 事件)

**COMPOUND.md 风险规避:**
- ✅ AI-03: 高熵截断幻觉，Base64 参数降噪
- ✅ AI-02: 硬约束偏移，System 角色强注入
- ✅ L4 表现层: 语气崩塌、信息过载防护

**测试策略 (DIAGNOSIS §2.3):**
- [ ] L4 表现层: 职业表达合规性测试
- [ ] L4 表现层: 事信分离验证测试
- [ ] 混沌测试: LLM 输出格式异常测试
- [ ] 智能阅卷: 职业素养评分测试

**备份策略:**
- [ ] SOUL.md 版本控制 (`.versions/` 目录)
- [ ] 输出快照保存到 `logs/message/`

---

#### 1.2.2 PLAN 进程 (SKILLS 层)

**目标:** 实现契约认知和标准化量规打分

**任务清单:**
- [ ] 创建 `apps/sh_plan/main.py`
- [ ] 实现 `ContractOrchestrator` 任务编排
- [ ] 实现 `RubricEngine` 1-5 分量规引擎
- [ ] 实现 `ComplianceChecker` 避嫌算法
- [ ] 实现 JD 变换逻辑 (ARCH §3.1)
- [ ] 实现 Redis 总线订阅 (USER_INTENT 事件)

**COMPOUND.md 风险规避:**
- ✅ AI-01: 反思逻辑坍塌，阈值熔断机制
- ✅ L3 逻辑层: 幻觉、SOP 执行偏离防护
- ✅ LAW-TENANT-001: 用户管理真空化 (无 RBAC)

**测试策略:**
- [ ] L3 逻辑层: SOP 召回准确率测试
- [ ] L3 逻辑层: 反思回路有效性测试
- [ ] L3 逻辑层: 避嫌算法合规性测试
- [ ] 混沌测试: LLM 幻觉注入测试

**备份策略:**
- [ ] SOP 知识库版本控制
- [ ] 决策报告保存到 `logs/plan/`

---

#### 1.2.3 EXECUTE 进程 (INTUITION 层)

**目标:** 实现物理存证和直觉解析

**任务清单:**
- [ ] 创建 `apps/sh_execute/main.py`
- [ ] 实现 `MultimodalParser` 多模态解析
- [ ] 实现 `EvidenceVault` 证据锚点管理
- [ ] 实现 `ConflictDetector` 逻辑冲突扫描
- [ ] 实现幂等性保证 (MAP §1.2)
- [ ] 实现原子写入协议 (LAW-DATA-002)

**COMPOUND.md 风险规避:**
- ✅ ENV-02: NTFS 写锁冲突，指数退避重试
- ✅ LAW-DATA-002: 三步写入协议 (Temp → Flush → Rename)
- ✅ L1 物理层: 句柄泄露、文件锁死防护

**测试策略:**
- [ ] L1 物理层: 原子写入完整性测试
- [ ] L1 物理层: 证据锚点映射验证测试
- [ ] L1 物理层: 幂等性测试 (重复执行防护)
- [ ] 混沌测试: 磁盘满、网络断开故障注入

**备份策略:**
- [ ] 证据链数据库定期备份
- [ ] 写操作前置快照保存到 `workspace/`

---

### 阶段 1.3: 集成测试与效能验证 (2-3 天)

#### 1.3.1 端到端集成测试

**目标:** 验证三层架构闭环和自愈回路

**任务清单:**
- [ ] MESSAGE → PLAN → EXECUTE → MESSAGE 闭环测试
- [ ] 进程间通信完整性测试
- [ ] WATCHDOG 故障自愈测试
- [ ] 性能基准测试 (响应时间、吞吐量)

**测试策略 (DIAGNOSIS §2):**
- [ ] 确定性边界测试: 基线 Payload 100% 成功消费
- [ ] 混沌注入测试: 100 次变异，崩溃率 = 0%
- [ ] 智能阅卷: L3/L4 输出逻辑审计
- [ ] 金牌测试集: 历史案例回归测试

### MAP §3.2 免疫机制与排异反应测试 ⚠️ P1-2 新增

> **修订说明 (P1-2):** 补充 MAP §3.2 的逻辑合并和排异反应测试机制。

**免疫机制执行:**
- [ ] **每个阶段完成后运行历史案例集**（金牌测试集）
- [ ] **若核心认知准确度下降 > 5%，判定为排异**
- [ ] **记录排异测试结果到 logs/regression/**

**排异反应测试流程:**

**步骤 1: 建立基线**
```bash
# 在阶段 1.0 完成后，记录基线性能
pytest tests/regression/ --baseline-output=logs/baseline/before_phase_1.1.json

# 基线指标:
# - SOP 召回准确率
# - LLM 幻觉率
# - 通信成功率
# - 进程存活率
```

**步骤 2: 合并新逻辑**
```bash
# 完成阶段 1.1 后，运行回归测试
pytest tests/regression/ --compare-baseline=logs/baseline/before_phase_1.1.json

# 输出报告:
# - 各指标变化百分比
# - 新引入的失败用例
# - 排异判定（是否 > 5% 下降）
```

**步骤 3: 排异处理**
```bash
# 如果判定为排异:
if [accuracy_drop > 0.05 ]; then
    echo "检测到排异反应！"
    # 选项 1: 拆分为更小单元分步实施
    # 选项 2: 回滚到上一阶段
    # 选项 3: 修复新逻辑后重新测试
fi
```

**排异测试集 (金牌测试集):**
```bash
tests/regression/gold_dataset/
├── ENV_01_max_path_test.py           # ENV-01: 路径深度溢出
├── ENV_02_sqlite_lock_test.py        # ENV-02: SQLite 写锁冲突
├── ENV_03_encoding_test.py           # ENV-03: 编码清洗
├── IPC_01_sequence_order_test.py     # IPC-01: 指令时序倒挂
├── IPC_06_pydantic_fields_test.py    # IPC-06: Pydantic 字段验证
├── AI_01_reflection_collapse_test.py # AI-01: 反思逻辑坍塌
├── AI_03_high_entropy_test.py        # AI-03: 高熵截断幻觉
└── 20260225_003_watchdog_race_test.py # [2026.02.25-003]: 启动竞态
```

**排异记录:**
- [ ] 所有排反事件记录到 `logs/regression/rejection_{timestamp}.log`
- [ ] 排反分析报告包含：下降指标、影响范围、修复建议
- [ ] 严重排反事件升级到 COMPOUND.md（新增失效模式）

---

## 🧪 测试与质量保证 (DIAGNOSIS.md 合规)

### 测试金字塔

```
        /\
       /  \      E2E Tests (10%)
      /____\     └─ 端到端集成测试
     /      \
    /        \   Integration Tests (30%)
   /__________\  └─ 进程间通信、总线测试
  /            \
 /              \ Unit Tests (60%)
/________________\ └─ 单元功能测试
```

### DIAGNOSIS §2.1 基线验证协议

**确定性边界测试:**
- [ ] 提取崩溃时的 `1_llm_intent.json` 作为载荷
- [ ] 直接注射给底层 Agent，要求 100% 成功消费
- [ ] 严禁在对话框用自然语言碰运气排查

### DIAGNOSIS §1.2 快照隔离实现 ⚠️ P0-3 新增

> **修订说明 (P0-3):** 补充 DIAGNOSIS §1.2 悬停协议与案发现场快照的具体实现机制。

**快照目录结构:**
```
logs/debug/
├── 1_llm_intent/           # LLM 输入快照
├── 2_agent_raw_result/     # Agent 输出快照
├── 3_final_response/       # 最终响应快照
└── 4_crash_dumps/          # 崩溃现场快照
```

**自动快照机制:**
- [ ] **L3 逻辑层快照:** 所有 LLM 调用前自动保存输入到 `1_llm_intent/{timestamp}_{trace_id}.json`
- [ ] **L3 逻辑层快照:** Agent 输出结果自动保存到 `2_agent_raw_result/{timestamp}_{trace_id}.json`
- [ ] **L4 表现层快照:** 最终响应自动保存到 `3_final_response/{timestamp}_{trace_id}.txt`
- [ ] **异常触发快照:** 所有异常发生时自动生成完整现场快照到 `4_crash_dumps/`

**快照文件命名规范:**
```
{timestamp}_{trace_id}_{layer}_{type}.{ext}
```

示例:
- `20260314_153022_abc123_L3_llm_intent.json`
- `20260314_153025_abc123_L4_final_response.txt`

**快照内容要求:**
- [ ] **1_llm_intent.json:** 包含完整的 LLM 输入（system prompt, user message, context）
- [ ] **2_agent_raw_result.json:** 包含 Agent 的原始输出（未经过滤的完整响应）
- [ ] **3_final_response.txt:** 包含经过 MESSAGE 层渲染后的最终用户可见输出
- [ ] **4_crash_dumps/*.json:** 包含异常时的完整堆栈、系统状态、环境变量（脱敏）

**快照保留策略:**
- [ ] 正常快照保留 7 天
- [ ] 崩溃快照保留 30 天
- [ ] 关键案例快照永久保留（手动标记）

**快照查询工具:**
- [ ] 实现 `debug_query.py` 脚本，支持按 trace_id、时间范围查询快照
- [ ] 实现 `debug_replay.py` 脚本，支持从快照复现问题

### DIAGNOSIS §2.2 混沌注入协议

**变异规则:**
- [ ] Whitespace Noise: 随机插入空格、换行
- [ ] Key Shuffling: 打乱 JSON Key 顺序
- [ ] Missing Fields: 随机剔除非必选字段
- [ ] Type Drift: 强制类型漂移 (`1` → `"1"`)

**验收标准:**
- 崩溃率 = 0%
- 异常捕获率 = 100%

### 混沌测试自动化工具 ⚠️ P1-5 新增

> **修订说明 (P1-5):** 补充自动化混沌测试工具的实现。

**工具 1: Fuzz Generator (tests/chaos/fuzz_generator.py)**

```python
# 用途: 自动生成变异的测试载荷
# 功能:
# - 从基线 Payload 读取 JSON 模板
# - 应用 4 种变异规则（Whitespace, Key Shuffling, Missing Fields, Type Drift）
# - 生成指定数量的变异载荷
# - 输出到 tests/fixtures/chaos_mutations/

# 使用方法:
python tests/chaos/fuzz_generator.py \
    --baseline=tests/fixtures/baseline_intent.json \
    --iterations=100 \
    --output=tests/fixtures/chaos_mutations/

# 验收标准:
# - 生成 100 个变异载荷
# - 所有载荷符合 JSON 格式
# - 变异覆盖率 > 90%（至少应用 4 种规则中的 1 种）
```

**工具 2: Chaos Runner (tests/chaos/chaos_runner.py)**

```python
# 用途: 自动化执行混沌测试并生成报告
# 功能:
# - 批量执行变异载荷测试
# - 记录每个载荷的测试结果（成功/失败/异常）
# - 计算崩溃率、异常捕获率
# - 生成 HTML 测试报告

# 使用方法:
pytest tests/chaos/chaos_runner.py \
    --chaos-iterations=100 \
    --chaos-report=logs/chaos_report.html \
    --chaos-verbose

# 验收标准:
# - 崩溃率 = 0%
# - 异常捕获率 = 100%
# - 生成详细报告（包含每个失败载荷的堆栈）
```

**工具 3: Chaos Test Suite (tests/chaos/test_chaos.py)**

```python
# 用途: pytest 集成的混沌测试套件
# 功能:
# - 与 pytest 框架集成
# - 支持参数化测试（每个变异载荷独立测试）
# - 失败时自动生成快照

# 使用方法:
pytest tests/chaos/test_chaos.py \
    --chaos-dataset=tests/fixtures/chaos_mutations/ \
    --chaos-parallel=4

# 验收标准:
# - 所有测试用例通过
# - 测试时间 < 5 分钟（100 次变异）
```

### DIAGNOSIS §4.1 风险定级

| 风险等级 | 定义 | 权限 | 示例 |
|---------|------|------|------|
| **P0 毁灭级** | 违反 LAW 核心禁令 | 人工熔断 | 容器化、绝对路径硬编码 |
| **P1 严重级** | 反思回路失效 | 人工介入 | 系统遇错无法自愈 |
| **P2 一般级** | 工具解析失败 | AI 自动修复 | L4 表现层风格偏离 |

### COMPOUND.md 回归测试集 ⚠️ P1-3 新增

> **修订说明 (P1-3):** 补充 COMPOUND.md 中记录的历史失效模式的回归测试，确保已知 Bug 不会重现。

**回归测试集结构:**
```bash
tests/regression/compound/
├── ENV/
│   ├── ENV_01_max_path_overflow_test.py
│   ├── ENV_02_ntfs_write_lock_test.py
│   ├── ENV_03_gbk_zombie_output_test.py
│   └── ENV_04_orphan_process_leak_test.py
├── IPC/
│   ├── IPC_01_sequence_order_test.py
│   ├── IPC_02_message_backlog_test.py
│   ├── IPC_04_boundary_violation_test.py
│   ├── IPC_05_event_loop_pollution_test.py
│   ├── IPC_06_pydantic_field_mismatch_test.py
│   ├── IPC_07_sequence_id_type_test.py
│   ├── IPC_08_object_attr_error_test.py
│   ├── IPC_09_type_contract_violation_test.py
│   ├── IPC_10_gateway_user_id_test.py
│   └── L2_06_feishu_api_encoding_test.py
├── AI/
│   ├── AI_01_reflection_collapse_test.py
│   ├── AI_02_constraint_drift_test.py
│   ├── AI_03_high_entropy_truncation_test.py
│   └── AI_04_startup_block_test.py
├── L2/
│   ├── L2_03_im_protocol_incomplete_test.py
│   ├── L2_04_protocol_parser_contract_test.py
│   ├── L2_05_model_factory_config_test.py
│   └── L2_06_feishu_content_encoding_test.py
├── L3/
│   ├── L3_01_intent_router_timeout_test.py
│   └── L3_02_sop_incomplete_test.py
└── incidents/
    ├── 20260225_003_watchdog_startup_race_test.py
    ├── 20260225_001_defender_sqlite_lock_test.py
    └── 20260225_002_sys_path_inconsistent_test.py
```

**测试用例示例 (IPC-06):**
```python
# tests/regression/compound/IPC/IPC_06_pydantic_field_mismatch_test.py
import pytest
from pydantic import ValidationError

def test_pydantic_field_mismatch():
    """
    测试目的: 验证 Pydantic 模型字段名不匹配会被检测到
    COMPOUND 引用: IPC-06
    """
    from packages.sh_core.models import PlatformContext

    # 错误的字段名（历史 Bug）
    with pytest.raises(ValidationError):
        ctx = PlatformContext(
            msg_id='test',  # 错误: 应该是 message_id
        )

    # 正确的字段名
    ctx = PlatformContext(
        message_id='test',  # 正确
    )
    assert ctx.message_id == 'test'
```

**回归测试执行:**
```bash
# 运行所有 COMPOUND.md 回归测试
pytest tests/regression/compound/ --compound-report=logs/compound_regression.html

# 验收标准:
# - 所有测试用例通过（100% 通过率）
# - 无历史 Bug 重现
# - 测试覆盖率 = 100%（所有 COMPOUND 记录的失效模式）

# 失败处理:
if [ failures_count > 0 ]; then
    echo "检测到历史 Bug 重现！"
    echo "失败用例:" ${failed_tests}
    echo "必须修复后才能继续开发"
    exit 1
fi
```

**持续集成:**
- [ ] 每次 Git commit 前自动运行回归测试
- [ ] 失败时禁止 push 到远程仓库
- [ ] 生成回归测试趋势图（确保无退化）

### DIAGNOSIS §4.2 沙盒彩排与回归测试铁律 ⚠️ P0-4 新增

> **修订说明 (P0-4):** 补充 DIAGNOSIS §4.2 沙盒彩排的具体流程。

**沙盒彩排流程 (适用于任何代码变更):**

**步骤 1: 创建隔离分支**
```bash
# 创建 shadow 分支
git checkout -b feature/fix-{bug_id}-shadow

# 验证分支创建成功
git branch
```

**步骤 2: 运行确定性验证**
```bash
# 使用基线 Payload 进行确定性测试
pytest tests/deterministic/ --baseline-payload=tests/fixtures/baseline_intent.json

# 验收标准: 100% 成功消费，无失败
```

**步骤 3: 运行混沌注入测试**
```bash
# 自动化混沌测试工具
pytest tests/chaos/ --chaos-iterations=100 --chaos-report=logs/chaos_report.json

# 验收标准:
# - 崩溃率 = 0%
# - 异常捕获率 = 100%
```

**步骤 4: 运行金牌测试集**
```bash
# 历史案例回归测试
pytest tests/regression/ --gold-dataset

# 验收标准: 所有历史案例通过，无排异反应
```

**步骤 5: 全量回归测试 (不退化原则)**
```bash
# 运行完整测试套件
pytest tests/ --cov=apps --cov=packages --cov-report=html

# 验收标准:
# - 测试覆盖率 > 80%
# - 无历史通过的测试用例失败
```

**步骤 6: 安全合并**
```bash
# 仅当所有测试通过时才合并
if [ $? -eq 0 ]; then
    git checkout main
    git merge feature/fix-{bug_id}-shadow
    git push origin main
else
    echo "测试未通过，禁止合并！"
    exit 1
fi
```

**沙盒环境隔离:**
- [ ] 使用独立的 Redis 数据库（DB 15 用于沙盒测试）
- [ ] 使用独立的测试数据库（`:memory:` SQLite 或临时文件）
- [ ] 使用独立的日志目录（`logs/test_sandbox/`）
- [ ] 严禁沙盒代码访问生产数据

**回滚机制:**
- [ ] 任何步骤失败立即停止，不进入下一步骤
- [ ] 失败时生成详细的失败报告（DIAGNOSIS §4.1 定损）
- [ ] 提交修复计划，重新进入沙盒流程
- [ ] 禁止强制合并或跳过测试步骤

---

## 💾 备份与回滚策略 (LAW-DEF-002)

### 备份协议

**代码备份 (LAW-ENG-003):**
- [ ] 每次 Feature 完成后自动 Git commit
- [ ] 每次 Bug 修复后自动 Git commit
- [ ] **⚠️ P0-2 修订:** 推送到远程仓库 `https://github.com/choupiyang/SmartHire.git`

**数据备份:**
- [ ] SQLite 数据库定期备份到 `backups/db/`
- [ ] Redis RDB 快照定期备份到 `backups/redis/`
- [ ] 配置文件版本控制 (`.env.example`)

**回滚协议:**
- [ ] 只读提审: AI 读取 `.versions/` 进行 Diff 分析
- [ ] 严禁 AI 自动执行抹除记忆或回滚
- [ ] 所有状态回滚必须由人类确权

---

## 📊 验收标准 (MAP v2.0 Phase 1)

### 核心指标

| 指标 | 目标值 | 测试方法 |
|------|--------|----------|
| **MTTR** | < 30 分钟 | ⚠️ P1-6 详细化（见下方） |
| **进程存活率** | > 99% | WATCHDOG 监控日志 |
| **通信成功率** | > 95% | Redis 总线统计 |
| **测试覆盖率** | > 80% | pytest coverage 报告 |
| **SOP 召回准确率** | > 90% | PLAN 进程测试 |

### MTTR 测试方法 ⚠️ P1-6 详细化

> **修订说明 (P1-6):** 详细化 MTTR 测试方法，从简单描述改为可执行的具体步骤。

**测试方法:**

**步骤 1: 故障注入准备**
```bash
# 创建 10 种不同类型的故障场景
tests/mttr/fault_scenarios/
├── L1_process_crash.py        # L1: 进程异常退出
├── L1_disk_full.py            # L1: 磁盘空间不足
├── L2_redis_timeout.py        # L2: Redis 超时
├── L2_network_partition.py    # L2: 网络分区
├── L3_llm_timeout.py          # L3: LLM 超时
├── L3_sop_conflict.py         # L3: SOP 冲突
├── L4_render_crash.py         # L4: 渲染层崩溃
├── MEMORY_leak.py             # 内存泄漏
├── HANDLE_leak.py             # 句柄泄漏
└── DEADLOCK_loop.py           # 死循环
```

**步骤 2: 执行故障注入测试**
```bash
# 对每个故障场景执行测试
pytest tests/mttr/ --mttr-scenarios=all --mttr-report=logs/mttr_report.json

# 测试流程:
# 1. 记录故障注入时间戳 (t0)
# 2. 注入故障
# 3. WATCHDOG 检测到故障 (t1)
# 4. 自动重启/恢复 (t2)
# 5. 系统恢复正常服务 (t3)
# 6. 计算 MTTR = t3 - t0
```

**步骤 3: MTTR 统计分析**
```bash
# 从 mttr_report.json 提取统计数据
python scripts/analyze_mttr.py logs/mttr_report.json

# 输出指标:
# - MTTR 平均值
# - MTTR 中位数
# - MTTR P95 (95 分位数)
# - MTTR P99 (99 分位数)
# - 各故障类型的 MTTR 分布
```

**验收标准:**
- [ ] **MTTR P95 < 30 分钟**（核心指标）
- [ ] **MTTR P99 < 60 分钟**（极端情况容忍）
- [ ] **所有 L1/L2 故障自动恢复**（无需人工介入）
- [ ] **P0 故障自动熔断**（人工介入但系统安全停机）

**监控点 (CP):**
- [ ] CP-01 (Day 3): MTTR 基线测试（初始值）
- [ ] CP-02 (Day 10): MTTR 优化验证（目标 < 45 分钟）
- [ ] CP-03 (Day 21): MTTR 最终验证（目标 < 30 分钟）

### LAW.md 核心禁令验证

- [ ] ✅ LAW-ENV-001: 无 Docker/容器化技术
- [ ] ✅ LAW-ENV-002: 无绝对路径硬编码
- [ ] ✅ LAW-TENANT-001: 无 RBAC/多租户
- [ ] ✅ LAW-ENG-001: 职责物理隔离 (4 进程)
- [ ] ✅ LAW-DEF-001: 重试、超时、状态自检
- [ ] ✅ LAW-DEF-002: 无空的 except 语句

### COMPOUND.md 规避验证

- [ ] ✅ ENV-01: 路径深度 ≤ 5 层
- [ ] ✅ ENV-02: SQLite 写锁冲突指数退避
- [ ] ✅ ENV-03: 编码清洗全覆盖
- [ ] ✅ IPC-01: sequence_id 指令时序防护
- [ ] ✅ IPC-06: Pydantic 模型验证测试

---

## 🚨 风险与缓解措施

### 已识别风险

| 风险 | 等级 | 缓解措施 | 备选方案 |
|------|------|----------|----------|
| Windows MAX_PATH 限制 | P0 | 根路径锚定，深度 ≤ 5 层 | 启用长路径支持 (Windows 10+) |
| Redis 单点故障 | P1 | 心跳监控，自动重启 | 本地队列降级 |
| LLM 幻觉导致 SOP 偏离 | P1 | 反思阈值熔断 | 人工审核介入 |
| NTFS 写锁冲突 | P2 | 指数退避重试 | 写权限收拢至单进程 |
| 编码污染 (GBK/UTF-8) | P2 | 双向清洗管道 | 强制 UTF-8 环境 |

---

## 📅 时间线 (甘特图)

```
Week 1: ██████████              (阶段 1.0: 基础设施)
Week 2:          ██████████     (阶段 1.1: 通信总线)
Week 3:                    ████████ (阶段 1.2: 核心进程 MVP)
Week 4:                            ██████ (阶段 1.3: 集成测试)
```

**总工期:** 4 周 (28 天)

**关键里程碑:**
- Day 3: 基础设施搭建完成
- Day 10: 通信总线与 WATCHDOG 完成
- Day 21: 三层核心进程 MVP 完成
- Day 28: 集成测试通过，Phase 1 交付

---

## 📖 相关文档

### 核心文档
- [ARCH.md](../../ARCH.md) - 系统架构蓝图
- [LAW.md](../../LAW.md) - 开发规范与工程宪法
- [MAP.md](../../MAP.md) - 战略指挥条令
- [COMPOUND.md](../../COMPOUND.md) - 司法防御与避坑指南
- [DIAGNOSIS.md](../../DIAGNOSIS.md) - 免疫诊断协议

### 参考文档
- [Python Monorepo Best Practices](https://github.com/goldbergyoni/python-monorepo)
- [Windows Job Objects API](https://docs.microsoft.com/en-us/windows/win32/procthread/job-objects)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## ✅ 审核清单

在开始开发前，请确认以下事项：

### P0 强制性修订（已完成）
- [x] **P0-1:** 项目路径修正 (smarthire → SmartHire)
- [x] **P0-2:** Git 仓库地址确认 (choupiyang/SmartHire)
- [x] **P0-3:** 快照隔离实现补充 (DIAGNOSIS §1.2)
- [x] **P0-4:** 沙盒彩排流程补充 (DIAGNOSIS §4.2)

### P1 强烈建议修订（已完成）
- [x] **P1-1:** 时间估算调整 (4-7 天 → 6-8 天)
- [x] **P1-2:** 合并与冲突管理机制补充 (MAP §3.2)
- [x] **P1-3:** COMPOUND.md 回归测试集补充
- [x] **P1-4:** L1 物理层测试具体化
- [x] **P1-5:** 混沌测试工具补充
- [x] **P1-6:** MTTR 测试方法详细化

### 文档审核
- [ ] ARCH.md 物理拓扑设计已审阅
- [ ] MAP.md 任务拆解策略已审阅
- [ ] DIAGNOSIS.md 测试要求已审阅
- [ ] COMPOUND.md 风险规避措施已审阅
- [ ] LAW.md 核心禁令已审阅

### 技术审核
- [ ] 开发环境已就绪 (Python 3.10+, Redis, Git)
- [ ] Windows 环境变量已配置
- [ ] Git 远程仓库已创建 (https://github.com/choupiyang/SmartHire.git)
- [ ] 测试框架已选择 (pytest + pytest-asyncio)

### 流程审核
- [ ] 备份策略已确认
- [ ] 回滚协议已确认
- [ ] 风险定级标准已确认
- [ ] 验收标准已确认

---

## 📝 审核状态

**当前状态:** ⚠️ **等待二次审核** (v1.1.0 修订版)

**修订摘要:**
- 已解决所有 P0 严重问题（4 项）
- 已完善所有 P1 中等问题（6 项）
- 已优化 P2 可选问题（2 项）

**下一步行动:**
1. 用户审核本修订版计划文档（v1.1.0）
2. 如有进一步修改建议，继续修订
3. 批准后开始阶段 1.0.1 开发任务
4. 每个阶段完成后提交完成报告

**审核人:** _______________
**审核日期:** _______________
**批准签字:** _______________

**审核状态跟踪:**
- [ ] v1.0.0 (2026-03-14): 初始版本
- [x] v1.1.0 (2026-03-14): 修订版 - 已完成 P0/P1 问题修订
- [ ] v1.1.0 审核批准: 待审核人签字

---

**文档生成时间:** 2026-03-14
**计划作者:** AI Agent (Claude)
**版本历史:**
- v1.1.0 (2026-03-14): **修订版** - 解决审核报告中的 P0 和 P1 问题
  - P0-1: 修正项目路径 smarthire → SmartHire
  - P0-2: 修正 Git 仓库地址
  - P0-3: 补充快照隔离实现机制
  - P0-4: 补充沙盒彩排流程
  - P1-1: 调整时间估算 4-7 天 → 6-8 天
  - P1-2: 补充合并与冲突管理机制
  - P1-3: 补充 COMPOUND.md 回归测试集
  - P1-4: 具体化 L1 物理层测试策略
  - P1-5: 补充混沌测试自动化工具
  - P1-6: 详细化 MTTR 测试方法
- v1.0.0 (2026-03-14): 初始版本创建

### 文档生命周期 ⚠️ P2-3 新增

**当前状态:** Planning Phase (docs/plans/)
**完成状态:** 移至 docs/reports/PHASE_1_COMPLETION_REPORT.md
**归档规则:** 实施完成后 7 天内归档到 docs/reports/

**文档生命周期管理 (LAW-DOC-001 §6.2.6):**
1. **创建阶段 (当前):**
   - [x] 初始版本创建 (v1.0.0)
   - [x] 审核反馈修订 (v1.1.0)
   - [ ] 待二次审核批准

2. **执行阶段 (开发开始后):**
   - [ ] 标记为 "In Progress"
   - [ ] 每个阶段完成后更新进度
   - [ ] 记录实际开始/结束时间

3. **完成阶段 (Phase 1 交付后):**
   - [ ] 生成完成报告: docs/reports/PHASE_1_COMPLETION_REPORT.md
   - [ ] 遵循 LAW-DOC-001 §6.2.2 完成报告标准
   - [ ] 包含: 执行摘要、问题诊断、解决方案、验证结果、统计分析、经验教训

4. **归档阶段 (交付 7 天后):**
   - [ ] 移动到 docs/reports/PHASE_1_COMPLETION_REPORT.md
   - [ ] 本计划文档保留在 docs/plans/ 作为历史记录
