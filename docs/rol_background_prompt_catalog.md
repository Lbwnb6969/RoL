# RoL 全视觉资源主清单（图标 / 大图 / 背景 / Prompt）

> 快照日期：2026-03-25  
> 真源目录：`C:\CK3Mods\RoL`  
> 本文档兼作：**命名清单 / 规格清单 / Prompt 清单 / 资源状态审计**

---

## 1) 状态定义

- **已接线**：文件存在且当前脚本 / UI 已实际使用
- **已接线（占位）**：文件已接线，但仍是临时占位图
- **已接线（隐式匹配）**：按 CK3 命名约定由 basename 隐式读取
- **原版占位**：当前仍读原版文件名或原版美术
- **尚未创建**：当前资源位已明确需要，但仓内暂无文件

---

## 2) 统一规格与通用 Prompt 前缀

| 资源类型 | 推荐规格 | 目录 | 通用 Prompt 前缀 |
|---|---|---|---|
| Event / Activity scene | `1592x848 / DDS BC1 / 无透明` | `gfx/interface/illustrations/event_scenes/` | `16:9 CK3 event background, epic dark fantasy matte painting, cinematic lighting, atmospheric, no text, no logo, no UI` |
| Activity 小图标 | `80x80 / DDS BC3 / 透明` | `gfx/interface/icons/activities/` | `centered game activity icon, high contrast emblem, clean silhouette, transparent background` |
| Activity Header 图标 | `164x164 / DDS BC3 / 透明` | `gfx/interface/icons/activities/` | `close-up heraldic activity icon, ornate fantasy UI asset, clean silhouette, transparent background` |
| Activity 大图 | `1592x848 / DDS BC1 / 无透明` | `gfx/interface/illustrations/activities/` | `wide CK3 activity illustration, painterly fantasy scene, cinematic lighting, no text, no UI` |
| Activity Header 背景 | `1100x440 / DDS BC1 / 无透明` | `gfx/interface/illustrations/activity_header_backgrounds/` | `wide fantasy activity header background, strong central composition, no text, no UI` |
| Artifact 图标 | `240x240 / DDS BC3 / 透明` | `gfx/interface/icons/artifact/` | `centered artifact icon, premium fantasy item art, sharp silhouette, transparent background` |
| Activity 选项分类图标 | `96x120 / DDS / 透明` | `gfx/interface/icons/activity_option_categories/` | `centered activity option category icon, expedition ledger, hired retainers, bundled gear, clean CK3 UI asset, transparent background` |

---

## 3) Activity UI 图标族

> 本组大量资源按 **activity ID basename 隐式匹配**。  
> 若图标不显示，先检查文件名，再检查缓存。

| 链 | 状态 | Basename / 文件 | Prompt |
|---|---|---|---|
| Rome / Mars | 已接线（隐式匹配） | `activity_rol_seek_mars_blade.dds` / `activity_rol_seek_mars_blade_header.dds` / `illustrations/activities/activity_rol_seek_mars_blade.dds` / `activity_header_backgrounds/activity_rol_seek_mars_blade.dds` | `Roman war relic emblem, sacred crimson sword sigil, bronze laurel, martial atmosphere` |
| Munich / Nibelung | 尚未创建 | `activity_rol_seek_nibelung_sphere*` | `frozen star sphere sigil, icy runes, cobalt glow, alpine occult expedition emblem` |
| Naxos / Thera | 尚未创建 | `activity_rol_seek_naxos_guard*` | `golden imperial guardian crest, spear motif, sacred halo, black-gold expedition emblem` |
| Sevilla / Astrolabe | 尚未创建 | `activity_rol_seek_astrolabe_of_ocean*` | `oceanic astrolabe emblem, brass rings, blue pointer, forbidden maritime sigil` |
| Carthage / Ash-Forged Mask | 已接线（隐式匹配，占位） | `activity_rol_seek_ash_forged_mask.dds` / `activity_rol_seek_ash_forged_mask_header.dds` / `illustrations/activities/activity_rol_seek_ash_forged_mask.dds` / `activity_header_backgrounds/activity_rol_seek_ash_forged_mask.dds` | `ash-forged golden mask emblem, black sand, cold starlight, Carthaginian desert relic expedition crest` |
| 统一筹备模块 | 已接线（占位） | `gfx/interface/icons/activity_option_categories/rol_option_expedition_preparation.dds` | `expedition planning ledger, hired retainers, bundled gear, premium CK3 option-category icon` |

