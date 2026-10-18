# 🧠 CU Chat Translator

> 《Casualties: Unknown Demo》联机聊天翻译后端

本项目是 [XUnity.AutoTranslator-CustomTranslate-LLM-translate](https://github.com/yexi-by/XUnity.AutoTranslator-CustomTranslate-LLM-translate) 的 fork。
上游是一套通用的 LLM 翻译后端；本仓库把提示词按本作重写，并增加了 LibreTranslate 风格的 `POST /translate` 接口与可配置端口。

## 📌 功能

- 提示词内置 600 余条术语对照表，覆盖模式、怪物、建筑、植物、医疗、枪械、状态与地点。
- 一名多译按上下文选择；状态名与台词分开处理。
- 中英双向，并覆盖其他语言与中文的互译。
- 语言与 AutoTranslate 声明的 23 种一致：zh-CN、en、ja、ko、ru、es、pt、fr、de、it、pl、uk、tr、ar、nl、cs、sv、fi、hu、ro、el、vi、id。
- 情感与口语保真：保留脏话、重复与语气强度。
- 默认 deepseek-flash，任何 OpenAI 兼容接口均可使用。

## ⚙️ 配置

编辑 `config.yaml`：

```yaml
model_name: "deepseek-flash"          # 模型名称
base_url: "https://api.deepseek.com"  # API 基础 URL
api_key: "your-api-key"               # 你的 API 密钥

port: 8000                            # 服务端口，默认 8000
```

> 端口填写非整数或超出 1~65535 时自动回退到 8000，并在启动日志中提示。
>
> 其余可选项（`temperature`、`thinking`、`timeout`、`max_retries` 等）见 `config.yaml` 注释。

## 🚀 启动

需要 **Python 3.9 及以上（推荐 3.10+）**，并已加入 PATH。

1. **双击** `install_requirements.bat` 安装依赖
2. **双击** `run.bat` 启动翻译服务

⚠️ **注意事项**：
- 8000 端口被占用时，修改 `config.yaml` 的 `port`，并同步修改插件的 `CustomApiUrl`。
- 启动后访问 `http://127.0.0.1:<端口>/health`，应返回 `{"status":"ok"}`。
- 修改 `config.yaml` 或 `prompt.txt` 后需要重启服务。

## 🧩 对接 AutoTranslate

本服务面向 Nexus Mods 上的 [AutoTranslate](https://www.nexusmods.com/scavprototype/mods/607) 对接；插件通过自定义 API 调用本服务。安装方式、依赖与版本以该页面说明为准，本仓库不包含插件本体。

在 `BepInEx\config\AutoTranslate.cfg` 中确认以下配置：

```ini
[General]
AdvancedTranslation=True
OutgoingLanguage=en
IncomingLanguage=zh-CN

[API]
CustomApiUrl=http://127.0.0.1:8000/

[AI]
AIBaseUrl=
AIApiKey=
```

- `AdvancedTranslation` 必须为 `True`，自定义 API 才会进入翻译链。
- `CustomApiUrl` 使用本服务端口，默认为 `8000`；需与 `config.yaml` 的 `port` 一致，并保留结尾斜杠。
- `[AI]` 段保持为空；填写后插件会优先使用自带的 AI 直连，本项目的术语表与语气规则不会生效。

## 🔌 接口

`POST /translate`（JSON 请求体）：

```bash
curl -X POST http://127.0.0.1:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"q":"没血了","source":"zh-CN","target":"en"}'
# {"translatedText":"I'm out of blood"}
```

`POST /` 为上游原有接口，字段与返回相同；`GET /health` 返回 `{"status":"ok"}`。

## 📖 提示词

- 术语表位于 `prompt.txt` 的【专有名词强制对照表】之后，一行一条 `英文 → 中文`，新增术语直接追加。
- 状态译名仅用于状态栏；台词中的同类情绪按口语表达。
- 遇到反复翻错的句式，优先在【示例】中补充正确示范。
- 修改 `prompt.txt` 后需重启服务才会生效。

## 🪵 排错

- **游戏内无反应**：先查 `/health`，再查插件的 `AdvancedTranslation`、`CustomApiUrl` 和游戏内开关。
- **返回 500 或 JSON 解析失败**：看控制台里模型返回的原文；多为服务商不支持 JSON 模式，关闭 `json_mode` 再试。
- **译文突然变机翻**：本地服务断开，插件降级到了免费引擎。
- **延迟高**：插件超时固定 15 秒；`thinking` 保持 `false`，`max_tokens` 不要太大。

## 🧭 已知限制

- 逐行翻译，不携带上下文，同一段对话里的指代与语气可能前后不一致。
- 术语表基于非官方翻译（社区中文文本）整理；游戏更新或中文源变动后，部分译名可能缺失或不准确，需要人工校准。

## 📝 许可证与致谢

本项目基于 **MIT License** 开源，与上游一致。

- 原始代码：yexi-by 及上游贡献者
- 聊天插件：AutoTranslate 作者
- 中文文本：cu-chinese-wiki-translations 维护者
- 游戏文本与素材：游戏作者

- 👉 原项目地址：[GitHub - yexi-by/XUnity.AutoTranslator-CustomTranslate-LLM-translate](https://github.com/yexi-by/XUnity.AutoTranslator-CustomTranslate-LLM-translate)
- 👉 聊天插件：[AutoTranslate · Nexus Mods](https://www.nexusmods.com/scavprototype/mods/607)
- 👉 中文文本源：[dodo23333/cu-chinese-wiki-translations](https://github.com/dodo23333/cu-chinese-wiki-translations)

本项目开发全程使用 **DeepSeek-V41-Flash** 辅助，不限于提示词：包括规则梳理、术语一致性检查、代码调整与多语言回归用例的整理；相关建议由维护者复核后采纳。该模型仅用于开发阶段，不参与运行时翻译；服务运行时使用 `config.yaml` 中配置的模型（默认 `deepseek-flash`）。
