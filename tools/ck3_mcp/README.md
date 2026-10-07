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

- `ck3_environment`：只读检查游戏、模组、日志路径及Documents侧 `RoL.mod` 的path是否指向当前真源；仓库descriptor存在不等于启动器已正确接线。
- `ck3_process` / `ck3_launch` / `ck3_stop`：管理开发者模式测试会话；`ck3_launch` 可用 `loadsave` 载入指定存档，等待时间可配置到 180 秒，并返回目标窗口是否已出现。
- `ck3_run_console_action`：调用 CK3 官方 console action 接口执行事件、决策调试或脚本探针。
- `ck3_send_console`：通过 Windows 原生输入把一条命令送入可见的 CK3 开发者控制台，适合完整游戏窗口中的交互测试；传入 `close_console=true` 可在命令执行后自动收起控制台，便于继续截图或点击事件窗口。
- `ck3_capture_screen` / `ck3_click` / `ck3_hotkey`：捕获当前 CK3 屏幕、按窗口相对坐标点击或发送受限快捷键，用于实际事件选项和活动 UI 回归；例如 `alt+a` 打开活动列表。
- `ck3_read_logs`：读取受限长度的日志尾部并支持关键字过滤。
- `ck3_snapshot_logs`：把日志复制到时间戳目录，保留原始日志。
- `ck3_static_audit`：不启动游戏，快速检查五条活动的统一结构、终局部分成功路由、随机挑战与多选项分支、活动背景文件、英中本地化键对齐和 RoL 自有 `gfx` 引用。
- `ck3_dds_audit`：不启动游戏，检查 RoL DDS 头、压缩标记和资源尺寸；历史资源的非规范尺寸以警告列出，损坏头才会失败。
- `ck3_validate_mod`：运行静态审计、BOM、ID 前缀和 smoke 检查。
- `ck3_smoke_test`：组合静态检查、CK3 1.20 开发者控制台初始化探针和 RoL 日志过滤。

完整游戏窗口测试仍可通过 `ck3_launch` 启动，再在游戏内打开开发者控制台。命令行 console action 适合重复的、可回归的脚本测试；它与完整窗口会话互斥，避免两个 CK3 进程同时写同一组日志。

当前用户要求游戏测试由维护者完成，代理只调用只读环境/日志与静态验证工具，不调用启动、停止、输入或游戏 smoke。`python tools/ck3_mcp/rol_stdio_probe.py` 通过真实独立服务进程验证 initialize、无响应的 initialized 通知、15项工具目录、环境查询及组合静态验证，不启动游戏。

`ck3_launch` 的 `suppress_error_log` 默认false，console action也不抑制错误日志，避免开发探针掩盖故障。本轮只静态检查参数，未重新执行运行时工具；旧游戏记录不代表新代码已加载。

## Static-first workflow

优先运行 `ck3_static_audit`，它不启动 CK3，适合每次脚本或文案改动后的快速反馈。活动定义按五条正式链统一检查：

- discovery event 是否接到对应活动入口事件；
- activity 是否包含显示、可开始、有效性、地点、阶段、host/guest intents、结算和图形字段；
- `header_background` 与活动 `background.texture` 是否指向真源中存在的文件；
- 每条链是否保留 Tier 4 完整圣物路由，以及 Tier 2/3 的部分成功收束；
- 每条链是否仍有多个事件选项和 `random_list` 挑战分支；
- 每个挑战分支是否保存基准概率，并让英中结果 tooltip 显示与实际权重一致的成功 / 失败百分比；
- 四条碎片路线的决策、原始圣物、两级 artifact modifier、三种挑战选项和成功 / 失败效果是否完整接线；
- `rol_compatibility_contracts.py` 检查原版同路径替换、全局本地化key、自有注册项/重复/引用、追加式on_action和隐式图标；本轮退役的原版GUI/custom loc只在archive中，传奇徽记走自有modifier。未宣称任意其他模组组合已兼容；
- `rol_quest_lifecycle_contracts.py` 检查五链原host/活动类型/地区/关闭状态、101个阶段按钮的点击资格复核、重复/错活动/死亡不发奖、已结算阶段收尾、失效/死亡/旧存档、圆环一次支付及竞争者原对象契约。阶段时间只检查接线，不模拟引擎时钟；
- `rol_relic_safety_contracts.py` 检查碎片实际费用声明、原物品指针/归属、升级/失败重复保护、转手不替换目标，以及传承领奖资格/费用；四链和五链条件分别验证。模型不模拟原版扣费或装备收益；
- Rome、Munich、Sevilla、Carthage 的终点唯一圣物奖励以及 Naxos 的终局单位奖励是否仍在终点事件内；
- 五条活动成长/笔记入口与结算是否接线；`rol_growth_contracts.py` 用有限源码模型检查笔记的地区消费、重复兑现守卫、研习替换，以及实际/显示概率算式。该模型不启动游戏，也不证明引擎作用域或特质UI；
- 五条同行/专长路线、归来结算和恢复决策；`rol_companion_contracts.py` 检查实际候选、老搭档优先、原人物支付、一次路线与经验、离队/死亡/资金不足、异常活动恢复和学者概率。原版进度效果只检查接线与调用次数；
- 十种圣物/训练用途及半年成果；`rol_relic_use_contracts.py` 检查实际选项/背景接线、原物品归属、修正替换、原属性保留、等待/冷却、项目编号、过时事件与停止/换主收束。模型不模拟时间、随机选择或原版装备效果；
- 两条研究图表路线、七类继承档案和约定来源队列；`rol_archive_contracts.py` 检查实际生产/消费、同地区资格、资料年限、已有同行保护、多来源/再次继承、原人物快照与不继承XP。原版死亡顺序/物品继承和排队存档仍需手测；
- English / Simplified Chinese 的 RoL 本地化键是否一一对应且无重复；
- 脚本中出现的 RoL-owned `gfx/` 引用是否都能解析到真源文件。

活动结构参考本机原版与Workshop的既有模式；资源检查区分自有与原版引用，而活跃原版GUI覆盖被兼容门槛拒绝。一次 `ck3_validate_mod` 已组合各静态项，stdio探针还检查真实协议，不必逐项重复。游戏测试按当前用户要求交接；只有用户明确恢复代理操作时，才使用所需运行时工具。

`ck3_dds_audit` 按目录区分事件背景、活动大图、header、活动图标和artifact图标。当前84张自有DDS通过；事件/活动背景目标 `1592x848 / DXT1`，header为 `1100x440`。历史非规范尺寸如再次出现会列为警告，损坏头或受规范锁定的资源不匹配则失败。

生成背景时，`tools/ck3_mcp/png_to_dds_bc1.py` 居中裁切并缩放PNG，再写出 `DDS / BC1(DXT1)`；静态审计按当前规范目录验证59张canonical资源。仅生成占位/缺失/场景不匹配的图，已完成可用旧图保留；事件背景不放人物，人物由CK3代码叠加。

窗口输入、点击和截图会先确认目标 CK3 窗口已经成为 Windows 前景窗口；如果系统的前景锁定策略或其他全屏程序阻止激活，工具会返回错误并拒绝注入输入，避免误操作其他程序。截图功能使用已安装的 Pillow `ImageGrab`；缺少 Pillow 时，窗口级工具会明确报告依赖缺失。
