"""使用 pyvis 将知识图谱渲染为单文件 HTML。"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Dict, Mapping

import networkx as nx
from pyvis.network import Network


MODULE_STYLES: Dict[str, Dict[str, str]] = {
    "linear": {
        "label": "线性结构",
        "primary": "#4E9AF1",
        "secondary": "#86BDF7",
        "tertiary": "#CFE4FC",
    },
    "tree": {
        "label": "树形结构",
        "primary": "#2ECC71",
        "secondary": "#79DFA0",
        "tertiary": "#CFF3DD",
    },
    "graph": {
        "label": "图",
        "primary": "#E74C3C",
        "secondary": "#F08C82",
        "tertiary": "#FAD3CF",
    },
    "sorting": {
        "label": "排序算法",
        "primary": "#F39C12",
        "secondary": "#F7C268",
        "tertiary": "#FCE7BD",
    },
    "searching": {
        "label": "查找算法",
        "primary": "#9B59B6",
        "secondary": "#BE91D0",
        "tertiary": "#E7D4EE",
    },
    "analysis": {
        "label": "算法分析",
        "primary": "#1ABC9C",
        "secondary": "#6BD7C4",
        "tertiary": "#C7F1EA",
    },
    "application": {
        "label": "应用场景",
        "primary": "#E67E22",
        "secondary": "#EFB06B",
        "tertiary": "#F8DEC2",
    },
}


RELATION_STYLES: Dict[str, Dict[str, Any]] = {
    "包含": {"color": "#888888", "width": 1.4, "dashes": False, "arrows": "to"},
    "演化自": {"color": "#3498DB", "width": 2.0, "dashes": False, "arrows": "to"},
    "实现方式": {"color": "#16A085", "width": 1.8, "dashes": False, "arrows": "to"},
    "应用于": {"color": "#E67E22", "width": 2.0, "dashes": False, "arrows": "to"},
    "复杂度为": {"color": "#8E44AD", "width": 1.5, "dashes": True, "arrows": "to"},
    "比较": {"color": "#C0392B", "width": 1.4, "dashes": True, "arrows": ""},
}


def render_graph(graph: nx.DiGraph, output_path: Path) -> None:
    """生成可直接离线打开的 HTML 文件。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    net = Network(
        height="850px",
        width="100%",
        directed=True,
        bgcolor="#FFFFFF",
        font_color="#243342",
        cdn_resources="in_line",
    )

    _configure_network(net)
    _add_nodes(net, graph)
    _add_edges(net, graph)

    html_text = net.generate_html()
    html_text = _inject_page_chrome(html_text, graph)
    output_path.write_text(html_text, encoding="utf-8")


def _configure_network(net: Network) -> None:
    """配置交互、布局和物理引擎参数。"""
    options = {
        "interaction": {
            "hover": True,
            "dragNodes": True,
            "dragView": True,
            "zoomView": True,
            "navigationButtons": True,
            "keyboard": True,
            "tooltipDelay": 120,
        },
        "physics": {
            "enabled": True,
            "solver": "barnesHut",
            "barnesHut": {
                "gravitationalConstant": -55000,
                "centralGravity": 0.18,
                "springLength": 150,
                "springConstant": 0.035,
                "damping": 0.55,
                "avoidOverlap": 0.18,
            },
            "stabilization": {
                "enabled": True,
                "iterations": 1200,
                "updateInterval": 50,
            },
        },
        "configure": {
            "enabled": True,
            "filter": ["physics"],
        },
        "nodes": {
            "borderWidth": 1,
            "borderWidthSelected": 3,
            "shape": "dot",
            "font": {"face": "Microsoft YaHei, PingFang SC, Arial", "strokeWidth": 0},
        },
        "edges": {
            "smooth": {"enabled": True, "type": "dynamic", "roundness": 0.35},
            "font": {
                "align": "middle",
                "size": 11,
                "face": "Microsoft YaHei, PingFang SC, Arial",
                "background": "rgba(255,255,255,0.72)",
            },
        },
    }
    net.set_options(json.dumps(options, ensure_ascii=False))


def _add_nodes(net: Network, graph: nx.DiGraph) -> None:
    """把 NetworkX 节点转换为 pyvis 节点。"""
    for node_id, attributes in graph.nodes(data=True):
        level = int(attributes.get("level", 3))
        module = str(attributes.get("module", "analysis"))
        color = _node_color(module, level)
        border_color = _module_primary_color(module)

        net.add_node(
            n_id=node_id,
            label=str(attributes.get("label", node_id)),
            title=_build_node_title(attributes),
            size=int(attributes.get("size", _size_by_level(level))),
            color={"background": color, "border": border_color, "highlight": "#FFFFFF"},
            font={"size": _font_size_by_level(level), "color": "#243342"},
            group=module,
            level=level,
            shape="dot",
        )


def _add_edges(net: Network, graph: nx.DiGraph) -> None:
    """把 NetworkX 边转换为 pyvis 边。"""
    for source, target, attributes in graph.edges(data=True):
        relation = str(attributes.get("relation", "包含"))
        relation_style = RELATION_STYLES.get(relation, RELATION_STYLES["包含"])
        color = str(attributes.get("color", relation_style["color"]))

        net.add_edge(
            source=source,
            to=target,
            label=relation,
            title=_build_edge_title(source, target, relation, graph),
            color=color,
            width=float(relation_style["width"]),
            dashes=bool(relation_style["dashes"]),
            arrows=relation_style["arrows"],
        )


