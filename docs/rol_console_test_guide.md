# RoL 控制台测试指南 / 调试 / 重置

> 真源目录：`C:\CK3Mods\RoL`  
> 当前覆盖五条正式主线：Rome / Munich / Naxos / Sevilla / Carthage
> 当前不再维护 `Documents\Paradox Interactive\Crusader Kings III\mod\RoL` 内容镜像；只检查 `RoL.mod` 的 `path` 与 `Documents\Paradox Interactive\Crusader Kings III\gfx` 缓存。

---

本轮不由代理启动游戏。先复制测试存档，在启动器开启 `-debug_mode`，由维护者打开控制台逐行执行。第16节为本次审计的优先验收顺序；以下直发/重置均只用于测试副本，不在正式存档删物品或清完成状态。

## 0. 调试模式

以下只开启RoL调试提示，不替代游戏的 `-debug_mode` 启动参数。

开启：
```txt
effect rol_relic_debug_enable_effect = yes
```

关闭：
```txt
effect rol_relic_debug_disable_effect = yes
```

---

## 1. 基础语法

```txt
event 事件ID
```

```txt
effect 效果名 = yes
```

---

## 2. 发现层测试

### 2.1 统一发现入口
```txt
event rol_relic_discovery.0001
```

### 2.2 直接测试各地区发现
```txt
event rol_relic_discovery.1000   # Rome
event rol_relic_discovery.1300   # Munich
event rol_relic_discovery.1400   # Naxos / Thera
event rol_relic_discovery.1500   # Sevilla
event rol_relic_discovery.1600   # Carthage / Qartajana
```

---

## 3. 五条正式活动链测试

下列事件表是ID/背景预览索引。直接 `event` 不携带真实host/activity作用域，阶段按钮和终局不会正常推进或领奖；不能把依次强制弹窗当成完整活动测试。正式测试先给传闻，再从活动界面规划并实际出发，走正常阶段。带作用域的终局测试见第6节。

### 3.1 Rome：Mars 链
```txt
effect add_character_flag = rol_heard_mars_legend
effect remove_character_flag = rol_mars_blade_claimed

event rol_quest_rome.0990
event rol_quest_rome.1000
event rol_quest_rome.1002
event rol_quest_rome.1003
event rol_quest_rome.1004
event rol_quest_rome.1001
event rol_quest_rome.1090
```

### 3.2 Munich：Nibelung 链
```txt
effect add_character_flag = rol_heard_nibelung_legend
effect remove_character_flag = rol_nibelung_sphere_claimed

event rol_quest_munich.0990
event rol_quest_munich.1000
event rol_quest_munich.1002
event rol_quest_munich.1001
event rol_quest_munich.1090
```

### 3.3 Naxos / Thera：禁军解锁链
```txt
effect add_character_flag = rol_heard_naxos_legend
effect remove_character_flag = rol_naxos_unit_unlocked

event rol_quest_naxos.0990
event rol_quest_naxos.1000
event rol_quest_naxos.1002
event rol_quest_naxos.1003
event rol_quest_naxos.1001
event rol_quest_naxos.1090
```

> 泰拉链成功结果是**解锁招募权限**，不是直接生成兵团。

### 3.4 Sevilla：Astrolabe 链
```txt
effect add_character_flag = rol_heard_astrolabe_legend
effect remove_character_flag = rol_astrolabe_of_ocean_claimed

event rol_quest_sevilla.0990
event rol_quest_sevilla.1000
event rol_quest_sevilla.1002
event rol_quest_sevilla.1050
event rol_quest_sevilla.1001
event rol_quest_sevilla.1090
```

### 3.5 Carthage：浴火金面链
```txt
effect add_character_flag = rol_heard_carthage_legend
effect remove_character_flag = rol_ash_forged_mask_claimed
effect remove_character_modifier = rol_carthage_quest_cooldown_modifier

event rol_quest_carthage.0990
event rol_quest_carthage.1000
event rol_quest_carthage.1002
event rol_quest_carthage.1050
event rol_quest_carthage.1001
event rol_quest_carthage.1090
```

预期：
- Discovery 条件允许 `c_tunis OR b_qartajana`
- 活动地点仍固定在 `b_qartajana`
- 终局成功时发放 **helmet 槽** artifact：`rol_ash_forged_mask`

---

## 4. 活动规划 UI 检查（统一“人员与装备等级”模块）

| 活动 | `low` 总价 | `standard` 总价（默认） | `high` 总价 | `supreme` 总价 |
|---|---:|---:|---:|---:|
| Rome | `180` | `300` | `750` | `1900` |
| Munich | `280` | `400` | `850` | `2000` |
| Naxos / Thera | `230` | `350` | `800` | `1950` |
| Sevilla | `280` | `400` | `850` | `2000` |
| Carthage / Qartajana | `280` | `400` | `850` | `2000` |

手动验证点：
- 五条活动都出现 `rol_option_expedition_preparation` 分类。
- 默认选项为 `rol_expedition_preparation_standard`。
- 活动主描述 / host_desc / selection_tooltip 不直接剧透最终奖励，也不写“低于 Tier4 视为失败”。
- RNG 选项 tooltip 显示**精确成功 / 失败百分比**。
- 每个可点击 option 都有一行 `flavor` 小字。
- “终止远征并进入 2 年冷却”只在 failure outcome 最底部出现一次。
- Carthage 默认总价应为 `400`。

---

## 4.1 五条正式活动链 Tier4 阈值回归

| 活动 | 起始进度 | 主阶段高成功参考值 | Tier4 真正门槛 | 收口说明 |
|---|---:|---:|---:|---|
| Rome | 30 | 70 | 70 | 4 个主阶段需要尽量命中 major / 高成功档 |
| Munich | 35 | 55 | 55 | 2 个主阶段需要尽量命中 major / 高成功档 |
| Naxos / Thera | 30 | 60 | 60 | 3 个主阶段需要尽量命中 major / 高成功档 |
| Sevilla | 35 | 55 | 55 | 2 个主阶段需要尽量命中 major / 高成功档 |
| Carthage / Qartajana | 35 | 55 | 55 | 2 个主阶段需要尽量命中 major / 高成功档 |

回归验证点：
- 五条正式链维持 **Tier4 完整圣物 / 终局奖励 + Tier2/3 部分成功 + Tier1 以下失败** 基线。
- **主阶段没失败 ≠ 自动 Tier4**；若某一主阶段只拿到 `medium / tiny` 成功，终局会保留进度奖励并走部分成功结算。
- Naxos 的 `1000.b`（learning）与 `1003.b`（intrigue）在成功时也给予 `major`；任一成功路线都不会再因进度不足而注定失败。
- `1050` 宾客正向事件只作为**额外余量**，不是隐藏硬门槛。
- 终局判定、`store_success_result_effect`、`apply_tiered_bonus_reward_effect` 三层阈值必须一致；只有 Tier4 发放唯一完整圣物，Tier2/3 使用部分成功 effect。
- 本次不重做 GUI 成功条，仅以终局判定和实际发奖结果为准。

## 5. 圣物直发 / 统一测试入口

### 5.1 单件直发
```txt
effect rol_create_blade_of_mars_effect = yes
effect rol_create_nibelung_star_sphere_effect = yes
effect rol_create_astrolabe_of_ocean_effect = yes
effect rol_create_ash_forged_mask_effect = yes
```

### 5.2 统一 artifact 测试入口
```txt
effect rol_debug_grant_all_artifact_relics_effect = yes
```

预期：
- 直接发放 Rome / Munich / Sevilla / Carthage 四件 artifact
- Naxos 仍不包含在该 effect 中

### 5.3 Munich 槽位修复验证
```txt
effect remove_character_flag = rol_nibelung_sphere_claimed
effect rol_create_nibelung_star_sphere_effect = yes
```

