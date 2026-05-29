# 数据结构知识图谱

这是一个以北航《数据结构》课程为背景的离线知识图谱可视化程序。程序读取 `data/knowledge.json`，使用 `networkx` 构建图结构，使用 `pyvis` 输出单个可直接打开的 HTML 文件。

## 环境

我已创建空 conda 环境：

```bash
conda activate /home/michael/Project/AI/.conda-env
```

该环境未安装 Python、pyvis、networkx 或其他包。依赖安装请你执行，例如：

```bash
conda install -p /home/michael/Project/AI/.conda-env python=3.10 pip
/home/michael/Project/AI/.conda-env/bin/python -m pip install -r project/requirements.txt
```

如果你想用已有 Python 环境，也可以直接安装：

```bash
python -m pip install -r project/requirements.txt
```

## 运行

```bash
cd /home/michael/Project/AI/project
python main.py
```

生成结果：

- `output/knowledge_graph.html`
- `output/stats.txt`

HTML 文件不依赖 Web 服务器，可直接用浏览器打开。
