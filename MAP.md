# MAP.md - 战略指挥条令 (Integrated Edition)

> **Version:** 7.0.0 (The Evolutionary Synthesis)
> **Status:** Active / Enforced
> **Role:** Executive Strategy & Lifecycle Management
> **Target:** Native Windows, Single-Node, Self-Healing Agent
> **Ecosystem:** Aligned with `ARCH.md`, `LAW.md`, `COMPOUND.md` & `DIAGNOSIS.md`

---

## 0. 治理五权分立 (Governance Quintet)

本项目依赖以下五大文档的动态制衡。作为战略指挥（MAP），必须在**弹性与原则**之间寻找平衡：

1. **蓝图对齐 (`ARCH.md`):** 所有任务拆分必须服务于系统架构的可持续性。
2. **立法遵从 (`LAW.md`):** 严禁违反环境铁律（核心禁令：`LAW-ENV-001` 禁止容器化、`LAW-ENV-002` 禁止绝对路径、`LAW-TENANT-001` 禁止多租户）。当效率受阻时，允许触发基于 `LAW.md §0.1` 的中止程序。
3. **司法防御 (`COMPOUND.md`):** 通过”分层蒸馏”管理复杂性，仅在 MAP 中保留核心关联。
4. **免疫诊断 (`DIAGNOSIS.md`):** 引入”混沌测试”，拒绝虚假安全，实施因病施治。
5. **行政执行 (MAP):** MAP 是唯一可执行源，支持 `[Fast-Track]` 快速迭代。

---

## 1. 任务拆分元模型：三维熵减法 (3D Decomposition)

在面对新需求时，必须进行“熵值分析”，将任务降维拆解至三个互不干扰的象限：

### 1.1 逻辑决策维度 (Reasoning - 策略层)

* **核心:** 追求“逻辑声明化”。
* **准则:** 变动频繁、依赖常识判断的逻辑需从硬编码剥离。
* **铁律:** 若 `if-else` 嵌套超过三层或涉及模糊语义，严禁硬编码。必须封装为独立的 Skill (技能) 并存入 SOP 知识库。

### 1.2 物理执行维度 (Actuation - 执行层)

* **核心:** 追求“逻辑真空”。
* **准则:** 代码应像 PLC 一样稳定，仅接受结构化参数，不进行主观决策。
* **铁律:** 所有物理交互（API/文件/IO）必须具备 **幂等性 (Idempotency)**，防止重复执行产生的破坏性副作用。

### 1.3 表现感知维度 (Presentation - 门户层)

* **核心:** 追求“事信分离”。
* **准则:** 彻底解耦“事实数据 (Data)”与“情感信息 (Information)”。
* **铁律:** 由“表现层注入器”根据用户画像实时注入语气与包装，系统仅传递纯净结果。

---

## 2. 阶段性效能螺旋 (The Efficiency Helix)

跳出“功能点计数”陷阱，关注系统认知成熟度：

* **Phase 1: 回路验证 (逻辑生存期):** 优先建立“报错 -> 捕获 -> 反思 -> 修正”的自愈循环。核心指标为 **MTTR (平均修复时长)**。
* **Phase 2: 认知广度 (技能爆发期):** 横向扩展技能库，每个新技能必须配备“负面案例测试集”，防止系统全局逻辑退化。核心指标为 **技能召回准确率**。
* **Phase 3: 自主优化 (进化期):** 系统基于日志自主合并相似功能、精简 SOP。核心指标为 **SOP 自动进化成功率**。

---

## 3. 合并与冲突管理 (Merging & Conflicts)

### 3.1 逻辑合并策略

* **功能合并 (Union):** 采取插件化合并，共享通信总线，互不干扰。
* **冲突合并 (Intersection):** 竞争物理资源时，引入“逻辑锁机制”，通过 SOP 明确动作优先级与回滚顺序。

### 3.2 免疫机制 (Regression Testing)

* **标准:** 新逻辑合并前，须由独立 Judge 模型运行历史案例集。
* **排异反应:** 若核心认知准确度下降 > 5%，判定为“排异”，强制拆分为更小单元分步实施。

---

## 4. 修复与进化的元路径 (Root Cause Analysis)

面对失效，根据三个层级“因病施治”：

* **环境级 (Physical):** Windows 或 API 异常。加固 Watchdog 与重试机制，严禁修改业务 SOP。
* **认知级 (Cognitive):** SOP 模糊或 LLM 幻觉。通过 Reflexion 记录上下文，更新向量库 Skill 描述，严禁在代码中写补丁。
* **协议级 (Protocol):** 通信字段不匹配。回归数据契约模型，执行严格的 Schema 迁移。

---

## 5. 开发者心法与执行铁律

* **视角:** 你在编写“员工手册 (SOP)”并构建“自动化车间 (Execute)”，而非传统程序。
* **极简原则:** 单个 SOP 超过 1000 字必须进行二层拆分。
* **数据原子性:** 遵循 `Write Temp -> Flush -> Fsync -> Atomic Rename` 流程防止损坏。
* **影子进化 (Shadow Evolution):** 新旧 SOP 并行运行，仅在新逻辑连续 10 次胜出后执行物理覆盖。