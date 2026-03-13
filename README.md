# 智雇家 (SmartHire) - 智能用工风险管理系统

> **Version:** 1.0.0-alpha
> **Status:** 🚧 Development Phase
> **Architecture:** ARCH v2.0 (契约之盾)
> **Compliance:** LAW v5.0 | MAP v7.0 | DIAGNOSIS v3.0

---

## 📋 项目简介

智雇家是一个基于**三层自进化矩阵**的智能用工风险管理系统，通过 **MESSAGE(SOUL)**、**PLAN(SKILLS)** 与 **EXECUTE(INTUITION)** 的物理隔离架构，实现从"感性吐槽"到"理性契约"的闭环，核心目标是**通过技术确定性消除用工纠纷**。

### 核心特性

✅ **物理隔离架构** - MESSAGE/PLAN/EXECUTE/WATCHDOG 四进程独立运行
✅ **证据锚点技术** - 每个结构化字段绑定物理源，可追溯
✅ **防御性表达** - 职业管家渲染，事信分离，规避纠纷
✅ **标准化量规** - 1-5 分契约化打分，避嫌算法控制
✅ **自愈机制** - 故障检测、自动重启、反思回路
✅ **Windows 原生** - 无容器化，直接利用原生 API 和硬件性能

---

## 🏗️ 系统架构

### 三层自进化矩阵

| 层级 | 模块名称 | 进化核心 | 认知等级 | 进化本质 |
|------|----------|----------|----------|----------|
| **MESSAGE** | **SOUL (灵魂)** | 职业沟通直觉 | 共情+避险 | 将理性结果包装为具备职业素养的建议 |
| **PLAN** | **SKILLS (技能)** | 逻辑契约直觉 | 理性指标 | 将模糊吐槽固化为 1-5 分的标准化量规 |
| **EXECUTE** | **INTUITION (直觉)** | 物理存证直觉 | 真实性锚点 | 建立"解析即存证"的物理反射 |

### 物理拓扑

```
F:\object\smarthire\
├── ss.py                           # 系统点火入口
├── start.ps1                       # Windows 环境变量注入
│
├── /apps                           # 【进程空间】
│   ├── /sh_message                 # [进程 A] SOUL：职业管家渲染
│   ├── /sh_plan                    # [进程 B] SKILLS：契约认知层
│   ├── /sh_execute                 # [进程 C] INTUITION：物理存证层
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

---

## 🚀 快速开始

### 环境要求

- **操作系统:** Windows 11/10 (原生物理机，禁止容器化)
- **Python:** 3.10+ (支持 asyncio 和类型标注)
- **Redis:** 6.0+ (本地进程间通信总线)
- **Git:** 版本控制和代码同步

### 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/choupiyang/shasha.git
cd shasha
```

#### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows

# 安装核心依赖
pip install -r requirements.txt
```

#### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置以下变量：
# - ANTHROPIC_API_KEY: Claude API 密钥
# - REDIS_HOST: Redis 服务器地址 (默认 localhost)
# - REDIS_PORT: Redis 端口 (默认 6379)
```

#### 4. 启动 Redis

```bash
# 使用 Windows 服务管理器启动 Redis
# 或使用命令行:
redis-server
```

#### 5. 启动系统

```powershell
# 使用 PowerShell 启动脚本
.\start.ps1

# 或手动启动:
python ss.py
```

---

## 📖 核心文档

### 五权分立治理体系

本项目采用**五权分立**的文档治理体系，每个文档都有明确的职责和边界：

| 文档 | 职责 | 状态 | 说明 |
|------|------|------|------|
| **[ARCH.md](ARCH.md)** | 蓝图 | ✅ Active | 系统架构蓝图、物理拓扑与协议规范 |
| **[LAW.md](LAW.md)** | 立法 | ✅ Active | 开发规范与工程宪法（最高准则） |
| **[MAP.md](MAP.md)** | 行政 | ✅ Active | 战略指挥条令、任务拆解与执行策略 |
| **[COMPOUND.md](COMPOUND.md)** | 司法 | ✅ Active | 历史问题避坑指南、失效模式库 |
| **[DIAGNOSIS.md](DIAGNOSIS.md)** | 免疫 | ✅ Active | 测试定损与诊断协议、自愈体系 |

### 开发文档

- **[docs/plans/](docs/plans/)** - 开发计划和实施计划
- **[docs/diagnosis/](docs/diagnosis/)** - 问题诊断文档
- **[docs/reports/](docs/reports/)** - 完成报告和审计报告
- **[CHANGELOG.md](CHANGELOG.md)** - 项目变更日志

---

## 🧪 测试策略

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

### 测试协议

遵循 **DIAGNOSIS.md v3.0** 测试法典：

1. **确定性边界测试** - 基线 Payload 100% 成功消费
2. **混沌注入测试** - 100 次变异，崩溃率 = 0%，异常捕获率 = 100%
3. **智能阅卷机制** - 独立 Judge 模型逻辑审计
4. **金牌测试集** - 历史案例回归测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 生成覆盖率报告
pytest --cov=apps --cov=packages --cov-report=html
```

---

## 📊 开发状态

### Phase 1: 回路验证 (逻辑生存期) 🚧

**目标:** 建立自愈循环，验证物理隔离架构

**状态:** 📋 计划中 (等待审核)

**核心指标:**
- MTTR < 30 分钟
- 进程存活率 > 99%
- 通信成功率 > 95%
- 测试覆盖率 > 80%

**详细计划:** [docs/plans/SMARTHIRE_PHASE1_DEVELOPMENT_PLAN.md](docs/plans/SMARTHIRE_PHASE1_DEVELOPMENT_PLAN.md)

### 后续阶段

- **Phase 2:** 认知广度 (技能爆发期) - 横向扩展技能库
- **Phase 3:** 自主优化 (进化期) - 系统自主合并相似功能

---

## 🤝 贡献指南

### 开发规范

遵循 **LAW.md v5.0** 开发宪法：

1. **环境主权**
   - 禁止使用 Docker/容器化技术 (LAW-ENV-001)
   - 禁止硬编码绝对路径 (LAW-ENV-002)
   - 模型接入标准化 (LAW-ENV-003)

2. **工程纪律**
   - 职责物理隔离 (LAW-ENG-001)
   - 严格的类型标注 (LAW-ENG-002)
   - 代码自动同步备份 (LAW-ENG-003)

3. **防御性防御**
   - 重试、超时、状态自检 (LAW-DEF-001)
   - 严禁空的 except 语句 (LAW-DEF-002)

### 提交规范

遵循语义化提交信息规范：

```
<type>: <description>

[optional body]

[optional footer]
```

**类型 (type):**
- `feat`: 新功能
- `fix`: Bug 修复
- `refactor`: 重构
- `docs`: 文档更新
- `test`: 测试相关
- `chore`: 构建/工具链相关

**示例:**
```
feat(message): 实现 SoulRenderer 职业话术渲染

- 添加防御性表达逻辑
- 实现事信分离
- 添加职业素养评分测试

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

---

## 📄 许可证

本项目为私有资产，版权归属于项目所有者。

---

## 📞 联系方式

- **项目仓库:** https://github.com/choupiyang/shasha.git
- **文档位置:** [docs/](docs/)
- **问题反馈:** 通过 GitHub Issues

---

> **架构师寄语：** 本系统不是束缚，而是保护。它将我们从琐碎的、通用的 Web 开发范式中解放出来，强制我们将所有的智力倾注在 AI 逻辑的深度与物理环境的稳健性上。

**最后更新:** 2026-03-14
**文档版本:** 1.0.0
