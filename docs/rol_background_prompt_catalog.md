# RoL 全视觉资源主清单（图标 / 大图 / 兵种图 / 背景）

> 快照日期：2026-03-24  
> 真源目录：`C:\CK3Mods\RoL`  
> 本文档同时承担：**命名清单 / 规格清单 / Prompt 清单 / 资源状态审计**

---

## 1) 状态定义

- **已接线**：文件已存在，且当前脚本 / UI 已实际使用。
- **已接线（占位）**：文件已存在且已接线，但当前仍是临时占位图，后续应以同名最终图覆盖。
- **已接线（隐式匹配）**：文件已存在，按 CK3 常见命名约定由 UI 直接按 ID/文件名读取，不一定有显式脚本文本引用。
- **已有文件未接线**：文件已存在，但当前脚本仍指向别的图片。
- **原版占位**：当前功能仍引用原版路径 / 原版命名资产，尚未切到 RoL 自定义文件名。
- **尚未创建**：本资源位已明确应该存在，但仓内目前没有对应文件。

---

## 2) 统一规格与通用 Prompt 前缀

| 资源类型 | 推荐规格 | 目标目录 | 通用 Prompt 前缀 |
|---|---|---|---|
| Event / Activity 场景背景 | `1592x848` / `DDS` / `DXT1(BC1)` / 无透明 | `gfx/interface/illustrations/event_scenes/` | `16:9 widescreen CK3 event background, epic dark fantasy matte painting, highly detailed, cinematic lighting, atmospheric, no text, no logo, no watermark, no UI` |
| Activity 小图标 | `80x80` / `DDS` / `DXT5(BC3)` / 带透明 | `gfx/interface/icons/activities/` | `centered game activity icon, high contrast emblem, ornate fantasy UI asset, clean silhouette, no text, transparent background` |
| Activity Header 图标 | `164x164` / `DDS` / `DXT5(BC3)` / 带透明 | `gfx/interface/icons/activities/` | `centered heraldic activity icon, close-up emblem, clean silhouette, premium fantasy UI asset, no text, transparent background` |
| Activity 大图 | `1592x848` / `DDS` / `DXT1(BC1)` / 无透明 | `gfx/interface/illustrations/activities/` | `wide CK3 activity illustration, painterly fantasy scene, cinematic lighting, no text, no logo, no UI` |
| Activity Header 背景 | `1100x440` / `DDS` / `DXT1(BC1)` / 无透明 | `gfx/interface/illustrations/activity_header_backgrounds/` | `wide fantasy activity header background, strong central composition, cinematic banner art, no text, no logo, no UI` |
| Artifact 2D 图标 | `240x240` / `DDS` / `DXT5(BC3)` / 带透明 | `gfx/interface/icons/artifact/` | `centered artifact icon, premium fantasy item art, sharp silhouette, no text, transparent background` |
| Text Icon | `60x60` / `DDS` / `DXT5(BC3)` / 带透明 | `gfx/interface/icons/artifact/` | `small UI token icon, simple golden insignia, high readability, no text, transparent background` |
| Activity 选项分类图标 | `96x120` / `DDS` / 原版同规格占位 | `gfx/interface/icons/activity_option_categories/` | `centered activity option category icon, expedition ledger, hired retainers, bundled gear, clean CK3 UI asset, no text, transparent background` |
| Men-at-arms 小图标 | `120x120` / `DDS` / `DXT5(BC3)` / 带透明 | `gfx/interface/icons/regimenttypes/` | `centered regiment icon, military emblem art, high contrast silhouette, no text, transparent background` |
| Men-at-arms 大图 | `680x400` / `DDS` / `DXT1(BC1)` / 无透明 | `gfx/interface/illustrations/men_at_arms_big/` | `wide military unit card art, disciplined formation, dramatic lighting, no text, no logo, no UI` |
| Decision 大图 | `1100x440` / `DDS` / `DXT1(BC1)` / 无透明 | `gfx/interface/illustrations/decisions/` | `wide CK3 decision illustration, painterly dramatic tabletop scene, no text, no logo, no UI` |

