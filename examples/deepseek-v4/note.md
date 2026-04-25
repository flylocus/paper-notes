# 【论文速记】百万 Token 上下文智能

> 原文标题：**DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence**  
> arXiv：https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/DeepSeek_V4.pdf  
> 总评分：**9.2 / 10**

## 评分
- 重要性 Impact：**2.0 / 2.0**
- 创新性 Novelty：**1.8 / 2.0**
- 可验证性 Evidence：**1.7 / 2.0**
- 产业可用性 Applicability：**1.9 / 2.0**
- 可复用性 Reusability：**1.8 / 2.0**

## A. 研究问题
长程推理、复杂 Agent 工作流和大规模跨文档分析正在推动模型进入百万 token 上下文阶段，但传统 attention 的计算复杂度和 KV cache 成本会迅速成为瓶颈。DeepSeek-V4 要解决的核心问题，是如何在保持强模型能力的同时，让百万 token 上下文变成可常规支持的工程能力。

## B. 核心贡献
1. 发布 DeepSeek-V4-Pro 与 DeepSeek-V4-Flash 两个 MoE 预览模型，分别为 1.6T/49B activated 与 284B/13B activated，并支持百万 token 上下文。
2. 提出 CSA + HCA hybrid attention，把超长上下文中的 attention FLOPs 和 KV cache 成本显著压低。
3. 将 mHC、Muon optimizer、FP4 QAT、MegaMoE2 和 on-disk KV cache 组合成面向训练与推理的一体化工程栈。

## C. 方法 / 框架
DeepSeek-V4 系列采用 MoE 架构，包括 DeepSeek-V4-Pro 和 DeepSeek-V4-Flash。技术报告提出 hybrid attention：Compressed Sparse Attention 先压缩 KV cache 再做稀疏选择，Heavily Compressed Attention 进一步重压缩长序列；同时引入 Manifold-Constrained Hyper-Connections 强化残差连接，用 Muon optimizer 提升收敛和稳定性，并配套 FP4 QAT、MegaMoE2、确定性 kernel、上下文并行和异构 KV cache 管理。

## D. 关键结果
- 报告称 DeepSeek-V4-Pro 在 1M token 场景下只需要 DeepSeek-V3.2 的 27% single-token inference FLOPs 和 10% KV cache。
- DeepSeek-V4-Flash 在 1M token 场景下进一步降至 DeepSeek-V3.2 的 10% FLOPs 和 7% KV cache。
- 两个模型分别在 32T+ tokens 上预训练，并通过领域专家训练与 on-policy distillation 统一能力。
- DeepSeek-V4-Pro-Max 在知识、推理、Agent 和长上下文评测上显著提升；报告称开源模型水平接近部分闭源前沿模型。

## E. 产业启示
- 百万 token 上下文让长文档审查、代码库理解、科研 workflow、合同/尽调和长程 Agent 任务从拼接检索转向原生上下文处理。
- 真正的竞争点不只是模型规模，而是 attention、KV cache、量化、kernel、并行训练和推理服务的全栈效率。
- 对企业来说，DeepSeek-V4 的价值在于降低长上下文 Agent 的单位成本，使更多需要完整上下文的 ToB 场景具备部署可行性。

## F. 一句话判断
这份技术报告真正重要的地方，是把长上下文从参数能力推进到可工程化部署的效率问题。
