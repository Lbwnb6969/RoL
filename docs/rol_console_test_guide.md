# RoL 控制台测试指南 / 调试 / 重置

> 真源目录：`C:\CK3Mods\RoL`  
> 当前覆盖 Rome、Munich、Naxos / Thera、Sevilla 四条主线。

---

## 0. 调试模式

1. 如需观察 debug toast，先开启调试模式：

```txt
effect rol_relic_debug_enable_effect = yes
```

2. 测完后可关闭：

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

如果需要连续测试多个事件，直接依次输入即可。

---

## 2. 发现层测试

### 2.1 统一发现入口

```txt
event rol_relic_discovery.0001
```

### 2.2 直接测试各发现事件

```txt
event rol_relic_discovery.1000   # Rome
event rol_relic_discovery.1300   # Munich
event rol_relic_discovery.1400   # Naxos / Thera
event rol_relic_discovery.1500   # Sevilla
```

---

## 3. 四条活动链测试

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

> 泰拉链的成功结果是 **解锁兵种招募权限**，不是直接生成兵团。

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

### 3.5 活动规划 UI：统一“人员与装备等级”模块

在分别给四条链加上对应 `rol_heard_*` flag、移除领取 flag / cooldown 后，手动打开活动规划界面，检查以下内容：

| 活动 | `low` 总价 | `standard` 总价（默认） | `high` 总价 | `supreme` 总价 |
|---|---:|---:|---:|---:|
| Rome | `180` | `300` | `750` | `1900` |
| Munich | `280` | `400` | `850` | `2000` |
| Naxos / Thera | `230` | `350` | `800` | `1950` |
| Sevilla | `280` | `400` | `850` | `2000` |

手动验证点：
- 四条活动都出现 `人员与装备等级` 分类（脚本 ID：`rol_option_expedition_preparation`）。
- 默认选项为 `standard`。
- 活动主描述 / host_desc / selection_tooltip 不再直接写明圣物 / 兵种奖励，也不再写“低于 Tier4 视为失败”。
- 活动选项描述会明确写出：成功率变化 + 成功后额外 `prestige / dynasty prestige`。
- 四档切换时，总价应与上表一致；图标应显示 `gfx/interface/icons/activity_option_categories/rol_option_expedition_preparation.dds`。


---

## 4. 圣物直发 / 统一测试入口

> 这里只覆盖三件 artifact 圣物；不包含泰拉禁军解锁。

### 4.1 单件直发

```txt
effect rol_create_blade_of_mars_effect = yes
effect rol_create_nibelung_star_sphere_effect = yes
effect rol_create_astrolabe_of_ocean_effect = yes
```

### 4.2 统一直发入口

```txt
effect rol_debug_grant_all_artifact_relics_effect = yes
```

执行后会直接生成 Rome / Munich / Sevilla 三件圣物，便于测试 UI、本地化与显示覆盖。

---

## 5. 成功结算模拟

> **注意**：直接触发 `event rol_quest_*.1001` 时通常没有 `scope:activity` 上下文。  
> 若要稳定测试 Tier4 发奖 / 成功 finalize，请优先使用 effect 方式模拟。

### 5.1 Rome：模拟成功结算

```txt
effect remove_character_flag = rol_mars_blade_claimed
effect rol_create_blade_of_mars_effect = yes
effect rol_rome_quest_success_finalize_effect = yes
```

### 5.2 Munich：模拟成功结算

```txt
effect remove_character_flag = rol_nibelung_sphere_claimed
effect rol_create_nibelung_star_sphere_effect = yes
effect rol_munich_quest_success_finalize_effect = yes
```

### 5.3 Naxos / Thera：解锁禁军

```txt
effect remove_character_flag = rol_naxos_unit_unlocked
effect rol_naxos_quest_success_finalize_effect = yes
```

执行后到军事界面检查 `rol_adeptus_custudes`；当前版本 **不再需要 Accolade**，只要成功解锁即可招募（仍受文化禁用限制约束）。

### 5.4 Sevilla：模拟成功结算

```txt
effect remove_character_flag = rol_astrolabe_of_ocean_claimed
effect rol_create_astrolabe_of_ocean_effect = yes
effect rol_sevilla_quest_success_finalize_effect = yes
```

### 5.5 筹备档位成功奖励验证

1. 记录当前角色的 `[prestige|E]` 与 `[dynasty_prestige|E]`。
2. 正常进入任意一条活动，并分别测试 `low / standard / high / supreme`。
3. 在相同能力档位下，观察随机检定 option：
   - 现在只显示定性风险文本；
   - 额外会出现当前筹备提示（更困难 / 无修正 / 更容易 / 显著更容易）。
