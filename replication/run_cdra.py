"""
CDRA 复现脚本
一键运行基线 vs CDRA 对比实验。
需要 Python 3.10+，openai 包。

使用方法：
    python run_cdra.py

输出：
    results/baseline_responses.json
    results/cdra_responses.json
    results/comparison_table.md
    results/summary.json
"""

import json
import os
import sys
import time
from datetime import datetime

# ============================================================
# 配置区 —— 在这里选择你的 LLM 后端
# ============================================================

# 后端选择（三选一，取消注释你要用的那一行）
BACKEND = "lmstudio"     # LM Studio 本地 (http://localhost:1234/v1)
# BACKEND = "ollama"      # Ollama 本地 (http://localhost:11434/v1)
# BACKEND = "openai"      # OpenAI 兼容 API (需要 BASE_URL + API_KEY)
# BACKEND = "openrouter"  # OpenRouter (需要 API_KEY)

# LM Studio 配置
LMSTUDIO_BASE_URL = "http://localhost:1234/v1"
LMSTUDIO_API_KEY = "lm-studio"

# Ollama 配置
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY = "ollama"

# OpenAI 兼容 API 配置（改为你自己的地址和密钥）
OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_API_KEY = "sk-your-key-here"

# OpenRouter 配置
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = ""  # 填入你的 key，例如 "sk-or-..."

# 模型选择
# "auto" = 自动检测列表中的第一个可用模型
# 也可手动指定，例如 "qwen2.5-7b" 或 "gpt-4o-mini"
MODEL = "auto"
AUTO_MODEL_LIST = [
    "qwen2.5-7b",
    "qwen3-8b",
    "llama-3.2-3b",
    "gemma-3-4b",
    "phi-4",
    "gpt-4o-mini",
    "claude-3-haiku",
]

# 请求间隔（秒），避免速率限制
REQUEST_DELAY = 1.0

# 单次请求超时（秒）
REQUEST_TIMEOUT = 120

# 最大 token 数
MAX_TOKENS = 256

# 温度（低温度保证可复现性）
TEMPERATURE = 0.3

# ============================================================
# 内部逻辑 —— 不需要修改
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, "results")
TEST_CASES_DIR = os.path.join(SCRIPT_DIR, "test_cases")
CONSTRAINTS_DIR = os.path.join(SCRIPT_DIR, "constraints")


def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def get_client():
    """根据配置获取 OpenAI 兼容客户端"""
    from openai import OpenAI

    if BACKEND == "lmstudio":
        return OpenAI(base_url=LMSTUDIO_BASE_URL, api_key=LMSTUDIO_API_KEY)
    elif BACKEND == "ollama":
        return OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)
    elif BACKEND == "openai":
        if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-your-key-here":
            print("错误：请先在脚本顶部设置 OPENAI_API_KEY")
            sys.exit(1)
        return OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)
    elif BACKEND == "openrouter":
        if not OPENROUTER_API_KEY:
            print("错误：请先在脚本顶部设置 OPENROUTER_API_KEY")
            sys.exit(1)
        return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)
    else:
        print(f"错误：未知后端 '{BACKEND}'")
        sys.exit(1)


def detect_model(client):
    """自动检测可用模型"""
    try:
        models = client.models.list()
        available = [m.id for m in models]
        print(f"  检测到 {len(available)} 个模型")
        for auto_model in AUTO_MODEL_LIST:
            for avail in available:
                if auto_model.lower() in avail.lower():
                    return avail
        return available[0] if available else None
    except Exception as e:
        print(f"  模型列表获取失败: {e}")
        return AUTO_MODEL_LIST[0]


