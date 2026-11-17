# 大模型技术全景

> 从 Transformer 到智能体时代的架构、训练与推理

**作者：Dr. Dezeming**　·　2026

**在线阅读**：[https://YOUR-NAME.github.io/llm-book/](https://YOUR-NAME.github.io/llm-book/)（[站点入口](index.html)）　|　**PDF 下载**：[output/llm-book.pdf](output/llm-book.pdf)

<!-- 发布到 GitHub Pages 后，把上面的 YOUR-NAME 换成你的 GitHub 用户名 -->

语言模型在几年里从“会续写”变成了“会推理、会用工具、会干活”。这本书沿着一条连续的技术线索，把这条路上真正起作用的设计讲清楚：数据怎么筛，模型怎么长高长宽，注意力为什么这样改，专家网络如何稀疏，对齐怎样从偏好里学出行为，推理引擎又如何在显存与延迟之间做取舍。

全书由动机出发，逐层展开到当前最先进的做法。每一处改进都放回它要解决的问题里去看，既解释为什么有效，也说明代价在哪里。公式配有白话解释，推导只保留帮助理解的部分，跳过不影响阅读。

## 全书结构

- **第一部　语言的概率起源**：从计数到预测下一个词、Transformer 的结构与代价、缩放定律
- **第二部　预训练**：数据、分词、位置编码、注意力改造、训练稳定性、混合专家、训练系统
- **第三部　对齐与评测**：指令微调、RLHF、DPO、可验证奖励、评测方法与榜单
- **第四部　能力扩展**：测试时计算、代码与工具、多模态、扩散模型、压缩、长上下文
- **第五部　系统与智能体**：推理引擎、服务成本、检索与记忆、智能体
- **第六部　正在发生的改变**：Attention Residuals、投机解码的第二代

## 目录

### 第一部　语言的概率起源

- [第1章　从计数到预测下一个词](book/chapters/ch01.md)
- [第2章　结构没变，代价变了](book/chapters/ch02.md)
- [第3章　规模为什么有效：缩放定律与预算](book/chapters/ch03.md)

### 第二部　预训练：把语料压进参数

- [第4章　数据：从网页到训练语料](book/chapters/ch04.md)
- [第5章　分词器：文本与数字的关口](book/chapters/ch05.md)
- [第6章　位置编码：从绝对到旋转](book/chapters/ch06.md)
- [第7章　注意力的效率改造](book/chapters/ch07.md)
- [第8章　深层网络的稳定性](book/chapters/ch08.md)
- [第9章　混合专家：用稀疏性换容量](book/chapters/ch09.md)
- [第10章　训练系统：并行、显存与通信](book/chapters/ch10.md)

### 第三部　对齐：从续写到按要求做事

- [第11章　指令微调：把续写变成对话](book/chapters/ch11.md)
- [第12章　奖励模型与 PPO：偏好如何变成梯度](book/chapters/ch12.md)
- [第13章　直接偏好优化及其家族](book/chapters/ch13.md)
- [第14章　可验证奖励与推理模型](book/chapters/ch14.md)
- [第15章　评测：我们到底在测什么](book/chapters/ch15.md)
- [第16章　榜单：排名在测什么](book/chapters/ch16.md)

### 第四部　能力扩展

- [第17章　测试时计算：多想一会儿](book/chapters/ch17.md)
- [第18章　代码、工具与函数调用](book/chapters/ch18.md)
- [第19章　多模态：把图像与声音接进语言模型](book/chapters/ch19.md)
- [第20章　扩散与统一建模](book/chapters/ch20.md)
- [第21章　蒸馏、剪枝与量化](book/chapters/ch21.md)
- [第22章　长上下文：窗口变长之后](book/chapters/ch22.md)

### 第五部　系统与智能体

- [第23章　推理引擎：算力闲着的那部分](book/chapters/ch23.md)
- [第24章　服务成本：一张账单](book/chapters/ch24.md)
- [第25章　检索与记忆](book/chapters/ch25.md)
- [第26章　智能体：三十步之后](book/chapters/ch26.md)

### 第六部　正在发生的改变

- [第27章　残差流上的注意力](book/chapters/ch27.md)
- [第28章　投机解码的第二代](book/chapters/ch28.md)

### 附录与后记

- [附录 A　关键论文一览](book/appendix/a-papers.md)
- [附录 B　术语表](book/appendix/b-glossary.md)
- [后记](book/front/afterword.md)

## 许可

本书文字与插图采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 许可，转载请注明作者与出处，不得用于商业用途。书中引用的论文版权归原作者所有。

## 分卷

| 卷 | 文件 | 页数 |
|---|---|---|
| 入门篇：大模型是什么 | [output/v1-intro.pdf](output/v1-intro.pdf) | 93 |
| 基础篇：从预测下一个词到 Transformer | [output/v2-basics.pdf](output/v2-basics.pdf) | 149 |
| 预训练篇：数据、词表与规模 | [output/v3-pretrain.pdf](output/v3-pretrain.pdf) | 147 |
| 架构改造篇：注意力、归一化与专家网络 | [output/v4-architecture.pdf](output/v4-architecture.pdf) | 113 |

每卷单独编译：双击 `build-v1-intro.bat` … `build-v4-architecture.bat`，或 `python book/build/build.py --vol v3-pretrain`。
