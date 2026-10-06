# RoL Project State

## Current goal

将 Relics of Legends 适配 Crusader Kings III 1.20.0.3，并保留现有五条圣物远征链的稳定性；在完成兼容迁移后，形成一份按优先级可执行的系统深化与内容拓宽路线图。

## Requirements

- 真源固定为 `C:\CK3Mods\RoL`。
- 所有 CK3 脚本和本地化文件使用 UTF-8 with BOM。
- 自定义 ID 保持 `rol_` 前缀。
- 重要文件不直接删除；需要退役时移动到专门废弃目录并保留 Git 记录。
- 选择能证明改动正确的最低充分验证，并记录剩余不确定性。

## Key decisions

- 当前目标版本锁定为 **1.20.0.3**：CK3 1.20 “Crozier / By God Alone” 于 2026-09-30 发布，1.20.0.3 于 2026-10-01 发布。
- 采用 1.20 新增的 `header_background` 字段，为五条活动显式接线已有 RoL header DDS；旅行和地点背景继续沿用当前 `background` 逻辑。
- 不因版本迁移自动把 Carthage 并入 `rol_legend_circle`；是否计入总事件属于内容设计决策。
- 先完成版本兼容和可回归验证，再分阶段扩展遗物传承、竞争者、碎片升级和跨链终局。
- 当前工作顺序调整为“静态审计与可回归工具优先，必要时再做最小游戏窗口验证”；完整活动点击流程不再作为每轮默认门槛。
- 事件背景默认只生成环境与道具，不生成人物、动物、雕像或人形轮廓；人物由事件代码的肖像和 `window_characters` 叠加。
- 新生成事件背景统一先输出高质量 PNG，再裁切到 `1592x848` 并转换为 `BC1/DXT1`；旧占位图按批次替换并保留到废弃目录。

## Progress

- 已检查项目结构、五条活动链、发现入口、artifact、Naxos men-at-arms、legacy 和 rival 模块。
- 已确认现有 `rol_smoke_checks.py` 与 ID 前缀检查通过。
- 已创建 Git 备份分支 `backup/pre-1.20-adaptation-20261005`，并提交迁移前快照 `ffa97e6`。
- 已将 `descriptor.mod` 目标版本改为 `1.20.0.3`、模组版本改为 `1.00`，并修复 BOM。
- 已为 Rome、Munich、Naxos、Sevilla、Carthage 五条活动显式添加 1.20 `header_background`。
- 已更新 README 和交接文档的版本基线。
- 最终验证已通过：BOM、`rol_` 前缀、RoL smoke checks、五个 header DDS 路径和 `git diff --check`。
- 已实现 Relic Legacy 2.0 第一批：圣物换主时的公开、隐秘、学术三种传承取向，以及对应短期角色修正。
- 已实现竞争者关系网络第一批：合作契约、强硬对抗后的积怨、后续契约代价事件和尊重/敌意意见修正。
- 已实现四条真品的碎片远征决策、三种能力挑战、两级 artifact modifier、失败压力代价和升级确认事件。
- 已实现五链增强终局：Carthage 不改变旧四链揭示条件，但完成第五件真品后会单独触发五重圆环事件和 dynasty/realm 级奖励。
- 竞争者、传承和碎片场景的生图提示词已记录在 `docs/rol_rival_legacy_image_prompts.md`；已通过代理 API 生成三张无人场景稿，筛选并接入竞争者远征、传承研究、传承换主三张 `1592x848 / BC1(DXT1)` 背景。
- 已完成第二批四张无人场景背景：竞争者契约、传承转手、碎片远征、碎片嵌合；它们替换了四张重复的带人物占位图，并分别采用外交帐篷、军械库、遗迹通道、圣物工坊环境。
- 已用本机 CK3 1.20 启动加载回归：新决策本地化和 AI 检查项已修正，RoL 相关脚本不再产生启动错误；日志剩余错误来自原版 GUI/数据和书签内容。
- 已新增 `tools/ck3_mcp` 本地 stdio MCP：基于 CK3 官方 `-debug_mode`、`-run_console_action` 接口和 Windows 原生 `SendInput` 提供环境探测、开发者模式启动/停止、命令行与窗口 console、日志读取/快照、RoL 静态检查和组合 smoke test；运行时产物被 `.gitignore` 忽略且日志只复制不删除。
- 已通过 MCP 协议握手、工具列表、环境探测、RoL 静态验证和 CK3 `debug_mode` console action；该探针加载了 RoL 事件命名空间与事件文件，返回码为 0，未发现 RoL error.log 条目。
- 已通过 MCP `ck3_launch` 启动带 `-debug_mode` 的真实 CK3 窗口，并通过 `ck3_send_console` 找到窗口句柄、发送 `debug_mode` 命令，随后用 `ck3_stop` 正常结束会话；窗口测试日志未出现 RoL 错误。
- 已完成一次完整游戏内 smoke：MCP 使用 `-skip -play=e_byzantium` 进入可操作角色，`ck3_send_console` 触发 `event rol_relic_fragment.0001`，随后读取 error.log 未发现 `rol_` 条目，并保存了日志快照。
- 已增强 MCP 窗口回归工具：`ck3_send_console`、`ck3_click`、`ck3_capture_screen` 先校验 CK3 HWND 是否真正处于 Windows 前景；激活失败时拒绝输入/点击/截图，避免误操作其他全屏程序；已在真实 CK3 窗口完成 launch、console、click、stop 协议回归。
- 已新增仓库内 `tools/ck3_mcp/rol_static_audit.py` 与 MCP `ck3_static_audit`：静态检查五条活动统一契约、活动背景文件、英中本地化键对齐/重复键和 RoL 自有 gfx 引用；该检查不启动 CK3，可作为每轮脚本与文案改动后的快速门槛。
- 已新增 `tools/ck3_mcp/png_to_dds_bc1.py`，并把七张新背景的 DDS 尺寸与 DXT1 fourCC 纳入静态审计；带人物草稿已移动到 `output/imagegen/rejected/rol_round1_with_people/` 保存。
- 已将 MCP `ck3_launch.wait_seconds` 上限扩展到 180 秒，并在返回结构中加入 `window_hwnd` / `window_ready`，用于区分新开局和大型存档的加载阶段。
- 已为 `ck3_send_console` 增加 `close_console` 参数；执行事件或脚本命令后可自动收起开发者控制台，继续做事件窗口截图和点击回归。
- 已完成一次真实窗口事件回归：新开局 `-skip -play=e_byzantium` 后触发 `event rol_relic_discovery.1000`，截图确认中文事件文案和 Rome 地宫背景正确显示；`close_console=true` 后控制台不会遮挡事件窗口。

