# -*- coding: utf-8 -*-
"""Quick API connectivity test"""
import sys, os, json, urllib.request

# Direct load secrets
secrets_path = r"e:\order-architect-factory\.secrets.ps1"

with open(secrets_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line.startswith("$") or "=" not in line:
            continue
        parts = line.split("=", 1)
        key = parts[0].strip().lstrip("$").strip()
        val = parts[1].strip().strip('"').strip("'")
        key_map = {"KEY": "CLAUDE_KEY", "DEEPSEEK_KEY": "DEEPSEEK_KEY", "QWEN_KEY": "QWEN_KEY"}
        env_name = key_map.get(key, key)
        os.environ[env_name] = val

def test_api(name, url, api_key, model):
    print(f"Testing {name}...")
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Say hello in exactly 3 words."}],
        "max_tokens": 30, "temperature": 0,
    }).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            content = data["choices"][0]["message"]["content"]
            print(f"  OK: {content[:80]}")
            return True
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

results = []
results.append(test_api("DeepSeek", "https://api.deepseek.com/v1/chat/completions",
                        os.environ.get("DEEPSEEK_KEY", ""), "deepseek-chat"))
results.append(test_api("Qwen", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                        os.environ.get("QWEN_KEY", ""), "qwen-plus"))
results.append(test_api("Claude", "https://lanyiapi.com/v1/chat/completions",
                        os.environ.get("CLAUDE_KEY", ""), "claude-opus-4-7"))

print(f"\nResult: {sum(results)}/3 APIs connected")
