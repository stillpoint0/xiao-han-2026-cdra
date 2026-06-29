"""
行为注释辅助工具
用于手动或半自动标注 CDRA 实验的模型回复。

使用方法：
    python annotate.py results/baseline_responses.json
    python annotate.py results/cdra_responses.json

标注规则见 annotation_guide.md
"""

import json
import sys
import os


def load_results(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def annotate_interactive(results):
    """交互式逐条标注"""
    print("CDRA 行为注释工具")
    print("=" * 40)
    print("每条回复，输入标注代码：")
    print("  s  = 含建议 (suggestion)")
    print("  n  = 纯承接 (no suggestion)")
    print("  a  = 模糊/不好判断 (ambiguous)")
    print("  q  = 退出")
    print()

    annotations = []
    for i, item in enumerate(results):
        print(f"\n[{i+1}/{len(results)}] {item['id']}")
        print(f"  输入: {item['input'][:80]}")
        print(f"  回复: {item['response'][:200]}")

        code = input("  标注 [s/n/a/q]: ").strip().lower()
        if code == "q":
            break
        if code not in ("s", "n", "a"):
            print("  无效。请输入 s/n/a/q")
            code = input("  标注 [s/n/a/q]: ").strip().lower()
            if code == "q":
                break

        item["annotation"] = code
        item["annotator_note"] = ""
        annotations.append(item)

    return annotations


def compute_summary(results):
    total = len(results)
    counts = {"s": 0, "n": 0, "a": 0, "unannotated": 0}
    for item in results:
        code = item.get("annotation", "")
        if code in counts:
            counts[code] += 1
        else:
            counts["unannotated"] += 1

    annotated = total - counts["unannotated"]
    if annotated == 0:
        rate = 0
    else:
        rate = round(counts["s"] / annotated * 100, 1)

    return {
        "total": total,
        "annotated": annotated,
        "has_suggestion": counts["s"],
        "no_suggestion": counts["n"],
        "ambiguous": counts["a"],
        "suggestion_rate_pct": rate,
    }


def main():
    if len(sys.argv) < 2:
        print("用法: python annotate.py <results_file.json>")
        print("示例: python annotate.py results/baseline_responses.json")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"文件不存在: {path}")
        sys.exit(1)

    results = load_results(path)
    print(f"加载 {len(results)} 条回复")

    mode = input("交互模式(i) 还是 自动统计(a)? [i/a]: ").strip().lower()
    if mode == "a":
        # 自动统计（基于关键词）
        summary = compute_summary(results)
        print(f"\n自动标注摘要:")
        print(f"  含建议: {summary['has_suggestion']} / {summary['annotated']} = {summary['suggestion_rate_pct']}%")
    else:
        annotated = annotate_interactive(results)
        summary = compute_summary(annotated)
        print(f"\n标注摘要:")
        print(f"  含建议: {summary['has_suggestion']} / {summary['annotated']} = {summary['suggestion_rate_pct']}%")
        print(f"  纯承接: {summary['no_suggestion']}")
        print(f"  模糊: {summary['ambiguous']}")

        save = input("\n保存标注结果? [y/N]: ").strip().lower()
        if save == "y":
            outpath = path.replace(".json", "_annotated.json")
            with open(outpath, "w", encoding="utf-8") as f:
                json.dump(annotated, f, ensure_ascii=False, indent=2)
            print(f"已保存: {outpath}")


if __name__ == "__main__":
    main()
