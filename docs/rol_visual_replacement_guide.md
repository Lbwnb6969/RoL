# Relics of Legend 资源替换对照（Activity / Event / Artifact）

> 真源目录：`C:\CK3Mods\RoL`  
> 当前实际加载路径：`Documents\Paradox Interactive\Crusader Kings III\mod\RoL.mod -> C:/CK3Mods/RoL`
> 当前不再维护 `Documents\Paradox Interactive\Crusader Kings III\mod\RoL` 内容镜像；视觉问题只检查 descriptor path、实际接线与 `gfx` 缓存。

---

## 1) 先确认你改的是哪一层

视觉问题优先按这个顺序排查：
1. **真实加载路径** 是否仍指向 `C:\CK3Mods\RoL`
2. **脚本显式引用** 是否指向正确 key / 文件名
3. **CK3 隐式命名匹配** 是否命中文件名
4. **gfx 缓存** 是否已清理
5. **DDS 规格 / alpha** 是否正确

---

## 2) 活动背景（Activity Window）

### 活动定义入口
- `common/activities/activity_types/rol_mars_activity.txt`
- `common/activities/activity_types/rol_nibelung_activity.txt`
- `common/activities/activity_types/rol_naxos_activity.txt`
- `common/activities/activity_types/rol_astrolabe_activity.txt`
- `common/activities/activity_types/rol_carthage_activity.txt`

### 直接改这些字段
- `background = { texture = "...dds" environment = "..." ambience = "..." }`
- `window_characters = { ... }`

### Carthage 当前已接线路径
- 旅途背景：`gfx/interface/illustrations/event_scenes/rol_activity_carthage_travel.dds`
- 地点背景：`gfx/interface/illustrations/event_scenes/rol_activity_carthage_location.dds`

---

## 3) 事件背景（Event Background）

### 事件里怎么引用
在 `events/*.txt` 中使用：
```txt
override_background = { reference = some_key }
```

### 背景 key 的真实注册文件
- **正确文件**：`common/event_backgrounds/rol_event_backgrounds.txt`
- 不再使用旧写法 `rol_activity_backgrounds.txt`

### Carthage 当前背景 key
- `rol_discovery_bg_carthage`
- `rol_bg_carthage_0990_arrival`
- `rol_bg_carthage_1000_desert`
- `rol_bg_carthage_1002_ash_temple`
- `rol_success_bg_carthage`
- `rol_bg_carthage_1090_summary`

### Legend Circle 当前背景 key
- `rol_bg_legend_circle_revelation`

---

## 4) 活动图标与隐式命名匹配

CK3 很多活动资源按 **activity ID 同名隐式读取**，不一定有显式脚本路径。

### 当前五链活动图标 basename
- Rome：`activity_rol_seek_mars_blade`
- Munich：`activity_rol_seek_nibelung_sphere`
- Naxos：`activity_rol_seek_naxos_guard`
- Sevilla：`activity_rol_seek_astrolabe_of_ocean`
- Carthage：`activity_rol_seek_ash_forged_mask`

### Carthage 当前已存在文件
- 小图标：`gfx/interface/icons/activities/activity_rol_seek_ash_forged_mask.dds`
- Header 图标：`gfx/interface/icons/activities/activity_rol_seek_ash_forged_mask_header.dds`
- 活动大图：`gfx/interface/illustrations/activities/activity_rol_seek_ash_forged_mask.dds`
- Header 背景：`gfx/interface/illustrations/activity_header_backgrounds/activity_rol_seek_ash_forged_mask.dds`

### 统一筹备模块图标
- `gfx/interface/icons/activity_option_categories/rol_option_expedition_preparation.dds`

---

## 5) Artifact 图标与视觉定义

### 视觉定义入口
- `common/artifacts/visuals/rol_artifact_visuals.txt`

### 图标目录
- `gfx/interface/icons/artifact/`

### 当前重点接线
- Rome：`rol_blade_of_mars_visual -> rol_blade_of_mars.dds`
- Munich：`rol_nibelung_star_sphere_visual -> rol_nibelung_star_sphere.dds`
- Sevilla：`rol_astrolabe_of_ocean_visual -> rol_astrolabe_of_ocean.dds`
- Carthage：`rol_ash_forged_mask_visual -> rol_ash_forged_mask.dds`

### 槽位与视觉是两层问题
- **槽位** 在 `common/artifacts/types/*.txt`
- **2D 图标 / 3D asset** 在 `common/artifacts/visuals/*.txt`
- Munich 当前已修为：`rol_nibelung_star_sphere -> slot = regalia`
- Munich 当前也已切到专用 artifact 图标，不再覆盖原版 `artifact_regalia.dds`

---

## 6) Carthage 当前资源清单（最小可替换集合）

### Event / Activity scene
- `gfx/interface/illustrations/event_scenes/rol_event_carthage_discovery.dds`
- `gfx/interface/illustrations/event_scenes/rol_event_carthage_0990_arrival.dds`
- `gfx/interface/illustrations/event_scenes/rol_event_carthage_1000_desert.dds`
- `gfx/interface/illustrations/event_scenes/rol_event_carthage_1002_ash_temple.dds`
- `gfx/interface/illustrations/event_scenes/rol_event_carthage_1001_terminal.dds`
- `gfx/interface/illustrations/event_scenes/rol_event_carthage_1090_summary.dds`
- `gfx/interface/illustrations/event_scenes/rol_activity_carthage_travel.dds`
- `gfx/interface/illustrations/event_scenes/rol_activity_carthage_location.dds`

### Activity icon family
- `gfx/interface/icons/activities/activity_rol_seek_ash_forged_mask.dds`
- `gfx/interface/icons/activities/activity_rol_seek_ash_forged_mask_header.dds`
- `gfx/interface/illustrations/activities/activity_rol_seek_ash_forged_mask.dds`
- `gfx/interface/illustrations/activity_header_backgrounds/activity_rol_seek_ash_forged_mask.dds`

### Artifact icon
- `gfx/interface/icons/artifact/rol_ash_forged_mask.dds`

> 这些文件名已经接线完成；后续替换时只需要**同名覆盖**。

---

## 7) 图没变化时的固定排查

1. 检查 `RoL.mod` 的 `path=` 是否仍指向 `C:/CK3Mods/RoL`
2. 检查事件是否真的使用了你改的 background key
3. 检查活动资源是否靠 basename 隐式匹配，而你改错了文件名
4. 删除：`Documents/Paradox Interactive/Crusader Kings III/gfx`
5. 完全重启启动器与游戏
6. 若是透明图标，再检查 DDS 是否真的含有效 alpha，而不是“格式对了但 alpha 全不透明”
7. 若是 text icon / artifact icon，确认 `@rol_legendary_icon!` 这类 60x60 图标也经过真透明验证

