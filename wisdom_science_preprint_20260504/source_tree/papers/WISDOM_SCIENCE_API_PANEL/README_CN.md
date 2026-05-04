# Wisdom Science API 六模型纵向面板

## 作用

这是 Wisdom Science 的最低成本新增强证据层：用本地 API 跑六模型、四策略、多轮 WisdomBench，生成可审计 raw JSONL、summary JSON/CSV、LaTeX 表格和 evidence gate。

它不能替代 RLBench/LIBERO 真实 rollout；它证明的是文本模型的纵向智慧分离、记忆机制和失败免疫是否跨模型成立。

## 快速检查

```powershell
python experiments\api_wisdombench_longitudinal_panel.py --check-only --max-tasks 2
```

## Dry Run

```powershell
python experiments\api_wisdombench_longitudinal_panel.py --dry-run --max-tasks 2 --rounds 2 --strategies cognitive_immunity
```

## 真实 Pilot

先在 PowerShell 里把 `.secrets.ps1` 变量映射到环境变量：

```powershell
. .\.secrets.ps1
$env:CLAUDE_KEY=$KEY
$env:CLAUDE_BASE=$BASE
$env:DEEPSEEK_KEY=$DEEPSEEK_KEY
$env:DEEPSEEK_BASE=$DEEPSEEK_BASE
$env:QWEN_KEY=$QWEN_KEY
$env:QWEN_BASE=$QWEN_BASE
```

然后跑低成本 pilot：

```powershell
python experiments\api_wisdombench_longitudinal_panel.py `
  --max-tasks 5 `
  --rounds 3 `
  --strategies no_memory,cognitive_immunity `
  --seeds 42 `
  --resume
```

完整强版是 6 models x 4 strategies x 20 tasks x 5 rounds x 3 seeds = 7,200 target cells，另有 judge calls。只有在 pilot 确认模型名和费用可控后再跑。