---

## 4) Artifact 图标 / Prompt

| 圣物 | 当前槽位 | 当前图标状态 | 文件 / 接线 | Prompt |
|---|---|---|---|---|
| Blade of Mars | weapon | 已接线 | `rol_blade_of_mars.dds` -> `rol_blade_of_mars_visual` | `legendary Roman sword, crimson edge glow, dark bronze hilt, centered artifact icon` |
| Nibelung Star Sphere | **regalia** | 已接线（专用图标） | `rol_nibelung_star_sphere_visual -> rol_nibelung_star_sphere.dds` | `ceremonial star sphere, frozen crystal armillary, blue-gold metal, regal occult artifact icon` |
| Astrolabe of Ocean | trinket | 已接线 | `rol_astrolabe_of_ocean.dds` -> `rol_astrolabe_of_ocean_visual` | `ancient ocean astrolabe, brass rings, luminous blue pointer, maritime relic icon` |
| Ash-Forged Mask | **helmet** | 已接线（占位） | `rol_ash_forged_mask.dds` -> `rol_ash_forged_mask_visual` | `legendary Carthaginian golden mask, ash-dark burn marks, cold starlight, black-sand relic icon` |

---

## 5) Event / Activity scene 背景族

### 5.1 Rome / Mars

| 场景 | 状态 | 文件 | Prompt |
|---|---|---|---|
| Discovery | 已接线（占位） | `rol_event_rome_discovery.dds` | `ancient Roman underground passage, relief of Mars, crimson torchlight, cracked stone walls` |
| Travel | 已接线（占位） | `rol_activity_rome_travel.dds` | `night journey through Roman underground corridor, ranks of torches, damp stone walls` |
| Location | 已接线（占位） | `rol_activity_rome_location.dds` | `sealed catacomb main chamber, heavy stone gate, ritual fire and chains` |
| `0990` Arrival | 已接线（占位） | `rol_event_rome_0990_arrival.dds` | `sealed catacomb entrance, half-collapsed arch, iron gate with wax seals` |
| `1000` Catacombs | 已接线（占位） | `rol_event_rome_1000_catacombs.dds` | `deep Palatine catacombs, broken statues, red dust haze, distant altar of Mars` |
| `1002` Collapse | 已接线（占位） | `rol_event_rome_1002_collapse.dds` | `narrow corridor with falling boulders, overturned torches, shattered dust` |
| `1003` Altar | 已接线（占位） | `rol_event_rome_1003_altar.dds` | `blood oath altar, crimson ritual markings, statue of Mars, solemn and mysterious` |
| `1004` Guardians | 已接线（占位） | `rol_event_rome_1004_guardians.dds` | `underground war hall, ghostly praetorian formation, glowing crimson eyes` |
| `1001` Terminal | 已接线（占位） | `rol_event_rome_1001_terminal.dds` | `blessing of Mars, legendary blade floating above altar, red-gold divine light` |
| `1090` Summary | 已接线（占位） | `rol_event_rome_1090_summary.dds` | `Roman armory after expedition, relic on display, dark red war banners` |

### 5.2 Munich / Nibelung

