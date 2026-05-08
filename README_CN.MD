# LightAlloy-HeatTreatment-AI-Radar

[![Project Type](https://img.shields.io/badge/project-research%20radar-blue)](#)
[![Focus](https://img.shields.io/badge/focus-AI%20for%20Manufacturing-important)](#)
[![Scope](https://img.shields.io/badge/scope-processes%2C%20control%2C%20digital%20twin-success)](#)
[![Status](https://img.shields.io/badge/status-active%20development-orange)](#)

> 面向铝合金与轻合金热处理的 AI/ML 研究雷达与结构化知识系统。

[English](README.md)

## 项目定位

`LightAlloy-HeatTreatment-AI-Radar` 是一个持续演化的研究情报系统，用于跟踪、整理和复用轻合金热处理领域中的 AI/ML 研究知识。

它不是一个简单的论文列表，也不是 PDF 存储仓库。这个项目的长期目标，是把分散在论文中的研究信息转化为可检索、可建模、可优化的结构化知识。

```text
论文 -> 结构化知识 -> 建模 -> 优化
```

## 为什么做这个项目

铝合金与轻合金热处理在工业中非常重要，数据丰富，但知识结构并不统一，很多工艺设计仍然依赖经验规则。与此同时，AI/ML 相关研究分散在材料、制造、建模和控制等不同方向中，缺少一个统一的整理框架。

本项目希望连接以下内容：

- 热处理工艺参数
- 合金体系与微观组织演化
- 力学性能与服役指标
- 机器学习与物理信息模型
- 工艺优化与数字孪生流程

## 系统模块

| 模块 | 作用 |
| --- | --- |
| 数据管线 | 收集论文、提取元数据、筛选相关性，并保存结构化记录。 |
| 知识结构化 | 将论文拆解为工艺、材料、性能、方法和数据集等信息。 |
| 研究输出 | 生成研究摘要、参考笔记、综述素材和结构化数据集。 |
| 建模基础 | 为机器学习、代理模型和物理信息学习准备数据与基线。 |
| 优化层 | 支持工艺优化、不确定性预测，以及未来闭环控制。 |

## 知识结构

每篇论文尽量围绕以下维度整理：

- **Process 工艺**：固溶、时效、淬火、变形、热机械处理路线
- **Material 材料**：合金体系、成分、初始状态、加工历史
- **Target 目标**：硬度、强度、延伸率、微观组织、析出行为
- **Method 方法**：机器学习模型、物理信息模型、代理模型、优化算法
- **Data 数据**：数据来源、输入特征、目标变量、评价指标

## 仓库结构

```text
LightAlloy-HeatTreatment-AI-Radar/
  data/
    raw_papers.json
    screened_papers.json
    curated_papers.json

  refs/
    aluminium_alloys.md
    heat_treatment_process.md
    ml_models.md
    physics_informed_ml.md

  scripts/
    paper_scanner.py
    paper_screener.py
    tag_assigner.py
    summary_generator.py

  outputs/
    daily_digest.md
    weekly_summary.md

  review/
    outline.md
    sections/

  README.md
  README_CN.MD
```

## 核心研究问题

1. 热处理机器学习目前已经解决了哪些问题？
2. 这个领域主要的数据瓶颈是什么？
3. 物理信息机器学习在哪些场景下优于纯数据驱动模型？
4. 如何建立可靠的热处理工艺-性能预测代理模型？
5. 如何引入不确定性预测？
6. 如何进一步走向工艺优化和闭环控制？

## 路线图

- 建立论文收集与筛选流程。
- 建立元数据与标签规范。
- 生成每日或每周研究简报。
- 沉淀综述写作素材和参考笔记。
- 构建面向机器学习的工艺-性能数据集。
- 探索物理信息机器学习与代理建模。
- 逐步走向基于强化学习的工艺优化和数字孪生集成。

## 当前状态

项目正在持续开发中，计划进行每日或每周研究更新。

## 作者

Xian
