# RoL 1.20 兼容与扩展路线图

## 1. 兼容基线

CK3 1.20 “Crozier / By God Alone” 于 2026-09-30 发布，当前 1.20 分支的最新补丁为 1.20.0.3（2026-10-01）。版本说明：<https://ck3.paradoxwikis.com/Patch_1.20.X>。

本次迁移的实际影响集中在活动和 artifact 展示层：

- 1.20 的活动类型支持 `header_background`。RoL 五条活动现在显式读取各自的 `gfx/interface/illustrations/activity_header_backgrounds/` DDS，避免活动头图依赖隐式文件名发现。
- 旅行/地点场景仍通过活动类型中的 `background` 选择；没有改变事件窗口的自定义 scene registry。
- 1.20 已加强 artifact 图标存在性检查。RoL 的四件真品和伪造品均使用 `rol_` 专用图标路径，继续保留独立图标可以避免覆盖原版 regalia 等资源。
- 1.20 的宗教、教会、圣徒和 holy relic 功能暂不强行接入主线；这些功能适合做可选后续模块，以免把 DLC 条件写进基础远征入口。

## 2. 当前系统盘点

RoL 已经有五条正式远征：Rome、Munich、Naxos/Thera、Sevilla、Carthage；每条链包含 discovery、activity、arrival、阶段检定、Tier4-only 终局和结算事件。公共层已经抽出筹备选项、进度、冷却、日志、竞争者、artifact 创建、legacy 和总事件接口。

当前的结构性空缺有四个：

1. 五条链的主线奖励仍主要是一次性奖励；本轮已补上遗物换主与碎片升级的第一层生命周期。
2. rival 已能制造 counterfeit；本轮已补上合作契约、积怨和后续声誉意见，勒索与放逐仍可继续扩展。
3. `rol_legend_circle` 目前固定为四链计数，Carthage 的内容价值与总事件脱节。
4. 活动选项、阶段检定和奖励数值仍分散在多条链中，未来增加地区时容易复制粘贴漂移。

## 3. 推荐实施顺序

### P0：兼容与回归（已完成静态部分）

- 目标版本、模组版本和文档统一为 1.20.0.3 / 1.00。
- 五条活动显式接入 `header_background`。
- 运行 BOM、前缀、smoke 检查，并在游戏中分别打开一次活动规划页和结算页。

### P1：Relic Legacy 2.0（第一批已实现）

把遗物从“拿到即结束”变成可持续的政治与家族资产：

- 记录 `provenance`：发现者、首次持有者、转手次数、原始地区。
- 继承或转让时，根据遗物类型触发不同的 `legacy` 事件：学者研究、持有者义务、争议归属、伪造品揭露。
- 将已有 `on_artifact_changed_owner` 与 `rol_relic_legacy` 事件扩展为三条选择：公开传承、秘密藏匿、交给学者研究；宗教机构桥接保留给 P2。
- 奖励以 prestige、dynasty prestige、opinion、legitimacy 或短期 modifier 为主，不重复发放同一件真 artifact。

这样能复用当前 on-action 和 artifact scope，改动集中，且不会改变主线结算门槛。

### P1：竞争者与远征关系网（第一批已实现）

- rival 初次出现时保存其地区、能力和路线偏好。
- 已实现“合作勘探 / 强硬对抗 / 接受其线索”的第一批关系分支，并为合作和积怨加入短期角色状态；互相勒索和放逐竞争者仍可继续扩展。
- counterfeit 结果不只给负面提示，还可以留下可追踪的 `rol_counterfeit_exposed` 标记，影响后续活动成功率和声誉。
- 将现有 `rol_expedition_cooperation_opinion` 变成跨链关系奖励，避免每条链重复造一套 opinion modifier。

### P1：Legend Circle 可选终局（五链增强已实现）

保留当前四链总事件作为默认兼容规则，同时增加一个明确的玩家决策或游戏规则：

- 四链完成：触发当前基础 reveal。
- 五链完成：保留原四链 reveal，同时新增五重圆环 reveal，追加 Carthage 的灰烬封印叙事、角色/家族修正和 dynasty prestige 奖励。
- 不要在成功 finalize 中无条件改动旧存档的计数语义；通过新 flag 或新决策分支保持旧档可预测。

### P2：遗物碎片与升级远征（第一批已实现）

每条主链结束后开放一次短型“fragment”任务，而不是重复完整主线：

- 四件真品各自开放低成本、两年冷却的短型碎片远征，只追加 artifact modifier，不重复创建主线 artifact。
- 三种能力挑战分别使用 learning、prowess、stewardship，并在失败时增加压力和短期失败修正。
- 收集同一地区的碎片后，可以选择强化原遗物、换取政治资源或解锁地区专属事件。
- 失败只消耗碎片机会或增加短期压力，不重新发放主线 artifact。

这会让五条链在主线结束后仍有内容，同时避免无限刷传奇物品。

### P2：1.20 宗教与 holy relic 可选桥接

仅在玩家拥有对应 DLC、角色信仰和合适 holy site 时启用：

- 允许把某件 RoL artifact “圣化”为 faith-specific holy relic，代价是失去原本的个人装备收益。
- 允许在“个人持有 / 家族传承 / 圣地供奉”之间切换，形成真正的战略取舍。
- 所有新增入口先用 `is_holy_relic`、`is_holy_relic_for` 和现有 sanctify 规则做条件检查，不修改基础 artifact type 的默认 slot。

这是最能利用 1.20 新系统的扩展，但必须单独做 DLC 缺失、宗教类型和旧存档测试。

### P3：内容拓宽

在模板和数值层稳定后，再新增两条地区链：

- Jerusalem / Levant：以圣地、朝圣者和多信仰争议为核心，适合接 P2。
- Silk Road / East Asia：以商路、翻译者和跨文化鉴定为核心，适合接 Ledger、商贸和远行系统。

新链必须复用 discovery -> activity -> staged trials -> Tier4 terminal -> summary 模板，并明确是否计入 Legend Circle；不建议先做大规模 GUI 重写或 AI 自动远征。

## 4. 质量门槛

每个阶段都应保持：

- `rol_` ID、UTF-8 BOM 和单一真源目录不变。
- 活动 tooltip 的成功率与实际检定一致。
- 新奖励有 toast、日志和失败/冷却反馈。
- artifact 不重复创建、不覆盖原版图标、不改变旧存档已有物品的 slot 语义。
- 先做最小 console smoke，再做一条完整活动流程；只有失败或新增风险出现时才扩大测试。
