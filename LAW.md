# LAW.md - 单租户 Windows 智能体开发动态宪法

> **Version:** 5.0.0 (The Integrated Constitution)
> **Status:** Active / Enforced
> **Scope:** 全局开发宪法 / The Supreme Code
> **前言：** 本宪法定义了在单租户 Windows 物理机环境下，构建智能体系统（如 shasha 等核心项目）必须遵循的底层原则与工程红线。它是所有开发行为的最高准则，凌驾于任何代码实现与功能需求之上。**核心理念：严守底线，弹性执行。**

---

## 📖 引用规范 (Citation Convention)

> ⚠️ **重要**: 本文档使用**永久标识符（Permanent IDs）**系统，确保其他文档的引用不会因为章节重组而失效。

### 引用格式

```
LAW-{CATEGORY}-{NUMBER}
```

**示例**:
- `LAW-ENV-001` - 环境主权：原生物理性原则（禁止容器化）
- `LAW-ENV-002` - 环境主权：绝对路径禁令
- `LAW-TENANT-001` - 单租户简约性：用户管理真空化
- `LAW-ENG-001` - 工程纪律：职责物理隔离

### 核心条款速查表

| 永久ID | 条款名称 | 当前章节 | 状态 |
|--------|---------|---------|------|
| LAW-ENV-001 | 原生物理性原则 | §1.1 | ✅ 强制 |
| LAW-ENV-002 | 绝对路径禁令 | §1.2 | ✅ 强制 |
| LAW-ENV-003 | 模型接入标准化 | §1.3 | ✅ 强制 |
| LAW-TENANT-001 | 用户管理真空化 | §2.1 | ✅ 强制 |
| LAW-ENG-001 | 职责物理隔离 | §3.1 | ✅ 强制 |
| LAW-ENG-002 | 代码铁律 | §3.2 | ✅ 强制 |
| LAW-ENG-003 | 代码同步与备份纪律 | §3.3 | ✅ 强制 |
| LAW-DEF-001 | 防御性防御 | §4.1 | ✅ 强制 |
| LAW-DEF-002 | 尸检记录与无害化失败 | §4.2 | ✅ 强制 |
| LAW-DATA-001 | 通信协议契约化 | §5.1 | ✅ 强制 |
| LAW-DATA-002 | 存储主权与安全写入协议 | §5.2 | ✅ 强制 |
| LAW-DOC-001 | 文档标准协议 | §6.2 | ✅ 强制 |

> **注**: 当本宪法升级时，永久ID保持不变，只有"当前章节"列会更新。

---

---

## 第 0 章：动态平衡与治理结构 (Dynamic Equilibrium & Governance)

### 0.1 动态宪法条款 (Dynamic Suspension)

写每一行代码时，假设三个月后你会彻底失忆。代码必须清晰到那时你能在一分钟内看懂。但本法律体系具有**动态适应性**，当满足以下条件时，允许临时中止非核心条款：

* **效率熔断：** 单一功能的文档维护时间超过实际编码时间的 50%。
* **中止程序：** 在 `MAP.md` 中标记 `[CONSTITUTION SUSPENSION]`，记录中止原因及预期恢复时间（最长不超过1周），并在期满后进行架构评审。

### 0.2 文档五权分立 (The Five Pillars)

1. **ARCH.md (蓝图):** 做什么。系统的终局形态与物理法则。
2. **LAW.md (立法):** 不能做什么。不可逾越的红线（即本文件）。
3. **MAP.md (行政):** 何时做。战术执行计划。
4. **COMPOUND.md (司法):** 曾经做错什么。动态避坑指南。
5. **DIAGNOSIS.md (免疫):** 怎么治。测试定损与诊断协议。

---

## 第一章：环境主权 (Environment Sovereignty)

### 1.1 原生物理性原则 (Native Physicality)

> **📌 永久标识符: `LAW-ENV-001`**

* **核心禁令：** 严禁使用 Docker、Podman 或任何形式的容器化/虚拟化技术。
* **理由：** 系统必须直接在 Windows 物理机环境下运行，以利用原生 API 响应和硬件性能。开发者必须直面并处理物理环境下的端口冲突、注册表依赖及驱动交互。

### 1.2 绝对路径禁令 (Absolute Path Ban)

