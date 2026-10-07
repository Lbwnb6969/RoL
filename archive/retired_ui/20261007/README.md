# 退役的全局装备界面覆盖

来源：审计前提交 `b29218a`，备份分支 `backup/pre-review-20261007-b29218a`。

五份 GUI 曾用 RoL 装备品质显示替换所有装备的显示，并包含过期原版代码。与本机 CK3 1.20.0.3 对照，旧 `cooltip.gui` 少了 874 行，旧装备详情缺少 holy relic 区域，其他全局窗口也有原版功能差异。旧 custom localization 随调用方一并退役；所有文件原样保留，禁止重新放回加载目录作为兼容修复。

当前使用原版或其他模组提供的 GUI 和品质/类别本地化。RoL 的传奇标记保留在自身 `rol_relic_tier_legendary_modifier` 文案，不覆盖原版 `ARTIFACT_RARITY_AND_TYPE` / `ARTIFACT_RARITY_AND_SLOT_TYPE`。旧 DDS、图标及 RoL 活动成功条保留。
