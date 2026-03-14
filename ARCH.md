# **ARCH (Architecture) - 智雇家 (SmartHire) 核心架构协议 v2.0 (Rational & Defensive Edition)**

> **版本**: 2.0
> **代号**: 契约之盾 (The Contract Shield)
> **状态**: 终极发布
> **导读**: 本协议定义了智雇家 Agent 在 Windows 原生环境下，如何通过 **MESSAGE(SOUL)**、**PLAN(SKILLS)** 与 **EXECUTE(INTUITION)** 的三层架构，实现从“感性吐槽”到“理性契约”的闭环，核心目标是**通过技术确定性消除用工纠纷**。

---

## **0. 物理拓扑：sh-mono 目录树 (The Infrastructure)**

遵循 **Python Monorepo** 规范，强制实现业务逻辑与风控引擎的物理隔离。

F:\object\smarthire\
├── swan.py                         # 系统点火入口（原ss.py）
├── start.ps1                       # Windows 环境变量与 Job Objects 注入
│
├── /apps                           # 【进程空间】
│   ├── /sh_message                 # [进程 A] SOUL：职业管家渲染
│   │   ├── soul_renderer.py        # 职业话术渲染 (严禁主观偏见)
│   │   ├── matrix_distributor.py   # “海报+风险书+面试提纲”三位一体输出
│   │   └── ui_radar_adapter.py     # 五维雷达图数据适配器
│   │
│   ├── /sh_plan                    # [进程 B] SKILLS：契约认知层
│   │   ├── contract_orchestrator.py# 任务编排：吐槽 -> JD -> 匹配的逻辑闭环
│   │   ├── rubric_engine.py        # 1-5 分标准化量规打分引擎
│   │   └── compliance_checker.py   # 避嫌算法控制 (地域、歧视、红线拦截)
│   │
│   ├── /sh_execute                 # [进程 C] INTUITION：物理存证层
│   │   ├── multimodal_parser.py    # 语音/截图/简历的原子化解析
│   │   ├── evidence_vault.py       # 证据锚点管理器 (字段与原始素材的物理映射)
│   │   └── conflict_detector.py    # 逻辑冲突点扫描 (如年龄与经验矛盾)
│   │
│   └── /sh_watchdog                # [进程 D] 免疫层：故障自愈与合规监控
│
├── /packages                       # 【内核空间】
│   ├── /sh_core                    # 统一模型：FactModel, DecisionReport
│   ├── /sh_legal_rules             # 行业法律法规库与屏蔽词库
│   └── /sh_win32_utils             # Windows 路径锚定与编码流双向清洗
│
├── /data                           # 【存储主权】
│   ├── /evidence/                  # trace_evidence.db (带源证据链存储)
│   └── /profiles/                  # employer_pref.db (雇主确认过的招募标准)
│
└── /workspace                      # 物理写操作沙箱

---

## **1. 三层自进化矩阵 (The Defensive Matrix)**

| 层级 | 模块名称 | 进化核心 (Focus) | 认知等级 | 进化本质 |
| --- | --- | --- | --- | --- |
| **MESSAGE** | **SOUL (灵魂)** | **职业沟通直觉** | 共情+避险 | 将理性结果包装为具备职业素养的建议。 |
| **PLAN** | **SKILLS (技能)** | **逻辑契约直觉** | 理性指标 | 将模糊吐槽固化为 1-5 分的标准化量规。 |
| **EXECUTE** | **INTUITION (直觉)** | **物理存证直觉** | 真实性锚点 | 建立“解析即存证”的物理反射。 |

---

## **2. MESSAGE 层：职业管家渲染协议**

### 2.1 事信分离与防御性表达 (Defensive Rendering)

* **原则**：`sh_message` 不参与任何打分逻辑。它仅从 `sh_plan` 接收结构化事实，并根据“职业管家”人设注入同理心。
* **纠纷规避**：对于任何 AI 识别出的高风险项（如阿姨频繁跳槽），`soul_renderer` 必须强制输出关联的**面试建议**。
* *错误表达*：“这个阿姨不太稳定。”
* *职业表达*：“该候选人近 3 年有 5 段从业经历，存在稳定性风险，已为您在面试指南中自动生成了针对性背调提纲。”



---

## **3. PLAN 层：逻辑契约与避嫌机制**

### 3.1 吐槽 -> 标准 JD 的逻辑补全 (JD Transformation)

* **拒绝脑补**：`jd_transformer` 仅提取吐槽中的有效维度。对于信息缺失项，生成《补全建议清单》而非自行填空。
* **契约化确认**：系统强制生成《招募标准确认单》，雇主必须在雷达图界面对 AI 提炼的维度进行二次确认，作为后续匹配的唯一合法基准。

### 3.2 1-5 分标准化打分引擎 (Rubric Engine)

* 打分逻辑必须遵循预设的 `sh_legal_rules`，严禁主观定性。
* **避嫌过滤**：所有输出结果在进入渲染前，由 `compliance_checker` 进行静态扫描。任何涉及地域、宗教、长相的歧视性评价将被强制重写为合规描述或直接脱敏。

---

## **4. EXECUTE 层：物理存证与直觉解析**

### 4.1 证据锚点技术 (Evidence Anchoring)

* **物理映射**：每个结构化字段（如：擅长川菜）必须绑定一个 `Source_ID`（语音偏移量或截图坐标）。
* **冲突红线扫描**：`conflict_detector` 具备“物理直觉”。当检测到“语音自述工龄”与“身份证换算工龄”存在大于 1 年的负向偏差时，立即触发 `RED_FLAG` 预警。

---

## **5. 确定性边界保护 (Deterministic Guardrails)**

1. **结果矩阵三位一体**：任何决策输出必须同时包含：**招募海报 (展示) + 风险提示书 (避险) + 面试指南 (验证)**。
2. **预期管理注入**：系统在输出末尾强制附加：“分析结果受限于素材真实性，建议通过试岗及背景调查进行终核。”
3. **IO 鲁棒性**：针对 Windows 编码地雷，`sh_win32_utils` 实现 ASR 文本与 OCR 结果的实时 GBK/UTF-8 自动修正。
