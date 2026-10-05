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
- 五条正式链维持 **Tier4-only + 严格高成功** 基线。
- **主阶段没失败 ≠ 自动 Tier4**；若某一主阶段只拿到 `medium / tiny` 成功，终局不保证过线。
- Naxos 的 `1000.b`（learning）与 `1003.b`（intrigue）在成功时也给予 `major`；任一成功路线都不会再因进度不足而注定失败。
- `1050` 宾客正向事件只作为**额外余量**，不是隐藏硬门槛。
- 终局判定、`store_success_result_effect`、`apply_tiered_bonus_reward_effect` 三层阈值必须一致。
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

以上 6 个 key 都能正常显示当前占位 DDS，不再黑底或丢失背景。

### 11.2 Regalia 图标污染回归
预期：
- `rol_nibelung_star_sphere_visual` 只读取 `rol_nibelung_star_sphere.dds`
- RoL 目录不再交付 `artifact_regalia.dds`
- 原版 / NPC 的 regalia 不再被 Nibelung 星界球封面污染

### 11.3 `@rol_legendary_icon!` 透明验证
1. 删除 `Documents/Paradox Interactive/Crusader Kings III/gfx`
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
