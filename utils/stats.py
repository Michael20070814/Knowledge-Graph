"""统计知识图谱结构信息并输出到终端和文件。"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import networkx as nx


def generate_stats_report(graph: nx.DiGraph) -> str:
    """生成完整统计报告文本。"""
    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()
    module_counts = _module_distribution(graph)
    top_degree_nodes = _top_degree_nodes(graph, limit=10)
    degree_distribution = _degree_distribution(graph)
    average_degree = _average_degree(graph)
    density = nx.density(graph)
    component_count = _connected_component_count(graph)

    lines: List[str] = []
    lines.append("数据结构知识图谱统计信息")
    lines.append("=" * 32)
    lines.append(f"总节点数：{node_count}")
    lines.append(f"总边数：{edge_count}")
    lines.append("")
    lines.append("各模块节点数量分布：")
    for module, count in module_counts:
        lines.append(f"- {module}：{count}")
    lines.append("")
    lines.append("度最高的前10个节点：")
    for rank, (label, degree) in enumerate(top_degree_nodes, start=1):
        lines.append(f"{rank}. {label}：{degree}")
    lines.append("")
    lines.append(f"平均度：{average_degree:.2f}")
    lines.append(f"图密度：{density:.6f}")
    lines.append(f"连通分量数量：{component_count}")
    lines.append("")
    lines.append("度分布：")
    for degree, count in degree_distribution:
        lines.append(f"- 度 {degree}：{count} 个节点")

    return "\n".join(lines)


def print_and_save_stats(graph: nx.DiGraph, output_path: Path) -> str:
    """打印统计报告，并保存到 output/stats.txt。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = generate_stats_report(graph)
    print(report)
    output_path.write_text(report + "\n", encoding="utf-8")
    return report


def _module_distribution(graph: nx.DiGraph) -> List[Tuple[str, int]]:
    """统计各模块节点数量。"""
    counter: Counter[str] = Counter()
    for _, attributes in graph.nodes(data=True):
        module_label = _module_label(str(attributes.get("module", "未分类")))
        counter[module_label] += 1
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))


def _top_degree_nodes(graph: nx.DiGraph, limit: int) -> List[Tuple[str, int]]:
    """获取度最高的核心节点。"""
    degree_items: List[Tuple[str, int]] = []
    for node_id, degree in graph.degree():
        label = str(graph.nodes[node_id].get("label", node_id))
        degree_items.append((label, int(degree)))

    degree_items.sort(key=lambda item: (-item[1], item[0]))
    return degree_items[:limit]


def _degree_distribution(graph: nx.DiGraph) -> List[Tuple[int, int]]:
    """统计度分布。"""
    counter: Counter[int] = Counter(dict(graph.degree()).values())
    return sorted(counter.items(), key=lambda item: item[0])


def _average_degree(graph: nx.DiGraph) -> float:
    """计算平均度。"""
    node_count = graph.number_of_nodes()
    if node_count == 0:
        return 0.0
    total_degree = sum(int(degree) for _, degree in graph.degree())
    return total_degree / node_count


def _connected_component_count(graph: nx.DiGraph) -> int:
    """计算连通分量数量；有向图使用弱连通分量。"""
    if graph.number_of_nodes() == 0:
        return 0
    if graph.is_directed():
        return nx.number_weakly_connected_components(graph)
    return nx.number_connected_components(graph)


def _module_label(module: str) -> str:
    """把模块 ID 转换为中文名称。"""
    labels: Dict[str, str] = {
        "linear": "线性结构",
        "tree": "树形结构",
        "graph": "图",
        "sorting": "排序算法",
        "searching": "查找算法",
        "analysis": "算法分析",
        "application": "应用场景",
    }
    return labels.get(module, module)