### 备注
- 当前 `rol_event_rome_discovery.dds` / `Discovery_Rome.dds` 仍是 `1592x868` 老尺寸占位；最终建议统一为 `1592x848`。
- 事件背景、活动背景、活动大图都应把主体放在中央 70% 区域，避免 UI 遮挡。
- 图标类资源优先考虑透明背景，便于 CK3 UI 混用。
- `rol_option_expedition_preparation.dds` 当前已接线，但仍直接复用原版 `inspection_option_allocated_funds.dds` 作为占位。

---

## 3) Activity UI 图标族

> 引用规则：本组资源按 **activity ID 文件名隐式匹配**。  
> 关联活动定义位于：`common/activities/activity_types/rol_*.txt`

### 3.1 Rome / Mars

| 资源类型 | 状态 | 文件名 | 推荐规格 | 目标目录 | 引用方式 / 引用文件 | Prompt |
|---|---|---|---|---|---|---|
| 活动小图标 | 已接线（隐式匹配） | `activity_rol_seek_mars_blade.dds` | `80x80 / DDS BC3` | `gfx/interface/icons/activities/` | 按 activity ID 隐式匹配；`common/activities/activity_types/rol_mars_activity.txt` | `Roman war relic emblem, crimson sword sigil, bronze laurel, centered game activity icon, transparent background` |
| 活动 Header 图标 | 已接线（隐式匹配） | `activity_rol_seek_mars_blade_header.dds` | `164x164 / DDS BC3` | `gfx/interface/icons/activities/` | 按 activity ID 隐式匹配；`common/activities/activity_types/rol_mars_activity.txt` | `close-up Mars expedition crest, sacred sword, Roman bronze ornament, red glow, centered icon, transparent background` |
| 活动大图 | 已接线（隐式匹配） | `activity_rol_seek_mars_blade.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/activities/` | 按 activity ID 隐式匹配；`common/activities/activity_types/rol_mars_activity.txt` | `Roman catacomb expedition, torches, sealed underground gate, martial crimson atmosphere` |
| 活动 Header 背景 | 已接线（隐式匹配） | `activity_rol_seek_mars_blade.dds` | `1100x440 / DDS BC1` | `gfx/interface/illustrations/activity_header_backgrounds/` | 按 activity ID 隐式匹配；`common/activities/activity_types/rol_mars_activity.txt` | `wide Roman catacomb banner art, sealed gate, braziers, crimson martial glow` |

### 3.2 Munich / Nibelung

| 资源类型 | 状态 | 文件名 | 推荐规格 | 目标目录 | 引用方式 / 引用文件 | Prompt |
|---|---|---|---|---|---|---|
| 活动小图标 | 尚未创建 | `activity_rol_seek_nibelung_sphere.dds` | `80x80 / DDS BC3` | `gfx/interface/icons/activities/` | 按 activity ID 隐式匹配；`common/activities/activity_types/rol_nibelung_activity.txt` | `frozen star sphere sigil, icy runes, cobalt glow, centered game activity icon, transparent background` |
| 活动 Header 图标 | 尚未创建 | `activity_rol_seek_nibelung_sphere_header.dds` | `164x164 / DDS BC3` | `gfx/interface/icons/activities/` | 按 activity ID 隐式匹配；`common/activities/activity_types/rol_nibelung_activity.txt` | `close-up Nibelung expedition crest, frozen armillary sphere, frost patterns, centered icon, transparent background` |
| 活动大图 | 尚未创建 | `activity_rol_seek_nibelung_sphere.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/activities/` | 按 activity ID 隐式匹配；`common/activities/activity_types/rol_nibelung_activity.txt` | `Alpine blizzard expedition to a hidden star crypt, frozen shrine, pale starlight` |
| 活动 Header 背景 | 尚未创建 | `activity_rol_seek_nibelung_sphere.dds` | `1100x440 / DDS BC1` | `gfx/interface/illustrations/activity_header_backgrounds/` | 按 activity ID 隐式匹配；`common/activities/activity_types/rol_nibelung_activity.txt` | `wide frozen star-crypt banner art, split ice gate, cold blue light, arcane frost` |

