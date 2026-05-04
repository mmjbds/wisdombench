# Wisdom Science 预印本上传信息

日期：2026-05-04

## 核心结论

P1--P4 已经投会：不再修改已投递版本。后续只维护公开预印本/Zenodo 版本，会议版本等 rebuttal、revision 或 camera-ready 时按规则同步。

P5--P9 当前适合立即做实名预印本占位。它们的强度来自组合证据：WB-E protocol、真实 supported-set rollout、public-checkpoint sidecar、LIBERO supported-set、Representation Genesis、Perspectival Grounding、Whole-Organism Intelligence、P9 failure antigen labeling、8-cell matched recovery-adapter pilot。

## 主上传包

- Zenodo record：https://zenodo.org/records/20027295
- DOI：10.5281/zenodo.20027295
- Concept DOI：10.5281/zenodo.20027294
- 路径：`E:\order-architect-factory\release\wisdom_science_preprint_20260504.zip`
- 大小：19,916,719 bytes
- SHA-256：`c42262799f00fd3164641a16c5067ab24c542479a26c1de4ec1aa652d1293c0b`
- 解压目录：`E:\order-architect-factory\release\wisdom_science_preprint_20260504`
- 内部 manifest：`OPEN_SOURCE_UPLOAD_MANIFEST.json`
- 安全扫描：未发现云端密码、SSH 登录串或硬编码真实 API key；包内保留实名信息用于公开占位。

## arXiv 源码包

| Paper | 路径 | 大小 | SHA-256 |
| --- | --- | ---: | --- |
| P5 | `E:\order-architect-factory\release\arxiv_sources_20260504\P5_embodied_wisdom_source.zip` | 533,666 | `20e351098f10f4d48af5cce14a94b8cb4b5ecba20373859adef6dfd1356e271a` |
| P6 | `E:\order-architect-factory\release\arxiv_sources_20260504\P6_wisdombench_embodied_source.zip` | 18,583 | `9c9517f41b54c41aa5fdd5e7784f31c3be127e5f316cdeae249447ac19c041a7` |
| P7 | `E:\order-architect-factory\release\arxiv_sources_20260504\P7_wbe_in_practice_source.zip` | 567,337 | `35e27a79db64bc543afcd906b370aadcbae4cbafaedfa75ad6f0d95c43a56866` |
| P8 | `E:\order-architect-factory\release\arxiv_sources_20260504\P8_representation_genesis_source.zip` | 15,898 | `c1e2e85c6161176977773dc03504bc4b6ebdabcebc7a0ce98e6b31c25056bfd1` |
| P9 | `E:\order-architect-factory\release\arxiv_sources_20260504\P9_embodied_failure_immunity_source.zip` | 20,844 | `ce704fe54009b84950b9d9761178919d80b3a3e7f6db001bc58b5275a97483c1` |

源码包已逐个解压并两遍 `pdflatex` 验证通过。

## P5--P9 当前数据强度

- P5/P6 self-trained low-dimensional RLBench：6,300 rows，口径必须写成 self-trained low-dimensional imitation baseline。
- P5/P6 public checkpoint sidecar：RVT-2、PerAct、Act3D、3D Diffuser supported/strict artifacts，不能写成 full public SOTA leaderboard。
- P7 LIBERO：official UnifoLM-VLA supported-set 1,200 rows，口径是 supported-set evidence discipline。
- P8：claim registry、macro mining、compression table、perspectival grounding toy lab。
- P9：6,256 failure antigens，7 failure classes，8 matched recovery-adapter cells，3 rescued，0 regressions，Wilson 95% interval approximately [0.137, 0.694]。

## 推荐发布顺序

1. 先 Zenodo：上传主包 `wisdom_science_preprint_20260504.zip`，拿总 DOI。
2. 更新 P5/P6/P7 现有 Zenodo 记录的新版本；P8/P9 新建 Zenodo 记录。
3. arXiv 分别上传 P5--P9，对应使用 `release/arxiv_sources_20260504/*_source.zip`。
4. GitHub 新建干净公开仓库，只放 release 包内内容，不推整个本地工作目录。
5. 后续投会另建匿名包，不复用公开实名包。

## 一句话定位

公开版可以说：

`Wisdom Science studies whether AI systems become better, more stable, and more transferable after failure, feedback, and perturbation.`

P5--P9 可以说：

`The embodied/representation layer extends this question from text agents to physical agents, representation systems, and failure-derived recovery mechanisms under explicit provenance gates.`

不能说：

- 已完成 public VLA/SOTA 6,300 leaderboard。
- 训练出了新机器人策略。
- 已证明通用机器人自愈。
- API panel 可以替代 RLBench/LIBERO rollout。
