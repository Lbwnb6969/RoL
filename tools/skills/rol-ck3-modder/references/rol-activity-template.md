# RoL Activity Template

## Canonical Flow

1. 发现事件（Discovery）
2. 活动入口（Decision/Activity）
3. 抵达事件（Arrival）
4. 阶段事件（Check -> Success/Failure feedback）
5. 终局事件（Tier 判定 + 发奖/失败）
6. 结算事件（1090 类）

## Mandatory Pieces

- `on_start` 清理残留变量/flag
- 成功条更新与 clamp
- `send_interface_toast` 使用 `title + desc`
- 所有事件 option 必须带 `flavor = ...` 小字
- 失败分支统一走 `*_quest_fail_now_effect`
- Tier4 发放唯一完整圣物或 Naxos 单位解锁；Tier2/3 走 `*_quest_partial_finalize_effect`，提供部分成果并进入冷却；其余走失败结算。
- 部分成果不写入完整完成 flag，不创建完整圣物；正常回归走真实活动上下文，直接 event 命令不能替代它。

## 统一“人员与装备等级”模块（2026-03-23 起默认要求）

### 固定接口
- 活动选项分类：`rol_option_expedition_preparation`
- 四档 option：
  - `rol_expedition_preparation_low`
  - `rol_expedition_preparation_standard`
  - `rol_expedition_preparation_high`
  - `rol_expedition_preparation_supreme`
- 默认档：`rol_expedition_preparation_standard`
- `host_intents` 默认仅保留：`rol_relic_hunt_intent`（`guest_intents` 可按活动需要单独决定）
- 统一图标：`gfx/interface/icons/activity_option_categories/rol_option_expedition_preparation.dds`

### 当前成本基线（修改前核对仓库）
- `low = 30`
- `standard = 150`
- `high = 600`
- `supreme = 1750`

### 共享随机检定规则
- 仅对**二元成功 / 失败**的随机检定加筹备修正
- 修正值：
  - `low = -10`
  - `standard = 0`
  - `high = +10`
  - `supreme = +20`
- 成功率必须统一 clamp 到 `5~95`
- 确定成功 / 确定失败 / 主动撤退分支不吃该修正
- 当前高属性分支基线为 90%；标准筹备下，三次独立必过检定的完整成功率为 `0.9³ ≈ 72.9%`。四次为 `65.6%`，必须核对稳定推进、补救与 Tier 判定后才能判断实际完整成功率；以 `docs/rol_success_model.md` 和实际代码为准。
- 随机分支设置 `rol_expedition_display_base_chance`；结果 tooltip 使用同一动态 script value。新增人物/证据修正也要纳入共享计算，不能只改 tooltip 或某一个分支。
- 不为了增加事件数量叠加必过随机关卡；新故事优先使用成本、关系、性格压力或失败补救选择。

### 固定成功后额外奖励
- 只在 `*_quest_success_finalize_effect` 里发放
- `low = +0 prestige / +0 dynasty prestige`
- `standard = +0 / +0`
- `high = +150 prestige / +25 dynasty prestige`
- `supreme = +350 prestige / +50 dynasty prestige`

### 文案禁忌
- 活动主描述 / host_desc / selection_tooltip **不要直接剧透奖励**
- 不要写“低于 Tier4 视为失败”
- 失败说明统一写：**远征失败并进入 2 年冷却**
- 风险 tooltip 必须保留精确 `%` 成功率；不要退回定性 odds 文案
- “远征终止并进入 2 年冷却”只能放在 failure outcome 最底部，不能独立重复出现
- 不要省略 `flavor` 小字

### 测试清单
- 活动规划界面出现统一分类与四档 option
- 默认 `standard` 总价约等于旧基线
- 切换四档时，总价与提示同步变化
- `low` 更难，`high / supreme` 更容易
- 无论哪档，仍只有 Tier4 能拿最终圣物 / 解锁
- `high / supreme` 成功结算会追加 prestige / dynasty prestige

## Common Pitfalls

- 手动 `event .1001` 缺 `scope:activity` 导致误判失败
- 概率 tooltip 与实际随机检定不同步
- 同一 artifact 多次 set_owner 导致双获得 / 双失去提示
- 忘记把新链接入统一筹备模块，导致 UI 与未来 AI 模板不一致

## 跨链终局事件接入规则（2026-03-24 起）

- **不是每条新活动链都自动并入跨链总事件。**
- 只有被明确指定为“正式主线完成计数”的链，才应在成功收尾写入永久完成 flag，并接入共享检查 effect。
- 基础四链接口：
  - `rol_has_all_major_relic_completions_trigger`
  - `rol_check_legend_circle_revelation_effect`
- 若某条链不并入基础四链计数：
  - 仍可完整复用活动模板
  - 仍可有自己的永久完成 flag
  - 在共享 trigger 内保留原有四链语义，不因新增链改写旧条件
  - 当前 Carthage 通过独立五重圆环分支接入，修改前读取仓库 `rol_legend_circle_effects.txt` / `rol_legend_circle_triggers.txt`；不要把“不参与旧四链计数”误写成“不参与任何跨链终局检查”
- 若某条新链属于正式完成计数链，接入顺序固定：
  1. 在 `*_quest_success_finalize_effect` 写入该链永久完成 flag
  2. 立刻调用共享检查 effect
  3. 再做 cleanup / abort / debug trace
- 老档补发统一通过控制台 `effect rol_check_legend_circle_revelation_effect = yes` 测，不做全局扫描。