### 3.3 Naxos / Thera

| 资源类型 | 状态 | 文件名 | 推荐规格 | 目标目录 | 引用方式 / 引用文件 | Prompt |
|---|---|---|---|---|---|---|
| 活动小图标 | 尚未创建 | `activity_rol_seek_naxos_guard.dds` | `80x80 / DDS BC3` | `gfx/interface/icons/activities/` | 按 activity ID 隐式匹配；`common/activities/activity_types/rol_naxos_activity.txt` | `golden imperial guardian crest, spear motif, sacred halo, centered game activity icon, transparent background` |
| 活动 Header 图标 | 尚未创建 | `activity_rol_seek_naxos_guard_header.dds` | `164x164 / DDS BC3` | `gfx/interface/icons/activities/` | 按 activity ID 隐式匹配；`common/activities/activity_types/rol_naxos_activity.txt` | `close-up Thera palace expedition emblem, golden guardian helm, black-gold frame, centered icon, transparent background` |
| 活动大图 | 尚未创建 | `activity_rol_seek_naxos_guard.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/activities/` | 按 activity ID 隐式匹配；`common/activities/activity_types/rol_naxos_activity.txt` | `Thera underground palace expedition, volcanic cliffs above, black-gold halls below, sacred military mood` |
| 活动 Header 背景 | 尚未创建 | `activity_rol_seek_naxos_guard.dds` | `1100x440 / DDS BC1` | `gfx/interface/illustrations/activity_header_backgrounds/` | 按 activity ID 隐式匹配；`common/activities/activity_types/rol_naxos_activity.txt` | `wide black-gold palace banner art, imperial pillars, volcanic ash glow, solemn command atmosphere` |

### 3.4 Sevilla / Astrolabe

| 资源类型 | 状态 | 文件名 | 推荐规格 | 目标目录 | 引用方式 / 引用文件 | Prompt |
|---|---|---|---|---|---|---|
| 活动小图标 | 尚未创建 | `activity_rol_seek_astrolabe_of_ocean.dds` | `80x80 / DDS BC3` | `gfx/interface/icons/activities/` | 按 activity ID 隐式匹配；`common/activities/activity_types/rol_astrolabe_activity.txt` | `oceanic astrolabe emblem, brass rings, blue pointer, maritime sigil, centered game activity icon, transparent background` |
| 活动 Header 图标 | 尚未创建 | `activity_rol_seek_astrolabe_of_ocean_header.dds` | `164x164 / DDS BC3` | `gfx/interface/icons/activities/` | 按 activity ID 隐式匹配；`common/activities/activity_types/rol_astrolabe_activity.txt` | `close-up ocean expedition crest, glowing astrolabe, brass and blue enamel, centered icon, transparent background` |
| 活动大图 | 尚未创建 | `activity_rol_seek_astrolabe_of_ocean.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/activities/` | 按 activity ID 隐式匹配；`common/activities/activity_types/rol_astrolabe_activity.txt` | `forbidden ocean voyage from Sevilla, stormy sea, masts in black fog, age-of-exploration mythic mood` |
| 活动 Header 背景 | 尚未创建 | `activity_rol_seek_astrolabe_of_ocean.dds` | `1100x440 / DDS BC1` | `gfx/interface/illustrations/activity_header_backgrounds/` | 按 activity ID 隐式匹配；`common/activities/activity_types/rol_astrolabe_activity.txt` | `wide maritime banner art, Sevilla port, astrolabe star map, dawn over the ocean` |

---

### 3.5 活动选项分类图标

| 资源类型 | 状态 | 文件名 | 推荐规格 | 目标目录 | 引用方式 / 引用文件 | Prompt |
|---|---|---|---|---|---|---|
| 活动选项分类图标 | 已接线（占位） | `rol_option_expedition_preparation.dds` | `96x120 / DDS / 原版同规格占位` | `gfx/interface/icons/activity_option_categories/` | 四条活动的 `options = { rol_option_expedition_preparation = { ... } }`；当前文件直接复制自原版 `inspection_option_allocated_funds.dds` | `expedition planning ledger, hired retainers, bundled gear, clean CK3 activity option category icon, transparent background` |