预期：
- 新生成的 `rol_nibelung_star_sphere` 出现在 **礼器 / regalia** 槽
- 不再落到配饰 / 杂项槽
- 旧存档历史实例若异常，保留原存档和旧物，在独立测试副本另发新实例比较；不删除正式物品
- 图标应来自 `rol_nibelung_star_sphere.dds`，不再借用 `artifact_regalia.dds`

### 5.4 Carthage 槽位验证
```txt
effect remove_character_flag = rol_ash_forged_mask_claimed
effect rol_create_ash_forged_mask_effect = yes
```

预期：
- 新生成的 `rol_ash_forged_mask` 出现在 **helmet / 头具** 槽

### 5.5 四件传奇圣物数值 spot-check
在角色 artifact 卡片 / modifier 面板中核对：

- `rol_blade_of_mars_modifier`
  - `martial = 9`
  - `prowess = 6`
  - `monthly_prestige_gain_mult = 0.15`
  - `knight_effectiveness_mult = 0.10`
  - `dread_gain_mult = 0.15`
  - `monthly_martial_lifestyle_xp_gain_mult = 0.15`
  - `army_damage_mult = 0.08`
- `rol_nibelung_star_sphere_modifier`
  - `learning = 9`
  - `diplomacy = 2`
  - `stewardship = 4`
  - `monthly_piety_gain_mult = 0.18`
  - `monthly_prestige_gain_mult = 0.08`
  - `stress_loss_mult = 0.10`
  - `domain_limit = 1`
  - `monthly_learning_lifestyle_xp_gain_mult = 0.15`
- `rol_astrolabe_of_ocean_modifier`
  - `learning = 7`
  - `stewardship = 6`
  - `monthly_prestige_gain_mult = 0.15`
  - `character_travel_safety = 15`
  - `character_travel_speed_mult = 0.15`
  - `monthly_stewardship_lifestyle_xp_gain_mult = 0.15`
- `rol_ash_forged_mask_modifier`
  - `martial = 8`
  - `learning = 5`
  - `prowess = 6`
  - `monthly_prestige_gain_mult = 0.15`
  - `knight_effectiveness_mult = 0.10`
  - `dread_gain_mult = 0.20`
  - `monthly_county_control_growth_factor = 0.10`

---

## 6. 带真实活动作用域的结算测试

先用测试角色从活动界面正常开启目标RoL远征，等抵达且该活动已运行 `on_start`。执行下面任一终局命令前，保存尚未结算的测试副本；完整与部分测试分别重载这个副本。命令直接设置终局进度，只验证结算，不能替代完整远征的选择、概率或费用测试。

### 6.1 Rome 完整成功

```text
effect save_scope_as = host involved_activity = { save_scope_as = activity set_variable = { name = activity_special_type_progression value = 100 } } trigger_event = rol_quest_rome.1001
```

预期：只新增一件Mars剑，Tier4基础250威望/150虔诚及所选筹备完整奖励，两天后30点复盘经验。已结算标记阻止再次领奖，活动阶段约一天内收尾并进入原版结束/归程流程，不继续占用365天。重复同一命令不得多发物品或经验；没有正在参加的活动时不要使用 `involved_activity` 命令。

### 6.2 Rome 部分成功

重载尚未结算的副本：

```text
effect save_scope_as = host involved_activity = { save_scope_as = activity set_variable = { name = activity_special_type_progression value = 40 } } trigger_event = rol_quest_rome.1001
```

预期：Tier2/3部分成果，没有Mars剑/完整完成flag，没有high或supreme的额外凯旋筹备奖励；有对应进度收益、五年证据、十年Mars笔记、两年冷却和20点复盘经验。约一天阶段收尾，重放不重复兑现或刷新冷却/笔记。

### 6.3 其他四链

在对应真实活动中，沿用同一命令，只替换最后的事件ID：

| 地区 | 终局ID | 完整进度 | 部分测试进度 | 完整奖励 |
|---|---|---:|---:|---|
| Munich | `rol_quest_munich.1001` | 100 | 40 | 星界球，regalia槽 |
| Naxos | `rol_quest_naxos.1001` | 100 | 40 | `rol_naxos_unit_unlocked`，招募权限，不自动生成兵团 |
| Sevilla | `rol_quest_sevilla.1001` | 100 | 40 | 星盘 |
| Carthage | `rol_quest_carthage.1001` | 100 | 40 | 金面，helmet槽 |

每条分别验证完整30XP、部分20XP/当地笔记、完整筹备奖励与一次收尾。真实高谋略Naxos 1003.b成功现在给major，起点30加三次major应达到60；概率保持该分支原70%，不能误当90%。

### 6.4 无上下文 / 错活动的负例

不参加活动时执行：

```text
event rol_quest_rome.1001
effect rol_rome_quest_success_finalize_effect = yes
effect rol_rome_quest_partial_finalize_effect = yes
```

预期：不发剑、威望/虔诚/XP/笔记/冷却，不改其他状态；控制台强制事件可能只显示通用文本。随后实际参加一次原版活动，在该活动中用6.1命令强制Rome终局，预期原版活动进度、费用、角色状态不被RoL改变。分别检查其余四链即可覆盖不同路线。

### 6.5 筹备差异

同一高属性角色分别比较low/standard/high/supreme，价格见第4节。90%基准的单关显示依次80/90/95/95；低基准极致仍可能高于high。完整成功high额外150威望/25宗族威望、supreme额外500/100；部分成功不获得这笔完整奖励。原有阶段与终局基础收益不包含在此差额中。

### 6.6 四链总事件 / 老档

只在新的测试副本中设置：

```text
effect add_character_flag = rol_mars_blade_claimed add_character_flag = rol_nibelung_sphere_claimed add_character_flag = rol_naxos_unit_unlocked add_character_flag = rol_astrolabe_of_ocean_claimed rol_check_legend_circle_revelation_effect = yes
```

预期：一天后 `rol_legend_circle.0001`，领奖500宗族威望及原有圆环修正；Carthage不影响旧四链条件。已拥有永久圆环修正的旧角色视为领过奖励，即使清revealed或强制事件也不再次领奖。不要为补领而删除旧修正/永久领奖flag。

---

## 7. 失败收口测试

在已经抵达的真实Rome活动中：

```text
effect save_scope_as = host involved_activity = { save_scope_as = activity } rol_rome_quest_fail_now_effect = yes
```

预期：失败toast、两年冷却、约一天阶段收尾；未完成阶段没有XP，完成至少一阶段后给10XP。同行约定仍对原人物结算，不重新找人。重复同命令不再奖励或刷新状态；活动取消/失效会走同一受保护收口。

其他地区替换为 `rol_munich_quest_fail_now_effect` / `rol_naxos_quest_fail_now_effect` / `rol_sevilla_quest_fail_now_effect` / `rol_carthage_quest_fail_now_effect`，只用于对应真实活动。

无活动时直接 `effect rol_rome_quest_fail_now_effect = yes` 等属于负例，预期不添加冷却/经验/结果，不弹正常失败奖励。

---

## 7.1 Legacy 2.0 / 竞争者 / 碎片系统

### 圣物换主事件

```txt
effect rol_create_blade_of_mars_effect = yes
effect rol_relic_legacy_debug_transition_effect = yes
```

预期：事件显示 `rol_bg_relic_legacy_transfer`，并提供公开传承、秘密藏匿、学者研究三种选择；同一角色五年内不会重复触发换主事件。研究需100金币。调试入口保存实际持有物品的作用域；单独 `event rol_relic_legacy.0003` 无此作用域不能证明正常换主流程。已有对应圣物时跳过创建命令。领奖前再转手应仅有关闭选项，不再支付奖励。

### 碎片远征最小 smoke

```txt
effect add_character_flag = rol_mars_blade_claimed
effect rol_create_blade_of_mars_effect = yes
effect rol_relic_fragment_begin_effect = { ROUTE = mars TYPE = rol_blade_of_mars LAST_MODIFIER = rol_blade_fragment_2_modifier }
```

