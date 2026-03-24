# RoL 图片分辨率规范（事件背景 / 活动背景 / 武器图标 / 活动图标）

> 结论基于 CK3 原版资源尺寸统计（当前本机版本）。

---

## 1) 事件背景图（Event Background）

- **用途**：`events/*.txt` 里 `override_background = { reference = ... }` 对应的背景图
- **注册文件**：`common/event_backgrounds/*.txt`
- **贴图路径**：`gfx/interface/illustrations/event_scenes/*.dds`
- **推荐分辨率**：**1592 x 848**（原版主流）
- **可用变体**：少量 DLC 用 1599x852 / 1593x852；不建议混用

### 建议
- 直接按 **1592x848** 出图最稳。
- 关键主体放在中间 70% 区域，避免 UI 遮挡。
- `rol_event_legend_circle_revelation.dds` 这类四链全通总事件，也沿用同一 `1592x848` event-scene 基线。

---

## 2) 活动背景图（Activity Background）

- **用途**：`common/activities/activity_types/*.txt` 的 `background = { texture = ... }`
- **贴图路径**：同上 `gfx/interface/illustrations/event_scenes/*.dds`
- **推荐分辨率**：**1592 x 848**

### 说明
活动窗口背景和事件背景共用同一套场景规格，所以你可以复用同一尺寸模板。

---

## 3) 决议大图（Decision Picture，若你后续用到）

- **用途**：`common/decisions/*.txt` 里 `picture = { reference = "..." }`
- **贴图路径**：`gfx/interface/illustrations/decisions/*.dds`
- **推荐分辨率**：**1100 x 440**（原版主流）
- **高分辨率可选**：2200 x 880（2x 资源）

---

## 4) 武器/圣物图标（Artifact Icon）

- **用途**：`common/artifacts/visuals/*.txt` 里 `icon = "xxx.dds"`
- **贴图路径**：`gfx/interface/icons/artifact/*.dds`
- **推荐分辨率**：**240 x 240**

### 你当前问题的根因
你之前那张是 **2048x2048**，UI 按 240 方图读取，会出现“只显示左上角”。

---

## 5) 活动图标（Activity Icon 系列）

## 5.1 活动主图标（列表/按钮）
- 路径：`gfx/interface/icons/activities/`
- 推荐：**80 x 80**

## 5.2 活动头图标（Header）
- 路径：同上
- 命名常见：`*_header.dds`
- 推荐：**164 x 164**

## 5.3 活动类型图标（Type）
- 路径：`gfx/interface/icons/activity_types/`
- 推荐：**78 x 78**

## 5.4 活动阶段图标（Phase）
- 路径：`gfx/interface/icons/activity_phases/`
- 推荐：**140 x 140**（主流）
- 兼容：160 x 160（少量存在）

## 5.5 活动意图图标（Intent）
- 路径：`gfx/interface/icons/activity_intents/`
- 推荐：**60 x 60**

---

## 6) 兵种图标（你的禁军会用到）

- **用途**：`common/men_at_arms_types/*.txt` 的 `icon = ...`
- **路径**：`gfx/interface/icons/regimenttypes/`
- **推荐分辨率**：**120 x 120**

---

## 7) RoL 实操建议（统一工作流）

1. 先按目标尺寸建 PSD/Krita 画布（不要先画超大再硬塞）。
2. 导出 DDS 时优先用带 Alpha 的格式（常用 DXT5 / BC3）。
3. 文件放入对应目录后，检查脚本引用路径是否一致。
4. 删除缓存：`Documents/Paradox Interactive/Crusader Kings III/gfx`。
5. **完全重启** 启动器和游戏再看效果。

---

## 8) 关于“传奇级武器”那 5 个紫字

- 你做的“伪稀有度”**有用**：可做分层数值、奖励判定、日志、调试与文案分档。
- 但这 5 个紫字来自原生稀有度 `illustrious` 显示链路。
- **只靠 artifact rarity 本身，不能做“仅 RoL 改名、原版不变”。**
- 若要“仅 RoL 显示传奇级武器”，需要走 **GUI + 条件本地化**（按 RoL 标记/修正符判断）定向改显示。