> **📌 永久标识符: `LAW-ENV-002`**

* **核心禁令：** 严禁在代码、配置或脚本中硬编码任何绝对路径（如 `C:\...`）。
* **执行：** 系统必须具备“绿色软件”特性。所有资源引用必须基于项目根目录（Root-Anchored），使用相对路径动态计算物理位置。

### 1.3 模型接入标准化 (Standardized Model Access)

> **📌 永久标识符: `LAW-ENV-003`** (Standardized Model Access)

* **执行：** 无论底层调用何种大语言模型，必须收敛并使用兼容 OpenAI 标准的 Python SDK 进行封装，确保系统认知层协议的绝对一致性与可替换性。

---

## 第二章：单租户简约性 (Single-Tenant Simplicity)

### 2.1 用户管理真空化 (Zero User Management)

> **📌 永久标识符: `LAW-TENANT-001`** (Zero User Management)

* **核心禁令：** 严禁引入 RBAC 权限管理、多账号注册或登录鉴权逻辑。
* **执行：** 即使系统采用网页作为前端交互界面，也严格被定义为“单租户”私有资产。系统默认当前物理机的操作者/前端页面的唯一访问者即为合法用户。安全边界由操作系统账户权限和本地文件系统保障。

---

## 第三章：工程纪律与认知 (Engineering Discipline)

### 3.1 职责物理隔离 (Physical Responsibility Isolation)

> **📌 永久标识符: `LAW-ENG-001`** (Physical Responsibility Isolation)

* **核心要求：** 严禁跨越逻辑边界进行功能堆砌。
* **执行：** 代码层面的解耦必须伴随着进程层面的隔离，按照职能分配到对应的独立物理进程中，确保单一故障不引发系统级雪崩。

### 3.2 代码铁律 (Strict Coding Standards)

> **📌 永久标识符: `LAW-ENG-002`** (Strict Coding Standards)

* **Type Hinting:** 所有函数定义必须包含严格的类型标注。
* **Explicit Returns:** 严禁隐式返回 `None`。
* **No Magic Numbers:** 严禁在业务逻辑中出现不明意义的数字或字符串，必须抽离为常量或配置。

### 3.3 代码同步与备份纪律 (Code Sync & Backup Discipline)

> **📌 永久标识符: `LAW-ENG-003`** (Code Sync & Backup Discipline)

* **核心要求:** 所有代码变更必须自动同步到远程 Git 仓库 `https://github.com/choupiyang/shasha.git`。
* **执行协议:**
  1. **自动同步触发条件:**
     - 每次功能开发完成并测试通过后
     - 每次Bug修复完成并验证后
     - 每次架构调整或重构完成后
  2. **同步前检查清单:**
     - [ ] 代码已通过本地测试
     - [ ] 敏感信息（API Key、密码等）已排除
     - [ ] 提交信息清晰描述变更内容
     - [ ] 遵循语义化版本号规范（如有影响）
  3. **同步协议:**
     - 使用 `git add` + `git commit` + `git push` 标准流程
     - 提交信息格式: `<type>: <description>` (type: feat/fix/refactor/docs等)
     - 确保本地分支与远程分支同步
  4. **异常处理:**
     - 网络故障时保留本地提交，待网络恢复后重试
     - 冲突解决必须通过代码审查，不可强制覆盖
     - 同步失败必须记录日志并告警
* **理由:** 确保代码资产的安全备份、多设备协作能力、以及变更历史的完整可追溯性。

---

## 第四章：鲁棒性与安全性 (Robustness & Security)

### 4.1 防御性防御 (Defensive Defense)

> **📌 永久标识符: `LAW-DEF-001`** (Defensive Defense)

* **核心要求：** 永远假设外部依赖（网络、硬件、模型）是不可靠的。
* **执行：** 所有物理交互必须实现重试 (Retry)、超时 (Timeout) 和状态自检 (Watchdog)。

### 4.2 尸检记录与无害化失败 (Crash Dumps & Graceful Degradation)

> **📌 永久标识符: `LAW-DEF-002`** (Crash Dumps & Graceful Degradation)

