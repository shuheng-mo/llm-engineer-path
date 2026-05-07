# 03_graph_rag — GraphRAG 实战

GraphRAG 是 Microsoft Research 开源的知识图谱增强 RAG 框架。本目录是基于其 CLI 的项目骨架，**不需要写 Python 代码**，关键在于 `settings.yaml` 配置 + 输入数据 + 索引/查询命令。

## 步骤总览（参考课程章节 三 / 4 ~ 5）

```bash
# 1. 安装 graphrag（在仓库根目录已经通过 uv pyproject 管理；如果想隔离可以在本目录下 uv venv）
uv pip install graphrag

# 2. 设置 API Key（PowerShell / bash 通用）
export QWEN_API_KEY="your-dashscope-key"

# 3. 初始化项目（会生成 settings.yaml + prompts/ 目录，建议在 graphrag-demo/ 下做）
graphrag init --root .

# 4. 把示例数据放到 input/ 下（已提供 input/sample.txt 给你练手）

# 5. 用本目录提供的 settings.yaml.example 覆盖默认 settings.yaml（用 Qwen 兼容模式）

# 6. 构建索引（最耗时）
graphrag index --root .

# 7. 查询
graphrag query --root . --method local  "马云创立了哪些公司？他与哪些人有合作关系？"
graphrag query --root . --method global "这些科技公司之间的主要竞争领域是什么？"
graphrag query --root . --method drift  "分析这些科技公司创始人的共同特点及其对公司发展的影响"
```

## 三种 search 方式适用场景

- **Local Search**：针对特定实体的问题（"X 创立了哪些公司？"），使用图局部邻域。
- **Global Search**：全局概览类问题（"这些公司主要竞争领域有哪些？"），使用社区报告。
- **DRIFT Search**：深入探索类问题（"分析他们的共同特点"），动态扩展。

## 故障排查

如果 index 卡在 `create_community_reports` 或部分 parquet 文件缺失：

```bash
rm -rf output cache
graphrag index --root . --verbose
grep -iE "community_reports|create_community_reports|error|exception" logs/*
```
