# RoL 新对话完整交接文档（Master Handoff）

> 当前快照日期：2026-03-24  
> 文档真源：`C:\CK3Mods\RoL\docs\rol_handoff_master.md`

---

## 0) 当前快照基线来源（只基于已存在事实）

本交接文档仅汇总以下已存在文件内容，不使用臆测：

- `C:\CK3Mods\RoL\docs\rol_console_test_guide.md`
- `C:\CK3Mods\RoL\docs\rol_visual_replacement_guide.md`
- `C:\CK3Mods\RoL\docs\rol_image_resolution_guide.md`
- `C:\Users\Falcons的Niko本人的PC\.codex\skills\rol-ck3-modder\SKILL.md`
- `C:\Users\Falcons的Niko本人的PC\.codex\skills\rol-ck3-modder\agents\openai.yaml`

---

## 1) 项目身份与目标

- 模组名称：**Relics of Legend（RoL）**。
- 核心玩法：玩家持有特定地区伯爵领后触发本地传说发现事件，通过决议/活动开启远征，经过多阶段检定后获得对应神兵或特殊奖励。
- 当前主线覆盖：
  - Rome（玛尔斯之剑）
  - Munich（尼伯龙根星界球）
  - Naxos/Thera（禁军解锁）
  - Sevilla（大洋统御星盘）

---

## 2) 强制工程规则（必须遵守）

1. **唯一开发真源目录**：`C:\CK3Mods\RoL`
2. Documents 目录仅作为镜像：
   - `c:\Users\Falcons的Niko本人的PC\Documents\Paradox Interactive\Crusader Kings III\mod\RoL`
3. 文件编码要求：脚本与本地化改动统一 **UTF-8 with BOM**。
4. 自定义命名统一前缀：`rol_`（兼容活动键 `activity_rol_`、`phase_rol_`）。
5. 不确定 CK3 接口写法时，先检索既有实例（game/RICE/docs/UsePlanguage.md）再改。

---

## 3) 当前已落地模块状态（实现快照）

### 3.1 四链活动状态
- 四链活动均已启用宾客系统：`max_guests = 12`，含 `guest_invite_rules`。
- 四链均有中段宾客事件：
  - `rol_quest_rome.1050`
  - `rol_quest_munich.1050`
  - `rol_quest_naxos.1050`
  - `rol_quest_sevilla.1050`
- 四链成功/失败 toast 已支持双行（title + desc）。

### 3.2 终局奖励门槛（Tier4）
- Rome：`activity_special_type_progression >= 75`
- Munich：`>= 80`
- Naxos：`>= 75`
- 直接 `event rol_quest_*.1001` 时若缺 `scope:activity`，通常会走失败分支（测试时需用成功 finalize effect）。

### 3.3 传奇显示覆盖（仅 RoL）
- 已接入 artifact custom loc 与本地化覆盖：`ARTIFACT_RARITY_AND_SLOT_TYPE` -> `RolArtifactRarityAndSlotType`。
- 已接入文本图标 token：`@rol_legendary_icon!`（可替换实际 DDS）。

### 3.4 发现事件入口

### 3.5 统一“人员与装备等级”模块（2026-03-23）
- 四条正式活动统一接入活动选项分类：`rol_option_expedition_preparation`。
- 四档固定为：`rol_expedition_preparation_low` / `standard` / `high` / `supreme`。
- 固定成本曲线：`30 / 150 / 600 / 1750`；`standard` 为默认档。
- 随机二元检定统一叠加筹备修正并 clamp 到 `5~95`：`low -10`、`standard 0`、`high +10`、`supreme +20`。
- 成功后额外奖励统一只在 `*_quest_success_finalize_effect` 发放：`high +150 prestige / +25 dynasty prestige`，`supreme +350 / +50`。
- Tier4-only 终局门槛不变；无论选哪档，仍只有达到各链 Tier4 才会拿到最终圣物 / 解锁。
- 活动规划文案统一改为神秘化叙述：不直写奖励、不写“低于 Tier4 视为失败”，仅保留失败进入 2 年冷却。