4. 仅当远征最终达到各链 Tier4 时，才会拿到最终奖励；低于终局门槛时统一失败并进入 2 年冷却。
5. 成功结算后对比额外收益：
   - `low`：无额外奖励
   - `standard`：无额外奖励
   - `high`：额外 `+150 prestige / +25 dynasty prestige`
   - `supreme`：额外 `+350 prestige / +50 dynasty prestige`

### 5.6 四链全通总事件 / 老档回填验证

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
- 事件背景为 `rol_bg_legend_circle_revelation`
- 关闭事件后获得：
  - 角色永久 modifier：`rol_legend_circle_conqueror_modifier`
  - House 75 年 modifier：`rol_legend_circle_house_modifier`
  - Dynasty 100 年 modifier：`rol_legend_circle_dynasty_modifier`
  - 额外 `+500 dynasty prestige`
- 再次执行 `effect rol_check_legend_circle_revelation_effect = yes` 不会重复触发


---

## 6. 失败收口测试

```txt
effect rol_rome_quest_fail_now_effect = yes
effect rol_munich_quest_fail_now_effect = yes
effect rol_naxos_quest_fail_now_effect = yes
effect rol_sevilla_quest_fail_now_effect = yes
```

这些命令会添加 2 年冷却并弹出失败 toast。

---

## 7. 重置命令

### 7.1 通用 recent result 清理

```txt
effect rol_relic_clear_recent_result_effect = yes
```

### 7.2 Rome

```txt
effect remove_character_flag = rol_heard_mars_legend
effect remove_character_flag = rol_mars_blade_claimed
effect remove_character_modifier = rol_mars_quest_cooldown_modifier
effect if = { limit = { has_variable = rol_rome_stage_count } remove_variable = rol_rome_stage_count }
```

### 7.3 Munich

```txt
effect remove_character_flag = rol_heard_nibelung_legend
effect remove_character_flag = rol_nibelung_sphere_claimed
effect remove_character_modifier = rol_nibelung_quest_cooldown_modifier
effect if = { limit = { has_variable = rol_munich_stage_count } remove_variable = rol_munich_stage_count }
```

### 7.4 Naxos / Thera

```txt
effect remove_character_flag = rol_heard_naxos_legend
effect remove_character_flag = rol_naxos_unit_unlocked
effect remove_character_modifier = rol_naxos_quest_cooldown_modifier
effect if = { limit = { has_variable = rol_naxos_stage_count } remove_variable = rol_naxos_stage_count }
```

### 7.5 Sevilla

```txt
effect remove_character_flag = rol_heard_astrolabe_legend
effect remove_character_flag = rol_astrolabe_of_ocean_claimed
effect remove_character_modifier = rol_astrolabe_quest_cooldown_modifier
effect if = { limit = { has_variable = rol_sevilla_stage_count } remove_variable = rol_sevilla_stage_count }
```

---

## 8. 活动 UI 不显示时先检查

需要满足：
- Rome：`rol_heard_mars_legend` 且未 `rol_mars_blade_claimed`
- Munich：`rol_heard_nibelung_legend` 且未 `rol_nibelung_sphere_claimed`
- Naxos：`rol_heard_naxos_legend` 且未 `rol_naxos_unit_unlocked`
- Sevilla：`rol_heard_astrolabe_legend` 且未 `rol_astrolabe_of_ocean_claimed`

如果仍不显示，依次检查：
1. 是否先执行了对应 `event` 或 added heard flag
2. 是否存在 `*_quest_cooldown_modifier`
3. 是否处于战争、未成年、被囚禁或 incapacity 状态
4. Sevilla 活动是否已被 `c_sevilla` 地点锁定

---

## 9. 常见问题

- `not a valid id`：通常是脚本未重新载入，或你改动的是错误目录而不是真源目录。
- 直接触发 `event rol_quest_*.1001` 看不到正常终局：因为没有活动上下文，先按第 5 节模拟成功结算。
- 泰拉活动成功后看不到兵种：执行 `effect rol_naxos_quest_success_finalize_effect = yes` 后，再到军事界面确认 `rol_adeptus_custudes` 是否可招募。
- 没有 debug toast：检查是否已开启 `effect rol_relic_debug_enable_effect = yes`。
- 背景 / 图标 / 界面缓存异常：删除 `Documents/Paradox Interactive/Crusader Kings III/gfx` 后完全重启启动器与游戏。