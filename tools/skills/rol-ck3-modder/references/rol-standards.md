# RoL Standards

## Source of Truth

- 真源目录：`C:\CK3Mods\RoL`
- 不再维护任何 Documents 侧 RoL 内容镜像。
- 启动器只通过 `Documents\Paradox Interactive\Crusader Kings III\mod\RoL.mod` 的 `path` 指向真源。

## Encoding

- 脚本和本地化文件使用 UTF-8 with BOM。
- 中文本地化统一放在 `localization/simp_chinese`。

## Naming

- 自定义内容统一 `rol_` 前缀。
- 兼容活动键名保留 `activity_rol_`、`phase_rol_` 风格。

## Safety Rules

- 先检索实例，再写新接口。
- 优先修改最小范围，避免一次性大改。
- 不绕过活动主流程直接堆事件。

## Persistent State and Backups

- 先读仓库 `PROJECT.md` 获取实现状态、用户约束、下一步与未验证项；只有这些状态变化时才更新它。
- skill 中保留可复用规则，不写入当前提交号、临时故障、测试存档或 API 凭证。
- 重要改动前检查 Git 工作区并创建备份；保留用户未提交内容，不做强制 reset。
- 重要资源和旧工具退役时移到专门 `archive/` 目录，保留 Git 记录。
- skill 的版本化维护副本位于 `tools/skills/rol-ck3-modder`；更新时同步已安装的 `.agents/skills/rol-ck3-modder` 和 `.codex/skills/rol-ck3-modder`，防止两个发现入口采用不同规则。这个目录是工具文档，不是 Documents 侧模组镜像。
