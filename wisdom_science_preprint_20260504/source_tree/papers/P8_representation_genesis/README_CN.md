# P8 Representation Genesis

定位：Wisdom Science 的表示法生成层。

一句话：智慧系统不只搜索答案，还搜索能让未来问题更短、更稳、更可迁移的表示法。

新增核心：视角接地（Perspectival Grounding）。看到的不是世界本身，而是某个视角/语境下的投影；智慧系统必须保留多种解释，并主动选择下一视角、触觉、语境或博弈信号来消歧。

## 当前状态

- 论文骨架：`main.tex`
- 题纲来源：`papers/P8_REPRESENTATION_GENESIS_OUTLINE_20260504_CN.md`
- 初始实验脚本：
  - `experiments/representation_lab_toy_monoid.py`
  - `experiments/representation_lab_metrics.py`
  - `experiments/wisdom_science_macro_mining.py`
  - `experiments/perspectival_grounding_lab.py`

## 首批证据

1. Toy monoid 宏搜索。
2. 15 篇 Zenodo/P0-P7 论文语料宏挖掘。
3. SOVEREIGN 代码技能宏挖掘。
4. WisdomBench/WB-E 任务接口压缩。
5. Perspectival Grounding toy lab：6 个 glyph/language/robotics/social/game case，平均初始歧义 1.56 bits，主动补证据后全部消歧。

## 边界

不声称“压缩=智能”首创。
不声称“宏发现/库学习”首创。
主张是：智慧系统中的跨域表示法治理、证据门和迁移评估。
视角接地不是声称首创 active perception、symbol grounding 或博弈论，而是把它们统一放进 Wisdom Science 的证据对象：projection、viewpoint、hypothesis set、evidence cost、counter-reflexive belief。
