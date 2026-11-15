# 🧠 CU Chat Translator

> 《Casualties: Unknown》正式版多人联机聊天翻译后端
>
> 仓库：[RedAsteroid/cu-chat-translator](https://github.com/RedAsteroid/cu-chat-translator)

本项目为 [XUnity.AutoTranslator-CustomTranslate-LLM-translate](https://github.com/yexi-by/XUnity.AutoTranslator-CustomTranslate-LLM-translate) 的 fork。
上游提供通用 LLM 翻译后端；本仓库针对本作正式版重写提示词与术语表，并保留 LibreTranslate 风格的 `POST /translate` 接口与可配置端口。

## 📌 功能

- 术语表依据游戏正式版中文文本整理，覆盖物品、材料、生物、建筑、医疗、状态等 23 个分类。
- 支持中英双向翻译，并兼容插件声明的 23 种语言。
- 术语统一按表输出；聊天保留原有语气与情感；物品名与状态名保持简短。
- 默认调用 `deepseek-flash`，可替换为任意 OpenAI 兼容端点。

## ⚙️ 配置

编辑 `config.yaml`，前三项为必填：

```yaml
model_name: "deepseek-flash"
base_url: "https://api.deepseek.com"
api_key: "your-api-key"
port: 8000          # 非法值回退 8000
temperature: 0.3
max_tokens: 2048
thinking: false     # 聊天翻译建议关闭
```

> 其余可选项（`json_mode`、`send_thinking`、`timeout`、`max_retries` 等）见文件内注释。

## 🚀 启动

运行环境要求 Python 3.10 及以上，且已加入 PATH。

1. 运行 `install_requirements.bat` 安装依赖；
2. 运行 `run.bat` 启动服务。

- 端口被占用时，修改 `config.yaml` 中的 `port`，并同步修改插件的 `CustomApiUrl`（若启用了 UI 翻译，`AIBaseUrl` 也要一起改）。
- 启动后可访问 `http://127.0.0.1:<端口>/health`，返回 `{"status":"ok"}` 即表示正常。
- 修改 `config.yaml` 或 `prompt.txt` 后需重启服务；热重载仅监视 `.py` 文件。

## 🧩 对接 AutoTranslate

插件位于 Nexus Mods（[AutoTranslate](https://www.nexusmods.com/scavprototype/mods/607)），插件本体不包含在本仓库中。配置文件为 `BepInEx\config\AutoTranslate\AutoTranslate.cfg`，修改后重启游戏生效。

确认以下片段：

```ini
# ---------- API ----------
# NOTE: the values below may contain '#' and spaces, so they carry no inline comment.
TranslationEngine=Auto
CustomApiUrl=http://localhost:8000

# ---------- AI ----------
# NOTE: the values below may contain '#' and spaces, so they carry no inline comment.
AIBaseUrl=http://localhost:8000
AIApiKey=
AIModel=
```

- `AdvancedTranslation` 必须为 `True`，自定义 API 才会进入翻译链；`Enabled` 保持 `True`，`CustomApiUrl` 的端口与 `config.yaml` 一致。
- `AIBaseUrl` 指向本服务时，插件的 UI 文本翻译沿用本项目的 `prompt.txt` 与术语表（§15 约束物品名、建筑描述等 UI 词条）；留空则只翻译聊天。物品名称与描述也要走 AI 时，另将 `UseAIForUI` 设为 `True`。
- `AIApiKey` / `AIModel` 留空即由本服务处理 UI 文本，插件内的 `AIPrompt` / `AIUIPrompt` 不参与翻译；填写这两项则调用 AutoTranslate 内置的 AI 翻译功能，不再经过本后端。

## 🔌 接口

```bash
curl -X POST http://127.0.0.1:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"q":"I need an L.R.D.","source":"en","target":"zh-CN"}'
# {"translatedText":"我需要局部复苏装置"}
```

术语按表命中（`L.R.D.` → 局部复苏装置）；将 `target` 改为 `ru`、`ja` 等语言代码即可译至其他语言。

`POST /` 为上游保留接口，字段与返回格式相同；`GET /health` 返回 `{"status":"ok"}`。

## 🪵 排错

| 现象 | 处理 |
|---|---|
| 游戏内无翻译结果 | 先检查 `/health`，再确认 `Enabled` 与 `AdvancedTranslation` 均为 `True`、`CustomApiUrl` 端口与 `config.yaml` 一致，并按 `ToggleKey`（默认 `\`）确认发言翻译没有被关掉 |
| UI 文本或物品描述仍是原文 | 确认 `AIBaseUrl` 已指向本服务、`AIApiKey` / `AIModel` 留空，并检查 `UseAIForUI` 与 `TranslateDescriptions` 是否开启 |
| 返回 500 或 JSON 解析失败 | 通常为端点不支持 JSON 模式，可将 `json_mode` 设为 `false` |
| 译文退化为机翻 | 本地服务不可用，插件已回退至免费翻译引擎 |
| 翻译延迟偏高 | 插件超时为 15 秒（`AITimeout`）；保持 `thinking` 为 `false`，并适当降低 `max_tokens` |

## 🧭 已知限制

- **逐行翻译，不含上下文**：同一段对话中的指代与语气可能前后不一致。
- **术语取自社区中文文本**：游戏版本更新后，部分译名可能需要人工同步。
- **语种判定为启发式**：短句及同形词（`no` / `si` / `sip`）仍可能误判；英/德/法等同类文字之间的进一步区分依赖插件的 `DetectLatinLanguages`。
- **俄语与乌克兰语默认采用男性写法**；**英文可能出现片段句**（如 `Stuck`、`A bit cold`），均属有意设计。

## 📝 许可证与致谢

本项目基于 **MIT License** 开源，与上游一致。

- 原始代码：yexi-by 及上游贡献者
- 聊天插件：AutoTranslate 作者
- 中文文本：cu-chinese-wiki-translations 维护者、维基中文制作组
- 游戏文本与素材：游戏作者

- 👉 本仓库：[RedAsteroid/cu-chat-translator](https://github.com/RedAsteroid/cu-chat-translator)
- 👉 原项目：[GitHub - yexi-by/XUnity.AutoTranslator-CustomTranslate-LLM-translate](https://github.com/yexi-by/XUnity.AutoTranslator-CustomTranslate-LLM-translate)
- 👉 聊天插件：[AutoTranslate · Nexus Mods](https://www.nexusmods.com/scavprototype/mods/607)
- 👉 中文文本源：[dodo23333/cu-chinese-wiki-translations](https://github.com/dodo23333/cu-chinese-wiki-translations)

开发阶段使用 **DeepSeek-V41-Flash** 辅助整理规则与术语；该模型不参与运行时翻译。