def _build_node_title(attributes: Mapping[str, Any]) -> str:
    """构造 hover 提示，展示定义、特点和复杂度。"""
    label = html.escape(str(attributes.get("label", "")))
    title = html.escape(str(attributes.get("title", "")))
    definition = html.escape(str(attributes.get("definition", "")))
    features = html.escape(str(attributes.get("features", "")))
    time_complexity = html.escape(str(attributes.get("time_complexity", "")))
    space_complexity = html.escape(str(attributes.get("space_complexity", "")))

    parts = [f"<strong>{label}</strong>"]
    if title:
        parts.append(title)
    if definition:
        parts.append(f"定义：{definition}")
    if features:
        parts.append(f"特点：{features}")
    if time_complexity:
        parts.append(f"时间复杂度：{time_complexity}")
    if space_complexity:
        parts.append(f"空间复杂度：{space_complexity}")
    return "<br>".join(parts)


def _build_edge_title(source: str, target: str, relation: str, graph: nx.DiGraph) -> str:
    """构造边的 hover 提示。"""
    source_label = html.escape(str(graph.nodes[source].get("label", source)))
    target_label = html.escape(str(graph.nodes[target].get("label", target)))
    relation_text = html.escape(relation)
    return f"{source_label} --{relation_text}--> {target_label}"


def _node_color(module: str, level: int) -> str:
    """根据模块和层级选择节点颜色。"""
    style = MODULE_STYLES.get(module, MODULE_STYLES["analysis"])
    if level == 1:
        return style["primary"]
    if level == 2:
        return style["secondary"]
    return style["tertiary"]


def _module_primary_color(module: str) -> str:
    """获取模块主色，用作节点边框色。"""
    return MODULE_STYLES.get(module, MODULE_STYLES["analysis"])["primary"]


def _size_by_level(level: int) -> int:
    """根据层级推导节点尺寸。"""
    if level == 1:
        return 40
    if level == 2:
        return 25
    return 15


def _font_size_by_level(level: int) -> int:
    """根据层级推导节点文字尺寸。"""
    if level == 1:
        return 24
    if level == 2:
        return 17
    return 13


def _inject_page_chrome(html_text: str, graph: nx.DiGraph) -> str:
    """向 pyvis 页面注入标题、图例和页面样式。"""
    page_css = _build_page_css()
    header_html = _build_header_html(graph)

    if "</head>" in html_text:
        html_text = html_text.replace("</head>", f"{page_css}\n</head>", 1)

    if "<body>" in html_text:
        html_text = html_text.replace("<body>", f"<body>\n{header_html}", 1)
    elif "<body >" in html_text:
        html_text = html_text.replace("<body >", f"<body>\n{header_html}", 1)
    else:
        html_text = f"{header_html}\n{html_text}"

    return html_text


def _build_page_css() -> str:
    """生成页面级 CSS。"""
    return """
<style>
  body {
    margin: 0;
    background: #f6f8fb;
    color: #243342;
    font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
  }
  .kg-header {
    padding: 20px 28px 12px;
    background: #ffffff;
    border-bottom: 1px solid #dde5ee;
  }
  .kg-title {
    margin: 0 0 12px;
    font-size: 26px;
    line-height: 1.25;
    font-weight: 700;
  }
  .kg-meta {
    margin: 0 0 12px;
    color: #5d6d7e;
    font-size: 14px;
  }
  .kg-legend,
  .kg-relations {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 14px;
    align-items: center;
    margin-top: 8px;
  }
  .kg-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #2c3e50;
    white-space: nowrap;
  }
  .kg-dot,
  .kg-line {
    display: inline-block;
    flex: 0 0 auto;
  }
  .kg-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }
  .kg-line {
    width: 26px;
    height: 0;
    border-top: 3px solid currentColor;
  }
  #mynetwork {
    width: 100% !important;
    height: calc(100vh - 172px) !important;
    min-height: 640px;
    border: 0 !important;
    background: #ffffff;
  }
  .vis-configuration-wrapper {
    background: #ffffff;
    border-left: 1px solid #dde5ee;
  }
</style>
"""


def _build_header_html(graph: nx.DiGraph) -> str:
    """生成标题和图例 HTML。"""
    legend_items = "\n".join(
        f"""<span class="kg-chip"><span class="kg-dot" style="background:{style['primary']}"></span>{style['label']}</span>"""
        for style in MODULE_STYLES.values()
    )
    relation_items = "\n".join(
        f"""<span class="kg-chip" style="color:{style['color']}"><span class="kg-line"></span>{relation}</span>"""
        for relation, style in RELATION_STYLES.items()
    )
    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()
    return f"""
<header class="kg-header">
  <h1 class="kg-title">数据结构知识图谱 —— 北航计算机学院</h1>
  <p class="kg-meta">共 {node_count} 个节点、{edge_count} 条关系；支持拖拽、滚轮缩放、悬停查看定义和复杂度。</p>
  <div class="kg-legend">{legend_items}</div>
  <div class="kg-relations">{relation_items}</div>
</header>
"""