* **No Silent Failures:** 严禁出现空的 `except:` 语句。系统发生致命错误时必须“优雅且安全”地停机或回滚。
* **记录定损:** 崩溃时必须将完整的 Traceback 写入本地日志。关键写操作必须具备“前置快照”和“后置验证”机制，保护用户的物理数据资产高于一切。

---

## 第五章：数据与通信 (Data & Communication)

### 5.1 通信协议契约化 (Contract-based IPC)

* **核心要求：** 严禁使用非结构化数据（如纯字符串、松散字典）进行跨进程通信。
* **执行：** 所有通过总线流转的消息必须经过严格的模式校验（如 Pydantic Schema），确保通信各方的认知完全对齐。

### 5.2 存储主权与安全写入协议 (Storage Sovereignty & Safe Write)

* **核心隔离：** 进程间的数据同步必须通过通信总线信号触发，严禁跨进程直接读写非本进程所属的数据库/物理文件，以避免文件锁死与逻辑损坏。
* **安全写入：** 严禁对核心数据文件进行“直接覆盖写入”。必须严格遵循三步走协议：
1. Write to `.tmp` (写入临时文件)
2. Flush buffer (刷入磁盘缓存)
3. Atomic Rename (原子级替换重命名)



---

## 第六章：知识治理与熵减 (Knowledge Governance)

### 6.1 熵减法则 (Entropy Reduction)

* **Token Limit:** 为保证系统记忆与 LLM 上下文的效率，类似 `COMPOUND.md` 等沉淀性文档的体积严禁超过 **5000 Tokens**。必须通过不断的蒸馏、合并与废弃，保持文档的极简与高信息密度。

### 6.2 文档标准协议 (Documentation Standards)

所有项目文档必须遵循以下标准协议，确保知识传递的一致性和可追溯性。

#### 6.2.1 文档分类 (Document Classification)

* **核心文档 (Core Documents):** 保留在项目根目录，定义系统的基本原则和架构

  > ⚠️ **神圣不可侵犯**: 以下7个文档是项目的宪法级文档，**严禁移动、重命名、删除或归档**

  - `README.md` - 项目入口和快速开始指南
  - `ARCH.md` - 系统架构蓝图（物理拓扑与协议规范）
  - `LAW.md` - 开发规范与工程宪法（**本文件**）
  - `MAP.md` - 战略指挥条令（任务拆解与执行策略）
  - `COMPOUND.md` - 司法防御与避坑指南（历史经验沉淀）
  - `DIAGNOSIS.md` - 免疫诊断协议（测试与自愈体系）
  - `CHANGELOG.md` - 项目变更日志

  **核心文档特征**:
  - 定义系统的"为什么"和"怎么做"
  - 长期有效（跨越多个 Sprint/Phase）
  - 被其他文档广泛引用
  - 修改需要架构师审批

* **工作文档 (Working Documents):** 存放在 `docs/` 目录，记录开发过程和临时分析
  - `reports/` - 完成报告、审计报告
  - `plans/` - 开发计划和实施计划
  - `diagnosis/` - 问题诊断文档
  - `architecture/` - 架构相关文档
  - `platforms/` - 平台集成文档
  - `phases/` - 阶段性项目文档
  - `mcp/` - MCP/MCPX 相关文档
  - `guides/` - 开发指南
  - `legacy/` - 历史文档

#### 6.2.2 完成报告标准 (Completion Report Template)

所有完成报告必须遵循以下标准结构：

```markdown
# [任务名称] 完成报告

## 执行摘要

**任务**: [简短描述任务目标]
**状态**: ✅ 已完成 / ⚠️ 部分完成 / ❌ 失败
**日期**: YYYY-MM-DD
**影响范围**: [影响模块/文件]

---

## 一、问题诊断
### 1.1 初始表现
[描述问题的具体表现]

### 1.2 根本原因分析
[分析问题的根本原因]

---

## 二、解决方案/实施计划
### 2.1 解决策略
[描述解决问题的策略]

### 2.2 实施详情
[详细说明实施步骤]

---

## 三、验证结果
### 3.1 测试验证
[列出测试结果和指标]

### 3.2 系统验证
[系统级别的验证结果]

---

## 四、统计分析
### 4.1 修改统计
[统计修改的文件数量和代码行数]

### 4.2 性能对比
[修复前后的性能对比]

---

## 五、经验教训
### 5.1 问题根源
[总结问题的根本原因]

### 5.2 改进建议
[提出防止类似问题再次发生的建议]

---

## 六、完成确认
### 6.1 验证清单
- [x] 问题诊断完成
- [x] 解决方案实施完成
- [x] 测试验证通过
- [x] 文档更新完整

### 6.2 遗留问题
[列出未解决的问题和后续计划]

---

## 七、附录
### 7.1 修改文件清单
[列出所有修改的文件]

### 7.2 相关文档
[链接相关的技术文档]

---

**报告生成时间**: YYYY-MM-DD HH:MM:SS
**报告作者**: [作者名称]
**审核状态**: ✅ 已完成 / ⏳ 待审核
```

