# RoL 图片分辨率规范（事件背景 / 活动背景 / 圣物图标 / 活动图标）

> 结论基于当前 CK3 原版常见规格与 RoL 已验证接线。

## 0) 旧版资源保留规则

- 旧版已经做出来、格式正确、场景一致且不是占位图的资源继续使用，不重复生成同一张图。
- 生图 API 只用于明确标记的占位图、缺失资源，或人物/环境与当前事件不匹配的资源。
- 生成前先检查现有 DDS、`docs/rol_background_prompt_catalog.md` 和同一地点的其他画面；新图必须延续环境、光色、道具和构图。
- 替换旧资源时先移动到 `archive/replaced_assets/<date>/`，再接入新 DDS。

---

## 1) Event / Activity scene 背景

### 适用范围
- `events/*.txt` 里的 `override_background = { reference = ... }`
- `common/activities/activity_types/*.txt` 里的 `background = { texture = ... }`
- 注册文件：`common/event_backgrounds/rol_event_backgrounds.txt`
- 贴图目录：`gfx/interface/illustrations/event_scenes/`

### 推荐规格
- 分辨率：**1592 x 848**
- 推荐格式：**DDS / BC1(DXT1)**
- 默认：**无透明**

### 当前 RoL 例子
- `rol_event_legend_circle_revelation.dds`
- `rol_event_carthage_discovery.dds`
- `rol_event_carthage_1000_desert.dds`
- `rol_activity_carthage_travel.dds`
- `rol_activity_carthage_location.dds`

### 实操建议
- 主体尽量放在中间 70% 区域，避免 UI 遮挡。
- 新活动链与大事件统一优先沿用 `1592x848`，不要混用奇怪变体尺寸。

---

## 2) Activity 图标族

### 2.1 小图标（列表 / 按钮）
- 路径：`gfx/interface/icons/activities/`
- 推荐：**80 x 80**
- 推荐格式：**DDS / BC3(DXT5)**
- 默认：**带透明**

### 2.2 Header 图标
- 路径：`gfx/interface/icons/activities/`
- 常见命名：`*_header.dds`
- 推荐：**164 x 164**
- 推荐格式：**DDS / BC3(DXT5)**
- 默认：**带透明**

### 2.3 活动大图
- 路径：`gfx/interface/illustrations/activities/`
- 推荐：**1592 x 848**
- 推荐格式：**DDS / BC1(DXT1)**
- 默认：**无透明**
- 五条 RoL 活动大图已统一为 `1592 x 848 / DXT1`；旧 `1592 x 841` 文件保存在 round 5 归档目录，不再被活动接线引用。

### 2.4 Header 背景
- 路径：`gfx/interface/illustrations/activity_header_backgrounds/`
- 推荐：**1100 x 440**
- 推荐格式：**DDS / BC1(DXT1)**
- 默认：**无透明**
- 五条 RoL header 已统一为 `1100 x 440 / DXT1`；旧 `1100 x 442` 文件保存在 round 5 归档目录。

### Carthage 当前例子
- `activity_rol_seek_ash_forged_mask.dds`
- `activity_rol_seek_ash_forged_mask_header.dds`
- `gfx/interface/illustrations/activities/activity_rol_seek_ash_forged_mask.dds`
- `gfx/interface/illustrations/activity_header_backgrounds/activity_rol_seek_ash_forged_mask.dds`

---

## 3) Artifact 图标

### 适用范围
- `common/artifacts/visuals/*.txt` 里的 `icon = "xxx.dds"`
- 目录：`gfx/interface/icons/artifact/`

### 推荐规格
- 分辨率：**240 x 240**
- 推荐格式：**DDS / BC3(DXT5)**
- 默认：**带透明**

### 当前 RoL 例子
- `rol_blade_of_mars.dds`
- `rol_ash_forged_mask.dds`
- `rol_nibelung_star_sphere.dds`
- Sevilla 当前读取自定义图标 `rol_astrolabe_of_ocean.dds`

### 常见错误
- 如果你拿 **2048x2048** 直接塞到 artifact icon 位，UI 往往只会显示左上角。
- 正解是直接按 **240x240** 出图再导出。

---

## 4) 其他常用尺寸

| 资源类型 | 路径 | 推荐规格 |
|---|---|---|
| Activity 选项分类图标 | `gfx/interface/icons/activity_option_categories/` | `96 x 120` |
| Men-at-arms 小图标 | `gfx/interface/icons/regimenttypes/` | `120 x 120` |
| Men-at-arms 大图 | `gfx/interface/illustrations/men_at_arms_big/` | `680 x 400` |
| Decision 大图 | `gfx/interface/illustrations/decisions/` | `1100 x 440` |
| Text Icon | `gfx/interface/icons/artifact/` | `60 x 60` |

---

## 5) 透明图标硬性检查

### 只看“格式是 BC3/DXT5”还不够
活动小图标、artifact icon、intent / option 类图标在交付前必须确认：
- 文件确实带 alpha 通道
- alpha **不是全 255**
- 游戏里边缘不是实心底

### 推荐核查顺序
1. 用支持 alpha 预览的软件打开 DDS
2. 确认透明区域不是棋盘被烤进图片本体
3. 导出后检查 alpha 仍存在
4. 清掉 `Documents/Paradox Interactive/Crusader Kings III/gfx`
5. 完全重启启动器与游戏再看
6. 对 text icon / artifact icon，必须额外确认 alpha 不是全 255；`rol_legendary_icon.dds` 当前基线为 `60x60` 真透明

---

## 6) RoL 当前统一工作流

1. 先按目标尺寸建画布，不要先画超大图再硬塞。
2. 背景类优先 `1592x848 / BC1`；图标类优先 `BC3 + alpha`。
3. 文件放到正确目录后，再检查：
   - 显式引用是否正确
   - 隐式 basename 是否正确
4. 清 `gfx` 缓存。
5. 完全重启游戏验证。
