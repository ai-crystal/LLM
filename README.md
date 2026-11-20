# 大模型技术全景

> 从 Transformer 到智能体时代的架构、训练与推理

**作者：Dr. Dezeming**　·　2026

**在线阅读**：[https://YOUR-NAME.github.io/llm-book/](https://YOUR-NAME.github.io/llm-book/)（[站点入口](index.html)）

<!-- 发布到 GitHub Pages 后，把上面的 YOUR-NAME 换成你的 GitHub 用户名 -->

语言模型在几年里从“会续写”变成了“会推理、会用工具、会干活”。这套书沿着一条连续的技术线索，把这条路上真正起作用的设计讲清楚：数据怎么筛，模型怎么长高长宽，注意力为什么这样改，专家网络如何稀疏，对齐怎样从偏好里学出行为，推理引擎又如何在显存与延迟之间做取舍。

每册独立成书，有自己的前言、目录与 PDF；章内图片用相对路径，在 GitHub 网页端点开 Markdown 就能看到。

## 各册

| 册 | 讲什么 | 章数 | 页数 | 在线阅读 | PDF |
|---|---|---|---|---|---|
| 入门篇：大模型是什么 | 零公式，从一句话的续写下半截讲到一张账单 | 10 | 91 | [读](books/v1-intro/README.md) | [下](output/v1-intro.pdf) |
| 基础篇：从预测下一个词到 Transformer | 语言模型、嵌入、RNN、注意力、Transformer、位置编码、参数账 | 11 | 157 | [读](books/v2-basics/README.md) | [下](output/v2-basics.pdf) |
| 预训练篇：数据、词表与规模 | 语料与清洗、分词器、缩放定律、训练系统、稳定性 | 12 | 147 | [读](books/v3-pretrain/README.md) | [下](output/v3-pretrain.pdf) |
| 架构改造篇：注意力、归一化与专家网络 | KV 缓存、MQA/GQA/MLA、FlashAttention、稀疏与 SSM、MoE、长上下文 | 9 | 113 | [读](books/v4-architecture/README.md) | [下](output/v4-architecture.pdf) |
| 对齐篇：从 SFT 到 Agent 后训练 | 指令微调、奖励模型、PPO、DPO 家族、可验证奖励、过程奖励与搜索、Agent 后训练 | 12 | 138 | [读](books/v5-alignment/README.md) | [下](output/v5-alignment.pdf) |
| 安全与攻破篇：红队、越狱、投毒与防御 | 威胁模型、越狱两类、提示注入、微调攻破、数据投毒、窃取与隐私、防御栈、评测 | 10 | 106 | [读](books/v6-safety/README.md) | [下](output/v6-safety.pdf) |
| 推理与部署篇：引擎、压缩与投机解码 | 两个阶段、KV 缓存、批处理、前缀复用、量化、剪枝蒸馏、投机解码、容量规划 | 10 | 125 | [读](books/v7-inference/README.md) | [下](output/v7-inference.pdf) |
| 应用与 Agent 系统篇：检索、工具与智能体 | 切块与索引、混合检索与重排、上下文组装、检索评测、工具调用、Agent 循环、记忆 | 10 | 124 | [读](books/v8-apps/README.md) | [下](output/v8-apps.pdf) |
| 多模态与生成篇：视觉、语音与扩散 | 视觉 token、图文对齐、语音识别与合成、视频、扩散与流匹配、统一模型 | 9 | 108 | [读](books/v9-multimodal/README.md) | [下](output/v9-multimodal.pdf) |
| 训练系统篇：并行、显存与通信 | 四种并行、ZeRO、流水线气泡、显存六块账、通信重叠、低精度、故障恢复 | 8 | 110 | [读](books/v10-systems/README.md) | [下](output/v10-systems.pdf) |
| 可解释性与评测篇：看得懂与测得准 | 探针与方向、稀疏自编码器、电路分析、logit lens、污染与判定模型、私有评测 | 8 | 106 | [读](books/v11-interpret/README.md) | [下](output/v11-interpret.pdf) |

## 目录

### 入门篇：大模型是什么

- [前言](books/v1-intro/front/preface.md)
- [第1章　一句话的下半截](books/v1-intro/chapters/ch01.md)
- [第2章　一次生成的全过程](books/v1-intro/chapters/ch02.md)
- [第3章　模型是怎么炼成的](books/v1-intro/chapters/ch03.md)
- [第4章　它会什么](books/v1-intro/chapters/ch04.md)
- [第5章　它不会什么](books/v1-intro/chapters/ch05.md)
- [第6章　一张账单：参数、显存、token 与价格](books/v1-intro/chapters/ch06.md)
- [第7章　三种用法：提示、微调、检索与智能体](books/v1-intro/chapters/ch07.md)
- [第8章　怎么判断一个模型好不好](books/v1-intro/chapters/ch08.md)
- [第9章　风险与边界：版权、隐私、安全、对齐](books/v1-intro/chapters/ch09.md)
- [第10章　这个系列怎么读：十一个方向与三条路线](books/v1-intro/chapters/ch10.md)

### 基础篇：从预测下一个词到 Transformer

- [前言](books/v2-basics/front/preface.md)
- [第1章　语言模型的来路：从计数到神经网络](books/v2-basics/chapters/ch01.md)
- [第2章　词与向量：嵌入到底是什么](books/v2-basics/chapters/ch02.md)
- [第3章　循环网络：把历史压进一个状态](books/v2-basics/chapters/ch03.md)
- [第4章　注意力：一次对症的修补](books/v2-basics/chapters/ch04.md)
- [第5章　注意力的计算：Q、K、V 与缩放](books/v2-basics/chapters/ch05.md)
- [第6章　Transformer 的一块砖：残差、归一化、前馈](books/v2-basics/chapters/ch06.md)
- [第7章　多头与并行：为什么能一次算完](books/v2-basics/chapters/ch07.md)
- [第8章　位置编码：从正弦到旋转](books/v2-basics/chapters/ch08.md)
- [第9章　训练目标与损失：它到底在优化什么](books/v2-basics/chapters/ch09.md)
- [第10章　一个迷你 Transformer 的完整前向](books/v2-basics/chapters/ch10.md)
- [第11章　参数量、计算量与显存：一张账本](books/v2-basics/chapters/ch11.md)

### 预训练篇：数据、词表与规模

- [前言](books/v3-pretrain/front/preface.md)
- [第1章　预训练到底在学什么](books/v3-pretrain/chapters/ch01.md)
- [第2章　数据从哪里来：Common Crawl 与开源语料](books/v3-pretrain/chapters/ch02.md)
- [第3章　清洗：抽取、语言识别、规则过滤](books/v3-pretrain/chapters/ch03.md)
- [第4章　去重与去污染](books/v3-pretrain/chapters/ch04.md)
- [第5章　质量与配比：分类器、DoReMi、退火](books/v3-pretrain/chapters/ch05.md)
- [第6章　分词器：BPE、unigram、SentencePiece](books/v3-pretrain/chapters/ch06.md)
- [第7章　词表大小的账](books/v3-pretrain/chapters/ch07.md)
- [第8章　缩放定律：Kaplan、Chinchilla、推理最优](books/v3-pretrain/chapters/ch08.md)
- [第9章　训练目标：因果语言建模与其他目标](books/v3-pretrain/chapters/ch09.md)
- [第10章　训练系统：并行、显存、通信](books/v3-pretrain/chapters/ch10.md)
- [第11章　稳定性：损失尖峰、回滚、检查点](books/v3-pretrain/chapters/ch11.md)
- [第12章　从零训一个小模型：一份可执行的配方](books/v3-pretrain/chapters/ch12.md)

### 架构改造篇：注意力、归一化与专家网络

- [前言](books/v4-architecture/front/preface.md)
- [第1章　KV 缓存与注意力的成本](books/v4-architecture/chapters/ch01.md)
- [第2章　MQA、GQA、MLA：把缓存压下来](books/v4-architecture/chapters/ch02.md)
- [第3章　FlashAttention：省的是带宽](books/v4-architecture/chapters/ch03.md)
- [第4章　稀疏、滑窗、线性注意力与 SSM](books/v4-architecture/chapters/ch04.md)
- [第5章　归一化、残差与深层稳定性](books/v4-architecture/chapters/ch05.md)
- [第6章　混合专家：路由、负载均衡、细粒度](books/v4-architecture/chapters/ch06.md)
- [第7章　长上下文：位置、注意力、数据、评测](books/v4-architecture/chapters/ch07.md)
- [第8章　Attention Residuals：残差流上的路由](books/v4-architecture/chapters/ch08.md)
- [第9章　架构取舍：什么场景选什么](books/v4-architecture/chapters/ch09.md)

### 对齐篇：从 SFT 到 Agent 后训练

- [前言](books/v5-alignment/front/preface.md)
- [第1章　对齐要解决什么](books/v5-alignment/chapters/ch01.md)
- [第2章　指令微调：用示范教它换个任务](books/v5-alignment/chapters/ch02.md)
- [第3章　SFT 的副作用：变听话的代价](books/v5-alignment/chapters/ch03.md)
- [第4章　偏好数据与奖励模型：把“更好”变成一个分数](books/v5-alignment/chapters/ch04.md)
- [第5章　PPO：用不可微的分数去改模型](books/v5-alignment/chapters/ch05.md)
- [第6章　DPO：把强化学习化简成监督学习](books/v5-alignment/chapters/ch06.md)
- [第7章　可验证奖励：当对错可以被算出来](books/v5-alignment/chapters/ch07.md)
- [第8章　过程奖励与搜索：把奖励拆细](books/v5-alignment/chapters/ch08.md)
- [第9章　蒸馏式对齐：让模型评判模型](books/v5-alignment/chapters/ch09.md)
- [第10章　Agent 后训练（一）：多步任务长什么样](books/v5-alignment/chapters/ch10.md)
- [第11章　Agent 后训练（二）：在环境里练](books/v5-alignment/chapters/ch11.md)
- [第12章　评测、对齐税与边界](books/v5-alignment/chapters/ch12.md)

### 安全与攻破篇：红队、越狱、投毒与防御

- [前言](books/v6-safety/front/preface.md)
- [第1章　威胁模型：先想清楚谁会怎么打](books/v6-safety/chapters/ch01.md)
- [第2章　越狱（一）：靠人写出来的绕过](books/v6-safety/chapters/ch02.md)
- [第3章　越狱（二）：让算法去找](books/v6-safety/chapters/ch03.md)
- [第4章　提示注入：把指令藏在数据里](books/v6-safety/chapters/ch04.md)
- [第5章　微调攻破：几十条数据拆掉安全对齐](books/v6-safety/chapters/ch05.md)
- [第6章　数据投毒：在训练集里埋一颗雷](books/v6-safety/chapters/ch06.md)
- [第7章　模型窃取与隐私：把学到的东西挖出来](books/v6-safety/chapters/ch07.md)
- [第8章　防御栈：没有单层是可靠的](books/v6-safety/chapters/ch08.md)
- [第9章　安全评测与治理：怎么知道它到底有多难破](books/v6-safety/chapters/ch09.md)
- [第10章　新攻击面：多模态、语音与代码 Agent](books/v6-safety/chapters/ch10.md)

### 多模态与生成篇：视觉、语音与扩散

- [前言](books/v9-multimodal/front/preface.md)
- [第1章　图像怎么变成 token](books/v9-multimodal/chapters/ch01.md)
- [第2章　视觉编码器与图文对齐](books/v9-multimodal/chapters/ch02.md)
- [第3章　多模态模型怎么训](books/v9-multimodal/chapters/ch03.md)
- [第4章　语音识别：从波形到文字](books/v9-multimodal/chapters/ch04.md)
- [第5章　语音合成：让模型说话](books/v9-multimodal/chapters/ch05.md)
- [第6章　视频：把图像的成本乘以时间](books/v9-multimodal/chapters/ch06.md)
- [第7章　扩散模型：从噪声里画出图](books/v9-multimodal/chapters/ch07.md)
- [第8章　流匹配与生成式 Transformer](books/v9-multimodal/chapters/ch08.md)
- [第9章　理解与生成：要不要放进一个模型](books/v9-multimodal/chapters/ch09.md)

### 训练系统篇：并行、显存与通信

- [前言](books/v10-systems/front/preface.md)
- [第1章　并行的四种切法](books/v10-systems/chapters/ch01.md)
- [第2章　数据并行与 ZeRO](books/v10-systems/chapters/ch02.md)
- [第3章　张量并行与序列并行](books/v10-systems/chapters/ch03.md)
- [第4章　流水线并行与专家并行](books/v10-systems/chapters/ch04.md)
- [第5章　显存账：权重、状态与激活](books/v10-systems/chapters/ch05.md)
- [第6章　通信与重叠](books/v10-systems/chapters/ch06.md)
- [第7章　精度：从 FP32 到 FP8](books/v10-systems/chapters/ch07.md)
- [第8章　故障、检查点与弹性](books/v10-systems/chapters/ch08.md)

### 可解释性与评测篇：看得懂与测得准

- [前言](books/v11-interpret/front/preface.md)
- [第1章　看不懂的时候，能做什么](books/v11-interpret/chapters/ch01.md)
- [第2章　探针与表示方向](books/v11-interpret/chapters/ch02.md)
- [第3章　稀疏自编码器：把激活拆开](books/v11-interpret/chapters/ch03.md)
- [第4章　注意力头与电路](books/v11-interpret/chapters/ch04.md)
- [第5章　归因与 logit lens](books/v11-interpret/chapters/ch05.md)
- [第6章　评测：污染与判定模型](books/v11-interpret/chapters/ch06.md)
- [第7章　竞技场、私有评测与线上实验](books/v11-interpret/chapters/ch07.md)
- [第8章　可解释性在安全与对齐里的用处](books/v11-interpret/chapters/ch08.md)

### 附录

- [附录 A　关键论文一览](books/appendix/a-papers.md)
- [附录 B　术语表](books/appendix/b-glossary.md)

## 构建

```bat
build.bat                 构建全部册
build.bat v2-basics       构建基础篇
build.bat check           核对目录、图片与路径
build.bat figures         重画插图
build.bat site            重新生成侧栏与各册首页
```

输出在 `output/`。每册的正文在 `books/<册名>/chapters/`，插图在 `books/<册名>/images/`，绘图脚本在 `books/code/`。

## 许可

本书文字与插图采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 许可，转载请注明作者与出处，不得用于商业用途。书中引用的论文版权归原作者所有。
