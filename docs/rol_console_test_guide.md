# RoL 控制台测试指南 / 调试 / 重置

> 真源目录：`C:\CK3Mods\RoL`  
> 当前覆盖五条正式主线：Rome / Munich / Naxos / Sevilla / Carthage
> 当前不再维护 `Documents\Paradox Interactive\Crusader Kings III\mod\RoL` 内容镜像；只检查 `RoL.mod` 的 `path` 与 `Documents\Paradox Interactive\Crusader Kings III\gfx` 缓存。

---

## 0. 调试模式

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
- 旧存档历史实例若异常，删旧物后重新发放再测
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
  - `travel_speed_mult = 0.15`
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

## 6. 成功结算模拟

> 直接 `event rol_quest_*.1001` 时通常没有 `scope:activity`。  
> 若要稳定测试成功 finalize，请优先用 effect。

### 6.1 Rome
```txt
effect remove_character_flag = rol_mars_blade_claimed
effect rol_create_blade_of_mars_effect = yes
effect rol_rome_quest_success_finalize_effect = yes
```

### 6.2 Munich
```txt
effect remove_character_flag = rol_nibelung_sphere_claimed
effect rol_create_nibelung_star_sphere_effect = yes
effect rol_munich_quest_success_finalize_effect = yes
```

### 6.3 Naxos / Thera
```txt
effect remove_character_flag = rol_naxos_unit_unlocked
effect rol_naxos_quest_success_finalize_effect = yes
```

### 6.4 Sevilla
```txt
effect remove_character_flag = rol_astrolabe_of_ocean_claimed
effect rol_create_astrolabe_of_ocean_effect = yes
effect rol_sevilla_quest_success_finalize_effect = yes
```

### 6.5 Carthage
```txt
effect remove_character_flag = rol_ash_forged_mask_claimed
effect rol_create_ash_forged_mask_effect = yes
effect rol_carthage_quest_success_finalize_effect = yes
```

### 6.6 筹备档位奖励验证
1. 记录当前角色的 `[prestige|E]` 与 `[dynasty_prestige|E]`。
2. 正常进入任意一条活动，分别测试 `low / standard / high / supreme`。
3. 在同一能力档位下，观察 RNG option：
   - 百分比会随筹备档位变化
   - low 更难，high / supreme 更容易
4. 最终仍只有达到各链 Tier4 才能拿到最终奖励。
5. 成功结算后对比额外收益：
   - `low`：无额外奖励
   - `standard`：无额外奖励
   - `high`：`+150 prestige / +25 dynasty prestige`
   - `supreme`：`+350 prestige / +50 dynasty prestige`

### 6.7 四链全通总事件 / 老档回填
```txt
effect add_character_flag = rol_mars_blade_claimed
effect add_character_flag = rol_nibelung_sphere_claimed
effect add_character_flag = rol_naxos_unit_unlocked
effect add_character_flag = rol_astrolabe_of_ocean_claimed
effect remove_character_flag = rol_legend_circle_revealed
effect rol_check_legend_circle_revelation_effect = yes
```

预期：
- `1` 天后触发 `rol_legend_circle.0001`
- 该总事件仍只认旧四条核心主线
- **Carthage 不会影响该总事件触发条件**
- 事件背景继续读取 `rol_bg_legend_circle_revelation`

---

## 7. 失败收口测试

```txt
effect rol_rome_quest_fail_now_effect = yes
effect rol_munich_quest_fail_now_effect = yes
effect rol_naxos_quest_fail_now_effect = yes
effect rol_sevilla_quest_fail_now_effect = yes
effect rol_carthage_quest_fail_now_effect = yes
```

这些命令会添加 2 年冷却并弹出失败 toast。

---

## 7.1 Legacy 2.0 / 竞争者 / 碎片系统

### 圣物换主事件

```txt
effect rol_create_blade_of_mars_effect = yes
event rol_relic_legacy.0003
```

预期：事件显示 `rol_bg_relic_legacy_transfer`，并提供公开传承、秘密藏匿、学者研究三种选择；同一角色五年内不会重复触发换主事件。

### 碎片远征最小 smoke

```txt
effect add_character_flag = rol_mars_blade_claimed
effect rol_create_blade_of_mars_effect = yes
effect add_character_flag = rol_fragment_route_mars
event rol_relic_fragment.0001
```

预期：事件显示 `rol_bg_fragment_expedition`；成功后给当前 Mars artifact 追加一级 modifier，并在一天后显示 `rol_bg_fragment_upgrade` 的确认事件。再次使用同一路线可追加二级 modifier；失败会增加压力并清除 route flag。

其余三条路线只需替换 artifact 创建 effect 和 route flag：

- `rol_create_nibelung_star_sphere_effect` + `rol_fragment_route_nibelung`
- `rol_create_astrolabe_of_ocean_effect` + `rol_fragment_route_astrolabe`
- `rol_create_ash_forged_mask_effect` + `rol_fragment_route_ash`

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

- `not a valid id`：通常是脚本没重载，或你改的是错误目录而不是真源目录。
- 直接 `event rol_quest_*.1001` 看不到正常终局：因为没有活动上下文，优先用第 6 节的 finalize effect。
- 泰拉活动成功后看不到兵种：执行 `effect rol_naxos_quest_success_finalize_effect = yes` 后，再到军事界面确认 `rol_adeptus_custudes` 是否可招募。
- 没有 debug toast：先执行 `effect rol_relic_debug_enable_effect = yes`。
- 背景 / 图标缓存异常：删除 `Documents/Paradox Interactive/Crusader Kings III/gfx` 后，完全重启启动器与游戏。

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

真实活动中断、主办者死亡、延迟事件保存/读档和人物指针作用域仍须引擎确认。主办者死亡不把其个人经验或本轮约定自动继承给继承人；代际接续将在后续阶段单独实现。

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