预期：一天后事件显示 `rol_bg_fragment_expedition`；成功给最初选中的 Mars artifact 追加一级 modifier，再过一天显示 `rol_bg_fragment_upgrade`。下一次成功追加二级，失败增加20压力并清除路线/指针；取消不退款且不奖励。已有圣物时跳过创建。此调试 effect 不扣决策费用、不执行决策冷却；正式决策需验证实际扣120金币、两年冷却和一次只开一个项目。第三种挑战另需50金币，只有成功时扣除。

其余三条路线替换创建 effect，并使用下表参数调用相同 begin effect：

| 创建 effect | ROUTE | TYPE | LAST_MODIFIER |
|---|---|---|---|
| `rol_create_nibelung_star_sphere_effect` | nibelung | rol_nibelung_star_sphere | rol_nibelung_fragment_2_modifier |
| `rol_create_astrolabe_of_ocean_effect` | astrolabe | rol_astrolabe_of_ocean | rol_astrolabe_fragment_2_modifier |
| `rol_create_ash_forged_mask_effect` | ash | rol_ash_forged_mask | rol_ash_fragment_2_modifier |

边界：开始后把原物品转给别人，或销毁原物品，即使自己另持同类型圣物也不能改选它升级。窗口应允许取消，无升级/威望/失败压力；取消不清两年冷却。已满二级不再出现正常入口。源代码模型覆盖这些状态，但需实测排队事件与物品变量在引擎中的保存行为。

竞争者事件依赖活动上下文，优先从五条正式活动的阶段选项进入；若只直接执行 `event rol_rival.1000`，没有 `scope:activity` 时不应把它作为完整回归结果。

### 五链增强终局

```txt
effect add_character_flag = rol_mars_blade_claimed
effect add_character_flag = rol_nibelung_sphere_claimed
effect add_character_flag = rol_naxos_unit_unlocked
effect add_character_flag = rol_astrolabe_of_ocean_claimed
effect add_character_flag = rol_ash_forged_mask_claimed
effect rol_check_legend_circle_fivefold_revelation_effect = yes
```

预期：一天后触发 `rol_legend_circle.0002`，发放五重圆环角色修正、家族/宗族奖励和 1000 dynasty prestige；旧四链 `rol_legend_circle.0001` 的触发语义保持不变。

## 8. 重置命令

仅用于一次性测试副本；重载结算前副本通常更可靠。不要在正在进行的活动中清上下文，也不要清永久圆环领奖资格或用途递增编号来模拟正常重试。

### 8.1 通用 recent result 清理
```txt
effect rol_relic_clear_recent_result_effect = yes
```

### 8.2 Rome
```txt
effect remove_character_flag = rol_heard_mars_legend
effect remove_character_flag = rol_mars_blade_claimed
effect remove_character_modifier = rol_mars_quest_cooldown_modifier
effect if = { limit = { has_variable = rol_rome_stage_count } remove_variable = rol_rome_stage_count }
```

### 8.3 Munich
```txt
effect remove_character_flag = rol_heard_nibelung_legend
effect remove_character_flag = rol_nibelung_sphere_claimed
effect remove_character_modifier = rol_nibelung_quest_cooldown_modifier
effect if = { limit = { has_variable = rol_munich_stage_count } remove_variable = rol_munich_stage_count }
```

### 8.4 Naxos / Thera
```txt
effect remove_character_flag = rol_heard_naxos_legend
effect remove_character_flag = rol_naxos_unit_unlocked
effect remove_character_modifier = rol_naxos_quest_cooldown_modifier
effect if = { limit = { has_variable = rol_naxos_stage_count } remove_variable = rol_naxos_stage_count }
```

### 8.5 Sevilla
```txt
effect remove_character_flag = rol_heard_astrolabe_legend
effect remove_character_flag = rol_astrolabe_of_ocean_claimed
effect remove_character_modifier = rol_astrolabe_quest_cooldown_modifier
effect if = { limit = { has_variable = rol_sevilla_stage_count } remove_variable = rol_sevilla_stage_count }
```

### 8.6 Carthage
```txt
effect remove_character_flag = rol_heard_carthage_legend
effect remove_character_flag = rol_ash_forged_mask_claimed
effect remove_character_modifier = rol_carthage_quest_cooldown_modifier
effect if = { limit = { has_variable = rol_carthage_stage_count } remove_variable = rol_carthage_stage_count }
```

---

## 9. 活动 UI 不显示时先检查

需要满足：
- Rome：`rol_heard_mars_legend` 且未 `rol_mars_blade_claimed`
- Munich：`rol_heard_nibelung_legend` 且未 `rol_nibelung_sphere_claimed`
- Naxos：`rol_heard_naxos_legend` 且未 `rol_naxos_unit_unlocked`
- Sevilla：`rol_heard_astrolabe_legend` 且未 `rol_astrolabe_of_ocean_claimed`
- Carthage：`rol_heard_carthage_legend` 且未 `rol_ash_forged_mask_claimed`

如果仍不显示，依次检查：
1. 是否已添加对应 heard flag
2. 是否存在 `*_quest_cooldown_modifier`
3. 是否处于战争、未成年、被囚禁或 incapacity 状态
4. 是否金币不足
5. Carthage 是否正确命中 `b_qartajana / c_tunis` 的位置验证

---

## 10. 常见问题

- `not a valid id`：检查真源、启动器加载路径及脚本是否重载。
- 直接 `event rol_quest_*.1001` 或无上下文finalize不发奖：当前是受保护的正确负例；正例用第6节的真实活动命令。
- 泰拉兵种检查：正常完整结算后确认 `rol_adeptus_custudes` 可招募。仅测兵种UI时，可在测试副本执行 `effect add_character_flag = rol_naxos_unit_unlocked`；此命令不证明远征成功。
- 没有RoL debug toast：用第0节的RoL调试开关；控制台仍需要游戏debug模式。
- 背景/图标异常：先核对真源加载路径、接线与DDS。确需清缓存时，关闭游戏与启动器，把Documents侧 `gfx` 移到带日期的缓存备份目录，再重启；保留原缓存，不直接删除。
- 装备品质/类型前缀：本轮已退役全局GUI与custom loc覆盖。不要把 `archive/retired_ui` 文件复制回活跃目录；按第16节比较模组组合与加载顺序。

---

## 11. 视觉回归检查

### 11.1 Carthage 事件背景
```txt
event rol_relic_discovery.1600
event rol_quest_carthage.0990
event rol_quest_carthage.1000
event rol_quest_carthage.1002
event rol_quest_carthage.1001
event rol_quest_carthage.1090
```

预期：
- `rol_discovery_bg_carthage`
- `rol_bg_carthage_0990_arrival`
- `rol_bg_carthage_1000_desert`
- `rol_bg_carthage_1002_ash_temple`
- `rol_success_bg_carthage`
- `rol_bg_carthage_1090_summary`

以上 6 个 key 都能正常显示当前接入的 DDS，不再黑底或丢失背景；其中仍可用的旧版资源按项目规则保留，不重复生图。

### 11.2 Regalia 图标污染回归
预期：
- `rol_nibelung_star_sphere_visual` 只读取 `rol_nibelung_star_sphere.dds`
- RoL 目录不再交付 `artifact_regalia.dds`
- 原版 / NPC 的 regalia 不再被 Nibelung 星界球封面污染

### 11.3 `@rol_legendary_icon!` 透明验证
1. 在游戏与启动器关闭时，把 `Documents/Paradox Interactive/Crusader Kings III/gfx` 移到带日期的缓存备份目录
2. 完整重启启动器与游戏
3. 打开任意使用 `@rol_legendary_icon!` 的文本

预期：
- 背景为真正透明
- 只显示大金星与两颗环绕小星
- 不再出现棋盘底、黑底或实心底

### 11.4 英文界面回归
切英文后重点抽查：
- Rome 主链按钮名与 `1010~1042` 过渡事件
- Munich `1010~1022`
- Carthage 全链 `0990 / 1000 / 1002 / 1050 / 1001 / 1090`
- 活动意图 `rol_relic_hunt_intent`

