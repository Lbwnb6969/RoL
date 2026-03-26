# RoL 控制台测试指南 / 调试 / 重置

> 真源目录：`C:\CK3Mods\RoL`  
> 当前覆盖五条正式主线：Rome / Munich / Naxos / Sevilla / Carthage

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

### 5.4 Carthage 槽位验证
```txt
effect remove_character_flag = rol_ash_forged_mask_claimed
effect rol_create_ash_forged_mask_effect = yes
```

预期：
- 新生成的 `rol_ash_forged_mask` 出现在 **helmet / 头具** 槽

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