#### 6.2.3 文档命名规范 (Naming Convention)

* **完成报告**: `*_COMPLETION_REPORT.md`
* **审计报告**: `*_AUDIT_REPORT.md`
* **诊断报告**: `DIAGNOSIS_*.md`
* **修复计划**: `*_FIX_PLAN.md`
* **实施计划**: `PLAN_*.md`
* **测试指南**: `*_TEST_GUIDE.md`

#### 6.2.4 文档质量标准 (Quality Standards)

* **完整性**: 所有报告必须包含执行摘要、问题诊断、解决方案、验证结果四个核心章节
* **可追溯性**: 必须记录修改的文件路径、行号和具体内容
* **数据驱动**: 必须提供具体的测试数据和统计指标
* **可复现性**: 必须提供足够的细节，使他人能够理解和复现
* **时效性**: 报告应在任务完成后 24 小时内完成

#### 6.2.5 文档存储路径规范 (Document Storage Rules)

* **路径决策原则 (Placement Decision Tree)**:

```
是否为系统级核心定义？
├─ 是 → 根目录 (README.md, ARCH.md, LAW.md, MAP.md, COMPOUND.md, DIAGNOSIS.md, CHANGELOG.md)
└─ 否 → 是否为临时分析/工作文档？
    ├─ 是 → docs/{category}/
    └─ 否 → 是否为长期参考？
        ├─ 是 → docs/guides/ 或 docs/platforms/
        └─ 否 → docs/legacy/
```

* **详细分类规则**:

| 文档类型 | 存储路径 | 命名格式 | 示例 |
|---------|---------|---------|------|
| **任务完成报告** | `docs/reports/` | `{TASK}_COMPLETION_REPORT.md` | `IMPORT_FIX_COMPLETION_REPORT.md` |
| **阶段完成报告** | `docs/reports/` | `PHASE_{N}_COMPLETION_REPORT.md` | `PHASE_1_COMPLETION_REPORT.md` |
| **Sprint完成报告** | `docs/reports/` | `SPRINT_{N}_COMPLETION_REPORT.md` | `SPRINT_3_COMPLETION_REPORT.md` |
| **审计报告** | `docs/reports/` | `{TARGET}_AUDIT_REPORT.md` | `ARCH_COMPLIANCE_AUDIT_REPORT.md` |
| **修复计划** | `docs/plans/` | `{ISSUE}_FIX_PLAN.md` | `IMPORT_FIX_PLAN.md` |
| **实施计划** | `docs/plans/` | `PLAN_{FEATURE}.md` | `PLAN_FEISHU_ONLY_DEVELOPMENT.md` |
| **问题诊断** | `docs/diagnosis/` | `DIAGNOSIS_{ISSUE}.md` | `DIAGNOSIS_IMPORT_ERRORS.md` |
| **架构文档** | `docs/architecture/` | `{TOPIC}_ARCHITECTURE.md` | `PROTOCOL_PARSER_ARCHITECTURE.md` |
| **平台指南** | `docs/platforms/` | `{PLATFORM}_SETUP_GUIDE.md` | `FEISHU_SETUP_GUIDE.md` |
| **MCP相关** | `docs/mcp/` | `MCPX_{TOPIC}.md` | `MCPX_INTEGRATION_PLAN.md` |
| **开发指南** | `docs/guides/` | `{TOPIC}_GUIDE.md` | `SHADOW_MODE_GUIDE.md` |
| **临时/旧文档** | `docs/legacy/` | 按原名称 | 超过30天的报告 |

