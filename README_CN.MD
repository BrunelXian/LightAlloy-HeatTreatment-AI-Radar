# LightAlloy-HeatTreatment-AI-Radar

[![Project Type](https://img.shields.io/badge/project-research%20radar-blue)](#)
[![Focus](https://img.shields.io/badge/focus-AI%20for%20Manufacturing-important)](#)
[![Scope](https://img.shields.io/badge/scope-processes%2C%20control%2C%20digital%20twin-success)](#)
[![Status](https://img.shields.io/badge/status-active%20development-orange)](#)

> 面向铝合金与轻合金热处理 AI/ML 研究的结构化文献雷达。

[English](README.md)

## 项目定位

`LightAlloy-HeatTreatment-AI-Radar` 是一个可持续维护的文献雷达系统，用于跟踪、筛选、人工整理和复用铝合金/轻合金热处理领域中的 AI/ML 研究知识。

它不是静态论文列表，也不是 PDF 仓库。目标是把分散在论文中的信息转化为结构化、可筛选、可人工复核、可用于综述写作的研究资产。

```text
论文 -> 结构化知识 -> 人工筛选 -> 综述素材
```

## 当前阶段

当前仓库已经支持 Phase 1 工作流：

- 以 arXiv 作为每日发现的主要来源。
- 将论文元数据规范化到稳定 schema。
- 按 DOI 优先、规范化标题其次进行去重。
- 使用确定性的关键词规则进行机器筛选。
- 自动分配材料、工艺、性能、模型方法和研究定位标签。
- 生成 daily digest、query quality report 和 source quality report。
- 导出候选论文供人工筛选。
- 将人工决策持久化到 curated/rejected JSON 资产。
- 生成 paper cards 和 core reading queue，用于综述阅读和面试准备。
- 使用 GitHub Actions 每日自动扫描，并把运行产物上传为 artifact。

Crossref 支持已经保留在代码中，但默认不参与每日发现，因为当前作为发现源仍然偏噪。后续可以重新用于 DOI、期刊/会议、出版社等元数据补全，或作为手动诊断工具。

## 快速开始

```bash
pip install -r requirements.txt
python scripts/run_pipeline.py
python scripts/curation_export.py --limit 20
python scripts/curation_status.py
python scripts/generate_paper_cards.py
```

## 主要输出

运行时输出，默认不提交到 git：

- `data/raw/raw_papers.json`
- `data/processed/normalized_papers.json`
- `data/processed/screened_papers.json`
- `outputs/daily_digest.md`
- `outputs/query_quality_report.md`
- `outputs/source_quality_report.md`
- `outputs/curation_candidates.md`
- `outputs/curation_status.md`

长期保存的研究资产，会提交到 git：

- `data/curated/curated_papers.json`
- `data/curated/rejected_papers.json`
- `review/core_reading_queue.md`
- `review/paper_cards/*.md`

## 人工筛选流程

机器筛选只是第一步，最终是否进入研究资产由人工决定。

```bash
python scripts/run_pipeline.py
python scripts/curation_export.py --limit 20
python scripts/curation_apply.py --paper-id PAPER_ID --status core --notes "Must-read paper for heat-treatment ML review."
python scripts/curation_apply.py --paper-id PAPER_ID --status curated --notes "Relevant candidate for process-property modelling."
python scripts/curation_apply.py --paper-id PAPER_ID --status rejected --notes "False positive: not focused on aluminium/light-alloy heat treatment."
python scripts/curation_status.py
```

- `screening_decision` 是机器筛选结果。
- `manual_status` 是人工决策层。
- `curated_papers.json` 是人工复核后的文献库。
- `rejected_papers.json` 用于避免反复审阅低价值误报。

## Paper Cards 与核心阅读队列

已人工筛选的论文可以转换为可复用的阅读笔记：

```bash
python scripts/generate_paper_cards.py
```

该命令会生成：

- `review/core_reading_queue.md`
- `review/paper_cards/<paper_id>.md`

每张 paper card 包含确定性的论文元数据、标签、机器筛选信息、摘要、综述位置建议，以及稳定的 `Human Reading Notes` 人工阅读笔记区。

重新生成 paper cards 时，已有的人工阅读笔记会被保留。

## 每日自动化

GitHub Actions 会每日运行文献雷达扫描，也支持手动触发。

工作流会：

- 安装依赖
- 运行 pipeline
- 导出 curation candidates
- 生成 curation status
- 运行测试
- 将运行时输出上传为 `literature-radar-output` artifact

生成的 raw、processed 和 outputs 文件不会自动提交。人工筛选仍然保持手动完成。

## 数据版本策略

以下运行时文件默认忽略：

- `data/raw/*.json`
- `data/processed/*.json`
- `data/checkpoints/*.json`
- `outputs/*.md`

人工 curated JSON 和 review paper cards 是长期保存的研究资产。

## 仓库结构

```text
LightAlloy-HeatTreatment-AI-Radar/
  config/
  data/
    raw/
    processed/
    curated/
    checkpoints/
  outputs/
  review/
    core_reading_queue.md
    paper_cards/
  scripts/
  tests/
  .github/workflows/
  README.md
  README_CN.MD
```

## 核心研究问题

1. 热处理机器学习目前已经解决了哪些问题？
2. 这个领域主要的数据瓶颈是什么？
3. 物理信息机器学习在哪些场景下优于纯数据驱动模型？
4. 如何建立可靠的工艺-性能预测代理模型？
5. 如何引入不确定性预测？
6. 如何进一步走向工艺优化、闭环控制和数字孪生？

## 作者

Xian
