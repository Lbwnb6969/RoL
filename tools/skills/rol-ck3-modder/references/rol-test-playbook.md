# RoL Test Playbook

## Choose the Evidence

先读 `PROJECT.md` 与本轮用户指令。项目默认静态优先；当游戏检验交给用户时，代理不启动 CK3、不运行 `-run_console_action`，不重启/停止会话，不发送窗口输入。后续用户明确改变这一安排后，才进行所需的最小真实流程。

选择与变更对应的最小充分检查；已通过后只因新改动、失败或具体未解决风险再扩大/重复。文档或 skill 改动检查文本、引用、元数据和部署一致性，不用游戏回归。

## Repository Checks and MCP

在 `C:\CK3Mods\RoL` 中运行与变更相关的命令：

```powershell
python tools/ck3_mcp/rol_static_audit.py
python tools/ck3_mcp/rol_dds_audit.py
python tools/ck3_mcp/check_bom_utf8.py .
python tools/ck3_mcp/check_rol_prefix.py .
python tools/ck3_mcp/rol_smoke_checks.py .
git diff --check
```

MCP 的 `ck3_validate_mod` 组合执行以上五类检查；已经运行组合验证后不必再把各项逐一重跑。按需单独使用 `ck3_static_audit` / `ck3_dds_audit`。仓库脚本优先于 skill 的旧备用脚本；环境配置和 MCP 协议用法查阅 `tools/ck3_mcp/README.md`。

静态检查可覆盖活动/碎片接线、英中键、gfx 引用、DDS 头和概率 tooltip 契约；不能证明 runtime scope、视觉遮罩或真实活动结算。

## Console Handoff

完整入口、奖励、部分成功、失败、碎片/传承与重置命令以仓库 `docs/rol_console_test_guide.md` 为准。先说明适用存档和预期结果；调试效果可能改变奖励/完成状态，优先使用独立测试存档。

```text
effect rol_relic_debug_enable_effect = yes

effect add_character_flag = rol_heard_mars_legend
event rol_relic_discovery.1000

effect add_character_flag = rol_heard_nibelung_legend
event rol_relic_discovery.1300

effect add_character_flag = rol_heard_naxos_legend
event rol_relic_discovery.1400

effect add_character_flag = rol_heard_astrolabe_legend
event rol_relic_discovery.1500

effect add_character_flag = rol_heard_carthage_legend
event rol_relic_discovery.1600
```

发现事件关闭后从活动界面打开远征。直接 `event rol_quest_*.0990` / `.1000` / `.1001` 只适合对应事件烟测，不能提供真实 `scope:activity`，不能用它证明完整奖励、筹备或部分成功正确。

直接创建圣物的 effect 只能验证该效果；不要反复调用后把重复物品误判为正常主线行为。完整流程需要真实 activity 上下文。

## Authorized Runtime Check

如果用户恢复代理侧游戏测试，选最小流程覆盖本次未确定行为，检查前置、活动规划、分支、奖励/冷却和相关日志即可。不要默认重复所有五条完整活动。

- MCP 发送输入/点击/截图前校验 CK3 HWND 和前景；激活失败时停止输入，不向其他窗口继续发送。
- `ck3_send_console` 可用 `close_console=true`，避免截图被控制台覆盖；大型存档加载可用 `ck3_launch` 的 `window_ready` / `window_hwnd` 判定，不能仅凭进程存在宣布可交互。
- 保留日志快照，只筛选相关时间段和 `rol_` 问题；不要删除历史日志。
- 如需缓存排查，先证明实际路径/格式正确，再在关闭游戏的授权会话中移动旧缓存做备份。

交付记录命令、结果、剩余不确定性；维护者测试尚未完成时不要将静态通过写成全部游戏行为已验证。