* **禁止的路径行为**:

  * ❌ **严禁在根目录创建非核心文档**: 任务报告、临时分析等必须放在 `docs/` 子目录
  * ❌ **严禁在源代码目录混合文档**: `apps/` 和 `packages/` 目录只存放代码，不存放文档
  * ❌ **严禁使用分散的命名**: 如 `report1.md`, `analysis_temp.md` 等无意义名称
  * ❌ **严禁在多个目录重复同名文档**: 每个文档只能有一个权威版本

#### 6.2.6 文档生命周期管理 (Document Lifecycle)

* **创建阶段 (Creation)**:
  1. **创建前检查**: 先搜索现有文档，避免重复创建
  2. **选择正确路径**: 根据存储路径规范选择目录
  3. **遵循模板**: 使用标准模板结构
  4. **添加索引**: 在相关目录的 README.md 中添加链接

* **维护阶段 (Maintenance)**:
  1. **定期审查**: 每周审查 `docs/plans/` 和 `docs/diagnosis/`
  2. **及时归档**: 完成的计划移至 `docs/reports/`
  3. **合并重复**: 将相似文档合并，删除旧版本
  4. **更新索引**: 文档移动后更新所有引用链接

* **归档阶段 (Archival)**:
  1. **归档条件**:
     - 计划类文档：实施完成后移至 `docs/reports/`
     - 诊断文档：问题解决30天后移至 `docs/legacy/`
     - 临时分析：相关功能稳定后移至 `docs/legacy/`
  2. **归档前操作**:
     - 提取关键经验教训到 `COMPOUND.md`
     - 更新相关架构文档
     - 确保无内部链接引用
  3. **清理策略**:
     - `docs/legacy/` 中超过90天且无引用的文档可删除
     - 定期清理空的子目录

#### 6.2.7 文档创建决策树 (Document Creation Decision Tree)

在创建新文档前，必须回答以下问题：

```
问题 1: 这个信息是否已经存在于现有文档中？
├─ 是 → 更新现有文档，而不是创建新文档
└─ 否 → 问题 2: 这个信息是否是系统的核心定义？

问题 2: 是否是架构/规范层面的核心定义？
├─ 是 → 考虑更新根目录的核心文档 (ARCH/LAW/MAP)
└─ 否 → 问题 3: 这是临时分析还是长期参考？

问题 3: 文档的预期生命周期？
├─ 临时 (< 7天) → docs/diagnosis/ 或 docs/plans/
├─ 短期 (7-30天) → docs/reports/
├─ 中期 (1-3月) → docs/guides/ 或 docs/platforms/
└─ 长期 (> 3月) → 考虑整合到核心文档

问题 4: 是否需要快速检索？
├─ 是 → 确保文件名包含关键关键词
└─ 否 → 使用标准命名格式
```

#### 6.2.8 Python脚本与工具文档规范 (Python Scripts Documentation)

* **根目录脚本规范**:
  * **诊断脚本** (`diagnose_*.py`): 保留在根目录，用于快速问题诊断
  * **启动脚本** (`start*.ps1`): 保留在根目录，作为系统入口
  * **工具脚本**: 移至 `scripts/` 目录，按功能分类

* **脚本存储路径**:

| 脚本类型 | 存储路径 | 命名格式 |
|---------|---------|---------|
| 诊断脚本 | 根目录 | `diagnose_{feature}.py` |
| 启动脚本 | 根目录 | `start*.ps1` |
| 部署脚本 | `scripts/deploy/` | `deploy_*.py` |
| 验证脚本 | `scripts/validate/` | `validate_*.py` |
| 测试脚本 | `tests/legacy/` | `test_*.py` (临时) |
| 兼容性测试 | `tests/compatibility/` | `test_*_compatibility.py` |

* **备份文件管理**:
  * **备份路径**: `backups/` 目录，按日期和任务组织
  * **命名格式**: `{YYYY-MM-DD}_{task_name}/{filename}.bak`
  * **保留期限**: 最多保留30天的备份
  * **禁止在源代码目录创建 .bak 文件**

---

> [!IMPORTANT]
> **架构师寄语：** 本宪法不是束缚，而是保护。它将我们从琐碎的、通用的 Web 开发范式中解放出来，强制我们将所有的智力倾注在 AI 逻辑的深度与物理环境的稳健性上。