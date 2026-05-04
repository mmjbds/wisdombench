# Wisdom Science 预印本与开源上传清单

日期：2026-05-04

## 当前策略

P1--P4 已经投会，不再改动已投递版本。公开预印本可以作为独立时间戳继续维护，但会议双盲版本只在 rebuttal、revision 或 camera-ready 阶段按会议规则同步。

P5--P9 采用实名公开占位路线：先发布 Zenodo/arXiv/GitHub 可复现材料，后续投会再制作匿名包。

## 已生成上传包

主上传包：

- Zenodo record: https://zenodo.org/records/20027295
- DOI: `10.5281/zenodo.20027295`
- Concept DOI: `10.5281/zenodo.20027294`
- `release/wisdom_science_preprint_20260504.zip`
- 压缩包最终大小和 SHA-256 以外层上传说明或 `Get-FileHash` 输出为准。

解压目录：

- `release/wisdom_science_preprint_20260504/`
- 文件数：364
- 未压缩大小约 46.5 MB
- manifest：`OPEN_SOURCE_UPLOAD_MANIFEST.json`

安全扫描：

- 未发现云端密码、SSH 登录串或硬编码真实 API key 等敏感模式。
- 包内保留实名作者、邮箱、Ouroboros Project、Zenodo/GitHub 信息，因为这是公开预印本占位包。

## arXiv 源码包

以下源码包已本地解压并用 `pdflatex` 两遍验证通过，无 undefined citation/reference/overfull/fatal：

| Paper | Source zip | SHA-256 |
| --- | --- | --- |
| P5 | `release/arxiv_sources_20260504/P5_embodied_wisdom_source.zip` | `20e351098f10f4d48af5cce14a94b8cb4b5ecba20373859adef6dfd1356e271a` |
| P6 | `release/arxiv_sources_20260504/P6_wisdombench_embodied_source.zip` | `9c9517f41b54c41aa5fdd5e7784f31c3be127e5f316cdeae249447ac19c041a7` |
| P7 | `release/arxiv_sources_20260504/P7_wbe_in_practice_source.zip` | `35e27a79db64bc543afcd906b370aadcbae4cbafaedfa75ad6f0d95c43a56866` |
| P8 | `release/arxiv_sources_20260504/P8_representation_genesis_source.zip` | `c1e2e85c6161176977773dc03504bc4b6ebdabcebc7a0ce98e6b31c25056bfd1` |
| P9 | `release/arxiv_sources_20260504/P9_embodied_failure_immunity_source.zip` | `ce704fe54009b84950b9d9761178919d80b3a3e7f6db001bc58b5275a97483c1` |

## 推荐上传顺序

1. Zenodo 新建或更新一个总包记录：上传 `wisdom_science_preprint_20260504.zip`。
2. Zenodo 更新 P5/P6/P7 现有记录的新版本，并新建 P8/P9 记录。
3. arXiv 分别上传 P5--P9，对应使用上方 source zip。
4. GitHub 新建干净公开仓库，只推送本 release 包中的 `data_code/`、`source_tree/`、`pdfs/` 和 manifest，不推送整个本地工作目录。
5. HuggingFace Dataset 可只放数据子集：`data_code/experiments/results/wisdom_science/`、P9 artifact manifest、WB-E raw JSONL。

## Zenodo 元数据建议

总包标题：

`Wisdom Science Research Portfolio: Evidence-Gated Evaluation of Learning After Failure`

总包描述短版：

`This release bundles the Wisdom Science preprint portfolio, executable evidence gates, generated tables, raw/summary artifacts, and a matched P9 recovery-adapter pilot. The package distinguishes first-round competence from after-experience improvement across text agents, embodied agents, representation systems, and whole-organism failure immunity.`

关键词：

- Wisdom Science
- WisdomBench
- Cognitive Immunity
- WisdomBench-Embodied
- Representation Genesis
- Embodied Failure Immunity
- evidence gate
- longitudinal evaluation
- robot learning
- public checkpoint provenance

License 建议：

- 论文与表格：CC-BY-4.0
- 代码：Apache-2.0
- 数据：CC-BY-4.0 或 CC0，按你希望的复用强度选择

## P5--P9 公开标题建议

| Paper | 建议标题 | 推荐分类 |
| --- | --- | --- |
| P5 | The Second Scaling Law in Physical Worlds: Why Architecture Determines Robot Learning Ability | cs.RO, cs.AI |
| P6 | WisdomBench-Embodied: A Longitudinal Benchmark for Measuring Learning Ability in Physical Agents | cs.RO, cs.LG |
| P7 | WisdomBench-Embodied in Practice: Measuring Learning Ability in Vision-Language-Action Agents on LIBERO | cs.RO, cs.LG |
| P8 | Representation Genesis: Compression, Perspectival Grounding, and Macro Search for Wisdom-Oriented Systems | cs.AI, cs.LG |
| P9 | Embodied Failure Immunity: Turning Robot Failures into Transferable Antigens | cs.RO, cs.AI |

## 必守口径

- P5--P7 支持 WB-E protocol、supported-set rollout、provenance discipline 和 embodied learning-ability measurement。
- P8 支持 representation governance、macro mining、toy monoid lab、perspectival grounding，不声称 compression/intelligence/macro discovery 首创。
- P9 支持 failure antigen schema、whole-organism evidence gates、6256 antigens、8-cell matched recovery-adapter pilot、3 rescue、0 regression。
- 不能写成 public VLA/SOTA 6,300 leaderboard。
- 不能写成训练出新 policy。
- 不能写成通用机器人自愈已经证明。

## 会议匿名策略

公开预印本用于占位和保护优先权。后续投会时另建匿名包：

- 删除作者、邮箱、Ouroboros、GitHub 用户名、Zenodo DOI、HuggingFace 用户名。
- 把自引改成 `Anonymous (2026)` 或 `suppressed for review`。
- GitHub 使用匿名仓库或匿名 artifact host。
- PDF 和源码都要重新做泄露扫描。
