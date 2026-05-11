# 🧠 Hermes Model Switcher

**Web 面板式 AI 模型一键切换工具** — 为 [Hermes Agent](https://github.com/nous-hermes/hermes-agent) 而生，支持在浏览器里点一下即可切换默认的 LLM provider / model。

> 🔧 v0.1.0 — 当前版本（机器定制版）  
> 🌍 v0.2.0 路线图：通用版（动态发现 hermes，跨机器一键部署）

---

## ✨ 功能

- 🌐 **可视化管理** — 深色主题 Web UI，直观展示所有 provider 和 model
- ⚡ **一键切换** — 点模型名即时切换 Hermes 默认 provider/model
- 🔄 **自动刷新** — 切换后立刻更新当前选中状态
- 📦 **开机自启** — systemd user 服务，重启机器后自动拉起
- 🔌 **API 驱动** — 前后端分离，REST API 供脚本/CI 调用

---

## 🚀 快速开始

### 前提条件

- 已安装 [Hermes Agent CLI](https://hermes-agent.nousresearch.com/docs)
- `~/.hermes/config.yaml` 已配置好 providers 和 models
- Python 3.8+ 和 `pyyaml`

### 1) 安装依赖

```bash
pip install pyyaml
```

### 2) 启动服务

```bash
cd ~/.hermes/model-switcher

# 方式 A：前台运行（调试）
python3 server.py

# 方式 B：后台运行
./ctl.sh start

# 方式 C：systemd 自启（推荐，生产环境）
cp model-switcher.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now model-switcher.service
```

访问：**http://localhost:8899**

---

## 📡 API

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 面板页面 |
| `GET` | `/api/models` | 获取所有 provider / model 列表及当前默认值 |
| `POST` | `/api/switch` | 切换默认模型（body: `{"provider":"...", "model":"..."}`） |

### 示例

```bash
# 查看当前模型
curl http://localhost:8899/api/models

# 切换到 DeepSeek V4 Pro
curl -X POST http://localhost:8899/api/switch \
  -H 'Content-Type: application/json' \
  -d '{"provider":"deepseek","model":"deepseek-v4-pro"}'
```

---

## 🖥️ 界面

深色主题 Web UI，Provider / Model 双栏布局，点击模型名即时切换，当前选中高亮。

---

## 🛠️ 运维命令

```bash
# systemd 管理
systemctl --user status  model-switcher   # 看状态
systemctl --user restart model-switcher   # 重启
systemctl --user stop    model-switcher   # 停止
journalctl --user -u model-switcher -f   # 实时日志

# 手动管理
./ctl.sh start    # 启动
./ctl.sh stop     # 停止
./ctl.sh status   # 查看

# 端口占用检查
fuser 8899/tcp
```

---

## 🏗️ 项目结构

```
model-switcher/
├── server.py          # Python 后端（HTTP 服务 + API + hermes CLI 调用）
├── index.html         # 前端页面（深色主题单页应用）
├── ctl.sh             # 启停脚本
├── model-switcher.service   # systemd user 单元模板
├── .pid               # 运行时 PID 文件（已 gitignore）
└── README.md
```

---

## 🔐 安全

- 监听 `0.0.0.0:8899`，仅推荐在内网/本机使用
- 如需外部访问请加反向代理 + 认证
- 不会直接操作 `config.yaml` 的 API key（只改 `model.default` / `model.provider`）

---

## 📋 版本历史

| 版本 | 日期 | 内容 |
|------|------|------|
| `v0.2.0` | 🚧 | 通用版：动态发现 hermes，跨机器一键部署 |
| `v0.1.0` | 2026-05-11 | 首个可用版：Web 切换 + systemd 自启 + hermes CLI 切换 |

---

## ⚙️ 许可证

MIT