### 3.6 四链全通总事件（2026-03-24）
- 新增一次性大型总事件：`rol_legend_circle.0001`。
- 触发条件固定为同一角色同时持有四个永久完成 flag：`rol_mars_blade_claimed`、`rol_nibelung_sphere_claimed`、`rol_naxos_unit_unlocked`、`rol_astrolabe_of_ocean_claimed`。
- 共享接口：`rol_has_all_major_relic_completions_trigger` + `rol_check_legend_circle_revelation_effect`。
- 防重 flag：`rol_legend_circle_revealed`。
- 奖励结构：当前角色永久 modifier + House 75 年 modifier + Dynasty 100 年 modifier + `+500 dynasty prestige`。

### 3.7 正式入口与已移除遗留
### 3.7 正式入口与已移除遗留
- 当前唯一正式发现链路：`common/on_action/rol_relic_discovery_on_actions.txt -> rol_relic_discovery.0001 -> 四条活动链`。
- 以下遗留 / 测试入口已从仓库移除，不再作为任何开发或测试基线：
  - `common/on_action/rol_on_actions.txt`
  - `events/rol_trigger_events.txt`
  - `common/decisions/rol_decisions.txt`
  - `events/rol_test_events.txt`
- 通用入口：`event rol_relic_discovery.0001`
- 地区直测：
  - Rome：`rol_relic_discovery.1000`
  - Munich：`rol_relic_discovery.1300`
  - Naxos：`rol_relic_discovery.1400`

---

## 4) 关键技术架构

1. **模板化底层**：通过 `scripted_effects` / `scripted_triggers` / `script_values` 承载可复用逻辑。
2. **活动主流程**：发现 -> 活动 -> 阶段检定反馈 -> 终局判定 -> 结算事件。
3. **统一筹备接口**：新活动链默认沿用 `rol_option_expedition_preparation` 与四档成本 / 成功率 / 成功奖励规则。
4. **可观测性**：
   - 活动成功条变化
   - 结果 toast 双行
   - 调试 trace/日志
5. **失败统一收口**：风险分支失败统一走 `*_quest_fail_now_effect`。

---

## 5) 资源与 UI 替换地图

### 5.1 活动背景
- 改 `common/activities/activity_types/*.txt` 的 `background` 与 `window_characters`。

### 5.2 事件背景
- 在事件内使用 `override_background = { reference = ... }`。
- 背景 reference 定义位于 `common/event_backgrounds/*.txt`。

### 5.3 圣物/武器图标
- 定义入口：`common/artifacts/visuals/rol_artifact_visuals.txt`
- 贴图目录：`gfx/interface/icons/artifact/`

### 5.4 推荐分辨率
- 事件/活动背景：`1592x848`
- artifact icon：`240x240`
- text icon：`60x60`（显示约 24x24）
- 活动图标常用：`80x80`；header `164x164`

---

## 6) 常见故障排查顺序

1. `not a valid id`：先确认是否在 `C:\CK3Mods\RoL` 真源改动并重启游戏+启动器。
2. 活动窗口不出现：确认不是直接事件链绕过活动入口；检查冷却/战争/金币/已领取标记。
3. 终局不给奖励：确认是否有 `scope:activity` 进度上下文。
4. 获得/失去提示异常：检查是否重复 set_owner 或重复发奖链路。
5. 中文乱码：检查 YAML 编码是否 BOM，且 key 是否存在。

---

## 7) 回归测试清单（控制台 + 预期）

### 7.1 预热
```txt
effect rol_relic_debug_enable_effect = yes
```

### 7.2 发现层
```txt
event rol_relic_discovery.0001
event rol_relic_discovery.1000
event rol_relic_discovery.1300
event rol_relic_discovery.1400
```
预期：对应发现弹窗可触发。

### 7.3 活动链
```txt
event rol_quest_rome.0990
event rol_quest_munich.0990
event rol_quest_naxos.0990
event rol_quest_sevilla.0990
```
预期：链路可推进，反馈事件可见。

