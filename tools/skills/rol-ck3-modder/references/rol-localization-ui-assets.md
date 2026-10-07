# RoL Localization, UI, and Asset Notes

## Localization

- 中英 key 同步新增。
- 对活动失败提示统一使用公共 key（如 `rol_relic_fail_ends_expedition_tt`）。
- 部分成功与失败使用各自结算描述；不要把低于 Tier4 的全部路径写成失败。
- 概率 tooltip 与实际 script value 同源，避免手填固定百分比。

## Legendary Display and Compatibility

- 原版品质/类型由原版GUI与 `ARTIFACT_RARITY_AND_TYPE` / `ARTIFACT_RARITY_AND_SLOT_TYPE` 处理；RoL不得覆盖这些全局key或整份原版GUI。fallback依赖调用上下文，不能据此宣称全局覆盖安全。
- 传奇徽记放在 `rol_relic_tier_legendary_modifier` 的自有本地化名称中，复用 `@rol_legendary_icon!`；保留原版稀有度、类型和第三方界面接线。
- 2026-10-07退役的五个原版GUI副本和custom loc只保留在 `archive/retired_ui/20261007`，不能恢复到加载目录。新增插件、texticon使用 `rol_` 自有名称和文件。
- `rol_compatibility_contracts.py` 检查原版同路径替换、全局key、自有定义/引用及追加式on_action；静态通过后仍须比较原版、单独RoL和日常模组组合的卡片/详情/悬浮/交互选物。

## Text Icon

- `gui/rol_texticons.gui` 定义 `@rol_legendary_icon!`。
- 推荐徽记贴图：`60x60 .dds`（显示约 24x24）。

## Asset Resolution Baseline

- 事件/活动背景：1592x848
- 活动 header 背景：1100x440（与 header 图标区分）
- artifact icon：240x240
- regiment icon：120x120
- activity icon：80x80
- header icon：164x164
- text icon：60x60

## Existing Art and Generation

- 旧版完成且可用的图片保留，只生成明确占位、缺失或与场景不匹配的图片；旧图片不因尺寸历史不同或风格较旧就自动重生。
- 先追踪真正加载路径，再读取现有 DDS 与 `docs/rol_background_prompt_catalog.md`；相关竞争者/传承/碎片提示词还在 `docs/rol_rival_legacy_image_prompts.md`。
- 生图前读取用户指定的 `C:\Users\Administrator\Desktop\mIDDLEFILE\image_generate.md` 与可用 imagegen skill；不需要生图时不读。
- 事件/活动环境图默认不生成人物、动物、雕像或人形轮廓；人物由事件 portrait / `window_characters` 叠加。物品图标按用途保留必要主体，不把环境图规则强套到所有图标。
- 对照既有圣物形态、地区建筑/材质、时代、天气与场景阶段组织提示词；重复出现的圣物或地点应共享视觉锚点。
- 新背景先生成 PNG，再裁切并转换为 `BC1/DXT1` DDS；透明图标参考该资源家族的 alpha 格式，不强制 DXT1。回读 DDS 头、尺寸和压缩格式，检查游戏引用与本地预览。
- 被替换的重要原图放入 `archive/replaced_assets/<date>/`。保留可复用 PNG 和提示词；凭证不进入文件与日志。静态预览通过仍保留游戏内裁切/遮罩效果未验证的说明。