## Next steps

1. 先用 `ck3_static_audit`、`ck3_validate_mod` 固化后续脚本/本地化/资源改动的快速回归；发现静态问题时优先修复，不启动游戏反复试错。
2. 在静态契约和资源清单稳定后，只选一个最小窗口流程验证 activity header、活动背景、筹备选项和 artifact modifier；不再每轮重复完整活动点击。
3. 继续按无人场景规则生成 Naxos 和五条活动的关键阶段背景，逐批转换 DDS 并做静态审计；最后再选一个最小窗口流程验证实际显示效果。

## Unresolved issues

- 已完成 CK3 进程级脚本加载回归；尚未通过可交互游戏窗口逐项执行控制台事件和活动流程。
- 启动器描述符仍位于 Documents 侧并正确指向 `C:\\CK3Mods\\RoL`；本轮按项目规范不修改 Documents 侧副本，若启动器仍显示旧版本号，应优先让启动器重新生成元数据。
- 当前 1.20.0.3 的宗教/圣物系统可作为后续接入点，但直接把 RoL artifact 改成 holy relic 需要额外 DLC 条件和存档兼容测试。
- AI 仍按玩家专用活动设计（`ai_will_do = 0`），是否开放 AI 远征需要单独的平衡目标。
- 新增碎片系统依赖 CK3 1.20 对 artifact scope 的 `add_artifact_modifier` 行为；当前已通过项目 smoke 检查，但仍需游戏内 console/事件回归确认。
- MCP 的命令行 console action 和窗口 console 注入已可用；当前已在新开局角色上触发碎片远征事件，完整存档中的 artifact 转移、升级和活动选项点击仍需选定适配 1.20 的测试存档逐项回归。窗口截图依赖 Pillow `ImageGrab`，并受桌面前景锁定与其他全屏程序影响；工具现在会在激活失败时安全拒绝操作。
- “克里特将军”存档已成功进入可操作界面，MCP 触发 `event rol_relic_discovery.0001` 并在 debug log 中确认执行；首次截图仍被开发者控制台覆盖，下一步用 `close_console=true` 验证事件弹窗本身。
- 已确认 `rol_relic_discovery.1000` 的发现按钮只结束发现事件并保留远征入口，活动仍需从 CK3 活动界面手动打开；当前已验证发现事件窗口，尚未完成活动规划页、筹备选项和结算页的完整点击流程。
- 本轮 API 代理返回图片 URL 而不是 `b64_json`，已用临时下载流程获取 PNG；凭证未写入仓库。当前三张新图已完成静态 DDS 回读验证，游戏内颜色、裁切和事件文字遮罩效果仍待最小窗口检查。