预期：
- 不再出现缺英文、空白文本、回退 key
- Rome / Munich / Carthage 的活跃事件标题、正文、按钮均有英文
- `error.log` 不再报相关 missing loc

## 12. 人物成长与地区笔记（2026-10-07）

此节由维护者在独立测试存档执行；代理本轮不启动游戏。静态通过不等于特质界面、作用域和定时事件已经在引擎中验证。

### 12.1 最小复盘与特质检查

```text
effect rol_expedition_growth_debug_queue_effect = yes
```

预期：打开“旅途留下的本领”，显示20点经验。选择考据、探险或交涉后获得“遗物探寻者”特质，对应轨道增加20经验并出现三年研习；勤勉/勇敢/合群匹配方向时失去5压力。打开特质检查三个轨道和20/60/100阈值显示。本轮特质有意复用原版 traveler 图标。

```text
event rol_expedition_growth.0001
```

预期：没有待处理经验时该事件不应自然显示；即使控制台强制打开并重复选择，也不会增加经验、刷新研习或重复减少压力。确需再测另一方向，重新执行 debug queue，然后选另一个方向；此前的研习消失，不同时保留三个BUFF。

若自动复盘因角色状态未打开，观察决策“复盘远征经历”：它只在待处理经验存在时出现，打开已有复盘，不产生新经验。

### 12.2 最小地区笔记检查

以 Rome 为例：

```text
effect add_character_modifier = { modifier = rol_expedition_mars_notes_modifier years = 10 }
effect add_character_flag = rol_heard_mars_legend
effect remove_character_flag = rol_mars_blade_claimed
effect remove_character_modifier = rol_mars_quest_cooldown_modifier
event rol_relic_discovery.1000
```

从真实活动界面开始 Rome 远征，选择标准筹备。预期：出发时地区笔记消失并有“循着上次的发现”提示；活动二元检定显示增益后的精确概率，高属性90%分支变为95%。高/极致筹备仍封顶95%，不能达到100%。同一个活动的后续检定继续保有增益，不能因为笔记已消耗而再次失去增益。

其他地区对应修正：`rol_expedition_nibelung_notes_modifier`、`rol_expedition_naxos_notes_modifier`、`rol_expedition_astrolabe_notes_modifier`、`rol_expedition_carthage_notes_modifier`。持有 Rome 笔记时开始别的地区远征，不应消耗 Rome 笔记或得到其增益。

### 12.3 真实结算检查

- 完整成功：两天后30点复盘经验，唯一奖励与原流程一致，不额外产生新的地区笔记。
- Tier2/3 部分成功：两天后20点经验，并获得同地区十年笔记；原有五年证据学习修正和两年冷却保留。不能得到完整圣物或完整完成flag。
- 已完成至少一阶段后失败：10点经验，不给地区笔记；冷却与失败总结保持。
- 未完成任何阶段的失败/撤退：无复盘经验；反复出发后立即退出不能刷经验。
- 重复 finalize：成长结算资格已关闭，不重复增加经验或发笔记。直接无活动上下文调用 finalize 不能验证真实结算，也不会得到新的成长奖励。

十年笔记到期、三年研习到期需要游戏时间验证；源码模型只核对时长参数与状态操作。若时间推进异常或事件错位，保留 `error.log` 中相关 `rol_` 行供后续定位。

### 12.4 测试状态清理

以下仅清理新增成长状态，测试存档中执行。移除特质会丢失该人物已经积累的三个专长轨道：

```text
effect remove_trait = rol_relic_seeker
effect remove_character_flag = rol_expedition_growth_pending
effect remove_variable = rol_expedition_growth_pending_xp
effect remove_character_modifier = rol_expedition_research_focus_modifier
effect remove_character_modifier = rol_expedition_exploration_focus_modifier
effect remove_character_modifier = rol_expedition_negotiation_focus_modifier
effect remove_character_modifier = rol_expedition_mars_notes_modifier
effect remove_character_modifier = rol_expedition_nibelung_notes_modifier
effect remove_character_modifier = rol_expedition_naxos_notes_modifier
effect remove_character_modifier = rol_expedition_astrolabe_notes_modifier
effect remove_character_modifier = rol_expedition_carthage_notes_modifier
```

活动中的笔记增益属于当前 activity，清理角色修正不会倒扣已经用于该次远征的笔记。活动结束后自然弃用该activity状态。

## 13. 同行、履约与专长路线（2026-10-07）

在独立测试存档中，通过真实活动规划邀请专家宾客并让其实际出席；单独强制打开同行事件无法建立队伍上下文。最低抽查Rome与一个三段链（Munich/Sevilla/Carthage），再按需要扩展；代理不启动游戏。

### 13.1 专长开局入口

```text
effect add_trait = rol_relic_seeker
effect add_trait_xp = { trait = rol_relic_seeker track = rol_research value = 60 }
gold 200
```

通过本手册原有发现事件打开远征，并从活动界面实际开始。预期：第一道难关出现“照着以往远征积累的方法”选项，扣100金币，进入正常成功反馈，继续下一阶段；不自动发完整圣物。其余探险/交涉轨道达到60也可解锁。护卫与专长两条稳妥路线不能在同次开局分别使用；强制重放初始事件不能重复收费或推进。

### 13.2 三种真实同行

学习≥12的学者、武勇≥12的护卫、外交≥12的交涉者需是存活、成年、未被囚禁且未失能的实际宾客。没有合格同行时直接进入原有第一道难关，不应卡住。抵达后的约定窗口显示真实候选姓名，拒绝订约仍能继续。

- 学者：标准筹备、90%基准分支显示93%；同时有本地笔记则95%。其离队/死亡后，后续检定回到不含3点帮助的数值，笔记仍正常生效。
- 护卫：仍同行时出现75金币稳妥开局，进入正常成功反馈；归来还需另付50金币。已离队/死亡时不能继续提供开局路线。
- 交涉者：如果宾客竞争事件出现，应多一个和平交换选项；无需决斗/赝品检定，减少10压力并改善进度。该原人物不能同时被抽为本次竞争者；竞争事件本身不保证出现。

### 13.3 归来与延期

有进展后完成、部分成功或失败，约四天后出现原同行的结算事件。充分履约分别扣50威望/50金币/75威望，护卫金币确实付给同一人物；双方+25好感，三年守信声誉，对应专长+10经验。未推进任何阶段便退出时仍可以结清费用和关系，但无经验。25金币协商给5经验，不新增老搭档；拒约无经验，诚实/公正者加15压力。

选择暂缓后“结清远征约定”决策保留原人物，新活动不会覆盖此约。也可检查入口：

```text
event rol_expedition_companion.0002
```

仅在已有待处理约定时使用。结清后重放不能再次收费、加经验或声誉；延迟自动事件也不得重复结算。充分履约的同一人物下次若实际参加且合格，应优先成为该角色候选；这不是自动建立原版“好友”关系。原同行死亡/失效后应只允许关闭，不付钱、不奖经验、不改选另一人。资金不足时充分履约不可选，约定保留，可暂缓或拒绝。

真实活动中断、主办者死亡、延迟事件保存/读档和人物指针作用域仍须引擎确认。主办者死亡不把个人经验自动继承；新增第15节可让继承人主动接续原人物约定，所得earned XP为0。

### 13.4 清理同行测试状态

仅在测试存档且没有正在进行的RoL活动时执行；清理后排队中的结算不应再次奖励：

```text
effect rol_expedition_companion_clear_effect = yes
effect remove_variable = rol_expedition_trusted_companion
effect remove_character_modifier = rol_expedition_kept_word_modifier
effect remove_character_modifier = rol_expedition_broken_word_modifier
```

清理不删除已有好感记录或专长经验；后者按12.4处理。保留有问题的存档与 `error.log` 相关 `rol_` 行，以便定位人物变量和活动上下文。

## 14. 圣物用途与半年成果（2026-10-07）

