# RoL CK3 MCP

这是一个面向本地 CK3 模组开发的 stdio MCP 服务。它不依赖第三方 Python 包，直接使用 CK3 1.20 的开发者参数：

- `-debug_mode`：启用游戏开发者模式；
- `-run_console_action=<command>`：让 CK3 初始化到指定阶段后执行一条控制台命令并退出。

## 启动

在 MCP 客户端配置：

```json
{
  "mcpServers": {
    "rol-ck3": {
      "command": "python",
      "args": ["C:/CK3Mods/RoL/tools/ck3_mcp/server.py"]
    }
  }
}
```

环境变量可覆盖默认路径：`CK3_GAME_ROOT`、`CK3_EXE`、`CK3_USER_DIR`。

## 工具

- `ck3_environment`：检查游戏、模组和日志路径。
- `ck3_process` / `ck3_launch` / `ck3_stop`：管理开发者模式测试会话；`ck3_launch` 可用 `loadsave` 载入指定存档，等待时间可配置到 180 秒，并返回目标窗口是否已出现。
- `ck3_run_console_action`：调用 CK3 官方 console action 接口执行事件、决策调试或脚本探针。
- `ck3_send_console`：通过 Windows 原生输入把一条命令送入可见的 CK3 开发者控制台，适合完整游戏窗口中的交互测试；传入 `close_console=true` 可在命令执行后自动收起控制台，便于继续截图或点击事件窗口。
- `ck3_capture_screen` / `ck3_click` / `ck3_hotkey`：捕获当前 CK3 屏幕、按窗口相对坐标点击或发送受限快捷键，用于实际事件选项和活动 UI 回归；例如 `alt+a` 打开活动列表。
- `ck3_read_logs`：读取受限长度的日志尾部并支持关键字过滤。
- `ck3_snapshot_logs`：把日志复制到时间戳目录，保留原始日志。
- `ck3_validate_mod`：运行 RoL 的 BOM、ID 前缀和 smoke 检查。
- `ck3_smoke_test`：组合静态检查、CK3 1.20 开发者控制台初始化探针和 RoL 日志过滤。

完整游戏窗口测试仍可通过 `ck3_launch` 启动，再在游戏内打开开发者控制台。命令行 console action 适合重复的、可回归的脚本测试；它与完整窗口会话互斥，避免两个 CK3 进程同时写同一组日志。

窗口输入、点击和截图会先确认目标 CK3 窗口已经成为 Windows 前景窗口；如果系统的前景锁定策略或其他全屏程序阻止激活，工具会返回错误并拒绝注入输入，避免误操作其他程序。截图功能使用已安装的 Pillow `ImageGrab`；缺少 Pillow 时，窗口级工具会明确报告依赖缺失。