---

## 4) Artifact 2D 图标 / Text Icon

| 资源类型 | 状态 | 文件名 | 推荐规格 | 目标目录 | 引用方式 / 引用文件 | Prompt |
|---|---|---|---|---|---|---|
| Artifact 图标（Rome） | 已接线 | `rol_blade_of_mars.dds` | `240x240 / DDS BC3` | `gfx/interface/icons/artifact/` | `common/artifacts/visuals/rol_artifact_visuals.txt -> rol_blade_of_mars_visual` | `legendary Roman sword, crimson edge glow, dark bronze hilt, centered artifact icon, transparent background` |
| Artifact 图标（Munich 目标名） | 尚未创建 | `rol_nibelung_star_sphere.dds` | `240x240 / DDS BC3` | `gfx/interface/icons/artifact/` | 目标接线：`common/artifacts/visuals/rol_artifact_visuals.txt -> rol_nibelung_star_sphere_visual`；当前仍指向 `artifact_regalia.dds` | `ceremonial star sphere, frozen crystal armillary, blue-gold metal, centered artifact icon, transparent background` |
| Artifact 图标（Sevilla 目标名） | 已有文件未接线 | `rol_astrolabe_of_ocean.dds` | `240x240 / DDS BC3` | `gfx/interface/icons/artifact/` | 目标接线：`common/artifacts/visuals/rol_artifact_visuals.txt -> rol_astrolabe_of_ocean_visual`；当前仍指向 `artifact_icons_unique_armillary.dds` | `ancient ocean astrolabe, brass rings, luminous blue pointer, maritime relic icon, transparent background` |
| Text Icon（传奇级标记） | 已有文件未接线 | `rol_legendary_icon.dds` | `60x60 / DDS BC3` | `gfx/interface/icons/artifact/` | 目标接线：`gui/rol_texticons.gui`；当前 `@rol_legendary_icon!` 仍读 `artifact_regalia.dds`，相关本地化在 `localization/*/rol_artifact_ui_*.yml` | `small golden relic insignia, simple laurel and star crest, high readability, transparent background` |

### 现状补充
- `artifact_regalia.dds`：当前为 Munich 图标的**原版命名占位**，也是 `gui/rol_texticons.gui` 当前读取的实际贴图。
- `artifact_icons_unique_armillary.dds`：当前为 Sevilla 星盘图标的**原版命名占位**。
- 本批文档只整理 **2D 图标**；3D `asset = ...entity` 不纳入 Prompt 范围。

---

## 5) Men-at-arms 图片

| 资源类型 | 状态 | 文件名 | 推荐规格 | 目标目录 | 引用方式 / 引用文件 | Prompt |
|---|---|---|---|---|---|---|
| 禁军小图标 | 尚未创建（当前原版占位） | `rol_adeptus_custudes.dds` | `120x120 / DDS BC3` | `gfx/interface/icons/regimenttypes/` | 当前 `common/men_at_arms_types/rol_naxos_maa_types.txt` 仍是 `icon = heavy_infantry`；目标应改为 `icon = rol_adeptus_custudes` | `golden imperial guardian helmet and spear emblem, sacred military icon, centered regiment icon, transparent background` |
| 禁军大图 | 尚未创建（当前原版占位） | `rol_adeptus_custudes.dds` | `680x400 / DDS BC1` | `gfx/interface/illustrations/men_at_arms_big/` | 配套同一兵种键 `rol_adeptus_custudes`；当前 UI 仍会落到原版 heavy infantry / 通用兵种图 | `elite golden guardians in perfect formation, long spears, black-gold sacred armor, dramatic roster card art` |

---

## 6) Event / Activity 背景总表

> 规则：
> - 所有 **Event 背景**都先在 `common/event_backgrounds/rol_event_backgrounds.txt` 注册，再由 `events/*.txt` 用 `override_background = { reference = ... }` 调用。
> - 所有 **Activity 旅途 / 地点背景**由 `common/activities/activity_types/rol_*.txt` 中的 `background = { texture = ... }` 直接调用。
> - 下表四链背景当前都已接线，但大多数仍是**同名占位 DDS**；后续只需覆盖同名文件即可。