代理仍不进游戏。先在独立测试存档抽查一件真品和Naxos方案，关注装备、实际物品转手回调和保存/读档后定时事件；这是源码模型无法证明的部分。

### 14.1 新入口与装备条件

测试角色尚无Mars剑时可执行一次：

```text
effect rol_create_blade_of_mars_effect = yes
gold 200
event rol_relic_use.0001
```

创建效果不检查重复，已有真品时跳过第一条；正式玩法通过原有完整远征获得。也可从“安排圣物用途”决策打开，选择Mars剑→骑士演练：扣50金币，原剑新增+5%骑士战斗力用途，原有真品属性和碎片修正保留；不创建第二件剑。切为公开誓约时改为+3普遍好感，两种用途不同时保留。

装备/卸下该物品，观察新增用途加成随装备生效/消失。未装备仍可完成半年计划，但没有装备加成。其余三件的两种用途与数值见 `docs/rol_system_expansion_plan.md` 第三阶段。

### 14.2 成果、等待与恢复

刚立项时再次选择用途不收费、不叠加，等待未满时“整理圣物用途成果”不出现；下列恢复命令也不能提前打开或结算：

```text
effect rol_relic_use_reopen_effect = yes
```

正常推进至少181天，预期自动成果事件出现。记录本领得对应用途10经验，匹配性格减5压力；公开成果改得100威望而不加专长经验。选择暂缓后决策重新出现；定时与手动恢复重复结算不奖励第二次。当前用途保留，一年冷却仍在。强制单独 `event rol_relic_use.0003` 缺少项目编号上下文，不是正确测试入口。

若只想缩短测试等待，可在测试存档执行：

```text
effect remove_character_flag = rol_relic_use_waiting
effect rol_relic_use_reopen_effect = yes
```

这只验证恢复/结算接线，不能证明真实180天标记到期。另保留一次自然181天测试，用来确认到期与自动事件顺序。

### 14.3 换主、停止与旧事件

- 有计划时将原物品赠予别人：转手后原用途应从物品移除，原主人卸下/失去物品不再有加成。成熟恢复事件仅允许关闭，无经验/威望，不退款，不抽取其他圣物来替代。新主人自行安排用途。
- “停止圣物部署”随时可选：移除所选用途，取消该对象待处理计划，无奖励/退款，冷却保留。停止另一件已部署物品，应保留当前项目的原物品、模式和待处理状态。
- 第一次计划结算后，等冷却过期再开始第二次；旧的排队事件不得提前结算/关闭新计划。保留此场景的存档，用来检查定时事件保存的项目编号。
- 50金币不足时用途不可选，取消菜单不收费。除停止/换主外，用途保持到后续切换；原物品不应丢失真品/碎片修正。

### 14.4 Naxos训练与清理

测试存档可解锁资格：

```text
effect add_character_flag = rol_naxos_unit_unlocked
```

选择Naxos配合训练或老兵授课，扣50金币，获得对应三年修正；切换替换另一方案，不创建兵团。两方案的记录成果均投入探险，分别匹配勇敢/勤勉减5压力。无资格不能新立项；训练到期后恢复已过期项目仅关闭，不奖励。

优先用“停止圣物部署”清理所选用途。需要重测立项，仅在测试存档、停止当前方案之后执行：

```text
effect rol_relic_use_clear_pending_effect = yes
effect remove_character_flag = rol_relic_use_cooldown
```

不要删除 `rol_relic_use_generation`：保留递增编号，确保旧事件不能与后续测试项目碰撞。清理待处理状态本身不删除其他物品的用途或已兑现经验。检查三年训练到期、真实转手回调及相关 `rol_` 日志后，再扩展抽查另外三件真品。

## 15. 跨链图表与代际接续（2026-10-07）

静态模型不证明引擎死亡顺序、实际继承物品或排队scope的保存。维护者在独立存档自行操作；代理不启动游戏，也不执行下面命令。

### 15.1 真实图表生产与快捷入口

按第14节做星界球持续观测或星盘路线校准，半年成果选“记录本领”：除10经验外，分别获得十年观测图/校准航路；公开100威望不应获得图表。图表出现时对应活动传闻入口可见；相同资料刷新不叠加。

只测消费时可用：

```text
effect add_character_modifier = { modifier = rol_star_observations_modifier years = 10 }
effect add_character_flag = rol_heard_astrolabe_legend
```

或：

```text
effect add_character_modifier = { modifier = rol_ocean_routes_modifier years = 10 }
effect add_character_flag = rol_heard_naxos_legend
```

通过活动界面实际开始Sevilla/Naxos，首阶段出现对应资料路线，扣40金币并耗资料，进入正常成功反馈。后续仍须完成。别的地区不出现；不足40金币不耗资料；已经使用护卫/专长稳妥开局后不能重复使用资料路线。无资料仍可按原路线完成。图表没有被动成功率或属性加成。

### 15.2 档案继承

保留有存活玩家继承人的测试角色，给至少一份地区笔记/图表。快捷检查打包可执行一次：

```text
effect rol_archive_export_effect = yes
```

此效果是一次性死亡打包逻辑；在活人测试角色上手动调用也会标记已递交，不能替代真实死亡回调。不要在正式存档执行。快捷流程可切换控制到该继承人（用debug界面确认ID后 `play <角色ID>`），等七天或执行：

```text
event rol_archive.0001
```

预期：已有未读档案时出现整理/保存/封存。整理扣50威望，缺少的七类资料得到五年副本；已有同类资料保留原期限；地区传闻入口可见。前任的特质XP、待复盘XP、完成flag、圣物或当前项目不被此效果复制。再打开不收费/不刷新副本。威望不足可延期，自己的活动不受阻。

另保留一次未调用快捷打包的副本，由你自行让角色正常死亡并选择继承，检查真实回调、物品原版继承和七天事件。原版物品换主应清除旧用途；Naxos继承承接旧资格入口，支付条件包含100金币、500威望及军事门槛。原训练BUFF不复制。

### 15.3 约定接续与多个来源

前任已有在途或待结算的学者/护卫/交涉者约定时，死亡打包后八天出现约定接续窗口；也可用继承人的“查阅继承的远征约定”决策。不要单独强制 `event rol_archive.0002`：它需要来源人物scope。

预期：姓名与原人物一致。承担后接入原第13节结算，条款仍为50威望/50金币/75威望，可协商或暂缓，但所有继承结算都不得增加前任经验。自愿履约可建立继承人自己的守信声誉与老搭档。尚未承担时拒绝不强加失信声誉。

已有自己的在途/待结算约定时，承担选项不能覆盖该人物；可以保存来信，结清个人约定后再打开。多个来源逐份保留，处理一份不移除另一份；继承人未读/未处理便再死亡时，档案和原来源队列继续递交给下一位。原参与者死亡只关闭对应来源，不改选支付人。保留相关存档用于排队上下文和历史人物指针的回归。

### 15.4 清理

仅在一次性测试存档中：

```text
effect rol_archive_clear_cargo_effect = yes
effect clear_variable_list = rol_archive_pact_sources
effect remove_character_modifier = rol_star_observations_modifier
effect remove_character_modifier = rol_ocean_routes_modifier
```

清理来信不取消已经主动承担的个人约定，后者按第13节处理。不要重置前任 `rol_archive_exported` 重新打包正式状态；另开测试副本测真实回调。保留 `error.log` 中继承/图表相关 `rol_` 行。


## 16. 本轮全面审计的优先验收（2026-10-07）

先做16.1兼容回归，再做16.2生命周期；其余按相关模块抽查。用同一份测试存档副本，记录版本、模组清单/顺序和暂停时的费用/XP。下列命令由维护者执行，代理本轮没有游戏操作。

### 16.1 原版与其他模组装备前缀（最高优先级）

