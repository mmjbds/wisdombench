# P9 Embodied Failure Immunity

定位：Wisdom Science 的具身失败免疫层。

一句话：机器人失败不是 episode log，而是可以转化为跨任务抗体的 embodied antigen。

新增核心：全机体智能（Whole-Organism Intelligence）。具身智能不是一个大脑模型控制一切，而是大脑、五官、经络/管线、血液/代谢、关节/肌肉、免疫、心理调节、社会规范和博弈心智的器官集群。

## 当前状态

- 论文骨架：`main.tex`
- 题纲来源：`papers/P9_EMBODIED_FAILURE_IMMUNITY_OUTLINE_20260504_CN.md`
- 初始工程产物：
  - `experiments/embodied_failure_atlas_schema.json`
  - `experiments/whole_organism_intelligence_schema.py`
  - `experiments/wisdom_science_claim_registry.py`

## 首批证据

1. Failure atlas schema。
2. 从 P5/P6/P7 现有日志抽取失败类型。
3. API/local adapter 生成 failure antibody draft。
4. 云端真实 rollout 时接入 WB-E gate。
5. Whole-Organism schema：9 个 organ-like engineering layers，每层都有 biological analogy、engineering substrate、typical failure、evidence gate 和 wisdom metric。
6. 扩展 failure atlas：加入 perspectival aliasing、active disambiguation、sensor pipeline、joint instability、metabolic budget、psychological calibration、social norm、counter-reflexive game 等失败类。

## 边界

`EWQ` 是跨轮次表现变化，不自动等于真实在线学习。
只有当失败记忆、策略更新或 recovery adapter 有完整 provenance 时，才可声称 failure immunity。
全机体智能不是生物学隐喻堆砌；每个“器官”必须落成可测 substrate 和 evidence gate。