| 场景 | 状态 | 文件 | Prompt |
|---|---|---|---|
| Discovery | 已接线（占位） | `rol_event_munich_discovery.dds` | `Bavarian mountain omen, ancient stone gate buried in snow, pale starlight, cold mist` |
| Travel | 已接线（占位） | `rol_activity_munich_travel.dds` | `expedition through Alpine blizzard trail, cold blue daylight, whipping snow` |
| Location | 已接线（占位） | `rol_activity_munich_location.dds` | `frozen star crypt, frost-covered pillars, ancient sarcophagi, cold blue reflections` |
| `0990` Arrival | 已接线（占位） | `rol_event_munich_0990_arrival.dds` | `mouth of the star crypt, split ice gate, swirling snow fog, faint runic glow` |
| `1000` Frost | 已接线（占位） | `rol_event_munich_1000_frost.dds` | `core frost corridor, giant frozen gate, chained ice, piercing blue-white light` |
| `1002` Abyss | 已接线（占位） | `rol_event_munich_1002_abyss.dds` | `abyssal cavern with mirrored ice reflecting stars, cold violet illusions` |
| `1001` Terminal | 已接线（占位） | `rol_event_munich_1001_terminal.dds` | `Nibelung star sphere floating above frozen dais, starlight raining down` |
| `1090` Summary | 已接线（占位） | `rol_event_munich_1090_summary.dds` | `quiet post-expedition snow camp beside star crypt, scholarly triumph` |

### 5.3 Naxos / Thera

| 场景 | 状态 | 文件 | Prompt |
|---|---|---|---|
| Discovery | 已接线（占位） | `rol_event_naxos_discovery.dds` | `Aegean volcanic island ruins, broken stairs descending underground, black rock and gold traces` |
| Travel | 已接线（占位） | `rol_activity_naxos_travel.dds` | `approach to Thera volcanic sea cliffs, black volcanic stone, sea wind and embers` |
| Location | 已接线（占位） | `rol_activity_naxos_location.dds` | `underground palace of Thera, black-gold colonnades, ancient imperial statues` |
| `0990` Arrival | 已接线（占位） | `rol_event_naxos_0990_arrival.dds` | `sea cliff entrance at Thera, stone stairway into the earth, sea mist` |
| `1000` Antechamber | 已接线（占位） | `rol_event_naxos_1000_antechamber.dds` | `gigantic black-gold doors, braziers before imperial icons, sacred pressure` |
| `1002` Verification | 已接线（占位） | `rol_event_naxos_1002_verification.dds` | `long verification hall, ancient mechanisms and trial altar, cold golden light` |
| `1003` Custodes | 已接线（占位） | `rol_event_naxos_1003_custodes.dds` | `golden guardian silhouettes in formation, long polearms, impassable sacred gate` |
| `1001` Terminal | 已接线（占位） | `rol_event_naxos_1001_terminal.dds` | `throne-like sanctuary, sacred gold light, elite guard insignia, final command bestowed` |
| `1090` Summary | 已接线（占位） | `rol_event_naxos_1090_summary.dds` | `underground sanctuary at rest, ritual wargear and banners, solemn closure` |

### 5.4 Sevilla / Astrolabe

| 场景 | 状态 | 文件 | Prompt |
|---|---|---|---|
| Discovery | 已接线（占位） | `rol_event_sevilla_discovery.dds` | `magical sea chart on tavern table in old port of Sevilla, candlelight, salt mist` |
| Travel | 已接线（占位） | `rol_activity_sevilla_travel.dds` | `forbidden ocean voyage, black waves, distant lightning, sailing ship into mist` |
| Location | 已接线（占位） | `rol_activity_sevilla_location.dds` | `quays of Triana, Iberian port, ropes and cargo crates, golden sea breeze` |
| `0990` Quays | 已接线（占位） | `rol_event_sevilla_0990_quays.dds` | `old sailing ships and dock lanterns, busy harbor district, excitement before departure` |
| `1000` Smugglers | 已接线（占位） | `rol_event_sevilla_1000_smugglers.dds` | `hidden cove, rough smugglers, weathered fast boats, illicit deal atmosphere` |
| `1002` Stormwall | 已接线（占位） | `rol_event_sevilla_1002_stormwall.dds` | `magnetic storm wall at world's edge, black sea vortex, purple-red sky` |
| `1001` Terminal | 已接线（占位） | `rol_event_sevilla_1001_terminal.dds` | `perfectly calm mirror sea, glowing astrolabe floating above water` |
| `1090` Summary | 已接线（占位） | `rol_event_sevilla_1090_summary.dds` | `triumphant return to Sevilla harbor, astrolabe with navigation charts on display` |