1. RoL关闭时保留原版与日常模组的武器/礼器等物品截图。覆盖普通、名作、稀有、卓越中的现有实例，记录品质和槽位/类型前缀，不更改原物品。
2. 仅开启RoL，检查相同原版物品的背包卡片、详情、悬浮提示、赠送/继承等交互的选物列表。英文也抽查一件。
3. 开RoL和日常模组组合，检查相同的第三方物品；换RoL与相关界面模组的相对加载顺序再抽查。记录失败界面与物品类型，避免只查一个背包卡片。
4. 原版holy relic详情、宗教/情势界面仍应有当前版本的字段，不被旧版RoL GUI替换。RoL没有继续占用这些原版窗口。

预期：原版和第三方品质/类型显示与关闭RoL时一致，如名作级礼器、稀有级武器不丢前缀。RoL真品仍走原版品质/类型，自己的修正列表显示 `@rol_legendary_icon!` 与传奇阶位；不要求全局原版品质被改名成“传奇”。若只在某组合失败，提供清单和顺序，不把单独RoL通过视为全组合兼容。

仅在测试角色尚无RoL四件真品时可直发一次用于观察：

```text
effect rol_debug_grant_all_artifact_relics_effect = yes
```

直发不是唯一性测试；正常主线应由第6节或真实远征验证。

### 16.2 结算、旧窗口、失效与死亡

按第6节分别做完整/部分，按第7节做零进展/有进展失败。每次观察约一天阶段结束和归程，不出现一年停留；终局后不又变成一次失败奖励，重复事件不刷新XP/冷却/笔记或多发神器。

让正常挑战窗口保持打开，在暂停时用第7节命令结束同一活动，再点击旧窗口。预期：无额外威望、虔诚、伤害、进度或下一阶段事件；按钮只关闭旧窗口。用已进入终局的存档再重放完整命令，物品数不增加。

另通过游戏中的取消/人物失能等操作使远征实际失效，验证失效钩子；不要只用失败effect替代这一项。主办者死亡测试保留一个未调用档案快捷打包的副本，在有在途原同行约定时正常死亡并继承，按第15节观察资料/原NPC约定传递。继承人不拿前任个人XP、不把原同行换成另一个人；已死亡主办者的旧排队事件不领奖。原版死亡/继承与活动结束回调先后需要真实游戏确认。

旧版本存档另留副本加载：没有新关闭标记的在途活动仍应能正常结算；已有完成flag和永久圆环奖励保持；此前完成物品不自动删除/重建。保存并读档后重复上述最小场景，确认指针和活动资格保留。

### 16.3 圆环与最后一项继承

在6.6四链测试领过一次后：

```text
event rol_legend_circle.0001
```

预期：不再增加500宗族威望、不刷新75/100年家族/宗族奖励。再增加第五链并检查：

```text
effect add_character_flag = rol_ash_forged_mask_claimed rol_check_legend_circle_fivefold_revelation_effect = yes
```

一天后五重圆环首次给1000宗族威望及既有修正；再次 `event rol_legend_circle.0002` 不重复支付/续期。比较暂停时即时变化，避免把日常被动宗族威望当重复奖励。

在另一个接近完成的角色上，通过赠送/原版继承取得最后一件真品，或通过Naxos继承事件支付500威望/100金币（军事≥10），预期自动检查对应圆环。资金不足或已解锁时旧Naxos窗口不能重复收费/领奖。Naxos承接必须来自实际持有资格的原前任；放弃所得50虔诚亦只兑现一次，无前任作用域的强制 `.0103` 不付款或领奖。

### 16.4 竞争者与传承互斥

正常远征遇到竞争者时合作；记住原NPC，后续用恢复决策“处理竞争者的约定”或：

```text
effect rol_rival_reopen_pact_effect = yes
```

预期始终是原NPC。选50金币换100威望、150威望但恶化关系、或减10压力之一后，一次资格消费；再恢复/强制 `.1001` 不重复支付。金币不足50时付费选项不可执行；NPC已死亡时恢复只清旧记录，不收费、不换NPC、不领奖；旧A窗口不关闭新B约定。由旧版本排队且缺原对象变量的窗口可关闭，不补发不可靠奖励。

已有真品时用7.1传承调试入口，选择公开取向；仅在测试副本清五年入口冷却，再次打开改选学术：

```text
effect remove_character_flag = rol_relic_legacy_transition_cooldown
effect rol_relic_legacy_debug_transition_effect = yes
```

预期当前100金币门槛有效，三种传承取向最多留一种；转手后旧窗口不清当前修正、不付款、不领奖。不要用清冷却来验证正常五年触发频率。

### 16.5 数值、定时与日志交付

最小先抽查Mars用途与Naxos训练，再按12–15节测一次真实181天等待并在180天前保存/读档；取消、原物品转手和旧编号事件都不兑现新项目。三种研习、守信/失信、传承取向、物品两用途和Naxos两训练各自互斥；基底/阶位/碎片是独立累计来源。

观察四件真品同时装备的实际收益、卸下后的消失，以及Naxos兵团4人/级的伤亡与维护。成本表与参考成功率见 `rol_success_model.md`；有限样本不能证明81%或90%的真实总体通过率。

手测反馈保存：测试前后存档、操作顺序、模组清单/顺序、失败界面和当前会话相关 `error.log` / `game.log` 中 `rol_` 或 `[ROL]` 行。不要删除原日志或正式缓存，不要求已有原版错误的日志全空；检查本次动作后是否新增RoL错误。

## 17. 链路验收与旧窗口回归（2026-10-07）

本轮详细证据与新增/精简建议见 [链路审计](rol_path_audit_20261007.md)。200个选项的源码见证不替代游戏手测；这份清单优先检查真实入口与跨系统衔接。用独立副本；测试过时窗口后读回测试前存档，避免把人为状态带入正式游戏。

### 17.1 各入口到成果

| 场景 | 操作 | 预期 |
|---|---|---|
| 发现 | 当前持有Roma/Munchen/Naxos/Sevilla/Tunis之一，`event rol_relic_discovery.0001`；另正常取得Thera/Qartajana | 对应传说与活动出现，头衔变化回调不影响别的模组；发现按钮后从原版活动界面规划 |
| 五链主线 | 每链真正规划、旅行、抵达并逐关选择；高属性走有利分支；另留低属性/受损进度副本 | Rome4/Naxos3/其他2关，完整/部分/失败收束；真品或Naxos资格只给一次；阶段不会无后继停住 |
| 部分重试 | 真实部分结算、复盘，等待两年再开同地活动；另开其他地区作对照 | 冷却结束能重试；同地十年笔记消费且显示+5个百分点，其他地区不消费；旧结算窗口不重复给XP |
| 同行 | 邀请实际合格宾客，选学者/护卫/交涉者；护卫75金币开局；归来充分履约/暂缓重开各一次 | 候选真正在场，原NPC肖像/付款一致；学者+3个百分点，护卫替首关；履约后旧记录不能处理新合同 |
| 跨链 | 持有星界球→安排观测→181天记录成果→星盘活动；星盘航路→Naxos重复 | 不必先占目的地也能听说并规划；40金币图表首关实际可选且一次消费，仍需完成后续关卡 |
| 用途 | 每件两用途至少抽查切换、停止、成果延期后“查看圣物用途成果”、转手原物品 | 50金币/年冷却有效；180天内无成果，第181天后10XP或100威望一次兑现；旧编号不兑现新项目 |
| 碎片 | 持实际真品走正式决策，每次120金币，二年后第二次；失败/取消/转手另留副本 | 两级加在原物品，一级保留，满二级不再可升级；失败收束；类型或归属变动不改选替代品 |
| 连续五链 | 同一角色完成五链，再重放圆环；或赠送最后一件真品给接近完成的继承人 | 四/五链分别500/1000宗族威望一次；家族修正不被重复续期；最后一项换主也检查圆环 |
| 继承 | 有笔记、图表、未履行同行约定时真实死亡→继承→档案/约定延期→相应决策重开 | 继承人可接续原人物、原条款；付款不给前任已赚XP；副本五年且可消费到下一远征；保存/读档后仍有效 |

