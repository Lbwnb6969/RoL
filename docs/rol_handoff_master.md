# RoL 新对话完整交接文档（Master Handoff）

> 当前快照日期：2026-10-07
> 真源目录：`C:\CK3Mods\RoL`  
> 当前启动器描述符：`C:\Users\Falcons的Niko本人的PC\Documents\Paradox Interactive\Crusader Kings III\mod\RoL.mod` -> `path="C:/CK3Mods/RoL"`

> 当前状态以 `PROJECT.md` 为准。全面审计已归档五个原版GUI/custom loc覆盖，装备品质/类型交由当前原版或用户UI模组，传奇徽记只挂RoL阶位modifier；禁止恢复退役界面。代理不启动游戏，本轮手测优先看控制台指南第16节，结算正例看第6节。下文早期ID直测不代表真实活动回归。

---

## 0) 当前项目基线

- 模组名称：**Relics of Legend（RoL）**。
- 唯一开发真源：`C:\CK3Mods\RoL`。
- Documents 目录不再维护任何 RoL 内容镜像；仅保留启动器 descriptor 与 CK3 缓存相关路径。
- 所有脚本 / 本地化文本统一 **UTF-8 with BOM**。
- 所有自定义 ID / 事件 / effect / trigger / 变量 / flag 保持 `rol_` 前缀。
- 当前目标游戏版本：**CK3 1.20.0.3**（“Crozier” / By God Alone）。
- 当前唯一正式发现入口：
  - `common/on_action/rol_relic_discovery_on_actions.txt`
  - `-> rol_relic_discovery.0001`
  - `-> 五条正式活动链`

---

## 1) 当前正式主线快照（2026-10-06）

| 地区 | Discovery | Activity | 最终结果 | 永久完成标记 | 是否计入 `rol_legend_circle` |
|---|---|---|---|---|---|
| Rome | `rol_relic_discovery.1000` | `activity_rol_seek_mars_blade` | 圣物 | `rol_mars_blade_claimed` | 是 |
| Munich | `rol_relic_discovery.1300` | `activity_rol_seek_nibelung_sphere` | 圣物 | `rol_nibelung_sphere_claimed` | 是 |
| Naxos / Thera | `rol_relic_discovery.1400` | `activity_rol_seek_naxos_guard` | 禁军解锁 | `rol_naxos_unit_unlocked` | 是 |
| Sevilla | `rol_relic_discovery.1500` | `activity_rol_seek_astrolabe_of_ocean` | 圣物 | `rol_astrolabe_of_ocean_claimed` | 是 |
| Carthage / Qartajana | `rol_relic_discovery.1600` | `activity_rol_seek_ash_forged_mask` | 圣物 | `rol_ash_forged_mask_claimed` | **否** |

### 当前四链全通总事件
- 事件：`rol_legend_circle.0001`
- 共享接口：
  - `rol_has_all_major_relic_completions_trigger`
  - `rol_check_legend_circle_revelation_effect`
- 只检查旧四条核心主线：
  - `rol_mars_blade_claimed`
  - `rol_nibelung_sphere_claimed`
  - `rol_naxos_unit_unlocked`
  - `rol_astrolabe_of_ocean_claimed`
- **Carthage 当前故意不接入** 该总事件。

---

## 2) 已落地工程规则

1. 真源只认 `C:\CK3Mods\RoL`。
2. 不在 Documents 下维护或修补第二份 RoL 内容副本；若需确认加载是否正确，只检查 `RoL.mod` 的 `path`。
3. CK3 文本文件统一 UTF-8 with BOM。
4. 先查现有实现与模板，再做最小改动。
5. 活动链固定遵循：**发现 -> 活动 -> 阶段反馈 -> 终局判定 -> 结算**。
6. 视觉问题排查顺序固定：**真实加载路径 -> 脚本/隐式接线 -> gfx 缓存 -> DDS 规格**。

---

## 3) 当前统一架构基线

### 3.1 统一“人员与装备等级”模块
- 分类：`rol_option_expedition_preparation`
- 四档：
  - `rol_expedition_preparation_low`
  - `rol_expedition_preparation_standard`
  - `rol_expedition_preparation_high`
  - `rol_expedition_preparation_supreme`
