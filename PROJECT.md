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
- 新增内容先使用现有 DDS 占位图；竞争者、传承和碎片场景的生图提示词已记录在 `docs/rol_rival_legacy_image_prompts.md`，尚未调用生图 API。

## Next steps

1. 运行静态检查并修正新脚本、本地化和背景键的回归问题。
2. 用 1.20 游戏实际启动一次活动窗口，验证 header、活动背景、选项、artifact modifier 和四条碎片决策。
3. 在代码验证和游戏内回归完成后，才按提示词生成并筛选新增图片，替换占位 DDS。
4. 再评估可选五链终局分支、圣物互相组合和 AI 远征开放的平衡目标。

## Unresolved issues

- 尚未在本轮直接启动 CK3 完整游戏做 UI 和活动流程回归；脚本静态检查不能替代实际窗口测试。
- 启动器描述符仍位于 Documents 侧并正确指向 `C:\\CK3Mods\\RoL`；本轮按项目规范不修改 Documents 侧副本，若启动器仍显示旧版本号，应优先让启动器重新生成元数据。
- 当前 1.20.0.3 的宗教/圣物系统可作为后续接入点，但直接把 RoL artifact 改成 holy relic 需要额外 DLC 条件和存档兼容测试。
- AI 仍按玩家专用活动设计（`ai_will_do = 0`），是否开放 AI 远征需要单独的平衡目标。
- 新增碎片系统依赖 CK3 1.20 对 artifact scope 的 `add_artifact_modifier` 行为；当前已通过项目 smoke 检查，但仍需游戏内 console/事件回归确认。
