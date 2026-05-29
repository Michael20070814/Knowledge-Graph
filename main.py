"""数据结构知识图谱主程序入口。"""

from __future__ import annotations

from pathlib import Path

from graph.builder import build_graph, load_knowledge_data
from graph.renderer import render_graph
from utils.stats import print_and_save_stats


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "knowledge.json"
OUTPUT_DIR = BASE_DIR / "output"
HTML_OUTPUT_PATH = OUTPUT_DIR / "knowledge_graph.html"
STATS_OUTPUT_PATH = OUTPUT_DIR / "stats.txt"


def main() -> None:
    """执行读取数据、构建图、统计信息和渲染 HTML 的完整流程。"""
    data = load_knowledge_data(DATA_PATH)
    graph = build_graph(data)
    print_and_save_stats(graph, STATS_OUTPUT_PATH)
    render_graph(graph, HTML_OUTPUT_PATH)
    print("知识图谱生成完成，请用浏览器打开 output/knowledge_graph.html")


if __name__ == "__main__":
    main()