### 7.3.1 活动规划 UI（统一筹备模块）
- 四条活动都应出现 `rol_option_expedition_preparation` 分类。
- 默认档为 `standard`，默认总价应约为：Rome `300`、Munich `400`、Naxos `350`、Sevilla `400`。
- 切换为 `low / high / supreme` 时，总价、活动描述与检定提示应同步变化。
- 失败说明统一只写“失败进入 2 年冷却”，不直接暴露 Tier4 数值门槛。

### 7.4 直接发奖测试
```txt
effect rol_create_blade_of_mars_effect = yes
effect rol_create_nibelung_star_sphere_effect = yes
```
预期：artifact 创建成功。

### 7.5 成功结算模拟
```txt
effect rol_rome_quest_success_finalize_effect = yes
effect rol_munich_quest_success_finalize_effect = yes
effect rol_naxos_quest_success_finalize_effect = yes
```
预期：成功结算标记、toast、奖励/解锁状态一致。

---

## 8) 如何使用 `$rol-ck3-modder`

### 8.1 安装位置与识别
- 全局 skill 目录：`~/.codex/skills/rol-ck3-modder`
- 本机实际路径：
  - `C:\Users\Falcons的Niko本人的PC\.codex\skills\rol-ck3-modder\SKILL.md`
- UI 元数据：`agents/openai.yaml`
  - `display_name: RoL CK3 Modder`
  - `policy.allow_implicit_invocation: true`

### 8.2 触发方式
1. **显式触发（推荐）**：在请求里写 `$rol-ck3-modder`
2. **隐式触发**：描述明显 RoL/CK3 脚本任务，系统可自动匹配

### 8.3 三类标准调用模板
1) 修 bug
```txt
Use $rol-ck3-modder to diagnose and fix the Munich chain crash, then provide a regression checklist.
```

2) 新增一条活动阶段
```txt
Use $rol-ck3-modder to add one new stage event to Naxos chain, including effects, localization (EN/ZH), and test commands.
```

3) 本地化/编码巡检
```txt
Use $rol-ck3-modder to scan all RoL localization for UTF-8 BOM and missing keys, then patch and report.
```

### 8.4 脚本工作流模板（建议固定）
1. 先检查（BOM / prefix / smoke）
2. 再改动（最小变更）
3. 再回归（控制台复现命令）
4. 最后同步镜像（真源 -> Documents）

### 8.5 一键检查命令集合
```powershell
python "C:\Users\Falcons的Niko本人的PC\.codex\skills\rol-ck3-modder\scripts\check_bom_utf8.py" "C:\CK3Mods\RoL"
python "C:\Users\Falcons的Niko本人的PC\.codex\skills\rol-ck3-modder\scripts\check_rol_prefix.py" "C:\CK3Mods\RoL"
python "C:\Users\Falcons的Niko本人的PC\.codex\skills\rol-ck3-modder\scripts\rol_smoke_checks.py" "C:\CK3Mods\RoL"
powershell -ExecutionPolicy Bypass -File "C:\Users\Falcons的Niko本人的PC\.codex\skills\rol-ck3-modder\scripts\sync_to_documents.ps1" -WhatIf
```

---

## 9) 下一位 Codex 接手指令模板（新对话首条可直接复制）

```txt
你现在是 RoL（Relics of Legend）模组的 CK3 专家开发助手。请严格遵守：
1) 唯一真源目录：C:\CK3Mods\RoL（Documents 目录仅镜像）
2) 修改文件统一 UTF-8 with BOM
3) 自定义 ID/事件/effect/trigger/变量/flag 保持 rol_ 前缀
4) 先检索现有实现与文档再改动，优先最小变更
5) 活动链遵循：发现 -> 活动 -> 阶段反馈 -> 终局判定 -> 结算
6) 输出必须包含：变更摘要、可执行测试步骤、预期结果、风险说明

请先读取以下基线文档后再开始：
- C:\CK3Mods\RoL\docs\rol_handoff_master.md
- C:\CK3Mods\RoL\docs\rol_console_test_guide.md
- C:\CK3Mods\RoL\docs\rol_visual_replacement_guide.md
- C:\CK3Mods\RoL\docs\rol_image_resolution_guide.md

当前任务：<在这里写你这次要做的具体需求>
```