### 6.1 Rome / Mars

| 资源类型 | 状态 | 文件名 | 推荐规格 | 目标目录 | 引用方式 / 引用文件 | Prompt |
|---|---|---|---|---|---|---|
| 发现事件背景 | 已接线（占位） | `rol_event_rome_discovery.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_discovery_bg_rome -> events/rol_relic_discovery_events.txt (.1000)` | `ancient Roman underground passage, relief of Mars, crimson torchlight, cracked stone walls, lost legion relic aura` |
| 活动旅途背景 | 已接线（占位） | `rol_activity_rome_travel.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `background.texture -> common/activities/activity_types/rol_mars_activity.txt` | `night journey through Roman underground corridor, ranks of torches, damp stone walls, oppressive atmosphere` |
| 活动地点背景 | 已接线（占位） | `rol_activity_rome_location.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `background.texture -> common/activities/activity_types/rol_mars_activity.txt` | `sealed catacomb main chamber, heavy stone gate, ritual fire and chains, Roman legion insignia` |
| `0990` 抵达封印地宫 | 已接线（占位） | `rol_event_rome_0990_arrival.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_rome_0990_arrival -> events/rol_quest_rome_events.txt (.0990)` | `sealed catacomb entrance, half-collapsed arch, iron gate with wax seals, braziers, tense pre-expedition mood` |
| `1000` 深入地宫 | 已接线（占位） | `rol_event_rome_1000_catacombs.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_rome_1000_catacombs -> events/rol_quest_rome_events.txt (.1000)` | `deep Palatine catacombs, broken statues, red dust haze, distant altar of Mars` |
| `1002` 落石回廊 | 已接线（占位） | `rol_event_rome_1002_collapse.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_rome_1002_collapse -> events/rol_quest_rome_events.txt (.1002)` | `narrow corridor with falling boulders, overturned torches, shattered dust, sudden danger` |
| `1003` 血誓祭坛 | 已接线（占位） | `rol_event_rome_1003_altar.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_rome_1003_altar -> events/rol_quest_rome_events.txt (.1003)` | `blood oath altar, stone offering table, crimson ritual markings, statue of Mars, solemn and mysterious` |
| `1004` 禁卫残影 | 已接线（占位） | `rol_event_rome_1004_guardians.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_rome_1004_guardians -> events/rol_quest_rome_events.txt (.1004)` | `underground war hall, ghostly praetorian formation, glowing crimson eyes, ancient Roman heavy armor silhouettes` |
| `1001` 终局赐福 | 已接线（占位） | `rol_event_rome_1001_terminal.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_success_bg_rome -> events/rol_quest_rome_events.txt (.1001)` | `blessing of Mars, legendary blade floating above altar, red-gold divine light, war temple atmosphere` |
| `1090` 远征结算 | 已接线（占位） | `rol_event_rome_1090_summary.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_rome_1090_summary -> events/rol_quest_rome_events.txt (.1090)` | `Roman armory after expedition, relic on display, braziers and dark red war banners, victorious but solemn` |

### 6.2 Munich / Nibelung

