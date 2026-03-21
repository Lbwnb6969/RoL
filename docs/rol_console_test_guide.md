# RoL 控制台测试手册（事件调用 / 武器发放 / 成功结算）

> 适用目录：`C:\CK3Mods\RoL`  
> 适用当前内容：Rome（玛尔斯之剑）、Munich（尼伯龙根星界球）、Naxos/Thera（禁军解锁）

---

## 0. 测试前准备

1. **完全退出游戏和启动器后重开**（防止脚本缓存）。
2. 确认你在测试角色（玩家角色）上执行命令。
3. 建议先开调试追踪（可看到链路是否生效）：

```txt
effect rol_relic_debug_enable_effect = yes
```

关闭调试：

```txt
effect rol_relic_debug_disable_effect = yes
```

---

## 1. 最常用命令格式

```txt
event 事件ID
```

```txt
effect 某个脚本效果 = yes
```

如果要对指定角色触发事件（可选）：

```txt
event 事件ID 角色ID
```

---

## 2. 先测“发现事件”是否正常

### 2.1 通用入口（自动检测）

```txt
event rol_relic_discovery.0001
```

### 2.2 各地区发现弹窗（直测）

```txt
event rol_relic_discovery.1000   # 罗马
 event rol_relic_discovery.1300   # 慕尼黑
 event rol_relic_discovery.1400   # 纳克索斯/泰拉
```

---

## 3. 任务链事件调用（逐条点测）

## 3.1 罗马链（Mars）

先给前置传说标记：

```txt
effect add_character_flag = rol_heard_mars_legend
 effect remove_character_flag = rol_mars_blade_claimed
```

按流程测试：

```txt
event rol_quest_rome.0990
 event rol_quest_rome.1000
 event rol_quest_rome.1002
 event rol_quest_rome.1003
 event rol_quest_rome.1004
 event rol_quest_rome.1001
 event rol_quest_rome.1090
```

## 3.2 慕尼黑链（Nibelung）

```txt
effect add_character_flag = rol_heard_nibelung_legend
 effect remove_character_flag = rol_nibelung_sphere_claimed

 event rol_quest_munich.0990
 event rol_quest_munich.1000
 event rol_quest_munich.1002
 event rol_quest_munich.1001
 event rol_quest_munich.1090
```

## 3.3 泰拉链（Naxos / Thera）

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

---

## 4. 直接“调用武器/礼器”测试（最快）

> 这部分不依赖活动进度，纯测试 artifact 创建是否成功。

```txt
effect rol_create_blade_of_mars_effect = yes
 effect rol_create_nibelung_star_sphere_effect = yes
```

---

## 5. 用“成功结算效果”模拟最终成功

> **重点**：`event rol_quest_*.1001` 直接手动触发时，通常没有 `scope:activity` 进度上下文，
> 会走“低于Tier4失败分支”。这是正常现象。  
> 你要测“成功拿奖励”，请用下面效果。

### 5.1 罗马：模拟成功拿玛尔斯之剑

```txt
effect remove_character_flag = rol_mars_blade_claimed
 effect rol_create_blade_of_mars_effect = yes
 effect rol_rome_quest_success_finalize_effect = yes
```

### 5.2 慕尼黑：模拟成功拿尼伯龙根星界球

```txt
effect remove_character_flag = rol_nibelung_sphere_claimed
 effect rol_create_nibelung_star_sphere_effect = yes
 effect rol_munich_quest_success_finalize_effect = yes
```

### 5.3 泰拉：模拟成功（解锁禁军兵种）

```txt
effect remove_character_flag = rol_naxos_unit_unlocked
 effect rol_naxos_quest_success_finalize_effect = yes
```

---

## 6. 失败分支与冷却测试

```txt
effect rol_rome_quest_fail_now_effect = yes
 effect rol_munich_quest_fail_now_effect = yes
 effect rol_naxos_quest_fail_now_effect = yes
```

---

## 7. 一键“重测前清理”命令（推荐每轮测试前跑）

### 7.1 通用清理

```txt
effect rol_relic_clear_recent_result_effect = yes
```

### 7.2 罗马重置

```txt
effect remove_character_flag = rol_heard_mars_legend
 effect remove_character_flag = rol_mars_blade_claimed
 effect remove_character_modifier = rol_mars_quest_cooldown_modifier
 effect if = { limit = { has_variable = rol_rome_stage_count } remove_variable = rol_rome_stage_count }
```

### 7.3 慕尼黑重置

```txt
effect remove_character_flag = rol_heard_nibelung_legend
 effect remove_character_flag = rol_nibelung_sphere_claimed
 effect remove_character_modifier = rol_nibelung_quest_cooldown_modifier
 effect if = { limit = { has_variable = rol_munich_stage_count } remove_variable = rol_munich_stage_count }
```

### 7.4 泰拉重置

```txt
effect remove_character_flag = rol_heard_naxos_legend
 effect remove_character_flag = rol_naxos_unit_unlocked
 effect remove_character_modifier = rol_naxos_quest_cooldown_modifier
 effect if = { limit = { has_variable = rol_naxos_stage_count } remove_variable = rol_naxos_stage_count }
```

---

## 8. 活动UI测试（不是只测事件）

活动显示前置：
- 罗马：`rol_heard_mars_legend` 且未 `rol_mars_blade_claimed`
- 慕尼黑：`rol_heard_nibelung_legend` 且未 `rol_nibelung_sphere_claimed`
- 泰拉：`rol_heard_naxos_legend` 且未 `rol_naxos_unit_unlocked`

如果你只看到事件连发、看不到活动窗口，先检查：
1. 是否真从活动入口启动（而不是只 `event` 触发链）
2. 是否在冷却中（对应 `*_quest_cooldown_modifier`）
3. 是否战争中 / 金币不足 / 已领取奖励标记

---

## 9. 常见报错速查

- `not a valid id`：通常是加载目录不对或未重启。
- 终局不发奖励：直接 `event .1001` 没有活动进度上下文，改用第5节方案。
- 想看每步是否生效：先执行 `effect rol_relic_debug_enable_effect = yes`。
