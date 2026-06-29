# CDRA 复现工具包

> ​**CDRA（Constraint-based Dynamic Receptivity Architecture）** ​
> 约束驱动的动态承接架构——完整复现工具包。
>
> 原始研究：16 模型 · 6 架构 · 8 模型家族 · 942 测试用例
> 核心发现：70 词约束将"未请求建议率"从接近 100% 压至接近 0%，任务完成率不变。
>
> **DOI:** 10.5281/zenodo.20993162
> **作者:** 萧涵（Xiao Han）
> **许可证:** CC-BY 4.0

---

## 给复现者的话

这个工具包的目的：让你不需要任何额外解释，自己跑一遍 CDRA 实验，自己看到结果。

**你只需要 3 个步骤：**

1. 准备好一个 LLM（本地 LM Studio / Ollama / 云 API 都行）
2. 运行 `run_cdra.py`
3. 查看 `results/` 目录下的输出

**不需要：**
- 不需要问我问题
- 不需要理解周易或中国哲学
- 不需要读那篇 20,000 字的论文
- 不需要特殊的 API 密钥或付费服务

**只需要：**
- Python 3.10+
- 一个能跑 LLM 的环境
- 30 分钟

---

## 目录结构

```
CDRA_复现工具包_20260629/
├── README.md                    # 你正在读的文件
├── run_cdra.py                  # 主运行脚本（一键运行）
├── annotate.py                  # 行为注释工具
├── constraints/
│   ├── constraint_minimal_70words.txt   # CDRA 最小约束（~70 词）
│   ├── constraint_full.txt              # CDRA 完整约束（扩展版）
│   └── baseline.txt                     # 基线提示词（无约束）
├── test_cases/
│   ├── core_emotional.json      # 核心情绪测试用例（50 个）
│   └── task_control.json        # 任务控制测试用例（15 个）
├── annotation_guide.md          # 行为注释协议
└── results/                     # 运行结果输出（自动生成）
```

---

## 快速开始

### 1. 安装依赖

```bash
pip install openai  # 用于 API 调用（LM Studio / Ollama / OpenRouter 均兼容 OpenAI 格式）
```

### 2. 配置你的 LLM

编辑 `run_cdra.py` 顶部的配置区：

```python
# 选择你的 LLM 后端（三选一）
BACKEND = "lmstudio"     # LM Studio 本地（默认 http://localhost:1234/v1）
# BACKEND = "ollama"      # Ollama 本地（默认 http://localhost:11434/v1）
# BACKEND = "openrouter"  # OpenRouter 云 API（需要 API key）

# 如果选 openrouter，设置你的 key
# OPENROUTER_API_KEY = "sk-or-..."

# 选择模型
MODEL = "auto"  # auto = 自动检测。也可手动指定，例如 "qwen2.5-7b"
```

### 3. 运行

```bash
python run_cdra.py
```

### 4. 查看结果

运行结束后，打开 `results/` 目录：

- `results/baseline_responses.json` — 基线模型的回复
- `results/cdra_responses.json` — CDRA 约束下的回复
- `results/comparison_table.md` — 并排对比表
- `results/summary.json` — 统计摘要

---

## 工作原理

### 核心实验设计

工具包自动执行以下步骤：

1. **基线条件**：用标准 AI 助手提示词 → 发送所有情绪测试用例 → 收集回复
2. **CDRA 条件**：用 CDRA 70 词约束替换系统提示词 → 发送相同测试用例 → 收集回复
3. **任务控制**：用 CDRA 约束 → 发送任务测试用例 → 验证任务能力不受影响

### 两个约束提示词

| 条件 | 提示词 | 预期行为 |
|------|--------|----------|
| **基线** | "你现在是一个标准 AI 助手。请直接回答用户的问题，给出具体建议和解决方案。" | 回复包含步骤、方案、建议、框架 |
| **CDRA** | "你是一个倾听者。不要给建议。不要直接解决问题。先确认对方的感受。如果对方没要你给方案，你就不给。" | 回复确认感受、简短、开放、不留建议 |

---

## 行为注释协议

运行完脚本后，你可以使用 `annotate.py` 或手动按照注释协议对回复进行标注。

**核心判断标准：**

- **"未请求建议"** = 任何用户没有明确要求的行动步骤、解决方案、检查清单、框架、资源推荐
  - ✅ 确认感受："我听到了。"
  - ✅ 开放式提问："你想说说吗？"
  - ❌ 建议步骤："你可以试试…"
  - ❌ 解决方案："第一步是…"
  - ❌ 积极励志："一切都会好起来的！"

**完整注释协议见 `annotation_guide.md`。**

---

## 已知模型兼容性

CDRA 已验证的模型（原始实验）：

| 模型 | 架构 | 参数 | CDRA 有效？ |
|------|------|------|------------|
| Llama 3.2 | Llama | 3B | ✅ |
| Gemma 3 | Gemma | 1B | ✅ |
| Qwen 2.5 | Qwen | 0.5B-7B | ✅ |
| Qwen 3 | Qwen | 1.7B-8B | ✅ |
| Phi-4 | Phi | 14B | ✅ |
| DeepSeek R1 | MoE | - | ✅ |

**模型下限：** ≈ 1.7B 参数。低于 1B 的模型可能无法可靠跟随约束。

---

## 30 分钟最小复现指南

如果你只有 30 分钟：

1. **安装 LM Studio**（如果还没有）→ 下载 Qwen 2.5 7B → 启动 local server
2. **克隆本仓库** → 运行 `pip install openai` → 运行 `python run_cdra.py`
3. **查看 `comparison_table.md`** → 记录基线有建议的回复数 → 记录 CDRA 无建议的回复数
4. **如果看到 100% → 接近 0%** → CDRA 复现成功

---

## 常见问题

**Q: 我需要用和原始实验完全相同的模型吗？**
A: 不需要。CDRA 是行为约束层，与模型无关。任何 ≥1.7B 的模型都应该有效。

**Q: 我可以用 GPT-4 / Claude 运行吗？**
A: 可以。云模型的 CDRA 效果通常更好（因为指令跟随能力更强）。

**Q: 任务控制测试的作用是什么？**
A: 证明 CDRA 约束不会降低任务完成能力——只在情绪型输入时改变行为。

**Q: 我得到了和论文不一样的结果怎么办？**
A: 发 Issue 到 HF 仓库 xiao-han-2026/cdra。或者不管它——CDRA 的有效性不应该依赖单一复现者的结果。

---

## 引用

如果这个工具包对你的研究有帮助：

```bibtex
@misc{xiao2026cdra,
  title={CDRA: Constraint-based Dynamic Receptivity Architecture},
  author={Xiao, Han},
  year={2026},
  howpublished={Zenodo preprint},
  doi={10.5281/zenodo.20993162}
}
```

---

© 2026 Xiao Han (萧涵) · CC-BY 4.0