需要快速配置主线的测试角色时，可在已有测试副本上使用第6节真实活动scope命令；它只检查结算，**不能代替17.1的逐关点击**。付费入口都应观察点击前后即时金币，而不是日常月收入。

### 17.2 四个年度旧窗口

仅在角色已有真品/Naxos资格的独立测试副本上，清相应冷却并触发一个事件：

```text
effect remove_character_flag = rol_relic_legacy_duty_cooldown
event rol_relic_legacy.0001
effect remove_character_flag = rol_relic_legacy_study_cooldown
event rol_relic_legacy.0002
effect remove_character_flag = rol_naxos_review_cooldown
event rol_relic_legacy.0101
effect remove_character_flag = rol_naxos_veteran_cooldown
event rol_relic_legacy.0102
```

每次只测试一个窗口。正常第一选项保持原奖励/费用：`.0001` +100威望/+15压力；`.0002` 50金币换125威望；`.0101` 40金币换100威望；`.0102` 75金币换150威望。第二选项保持原效果。清冷却只用于构造回归，不证明真实年度频率。

窗口打开后暂停，以 `gold -100` 等扣款把余额降到不足对应费用，再点击原付费项。预期按钮失效或不收费/领奖，金币不因旧选择变负；仍可选非付费项。另赠送窗口选中的原圣物，或在Naxos测试副本上：

```text
effect remove_character_flag = rol_naxos_unit_unlocked
```

预期失效的窗口可“了结此事”，没有威望、虔诚、压力收益。即使还持有另一件真品，旧窗口不改用它。升级前已有打开的旧年度窗口缺新编号时，也应安全关闭，不强行补奖。

在允许多个事件排队的游戏模式下，可在尚未回答A时清对应冷却、再触发同类B，随后点击A：预期A不消费B，不付费/领奖；B仍能正常回答一次。真实能否同时保留事件窗口及存读档后的编号，要以游戏界面为准；无法构造时记录该限制，不把模型结果当实测。

### 17.3 同行、竞争者、换主的旧约定

同行A归来后，打开“结清远征约定”，再用同一决策或以下命令将同一A排队；结清一份，再真正开启后续远征并订立B。同一NPC再次签约也要抽查：

```text
event rol_expedition_companion.0002
```

在B归来后，点击保留的旧A充分履约/补偿/拒绝/关闭：预期不扣钱、不给经验/声誉、不付给B、不取消B。再用恢复决策正常处理B，原人物可收款。无新编号的旧存档待结算约定通过决策重开后应有效；旧NPC死亡时可关闭且不奖经验。

竞争者A订约后，用恢复入口保留另一份A，在结清后通过真实下一远征再次与相同NPC建立B：

```text
effect rol_rival_reopen_pact_effect = yes
```

预期旧A任何选项都不领取或取消B；恢复B仍是同一NPC，一次正常兑现。传承取向也按16.4清冷却构造A/B，旧A不能替换新B取向或发宗族威望。所有这些场景需至少一次保存/读档，确认新编号和原人物scope由引擎保留。

本轮新编号不需要清零。结束此组人为回归后读回测试前副本，再按正常五年/年度触发观察。兼容前缀仍优先按16.1；现场能力、装备加成、原生回调次序和真实到期均待你的手测。

## 18. Gemini内容合入与审计修复（2026-10-16）

本节使用独立测试存档。代理只执行静态与源码模型，以下游戏操作由维护者完成。旧版原始报告保留在 `rol_gemini_audit_20261016.md`，当前规则以 `rol_success_model.md` 和本节为准。

### 18.1 筹备与失败补救

同一角色分别规划标准和至尊活动，确认四档说明完整换行，实际支付价格按第6节。至尊出发后，Rome/Munich/Naxos/Sevilla/Carthage的基础起点应为35/40/35/40/40，基础压力减15；相对标准多5分，不应在抵达前被初始化覆盖。五地任取一地做引擎抽查即可，五条源码接线已逐一验证。

用未加经验的探寻者和任一轨道60XP的探寻者各观察一次真实阶段失败：

```text
add_trait rol_relic_seeker
effect add_trait_xp = { trait = rol_relic_seeker track = rol_exploration value = 60 }
```

第一条命令单独执行对应新手资格；第二条提升到继续资格。新手危机窗口只有保全与撤退；60XP、已消耗同地区笔记或实际在场老搭档才可付50金币/10基础压力继续。继续只恢复本次检定扣分后再加10，不因原损失为0或5而多赚进度；原伤病、威望和压力代价不回滚。保全应显示Tier2/3且最高Tier3，给20复盘XP、五年证据、十年同地笔记和两年冷却，没有唯一奖励/完整完成flag；撤退按当前按钮提示结算。

危机打开后保存/读档，确认资格仍可用一次。若能保留多窗口，将旧活动的危机窗口留到新活动再次触发危机后再关闭或选择：旧窗口不得付费、奖励、推进或清掉新资格，新窗口仍能完成。升级前已经打开、缺少编号的旧窗口只能中性关闭，然后从“重新评估远征危机”决策恢复原抉择；从旧版排队后才打开的有效危机会初始化编号，未记录检定损失时只允许保全/撤退，避免猜测损失。

### 18.2 碎片共鸣与诸圣教义

用第12节真实碎片决策完成一次升级，检查三种共鸣任选其一，修改/5XP和额外威望、虔诚、生活经验或减压均只兑现一次。精铸成功额外花50金币、失败额外花25金币，失败保留两年修正，不再描述为相对旧版花费减半。

可从“选择待定的残片共鸣”决策恢复。以下命令也只重新打开尚未消费的原共鸣资格，不发放新资格、不升级物品；待选择期间其他碎片远征决策会显示先完成共鸣的要求：

```text
effect rol_fragment_review_resonance_effect = yes
```

裸调 `event rol_relic_fragment.0002` 不负责建立新编号或新资格；使用上述effect保留正确窗口编号。可在未回答时重开一次，先回答其中一份，再点击另一份，确认所有即时奖励都不重放。再完成真实第二级升级，保留的旧一级窗口不得消费第二级资格；失效关闭也不得清掉第二级pending。上述场景至少抽查一次存读档。

可在独立存档中用以下命令取得四件物品，再从决策面板选择“校勘诸圣共鸣”：

```text
effect rol_debug_grant_all_artifact_relics_effect = yes
```

该调试命令会新建物品，不应反复执行。共鸣花费100金币、五年冷却、十年教义、15对应XP；古帝国组合为剑+金面/禁军，寰宇组合为球+星盘，其余任意双来源可选万邦。新教义替换同组旧教义，不与同组三种叠加；它代表已学会的知识，之后失去圣物仍保留到期。旅行安全+10是数值点数。窗口打开后失去资格、保留旧窗口直到下一轮等情形均不得重复领奖。

### 18.3 圆环点击顺序与旧存档迁移

用五链已完成且圆环尚未领奖的测试副本，分别按“四重→五重”和“五重→四重”两种顺序回答。两次均应总计1500宗族威望、两种独立宗族修正，最终个人只有五重；重复调事件不得重新发奖或刷新家族修正。第五重先回答时会一并结清尚未领取的四重独立奖励，后续四重窗口无额外收益。

旧存档已有四重/五重两个个人修正时，自动迁移在下次年度持有者pulse或圆环检查执行；无需等待、仅修状态的入口为：

```text
effect rol_legend_circle_migrate_effect = yes
```

这里“只修状态”指不改货币和奖励，命令会清旧四重个人修正并补已领奖标记。连续执行两次，宗族威望和家族/宗族修正期限均不变；个人最终只剩五重。不要清除已领奖flag来测试迁移，否则人为改变了旧存档证据。结束后读回测试前副本。

## 19. 系统深化：任务身份、原竞争者与家族底本（2026-10-27）

本节由维护者在独立测试存档执行，代理没有启动CK3。基础加载后先检查新增决策的中文名称与数值提示；模型检查不代替事件scope、出席者和house变量的实际保存。

### 19.1 碎片挑战恢复