| 资源类型 | 状态 | 文件名 | 推荐规格 | 目标目录 | 引用方式 / 引用文件 | Prompt |
|---|---|---|---|---|---|---|
| 发现事件背景 | 已接线（占位） | `rol_event_munich_discovery.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_discovery_bg_munich -> events/rol_relic_discovery_events.txt (.1300)` | `Bavarian mountain omen, ancient stone gate buried in snow, pale starlight, cold mist` |
| 活动旅途背景 | 已接线（占位） | `rol_activity_munich_travel.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `background.texture -> common/activities/activity_types/rol_nibelung_activity.txt` | `expedition through Alpine blizzard trail, cold blue daylight, whipping snow, steep mountain ridge` |
| 活动地点背景 | 已接线（占位） | `rol_activity_munich_location.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `background.texture -> common/activities/activity_types/rol_nibelung_activity.txt` | `frozen star crypt, frost-covered pillars, ancient sarcophagi, cold blue reflections` |
| `0990` 星冢入口 | 已接线（占位） | `rol_event_munich_0990_arrival.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_munich_0990_arrival -> events/rol_quest_munich_events.txt (.0990)` | `mouth of the star crypt, split ice gate, swirling snow fog, faint runic glow` |
| `1000` 踏入极寒 | 已接线（占位） | `rol_event_munich_1000_frost.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_munich_1000_frost -> events/rol_quest_munich_events.txt (.1000)` | `core frost corridor, giant frozen gate, chained ice, piercing blue-white light` |
| `1002` 心灵深渊 | 已接线（占位） | `rol_event_munich_1002_abyss.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_munich_1002_abyss -> events/rol_quest_munich_events.txt (.1002)` | `abyssal cavern with mirrored ice reflecting stars, cold violet illusions, eerie stillness` |
| `1001` 星辰陨心 | 已接线（占位） | `rol_event_munich_1001_terminal.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_success_bg_munich -> events/rol_quest_munich_events.txt (.1001)` | `Nibelung star sphere floating above frozen dais, starlight raining down, ancient ice shrine` |
| `1090` 远征结算 | 已接线（占位） | `rol_event_munich_1090_summary.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_munich_1090_summary -> events/rol_quest_munich_events.txt (.1090)` | `quiet post-expedition snow camp beside star crypt, relic illuminating scrolls and frost, scholarly triumph` |

### 6.3 Naxos / Thera

| 资源类型 | 状态 | 文件名 | 推荐规格 | 目标目录 | 引用方式 / 引用文件 | Prompt |
|---|---|---|---|---|---|---|
| 发现事件背景 | 已接线（占位） | `rol_event_naxos_discovery.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_discovery_bg_naxos -> events/rol_relic_discovery_events.txt (.1400)` | `Aegean volcanic island ruins, broken stairs descending underground, black rock and golden sacred traces` |
| 活动旅途背景 | 已接线（占位） | `rol_activity_naxos_travel.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `background.texture -> common/activities/activity_types/rol_naxos_activity.txt` | `approach to Thera volcanic sea cliffs, black volcanic stone, sea wind and embers, dusk light` |
| 活动地点背景 | 已接线（占位） | `rol_activity_naxos_location.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `background.texture -> common/activities/activity_types/rol_naxos_activity.txt` | `underground palace of Thera, black-gold colonnades, ancient imperial statues, stern majesty` |
| `0990` 抵达泰拉 | 已接线（占位） | `rol_event_naxos_0990_arrival.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_naxos_0990_arrival -> events/rol_quest_naxos_events.txt (.0990)` | `sea cliff entrance at Thera, stone stairway down into the earth, sea mist, lost palace ruins` |
| `1000` 帝皇前厅 | 已接线（占位） | `rol_event_naxos_1000_antechamber.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_naxos_1000_antechamber -> events/rol_quest_naxos_events.txt (.1000)` | `gigantic black-gold doors, braziers before imperial icons, baroque techno-relic atmosphere, sacred pressure` |
| `1002` 验证大厅 | 已接线（占位） | `rol_event_naxos_1002_verification.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_naxos_1002_verification -> events/rol_quest_naxos_events.txt (.1002)` | `long verification hall, ancient mechanisms and trial altar, cold golden light, ruthless order` |
| `1003` 禁军守门阵列 | 已接线（占位） | `rol_event_naxos_1003_custodes.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_naxos_1003_custodes -> events/rol_quest_naxos_events.txt (.1003)` | `golden guardian silhouettes in formation, long polearms, impassable sacred gate, imperial holiness` |
| `1001` 最终裁决 | 已接线（占位） | `rol_event_naxos_1001_terminal.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_success_bg_naxos -> events/rol_quest_naxos_events.txt (.1001)` | `throne-like sanctuary, sacred gold light, elite guard insignia, final command bestowed` |
| `1090` 远征结算 | 已接线（占位） | `rol_event_naxos_1090_summary.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_naxos_1090_summary -> events/rol_quest_naxos_events.txt (.1090)` | `underground sanctuary at rest, ritual wargear and banners, lingering glory, solemn closure` |