def call_model(client, model, system_prompt, user_message):
    """调用模型并返回回复文本"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            timeout=REQUEST_TIMEOUT,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERROR] {e}"


def load_test_cases(filename):
    """加载 JSON 格式的测试用例"""
    path = os.path.join(TEST_CASES_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_condition(client, model, system_prompt, test_cases, label):
    """对一组测试用例运行一个条件"""
    print(f"\n{'='*60}")
    print(f"运行条件: {label}")
    print(f"{'='*60}")
    results = []
    total = len(test_cases)
    for i, tc in enumerate(test_cases):
        msg = tc["input"]
        tc_id = tc["id"]
        print(f"  [{i+1}/{total}] {tc_id}: {msg[:50]}...")
        response = call_model(client, model, system_prompt, msg)
        results.append({
            "id": tc_id,
            "input": msg,
            "response": response,
            "category": tc.get("category", "emotional"),
            "timestamp": datetime.now().isoformat(),
        })
        if i < total - 1:
            time.sleep(REQUEST_DELAY)
    return results


def compute_stats(baseline_results, cdra_results):
    """计算对比统计"""
    bl_suggest_count = 0
    cdra_suggest_count = 0
    bl_total = len(baseline_results)
    cdra_total = len(cdra_results)

    # 简单启发式检测"建议"关键词
    suggest_keywords = [
        "你应该", "我建议", "建议你", "试试", "可以试试",
        "第一步", "首先", "你可以", "不妨", "最好",
        "should", "recommend", "suggest", "try", "first step",
        "you could", "you should", "why don't you",
        "考虑", "不妨试试", "有个方法", "去试试",
        "建议", "方案", "步骤",
    ]

    for r in baseline_results:
        resp = r["response"].lower()
        if any(kw in resp for kw in suggest_keywords):
            bl_suggest_count += 1

    for r in cdra_results:
        resp = r["response"].lower()
        if any(kw in resp for kw in suggest_keywords):
            cdra_suggest_count += 1

    bl_rate = round(bl_suggest_count / bl_total * 100, 1) if bl_total else 0
    cdra_rate = round(cdra_suggest_count / cdra_total * 100, 1) if cdra_total else 0

    return {
        "baseline_total": bl_total,
        "cdra_total": cdra_total,
        "baseline_suggest_count": bl_suggest_count,
        "cdra_suggest_count": cdra_suggest_count,
        "baseline_suggest_rate_pct": bl_rate,
        "cdra_suggest_rate_pct": cdra_rate,
        "reduction_pct": round(bl_rate - cdra_rate, 1),
        "model": model,
        "backend": BACKEND,
        "timestamp": datetime.now().isoformat(),
    }


def generate_comparison_table(baseline_results, cdra_results, stats):
    """生成并排对比 Markdown 表格"""
    timestamp = stats["timestamp"].replace("T", " ")[:19]

    lines = [
        f"# CDRA 复现结果对比表",
        f"",
        f"**运行时间:** {timestamp}",
        f"**模型:** {stats['model']}",
        f"**后端:** {stats['backend']}",
        f"",
        f"## 统计摘要",
        f"",
        f"| 指标 | 基线 | CDRA | 变化 |",
        f"|------|------|------|------|",
        f"| 测试用例数 | {stats['baseline_total']} | {stats['cdra_total']} | — |",
        f"| 含建议的回复数 | {stats['baseline_suggest_count']} | {stats['cdra_suggest_count']} | -{stats['baseline_suggest_count'] - stats['cdra_suggest_count']} |",
        f"| 未请求建议率 | {stats['baseline_suggest_rate_pct']}% | {stats['cdra_suggest_rate_pct']}% | -{stats['reduction_pct']}% |",
        f"",
        f"## 逐条对比",
        f"",
        f"| # | 输入 | 基线回复 | CDRA 回复 |",
        f"|----|------|----------|-----------|",
    ]

    for i, (bl, cdra) in enumerate(zip(baseline_results, cdra_results)):
        bl_resp = bl["response"].replace("\n", " ").replace("|", "\\|")[:200]
        cdra_resp = cdra["response"].replace("\n", " ").replace("|", "\\|")[:200]
        inp = bl["input"][:60]
        lines.append(f"| {i+1} | {inp} | {bl_resp} | {cdra_resp} |")

    # 任务控制对比
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("> **提示：** 对比两列。基线回复是否包含步骤/方案/建议？CDRA 回复是否确认感受并留出空间？")
    lines.append("")
    lines.append(f"> **核心发现：** 未请求建议率从 {stats['baseline_suggest_rate_pct']}% 降至 {stats['cdra_suggest_rate_pct']}%（降低 {stats['reduction_pct']} 个百分点）。")
    lines.append("")
    lines.append(f"> **原始研究结果：** 16 模型 · 6 架构 · 100%→0%")

    return "\n".join(lines)


def main():
    print("=" * 60)
    print("CDRA 复现工具 v1.0")
    print("约束驱动的动态承接架构 —— 独立复现脚本")
    print("=" * 60)

    # 确保结果目录存在
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # 连接 LLM
    print(f"\n后端: {BACKEND}")
    try:
        client = get_client()
    except ImportError:
        print("错误：需要安装 openai 包")
        print("  pip install openai")
        sys.exit(1)

    # 确定模型
    global model
    if MODEL == "auto":
        print("自动检测模型...")
        model = detect_model(client)
        if not model:
            print("错误：未检测到可用模型。请手动设置 MODEL 变量。")
            sys.exit(1)
    else:
        model = MODEL
    print(f"模型: {model}")

    # 加载测试用例
    print("\n加载测试用例...")
    emotional_cases = load_test_cases("core_emotional.json")
    print(f"  情绪测试用例: {len(emotional_cases)} 个")

    # 加载约束提示词
    baseline_prompt = load_file(os.path.join(CONSTRAINTS_DIR, "baseline.txt"))
    cdra_prompt = load_file(os.path.join(CONSTRAINTS_DIR, "constraint_minimal_70words.txt"))
    print(f"  基线提示词: {len(baseline_prompt)} 字符")
    print(f"  CDRA 约束: {len(cdra_prompt)} 字符")

    # 预检查
    print(f"\n预计耗时: 约 {len(emotional_cases) * 2 * 2} 秒")
    print(f"（每个用例 × 2 条件 × {REQUEST_DELAY}s 间隔）")
    answer = input("\n开始运行？[Y/n] ").strip().lower()
    if answer and answer != "y":
        print("已取消。")
        return

    # 运行基线
    baseline_results = run_condition(
        client, model, baseline_prompt, emotional_cases, "基线（无约束）"
    )

    # 运行 CDRA
    cdra_results = run_condition(
        client, model, cdra_prompt, emotional_cases, "CDRA（70词约束）"
    )

    # 保存原始结果
    print("\n保存结果...")
    with open(os.path.join(RESULTS_DIR, "baseline_responses.json"), "w", encoding="utf-8") as f:
        json.dump(baseline_results, f, ensure_ascii=False, indent=2)
    with open(os.path.join(RESULTS_DIR, "cdra_responses.json"), "w", encoding="utf-8") as f:
        json.dump(cdra_results, f, ensure_ascii=False, indent=2)
    print(f"  baseline_responses.json ({len(baseline_results)} 条)")
    print(f"  cdra_responses.json ({len(cdra_results)} 条)")

    # 计算统计
    stats = compute_stats(baseline_results, cdra_results)
    with open(os.path.join(RESULTS_DIR, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    # 生成对比表
    table_md = generate_comparison_table(baseline_results, cdra_results, stats)
    with open(os.path.join(RESULTS_DIR, "comparison_table.md"), "w", encoding="utf-8") as f:
        f.write(table_md)

    # 打印摘要
    print("\n" + "=" * 60)
    print("结果摘要")
    print("=" * 60)
    print(f"  模型: {stats['model']}")
    print(f"  测试用例: {stats['baseline_total']} 个")
    print(f"  基线未请求建议率: {stats['baseline_suggest_rate_pct']}%")
    print(f"  CDRA 未请求建议率: {stats['cdra_suggest_rate_pct']}%")
    print(f"  降低: {stats['reduction_pct']} 个百分点")
    print(f"\n原始研究参考值: 100% → 0%")
    print(f"\n详细结果见 results/comparison_table.md")

    if stats['reduction_pct'] > 50:
        print("\n✅ CDRA 约束在您的环境中有效！")
    else:
        print("\n⚠️ 约束效果低于预期。尝试：")
        print("  1. 更换更大模型（≥ 3B）")
        print("  2. 检查约束提示词是否正确加载")
        print("  3. 查看逐条对比表找到失败案例")

    return stats


if __name__ == "__main__":
    main()
