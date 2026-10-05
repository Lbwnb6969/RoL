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

## Next steps

1. 运行 BOM、前缀、smoke 检查并检查五个 header 资源路径。
2. 用 1.20 游戏实际启动一次活动窗口，验证 header、活动背景、选项和 artifact 卡片。
3. 根据 `docs/rol_roadmap_1_20.md` 选择下一阶段：优先建议 Relic Legacy 2.0 与可选五链终局分支。

## Unresolved issues

- 尚未在本轮直接启动 CK3 完整游戏做 UI 和活动流程回归；脚本静态检查不能替代实际窗口测试。
- 启动器描述符仍位于 Documents 侧并正确指向 `C:\\CK3Mods\\RoL`；本轮按项目规范不修改 Documents 侧副本，若启动器仍显示旧版本号，应优先让启动器重新生成元数据。
- 当前 1.20.0.3 的宗教/圣物系统可作为后续接入点，但直接把 RoL artifact 改成 holy relic 需要额外 DLC 条件和存档兼容测试。
- AI 仍按玩家专用活动设计（`ai_will_do = 0`），是否开放 AI 远征需要单独的平衡目标。