### 6.4 Sevilla / Astrolabe

| 资源类型 | 状态 | 文件名 | 推荐规格 | 目标目录 | 引用方式 / 引用文件 | Prompt |
|---|---|---|---|---|---|---|
| 发现事件背景 | 已接线（占位） | `rol_event_sevilla_discovery.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_discovery_bg_sevilla -> events/rol_relic_discovery_events.txt (.1500)` | `magical sea chart spread across tavern table in old port of Sevilla, navigation tools, candlelight, salt mist` |
| 活动旅途背景 | 已接线（占位） | `rol_activity_sevilla_travel.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `background.texture -> common/activities/activity_types/rol_astrolabe_activity.txt` | `forbidden ocean voyage, black waves, distant lightning, sailing ship charging into mist` |
| 活动地点背景 | 已接线（占位） | `rol_activity_sevilla_location.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `background.texture -> common/activities/activity_types/rol_astrolabe_activity.txt` | `quays of Triana, Iberian port, ropes and cargo crates, golden sea breeze at dawn` |
| `0990` 特里亚纳码头 | 已接线（占位） | `rol_event_sevilla_0990_quays.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_sevilla_0990_quays -> events/rol_quest_sevilla_events.txt (.0990)` | `old sailing ships and dock lanterns, busy harbor district, crates and mooring ropes, excitement before departure` |
| `1000` 海峡走私者 | 已接线（占位） | `rol_event_sevilla_1000_smugglers.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_sevilla_1000_smugglers -> events/rol_quest_sevilla_events.txt (.1000)` | `hidden cove, rough smugglers, weathered fast boats, warm lantern light and deep shadows, illicit deal atmosphere` |
| `1002` 磁暴风墙 | 已接线（占位） | `rol_event_sevilla_1002_stormwall.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_sevilla_1002_stormwall -> events/rol_quest_sevilla_events.txt (.1002)` | `magnetic storm wall at world’s edge, black sea vortex, purple-red sky, electromagnetic tempest, mad compass needles` |
| `1001` 镜海星盘 | 已接线（占位） | `rol_event_sevilla_1001_terminal.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_success_bg_sevilla -> events/rol_quest_sevilla_events.txt (.1001)` | `perfectly calm mirror sea, glowing astrolabe floating above water, sacred blue-gold radiance, destiny of the age of exploration` |
| `1090` 远征结算 | 已接线（占位） | `rol_event_sevilla_1090_summary.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_sevilla_1090_summary -> events/rol_quest_sevilla_events.txt (.1090)` | `triumphant return to Sevilla harbor, astrolabe with navigation charts on display, dawn harbor, victorious expedition mood` |

---

### 6.5 四链总揭示 / Legend Circle

| 资源类型 | 状态 | 文件名 | 推荐规格 | 目标目录 | 引用方式 / 引用文件 | Prompt |
|---|---|---|---|---|---|---|
| 四链全通总事件背景 | 已接线（占位） | `rol_event_legend_circle_revelation.dds` | `1592x848 / DDS BC1` | `gfx/interface/illustrations/event_scenes/` | `rol_bg_legend_circle_revelation -> events/rol_legend_circle_events.txt (.0001)` | `Mediterranean-centered legendary revelation scene, relic discoveries forming an arc around the Mediterranean and Alps, ancient Europe map symbolism, colossal sacred atmosphere, dark gold and deep blue, triumphant yet ominous, CK3 event background, no text, no logo` |

---

## 7) 状态审计附录

### 7.1 已接线