### 5.5 Carthage / Ash-Forged Mask

| 场景 | 状态 | 文件 | Prompt |
|---|---|---|---|
| Discovery | 已接线（占位） | `rol_event_carthage_discovery.dds` | `storm-stripped black sands outside ruined Carthage, half-buried temple revealed under rare sandstorm, ominous desert night` |
| Travel | 已接线（占位） | `rol_activity_carthage_travel.dds` | `night caravan across black sand desert, cold stars, ash-laden wind, silent dread` |
| Location | 已接线（占位） | `rol_activity_carthage_location.dds` | `half-buried Carthaginian temple entrance, ash-dark stone, broken reliefs, cold starlight` |
| `0990` Arrival | 已接线（占位） | `rol_event_carthage_0990_arrival.dds` | `desert expedition reaching a half-buried temple after sandstorm, black dunes, buried threshold, night entry mood` |
| `1000` Desert | 已接线（占位） | `rol_event_carthage_1000_desert.dds` | `black desert under freezing stars, Bedouin guides and ancient charts, cursed salt and ash, Carthaginian ruins in the distance` |
| `1002` Ash Temple | 已接线（占位） | `rol_event_carthage_1002_ash_temple.dds` | `interior of buried temple filled with ash and impossible starlight, ghostly war elephants, ancient Punic tragedy` |
| `1001` Terminal | 已接线（占位） | `rol_event_carthage_1001_terminal.dds` | `ash-forged golden mask on weathered stone dais beneath a shaft of cold starlight, old gold, dread majesty` |
| `1090` Summary | 已接线（占位） | `rol_event_carthage_1090_summary.dds` | `black-sand expedition returning from the buried sanctuary, relic record table, cold desert dawn, haunted triumph` |

### 5.6 Legend Circle / 四链总揭示

| 场景 | 状态 | 文件 | Prompt |
|---|---|---|---|
| `rol_legend_circle.0001` | 已接线（占位） | `rol_event_legend_circle_revelation.dds` | `Mediterranean-centered legendary revelation scene, relic discoveries forming an arc around the Mediterranean and Alps, colossal sacred atmosphere, dark gold and deep blue` |

---

## 6) 当前状态审计（2026-03-25）

### 6.1 已接线的重点资源
- Rome 活动图标族已落地。
- Carthage 活动图标族、artifact 图标、整套 event/activity scene 占位资源已落地。
- 五条正式活动链都已接入统一筹备模块图标：`rol_option_expedition_preparation.dds`。
- Legend Circle 大事件背景已接线。

### 6.2 仍在用原版占位的地方
- Sevilla artifact 图标：已切到 `rol_astrolabe_of_ocean.dds`
- `@rol_legendary_icon!` 已切到 `rol_legendary_icon.dds`
- Athena / Anubis discovery 仍读原版 scene

### 6.3 仍缺的活动图标族
- `activity_rol_seek_nibelung_sphere*`
- `activity_rol_seek_naxos_guard*`
- `activity_rol_seek_astrolabe_of_ocean*`

### 6.4 当前最稳妥的替换策略
- 已接线文件统一**同名覆盖**。
- 未接线或仍在用原版占位的资源，先补文件，再改 visual / GUI / basename 接线。
- 活动图标透明问题先看 alpha 是否真实存在，再清 `gfx` 缓存，不要只看导出格式名。

### 6.5 当前新增视觉基线
- Munich artifact 专用图标：`rol_nibelung_star_sphere.dds`
- Carthage 事件背景 key 已补齐到 `common/event_backgrounds/rol_event_backgrounds.txt`
- `rol_legendary_icon.dds` 需保持：`60x60`、真透明背景、大金星 + 两颗环绕小星