- 固定成本：`30 / 150 / 600 / 1750`
- 默认档：`standard`
- 成功率修正：`-10 / 0 / +10 / +20`
- 成功额外奖励：
  - `high = +150 prestige / +25 dynasty prestige`
  - `supreme = +350 prestige / +50 dynasty prestige`
- 五条正式活动链都应接入该模块。

### 3.2 活动 UI / 文案基线
- `host_intents` 当前默认只保留 `rol_relic_hunt_intent`。
- 所有可点击 option 必须带 `flavor = ...`。
- RNG 结果 tooltip 已通过 `rol_expedition_display_*_chance_value` 显示**精确成功 / 失败百分比**，并由静态审计覆盖 64 个挑战列表。
- “终止远征并进入 2 年冷却”只能写在 failure outcome 最底部一次。
- 活动主描述 / host_desc / selection_tooltip 不直接剧透最终奖励。

### 3.3 遗留入口状态
以下旧入口已移除，不再作为任何测试基线：
- `common/on_action/rol_on_actions.txt`
- `events/rol_trigger_events.txt`
- `common/decisions/rol_decisions.txt`
- `events/rol_test_events.txt`

### 3.4 五条正式活动链真实结算阈值基线（2026-10-06）

| 活动 | 起始进度 | 主阶段高成功参考值 | Tier4 | Tier3 | Tier2 |
|---|---:|---:|---:|---:|---:|
| Rome | `30` | `70` | `70` | `50` | `30` |
| Munich | `35` | `55` | `55` | `45` | `35` |
| Naxos / Thera | `30` | `60` | `60` | `45` | `30` |
| Sevilla | `35` | `55` | `55` | `45` | `35` |
| Carthage / Qartajana | `35` | `55` | `55` | `45` | `35` |

- 当前五条正式链都按“**Tier4 完整圣物 + Tier2/3 部分成功 + Tier1 以下失败**”收口。
- **主阶段没失败 ≠ 自动 Tier4**；若某段只拿到 `medium / tiny` 成功，终局会保留对应部分奖励并进入部分成功结算。
- `1050` 宾客正向事件的定位仍是**额外余量**，不是终局 Tier4 必需条件。
- 终局保持 **Tier4-only** 发放最终圣物 / 解锁；Tier2/3 记录部分成功、保留进度奖励并进入短期冷却，低于 Tier2 才判失败并进入冷却。

---

## 4) Carthage / 浴火金面实现快照

### 4.1 发现与地点规则
- Discovery：`rol_relic_discovery.1600`
- 发现条件：`c_tunis OR b_qartajana`
- 活动地点固定：`b_qartajana`
- `is_location_valid` 允许：
  - `barony = title:b_qartajana`
  - `county = title:c_tunis`

### 4.2 链路模板
- 命名空间：`rol_quest_carthage`
- 链路：
  - `0990` 抵达
  - `1000` 夜砂阶段
  - `1002` 灰烬幻象阶段
  - `1050` 宾客插曲
  - `1001` 终局判定
  - `1090` 结算
- 结构保持 **两主阶段模板**；当前版本通过加厚现有事件正文 / flavor / summary 来增强终局感，不新增第三主阶段。
- 成功收口：`rol_carthage_quest_success_finalize_effect`
- 失败收口：`rol_carthage_quest_fail_now_effect`

### 4.3 关键状态与产物
- heard flag：`rol_heard_carthage_legend`
- cooldown：`rol_carthage_quest_cooldown_modifier`
- recent flags：
  - `rol_recent_carthage_quest_success`
  - `rol_recent_carthage_quest_failure`
- 变量 / flag：
  - `rol_carthage_stage_count`
  - `rol_carthage_guest_event_fired`
- artifact：`rol_ash_forged_mask`
  - slot = `helmet`
  - visual = `rol_ash_forged_mask_visual`
  - create effect = `rol_create_ash_forged_mask_effect`