| 分类 | 条目 | 说明 |
|---|---|---|
| 四链背景 | `rol_event_*.dds`、`rol_activity_*.dds` 共 36 张 | 当前均已接线；大多数仍是占位图，可直接同名覆盖 |
| 总揭示背景 | `rol_event_legend_circle_revelation.dds` | 已接线占位，可直接同名替换为最终大事件图 |
| Mars 活动图标族 | `activity_rol_seek_mars_blade*.dds`（小图 / header / 大图 / header 背景） | 已存在并按 activity ID 命名落地 |
| Rome Artifact 图标 | `rol_blade_of_mars.dds` | 已由 `rol_blade_of_mars_visual` 使用 |
| 活动选项分类图标 | `gfx/interface/icons/activity_option_categories/rol_option_expedition_preparation.dds` | 已接线，但当前仍为原版资金图标占位 |

### 7.2 已有文件未接线

| 分类 | 条目 | 说明 |
|---|---|---|
| Artifact 图标 | `gfx/interface/icons/artifact/rol_astrolabe_of_ocean.dds` | 文件已存在，但 `rol_astrolabe_of_ocean_visual` 仍指向 `artifact_icons_unique_armillary.dds` |
| Text Icon | `gfx/interface/icons/artifact/rol_legendary_icon.dds` | 文件已存在，但 `gui/rol_texticons.gui` 仍指向 `artifact_regalia.dds` |
| Legacy 背景 | `gfx/interface/illustrations/event_scenes/Discovery_Rome.dds` | 旧 Rome 发现图遗留文件；当前主接线已转到 `rol_event_rome_discovery.dds` |

### 7.3 仍使用原版占位

| 分类 | 条目 | 说明 |
|---|---|---|
| Munich Artifact 图标 | `rol_nibelung_star_sphere_visual -> artifact_regalia.dds` | 当前仍未切到 `rol_nibelung_star_sphere.dds` |
| Sevilla Artifact 图标 | `rol_astrolabe_of_ocean_visual -> artifact_icons_unique_armillary.dds` | 当前仍是原版星盘图标 |
| 传奇 Text Icon 贴图 | `gui/rol_texticons.gui -> artifact_regalia.dds` | 当前 `@rol_legendary_icon!` 实际贴图不是 `rol_legendary_icon.dds` |
| 禁军兵种图 | `rol_adeptus_custudes -> heavy_infantry` | 当前小图仍用原版重步兵；大图也未做自定义 |
| 额外发现槽位 | `rol_discovery_bg_athena -> corridor.dds` | 仍是原版占位 |
| 额外发现槽位 | `rol_discovery_bg_anubis -> dungeon.dds` | 仍是原版占位 |

### 7.4 尚未创建

| 分类 | 条目 | 说明 |
|---|---|---|
| Munich 活动图标族 | `activity_rol_seek_nibelung_sphere*.dds` 共 4 件 | 小图 / header 图标 / 大图 / header 背景均缺 |
| Naxos 活动图标族 | `activity_rol_seek_naxos_guard*.dds` 共 4 件 | 小图 / header 图标 / 大图 / header 背景均缺 |
| Sevilla 活动图标族 | `activity_rol_seek_astrolabe_of_ocean*.dds` 共 4 件 | 小图 / header 图标 / 大图 / header 背景均缺 |
| Munich Artifact 目标图标 | `rol_nibelung_star_sphere.dds` | 已定义为推荐目标名，但文件还没做 |
| 禁军小图标 | `gfx/interface/icons/regimenttypes/rol_adeptus_custudes.dds` | 后续若自定义兵种 icon，需要同时改 MAA type 引用 |
| 禁军大图 | `gfx/interface/illustrations/men_at_arms_big/rol_adeptus_custudes.dds` | 与上行共用 basename |

---

## 8) 后续落地建议

1. **优先级 1：补齐缺位资源族**
   - Munich / Naxos / Sevilla 的 12 张活动图标族
   - 禁军 2 张兵种图
   - `rol_nibelung_star_sphere.dds`

2. **优先级 2：把已有文件接上线**
   - `rol_astrolabe_of_ocean.dds`
   - `rol_legendary_icon.dds`

3. **优先级 3：清理遗留 / 原版占位**
   - `Discovery_Rome.dds`
   - `artifact_regalia.dds` 的 Nibelung / text icon 临时职责
   - `rol_option_expedition_preparation.dds` 的原版占位临时职责