---

## 10) 接口/类型变更说明

- 新增四链全通总事件接口：`rol_has_all_major_relic_completions_trigger`、`rol_check_legend_circle_revelation_effect`、`rol_legend_circle.0001`
- 新增总事件奖励 modifier：`rol_legend_circle_conqueror_modifier`、`rol_legend_circle_house_modifier`、`rol_legend_circle_dynasty_modifier`
- 新增统一活动选项分类：`rol_option_expedition_preparation`
- 新增四档固定 option ID：`rol_expedition_preparation_low / standard / high / supreme`
- 新增共享层：
  - `common/scripted_triggers/rol_expedition_preparation_triggers.txt`
  - `common/script_values/rol_expedition_preparation_values.txt`
  - `common/scripted_effects/rol_expedition_preparation_effects.txt`
- 删除四个遗留测试入口文件（见 3.7）
- 四链活动文本规范更新为：神秘化描述、失败仅写 2 年冷却、未来新链默认沿用统一筹备模块。

---

## 11) 2026-03-22 更新：Sevilla / Astrolabe of Ocean-Sea

### 11.1 新增内容
- 新增第四条完整主线：**Sevilla 大洋统御星盘**。
- 新发现事件：`rol_relic_discovery.1500`
- 新活动 ID：`activity_rol_seek_astrolabe_of_ocean`
- 新任务命名空间：`rol_quest_sevilla`
- 新 artifact：`rol_astrolabe_of_ocean`

### 11.2 规则 / 流程 / 门槛
- 发现与活动地点统一固定为 `c_sevilla`，不再允许手动改址。
- 活动阶段通过 `c_sevilla` 的 scripted location 直接锁定位置。
- 初始进度为 `35`。
- Tier4 门槛为 `>= 80`。
- 只有终局达到 Tier4 才会发放圣物；低于 Tier4 直接按失败收口。
- 成功 finalize：`rol_sevilla_quest_success_finalize_effect`
- 失败 finalize：`rol_sevilla_quest_fail_now_effect`
- 圣物创建 effect：`rol_create_astrolabe_of_ocean_effect`

### 11.3 Discovery / Activity / Finalize 测试命令
```txt
event rol_relic_discovery.1500
event rol_quest_sevilla.0990
event rol_quest_sevilla.1000
event rol_quest_sevilla.1002
event rol_quest_sevilla.1001
event rol_quest_sevilla.1090

effect rol_create_astrolabe_of_ocean_effect = yes
effect rol_sevilla_quest_success_finalize_effect = yes
effect rol_sevilla_quest_fail_now_effect = yes
```

### 11.4 相关状态
- `rol_heard_astrolabe_legend`
- `rol_astrolabe_of_ocean_claimed`
- `rol_astrolabe_quest_cooldown_modifier`
- `rol_recent_sevilla_quest_success`
- `rol_recent_sevilla_quest_failure`
- `rol_sevilla_stage_count`
- `rol_astrolabe_guest_event_fired`

### 11.5 2026-03-22 后续维护项
- Sevilla 简中、本地化、toast 与 debug 文案已补齐。
- 泰拉 / Naxos 的 `rol_adeptus_custudes` 已改为 **只需 `rol_naxos_unit_unlocked` 解锁**，不再要求 `vanguard` 5 级 accolade。
- 新增统一圣物测试入口：
```txt
effect rol_debug_grant_all_artifact_relics_effect = yes
```
- 该入口只发放三件 artifact：Rome / Munich / Sevilla；不包含泰拉禁军解锁。
- 泰拉兵种解锁仍使用：
```txt
effect rol_naxos_quest_success_finalize_effect = yes
```