持有合格真品并用第12节的正式120金币决策开始碎片任务后，可通过“重阅未决的碎片远征”免费重开；对应命令为：

```text
effect rol_fragment_review_route_effect = yes
```

恢复始终指向原物品，不再次收费或生成新任务。完成一份窗口后，另一份不能重复增加物品等级、奖励、精铸修正或压力变化。再开启同一物品第二级或另一物品任务，旧挑战/取消/关闭按钮均不能动新任务；新任务可通过决策正常处理。

打开挑战后转出原物品，结束应无奖励且不选另一物品替代。旧存档未编号的待处理任务通过恢复入口初始化一次；已有新任务时，旧窗口不能借打开动作改绑。抽查一次保存/读档；界面无法同时保留多窗口时记录该限制。

### 19.2 原竞争者重逢

一次真实远征与A合作并结清契约后，在十年内安排另一条未完成远征，让A实际出席。竞争者插曲若触发应优先是A，并出现“共同考据”选择；确定增加5进度、原NPC双方尊重，无额外专长XP。重复旧窗口不能再推进。

通过竞争或拒绝契约形成A积怨后，再遇本人可付50金币调解；金币付给A，转为十年合作，无进度/XP奖励。将余额降至不足50再点击旧付费项，应不付款、不改变关系。调解后的后续相遇走合作选项。

A缺席时应按普通竞争者处理，新人B没有A的专属重逢选择；A死亡、被囚、失能或已经是本场签约同行时，不扮演本场竞争者。没有人物指针的旧合作/积怨标记不推定为新NPC。暂时缺席不删除仍有效的A记忆；当前只保留最近一位有合作/积怨的竞争者。

跨活动保留旧竞争者窗口时，旧窗口不能消费新活动遭遇，即使新旧都是A。实际邀约、肖像、十年到期与原NPC指针至少抽查一次存读档。

### 19.3 家族底本与刊印

用已有部分成功笔记或用途研究图表测试。只需准备一类知识；没有现成资料时，独立测试副本可用：

```text
effect add_character_modifier = { modifier = rol_expedition_mars_notes_modifier years = 10 }
```

从决策“编修家族底本”打开菜单，选择Mars笔记：普通角色支付100金币，考据100XP支付50金币；知识副本保留，同家同类再点不收费。大师角色的准备命令为：

```text
add_trait rol_relic_seeker
effect add_trait_xp = { trait = rol_relic_seeker track = rol_research value = 100 }
```

用同家继承人或当前角色（先消耗/到期对应笔记）选择“刊印家族资料”，支付40金币，获得五年资料并揭示对应远征入口。当前已有副本不能付费续期；所有七类共用个人三年刊印冷却。五地笔记仍在对应地区启程消耗，图表仍在Sevilla/Naxos的40金币首关选择消耗。任取一条真实活动检查印本进入既有消费者即可。

菜单打开后将金币降到不足，再点击付费项应不收费、不添收藏/副本。换到另一house后，旧菜单不能访问原house；同家其他人物可刊印，异家人物不能。新家族分支从空收藏开始；死亡档案和个人XP保持原流程，底本本身不提供角色属性或完成记录。

编目后保存并重载，切到同家继承人确认收藏仍在；三年冷却到期与五年副本到期至少各检查一次。这一组验证house持久变量与实际日历，静态模型仅模拟其契约。

## 20. 原人物观测委托与大师取舍（2026-10-27，第二批）

### 20.1 委托星界球观测

用持有星界球的独立测试存档。先履行一次真实同行契约，取得仍在本人宫廷的老搭档；其须成年、存活、未被囚禁/失能、学习至少12且对本人好感非负。从“安排圣物用途”选择星界球，检查委托按钮显示这位老搭档的姓名。原两种用途仍可正常选择。

委托原价50金币立项，等待180天，第181天打开成果。付款项另转50金币给原观测者：对方获得10考据经验，缺少探寻者特质时一并取得；自己获得十年星界观测图并揭示Sevilla，双方五年+10好感，自己没有XP或100威望。公开署名则只给原观测者100威望及双方五年+25好感，自己没有星图/XP/威望，对方也没有研究XP。

将金币降至不足50时，付款项不得扣款/培养/发图，仍可公开署名或暂缓。暂缓后用原“整理圣物用途成果”决策恢复；可用命令只重开已经成熟的当前项目，不跳过等待：

```text
effect rol_relic_use_reopen_effect = yes
```

项目中老搭档记录换成B，成果仍属于原观测者A；A后期学习/好感降低不撤销原约定。A死亡、离廷、被囚或失能时无奖关闭；换主/停止用途也不退款、不替换另一物品、不清原冷却。等待期与成熟各保存/读档一次，检查原人和编号仍在。第二个同人项目开始后，旧窗口不得付款、署名或清掉新项目。项目/未付报酬不继承，已得到的星图仍走原档案与家族底本。

### 20.2 探险大师亲自带队

在独立存档准备100探险经验：

```text
add_trait rol_relic_seeker
effect add_trait_xp = { trait = rol_relic_seeker track = rol_exploration value = 100 }
```

真实活动主阶段失败后，危机应增加“由我亲自带队绕行”。它不花金币（负债也可选），增加25基础压力；与原50金币/10基础压力继续共用同一次危机。两者都只补回本次实际扣去的0/5/10进度，再增加10，保留等待时其他插曲的变化，照常进入下一阶段。不立即给XP，不保证后续检定或免除Tier4门槛。

99探险、仅其他轨道100或没有探寻者特质时不能使用；缺真实损失记录的旧危机也不开放。选一条后，旧窗不能再选另一条；后续新活动有新危机时，旧编号窗口不改变新资格。基础压力受原版人物倍率影响，先比较提示中的基础25，不把修正后的数值当作脚本出错。

### 20.3 交涉大师公开护卫功绩

给同一测试角色交涉100经验：

```text
effect add_trait_xp = { trait = rol_relic_seeker track = rol_negotiation value = 100 }
```

与实际护卫签约并完成至少一个阶段，归来可用100威望公开其功绩。自己扣100威望、同一护卫加100，双方五年+10好感，保存原老搭档；无金币转移、额外XP或新增守信声誉。原50金币充分履约、25金币补偿、拒约与暂缓保留。

威望99、交涉99、其他角色职责、无阶段进展或继承约定时不开放。死者不替换收款人，原编号/原人物失效时不能付给新护卫。暂缓恢复及同NPC后续新约各抽查一次；旧窗口不能消费新约。以上菜单、原NPC和编号仍须游戏scope/存读档确认。

## 21. 远征日志与原贡献者（2026-10-27，第三批）

本批不新增费用、概率、奖励或事件选项。用既有测试存档进行一场活动，在活动日志和结算页查看新条目；原版结算筛选仍决定展示顺序。

- 选择护卫稳定开局时，日志应记录原护卫姓名；专长开局应写本人筹划，不能因为护卫也在场就抢记护卫贡献。星界观测图/爱琴海图分别记录正确图表消费。资金不足、原护卫离队/死亡或首关已用时，不新增成功记录。
- 同地笔记在出发时消费，应有对应地区的使用记录；部分成功实际留下新笔记时，另有对应地区十年资料和下一次用途记录。其他地区的笔记不被记录为已经使用；旧存档没有实际取得新资料时不回填历史。
- 实际老搭档重逢、交涉者化解争执、旧竞争者共同考据与50金币和解，各自记录原人。窗口回答后，即使老搭档变量改成B，已经完成的A贡献仍属于A。
- 危机付费继续、大师绕行、保全、撤退分别写明处理方式。选择之后的重复/旧编号窗口不能再记一次成功，也不能把另一个新活动的危机写到旧记录里。

保存/读档后检查上述原人姓名，确认没有裸本地化key或空姓名。结算页应保留原完整/部分/失败记录，新贡献条目与原阶段日志并存。Rome以外的开始、推进和撤离不再统一写“地宫”。静态契约覆盖接线与记录身份，日志排版、原版筛选和人物名称持久化由本节手测确认。
