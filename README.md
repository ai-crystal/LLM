# 大模型技术全景

> 从 Transformer 到智能体时代的架构、训练与推理

**作者：Dr. Dezeming**　·　2026

**在线阅读**：[https://YOUR-NAME.github.io/llm-book/](https://YOUR-NAME.github.io/llm-book/)（[站点入口](index.html)）　|　**PDF 下载**：[分卷 PDF](#分卷)

<!-- 发布到 GitHub Pages 后，把上面的 YOUR-NAME 换成你的 GitHub 用户名 -->

语言模型在几年里从“会续写”变成了“会推理、会用工具、会干活”。这套书沿着一条连续的技术线索，把这条路上真正起作用的设计讲清楚：数据怎么筛，模型怎么长高长宽，注意力为什么这样改，专家网络如何稀疏，对齐怎样从偏好里学出行为，推理引擎又如何在显存与延迟之间做取舍。

每卷独立成书，有自己的前言、目录与构建脚本；跨卷引用只写“第 X 卷”，不写章号。公式配有白话解释，推导只保留帮助理解的部分，跳过不影响阅读。

## 全书结构

| 卷 | 书名 | 讲什么 | 状态 |
|---|---|---|---|
| V1 | 入门篇：大模型是什么 | 零公式，从一句话的续写下半截讲到一张账单 | 已成稿 |
| V2 | 基础篇：从预测下一个词到 Transformer | 语言模型、嵌入、RNN、注意力、Transformer、位置编码、参数账 | 已成稿 |
| V3 | 预训练篇：数据、词表与规模 | 语料与清洗、分词器、缩放定律、训练系统、稳定性 | 已成稿 |
| V4 | 架构改造篇：注意力、归一化与专家网络 | KV 缓存、MQA/GQA/MLA、FlashAttention、稀疏与 SSM、MoE、长上下文 | 已成稿 |
| V5 | 对齐篇：SFT 与强化学习 | 指令微调、奖励模型、PPO、DPO 家族、RLVR、测试时计算、评测与榜单 | 待写 |
| V6 | 推理与部署篇：引擎、压缩与投机解码 | prefill/decode、KV 管理、连续批处理、量化蒸馏、投机解码、容量规划 | 待写 |
| V7 | 应用篇：检索、工具与智能体 | RAG、检索评测、工具调用、智能体循环、长程任务 | 待写 |
| V8 | 多模态与生成篇：视觉、语音与扩散 | 视觉编码器、语音、扩散与统一建模 | 待写 |

## 目录

### 第一卷　入门篇：大模型是什么

- [前言](book/v1-intro/front.md)
- [第1章　一句话的下半截](book/v1-intro/chapters/ch01.md)
- [第2章　一次生成的全过程](book/v1-intro/chapters/ch02.md)
- [第3章　模型是怎么炼成的](book/v1-intro/chapters/ch03.md)
- [第4章　它会什么](book/v1-intro/chapters/ch04.md)
- [第5章　它不会什么](book/v1-intro/chapters/ch05.md)
- [第6章　一张账单：参数、显存、token 与价格](book/v1-intro/chapters/ch06.md)
- [第7章　三种用法：提示、微调、检索与智能体](book/v1-intro/chapters/ch07.md)
- [第8章　怎么判断一个模型好不好](book/v1-intro/chapters/ch08.md)
- [第9章　风险与边界：版权、隐私、安全、对齐](book/v1-intro/chapters/ch09.md)
- [第10章　这个系列怎么读：八卷地图与三条路线](book/v1-intro/chapters/ch10.md)

### 第二卷　基础篇：从预测下一个词到 Transformer

- [前言](book/v2-basics/front.md)
- [第1章　语言模型的来路：从计数到神经网络](book/v2-basics/chapters/ch01.md)
- [第2章　词与向量：嵌入到底是什么](book/v2-basics/chapters/ch02.md)
- [第3章　循环网络：把历史压进一个状态](book/v2-basics/chapters/ch03.md)
- [第4章　注意力：一次对症的修补](book/v2-basics/chapters/ch04.md)
- [第5章　注意力的计算：Q、K、V 与缩放](book/v2-basics/chapters/ch05.md)
- [第6章　Transformer 的一块砖：残差、归一化、前馈](book/v2-basics/chapters/ch06.md)
- [第7章　多头与并行：为什么能一次算完](book/v2-basics/chapters/ch07.md)
- [第8章　位置编码：从正弦到旋转](book/v2-basics/chapters/ch08.md)
- [第9章　训练目标与损失：它到底在优化什么](book/v2-basics/chapters/ch09.md)
- [第10章　一个迷你 Transformer 的完整前向](book/v2-basics/chapters/ch10.md)
- [第11章　参数量、计算量与显存：一张账本](book/v2-basics/chapters/ch11.md)

### 第三卷　预训练篇：数据、词表与规模

- [前言](book/v3-pretrain/front.md)
- [第1章　预训练到底在学什么](book/v3-pretrain/chapters/ch01.md)
- [第2章　数据从哪里来：Common Crawl 与开源语料](book/v3-pretrain/chapters/ch02.md)
- [第3章　清洗：抽取、语言识别、规则过滤](book/v3-pretrain/chapters/ch03.md)
- [第4章　去重与去污染](book/v3-pretrain/chapters/ch04.md)
- [第5章　质量与配比：分类器、DoReMi、退火](book/v3-pretrain/chapters/ch05.md)
- [第6章　分词器：BPE、unigram、SentencePiece](book/v3-pretrain/chapters/ch06.md)
- [第7章　词表大小的账](book/v3-pretrain/chapters/ch07.md)
- [第8章　缩放定律：Kaplan、Chinchilla、推理最优](book/v3-pretrain/chapters/ch08.md)
- [第9章　训练目标：因果语言建模与其他目标](book/v3-pretrain/chapters/ch09.md)
- [第10章　训练系统：并行、显存、通信](book/v3-pretrain/chapters/ch10.md)
- [第11章　稳定性：损失尖峰、回滚、检查点](book/v3-pretrain/chapters/ch11.md)
- [第12章　从零训一个小模型：一份可执行的配方](book/v3-pretrain/chapters/ch12.md)

### 第四卷　架构改造篇：注意力、归一化与专家网络

- [前言](book/v4-architecture/front.md)
- [第1章　KV 缓存与注意力的成本](book/v4-architecture/chapters/ch01.md)
- [第2章　MQA、GQA、MLA：把缓存压下来](book/v4-architecture/chapters/ch02.md)
- [第3章　FlashAttention：省的是带宽](book/v4-architecture/chapters/ch03.md)
- [第4章　稀疏、滑窗、线性注意力与 SSM](book/v4-architecture/chapters/ch04.md)
- [第5章　归一化、残差与深层稳定性](book/v4-architecture/chapters/ch05.md)
- [第6章　混合专家：路由、负载均衡、细粒度](book/v4-architecture/chapters/ch06.md)
- [第7章　长上下文：位置、注意力、数据、评测](book/v4-architecture/chapters/ch07.md)
- [第8章　Attention Residuals：残差流上的路由](book/v4-architecture/chapters/ch08.md)
- [第9章　架构取舍：什么场景选什么](book/v4-architecture/chapters/ch09.md)

第五至第八卷尚未成稿，目录规划见 `_private/notes/series-plan.md`（不进仓库）。

### 附录

- [附录 A　关键论文一览](book/appendix/a-papers.md)
- [附录 B　术语表](book/appendix/b-glossary.md)

## 分卷

| 卷 | PDF | 页数 |
|---|---|---|
| 入门篇：大模型是什么 | [output/v1-intro.pdf](output/v1-intro.pdf) | 93 |
| 基础篇：从预测下一个词到 Transformer | [output/v2-basics.pdf](output/v2-basics.pdf) | 153 |
| 预训练篇：数据、词表与规模 | [output/v3-pretrain.pdf](output/v3-pretrain.pdf) | 147 |
| 架构改造篇：注意力、归一化与专家网络 | [output/v4-architecture.pdf](output/v4-architecture.pdf) | 113 |

每卷单独编译：双击 `build-v1-intro.bat` … `build-v4-architecture.bat`，或 `python book/build/build.py --vol v3-pretrain`；不带 `--vol` 则构建全部已成稿的卷。

## 许可

本书文字与插图采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 许可，转载请注明作者与出处，不得用于商业用途。书中引用的论文版权归原作者所有。
