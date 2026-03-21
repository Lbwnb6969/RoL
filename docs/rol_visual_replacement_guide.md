# Relics of Legend 资源替换对照（Activity / Event / Artifact）

## 1) 活动背景（Activity Window）

### 直接改活动类型（首选）
- `C:\CK3Mods\RoL\common\activities\activity_types\rol_mars_activity.txt`
- `C:\CK3Mods\RoL\common\activities\activity_types\rol_nibelung_activity.txt`
- `C:\CK3Mods\RoL\common\activities\activity_types\rol_naxos_activity.txt`

在每个 `activity_... = {}` 中修改：
- `background = { texture = "...dds" environment = "..." ambience = "..." }`
- `window_characters = { ... }`（控制活动背景里的人物演出）

## 2) 事件背景（Event Background）

### 在事件里指定背景引用
- 在 `events/*.txt` 中使用：
  - `override_background = { reference = xxx }`

### 自定义背景引用定义文件
- `C:\CK3Mods\RoL\common\event_backgrounds\rol_activity_backgrounds.txt`

可在该文件中新增/调整：
- `some_background_key = { background = { reference = "gfx/interface/illustrations/event_scenes/xxx.dds" ... } }`

## 3) 圣物/武器图标（Artifact Icon）

### 图标定义入口
- `C:\CK3Mods\RoL\common\artifacts\visuals\rol_artifact_visuals.txt`

例如：
- `rol_blade_of_mars_visual = { icon = "rol_blade_of_mars.dds" ... }`
- `rol_nibelung_star_sphere_visual = { icon = "artifact_regalia.dds" ... }`

### 图标文件放置目录
- `C:\CK3Mods\RoL\gfx\interface\icons\artifact\`

将你的 `.dds` 放进上述目录，并在 `icon =` 中填写文件名即可。