### 4.4 当前美术接线
- 活动图标族：
  - `gfx/interface/icons/activities/activity_rol_seek_ash_forged_mask.dds`
  - `gfx/interface/icons/activities/activity_rol_seek_ash_forged_mask_header.dds`
- 活动大图 / header 背景：
  - `gfx/interface/illustrations/activities/activity_rol_seek_ash_forged_mask.dds`
  - `gfx/interface/illustrations/activity_header_backgrounds/activity_rol_seek_ash_forged_mask.dds`
- 事件 / 活动 scene：
  - `rol_event_carthage_discovery.dds`
  - `rol_event_carthage_0990_arrival.dds`
  - `rol_event_carthage_1000_desert.dds`
  - `rol_event_carthage_1002_ash_temple.dds`
  - `rol_event_carthage_1001_terminal.dds`
  - `rol_event_carthage_1090_summary.dds`
  - `rol_activity_carthage_travel.dds`
  - `rol_activity_carthage_location.dds`
- 当前 scene DDS 已接入且通过尺寸 / 压缩审计；旧版可用资源继续保留，只有明确占位、缺失或场景冲突时才同名替换。

---

## 5) Munich 当前特别说明

- `rol_nibelung_star_sphere` 现已修正为：`slot = regalia`。
- `rol_nibelung_star_sphere_visual` 现已改为读取 **`rol_nibelung_star_sphere.dds`**，不再借用 `artifact_regalia.dds`。
- RoL 不再交付自定义 `artifact_regalia.dds`，避免污染原版与 NPC 的 regalia 图标。
- 当前修复仍保持**最小修复**：不扩大战线改 3D asset 或额外 UI 逻辑。
- 新生成实例应进入 **礼器 / regalia** 槽；旧存档里历史实例若异常，需删旧物后重新发放测试。

---

## 5.1) 四件传奇 artifact 当前数值基线

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

## 6) 当前常用回归命令

### 6.1 一键静态检查
```powershell
python tools/ck3_mcp/rol_stdio_probe.py
git diff --check
```

### 6.2 Carthage 直测

仅为旧事件/背景预览索引；无host/activity上下文的finalize/fail现在不改变奖励或冷却。真实活动终局使用控制台指南第6节的带作用域命令；创建effect只适用于尚无该物品的测试副本。
```txt
event rol_relic_discovery.1600
event rol_quest_carthage.0990
event rol_quest_carthage.1000
event rol_quest_carthage.1002
event rol_quest_carthage.1050
event rol_quest_carthage.1001
event rol_quest_carthage.1090

effect rol_create_ash_forged_mask_effect = yes
effect rol_carthage_quest_success_finalize_effect = yes
effect rol_carthage_quest_fail_now_effect = yes
```

### 6.3 统一 artifact 测试入口
```txt
effect rol_debug_grant_all_artifact_relics_effect = yes
```
预期：当前一次性发放 **Rome / Munich / Sevilla / Carthage** 四件 artifact；Naxos 不包含在内。

## 7) 给下一位 Codex 的明确约束

- 新活动链默认沿用统一筹备模块与当前 tooltip / flavor / cooldown 规范。
- **不是每条新链都自动并入 `rol_legend_circle`**；只有明确指定为“正式核心计数链”时，才在成功 finalize 里写永久完成 flag 并调用共享检查 effect。
- 若只是像 Carthage 这样新增正式活动链但**不想并入总事件**，就不要调用 `rol_check_legend_circle_revelation_effect`。
- 不再执行任何真源 -> Documents 的镜像同步；只需确保 `Documents\Paradox Interactive\Crusader Kings III\mod\RoL.mod` 仍指向 `C:\CK3Mods\RoL`。




## 8) 本地化收口基线

- 当前规则：**活跃显示 key 必须双语齐全；死 key 直接删除，不再为“数量对齐”保留孤儿 loc。**
- 已补齐重点：Rome 活跃按钮 / 过渡事件英文、Munich `1010~1022` 英文、Carthage 全链英文润色、统一 `rol_relic_hunt_intent` 英文。
- 已清理重点：旧 `rol_seek_mars_blade_decision*`、Rome 旧终局残留孤儿描述 key。
