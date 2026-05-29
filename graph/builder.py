"""从 JSON 数据构建 NetworkX 知识图谱。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Set

import networkx as nx


REQUIRED_NODE_FIELDS = {"id", "label", "level", "module", "title"}
REQUIRED_EDGE_FIELDS = {"from", "to", "relation"}
SUPPORTED_RELATIONS = {"包含", "演化自", "实现方式", "应用于", "复杂度为", "比较"}


def load_knowledge_data(json_path: Path) -> Dict[str, Any]:
    """读取知识图谱 JSON 文件。"""
    if not json_path.exists():
        raise FileNotFoundError(f"找不到知识数据文件：{json_path}")

    with json_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    validate_knowledge_data(data)
    return data


def validate_knowledge_data(data: Mapping[str, Any]) -> None:
    """校验 JSON 顶层结构、节点字段、边字段和引用关系。"""
    if not isinstance(data, Mapping):
        raise ValueError("knowledge.json 顶层必须是 JSON 对象。")

    nodes = data.get("nodes")
    edges = data.get("edges")
    if not isinstance(nodes, list):
        raise ValueError("knowledge.json 必须包含 nodes 数组。")
    if not isinstance(edges, list):
        raise ValueError("knowledge.json 必须包含 edges 数组。")

    node_ids = _validate_nodes(nodes)
    _validate_edges(edges, node_ids)


def _validate_nodes(nodes: Iterable[Mapping[str, Any]]) -> Set[str]:
    """校验节点字段，并返回节点 ID 集合。"""
    node_ids: Set[str] = set()
    labels: Set[str] = set()

    for index, node in enumerate(nodes, start=1):
        if not isinstance(node, Mapping):
            raise ValueError(f"第 {index} 个节点必须是 JSON 对象。")

        missing_fields = REQUIRED_NODE_FIELDS - set(node)
        if missing_fields:
            missing_text = "、".join(sorted(missing_fields))
            raise ValueError(f"节点 {index} 缺少字段：{missing_text}")

        node_id = str(node["id"])
        label = str(node["label"])
        if node_id in node_ids:
            raise ValueError(f"节点 ID 重复：{node_id}")
        if label in labels:
            raise ValueError(f"节点 label 重复，建议保持唯一以便检索：{label}")

        level = int(node["level"])
        if level not in {1, 2, 3}:
            raise ValueError(f"节点 {node_id} 的 level 必须是 1、2 或 3。")

        node_ids.add(node_id)
        labels.add(label)

    return node_ids


def _validate_edges(edges: Iterable[Mapping[str, Any]], node_ids: Set[str]) -> None:
    """校验边字段、关系类型和端点引用。"""
    seen_edges: Set[tuple[str, str, str]] = set()

    for index, edge in enumerate(edges, start=1):
        if not isinstance(edge, Mapping):
            raise ValueError(f"第 {index} 条边必须是 JSON 对象。")

        missing_fields = REQUIRED_EDGE_FIELDS - set(edge)
        if missing_fields:
            missing_text = "、".join(sorted(missing_fields))
            raise ValueError(f"边 {index} 缺少字段：{missing_text}")

        source = str(edge["from"])
        target = str(edge["to"])
        relation = str(edge["relation"])

        if source not in node_ids:
            raise ValueError(f"边 {index} 的 from 引用了不存在的节点：{source}")
        if target not in node_ids:
            raise ValueError(f"边 {index} 的 to 引用了不存在的节点：{target}")
        if relation not in SUPPORTED_RELATIONS:
            raise ValueError(f"边 {index} 使用了不支持的关系类型：{relation}")

        edge_key = (source, target, relation)
        if edge_key in seen_edges:
            raise ValueError(f"重复边：{source} -> {target} ({relation})")
        seen_edges.add(edge_key)


def build_graph(data: Mapping[str, Any]) -> nx.MultiDiGraph:
    """根据 JSON 数据构建有向图。"""
    graph = nx.MultiDiGraph(name="数据结构知识图谱")

    for node in data["nodes"]:
        graph.add_node(str(node["id"]), **_copy_node_attributes(node))

    for edge in data["edges"]:
        source = str(edge["from"])
        target = str(edge["to"])
        attributes = _copy_edge_attributes(edge)
        graph.add_edge(source, target, **attributes)

    return graph


def _copy_node_attributes(node: Mapping[str, Any]) -> Dict[str, Any]:
    """复制节点属性，避免后续修改影响原始 JSON 数据。"""
    attributes: Dict[str, Any] = dict(node)
    attributes["id"] = str(attributes["id"])
    attributes["label"] = str(attributes["label"])
    attributes["module"] = str(attributes["module"])
    attributes["level"] = int(attributes["level"])
    attributes["size"] = int(attributes.get("size", _default_size(attributes["level"])))
    return attributes


def _copy_edge_attributes(edge: Mapping[str, Any]) -> Dict[str, Any]:
    """复制边属性，并保留 from/to 以便调试和导出。"""
    attributes: MutableMapping[str, Any] = dict(edge)
    attributes["from"] = str(attributes["from"])
    attributes["to"] = str(attributes["to"])
    attributes["relation"] = str(attributes["relation"])
    return dict(attributes)


def _default_size(level: int) -> int:
    """根据节点层级推导默认尺寸。"""
    if level == 1:
        return 40
    if level == 2:
        return 25
    return 15
