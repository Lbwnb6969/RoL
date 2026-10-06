# RoL 全视觉资源主清单（图标 / 大图 / 背景 / Prompt）

> 快照日期：2026-10-06
> 真源目录：`C:\CK3Mods\RoL`  
> 本文档兼作：**命名清单 / 规格清单 / Prompt 清单 / 资源状态审计**

---

## 1) 状态定义

- **已接线**：文件存在且当前脚本 / UI 已实际使用
- **已接线（占位）**：文件已接线，但仍是临时占位图
- **已接线（隐式匹配）**：按 CK3 命名约定由 basename 隐式读取
- **原版占位**：当前仍读原版文件名或原版美术
- **尚未创建**：当前资源位已明确需要，但仓内暂无文件

### 资源保留与生图边界

- 旧版已经制作完成、内容可用且与当前场景一致的图片直接保留，不重复调用生图 API。
- 只有明确标为“占位”、内容错误、带人物而场景需要空背景，或确实缺失的资源才进入生图批次。
- 生成前先读取现有 DDS 和本目录中的同源 Prompt，确认场景、色调、道具和构图能延续；生成后才按目标尺寸转换并接线。
- 被替换的旧资源移动到 `archive/replaced_assets/` 保存，保留其 Git 记录，方便回退和比较。

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
| Munich / Nibelung | 已接线（旧版资源保留） | `activity_rol_seek_nibelung_sphere*` | `frozen star sphere sigil, icy runes, cobalt glow, alpine occult expedition emblem` |
| Naxos / Thera | 已接线（旧版资源保留） | `activity_rol_seek_naxos_guard*` | `golden imperial guardian crest, spear motif, sacred halo, black-gold expedition emblem` |
| Sevilla / Astrolabe | 已接线（旧版资源保留） | `activity_rol_seek_astrolabe_of_ocean*` | `oceanic astrolabe emblem, brass rings, blue pointer, forbidden maritime sigil` |
| Carthage / Ash-Forged Mask | 已接线（旧版资源保留） | `activity_rol_seek_ash_forged_mask.dds` / `activity_rol_seek_ash_forged_mask_header.dds` / `illustrations/activities/activity_rol_seek_ash_forged_mask.dds` / `activity_header_backgrounds/activity_rol_seek_ash_forged_mask.dds` | `ash-forged golden mask emblem, black sand, cold starlight, Carthaginian desert relic expedition crest` |
| 统一筹备模块 | 已接线（旧版资源保留） | `gfx/interface/icons/activity_option_categories/rol_option_expedition_preparation.dds` | `expedition planning ledger, hired retainers, bundled gear, premium CK3 option-category icon` |

五条活动的大图和 header 已在 round 5 统一替换为无人环境图；round 6 替换了五地 Travel / Location 背景，round 7 又替换了 Rome、Sevilla、Carthage 和 Legend Circle 的旧事件场景。三批均按 `1592x848 / DXT1` 接线，round 5 还从同源生成图裁出 `1100x440 / DXT1` header。活动窗口中的人物继续由 `window_characters` 提供。

---

## 4) Artifact 图标 / Prompt

| 圣物 | 当前槽位 | 当前图标状态 | 文件 / 接线 | Prompt |
|---|---|---|---|---|
| Blade of Mars | weapon | 已接线 | `rol_blade_of_mars.dds` -> `rol_blade_of_mars_visual` | `legendary Roman sword, crimson edge glow, dark bronze hilt, centered artifact icon` |
| Nibelung Star Sphere | **regalia** | 已接线（专用图标） | `rol_nibelung_star_sphere_visual -> rol_nibelung_star_sphere.dds` | `ceremonial star sphere, frozen crystal armillary, blue-gold metal, regal occult artifact icon` |
| Astrolabe of Ocean | trinket | 已接线 | `rol_astrolabe_of_ocean.dds` -> `rol_astrolabe_of_ocean_visual` | `ancient ocean astrolabe, brass rings, luminous blue pointer, maritime relic icon` |
| Ash-Forged Mask | **helmet** | 已接线（旧版资源保留） | `rol_ash_forged_mask.dds` -> `rol_ash_forged_mask_visual` | `legendary Carthaginian golden mask, ash-dark burn marks, cold starlight, black-sand relic icon` |

---

## 5) Event / Activity scene 背景族

### 5.1 Rome / Mars

| 场景 | 状态 | 文件 | Prompt |
|---|---|---|---|
| Discovery | 已接线（round 7 / 无人场景） | `rol_event_rome_discovery.dds` | `empty Roman underground discovery passage, basalt chamber, geometric laurel, crimson torchlight` |
| Travel | 已接线（round 6 / 无人场景） | `rol_activity_rome_travel.dds` | `empty torchlit Roman underground route, vaulted corridor, sealed doors, no expedition members` |
| Location | 已接线（round 6 / 无人场景） | `rol_activity_rome_location.dds` | `empty Palatine catacomb entrance, basalt arch, red torchlight, no figures` |
| `0990` Arrival | 已接线（round 7 / 无人场景） | `rol_event_rome_0990_arrival.dds` | `empty sealed Roman catacomb arrival, iron gate, broken arch, torch brackets` |
| `1000` Catacombs | 已接线（round 7 / 无人场景） | `rol_event_rome_1000_catacombs.dds` | `empty deep Palatine chamber, basalt, red dust, geometric altar` |
| `1002` Collapse | 已接线（round 7 / 无人场景） | `rol_event_rome_1002_collapse.dds` | `empty corridor collapse, falling boulders, overturned torches` |
| `1003` Altar | 已接线（round 7 / 无人场景） | `rol_event_rome_1003_altar.dds` | `empty Roman oath altar, abstract crimson marks, sealed door` |
| `1004` Guardians | 已接线（round 7 / 无人场景） | `rol_event_rome_1004_guardians.dds` | `empty war hall, abandoned shields, red-lit final gate` |
| `1001` Terminal | 已接线（round 7 / 无人场景） | `rol_event_rome_1001_terminal.dds` | `empty terminal altar, red-gold aperture, sacred shaft of light` |
| `1090` Summary | 已接线（round 7 / 无人场景） | `rol_event_rome_1090_summary.dds` | `empty Roman armory, covered display table, dark red banners` |

### 5.2 Munich / Nibelung

| 场景 | 状态 | 文件 | Prompt |
|---|---|---|---|
| Discovery | 已接线（无人场景 / 已统一尺寸） | `rol_event_munich_discovery.dds` | `Bavarian mountain omen, empty ancient stone gate buried in snow, pale starlight, cold mist` |
| Travel | 已接线（round 6 / 无人场景） | `rol_activity_munich_travel.dds` | `empty Alpine pass to the star crypt, snow, blue ice cliffs, no travelers` |
| Location | 已接线（round 6 / 无人场景） | `rol_activity_munich_location.dds` | `empty glacial star-crypt approach, blue ice cavern, sealed gate, no figures` |
| `0990` Arrival | 已接线（无人场景 / 已统一尺寸） | `rol_event_munich_0990_arrival.dds` | `empty ice crypt antechamber, frost pillars, blue star light` |
| `1000` Frost | 已接线（无人场景 / 已统一尺寸） | `rol_event_munich_1000_frost.dds` | `empty frozen gate chained in blue-white light` |
| `1002` Abyss | 已接线（无人场景 / 已统一尺寸） | `rol_event_munich_1002_abyss.dds` | `empty mirrored ice cavern with violet star reflections` |
| `1001` Terminal | 已接线（无人场景 / 已统一尺寸） | `rol_event_munich_1001_terminal.dds` | `empty frozen dais beneath a star beam, ambiguous sphere kept quiet` |
| `1090` Summary | 已接线（无人场景 / 已统一尺寸） | `rol_event_munich_1090_summary.dds` | `empty snow camp and star crypt, maps and firelight, no expedition figures` |

### 5.3 Naxos / Thera

| 场景 | 状态 | 文件 | Prompt |
|---|---|---|---|
| Discovery | 已接线（无人场景） | `rol_event_naxos_discovery.dds` | `Black-volcanic Aegean cliff ruin, sealed doorway, cold sea light; see rol_rival_legacy_image_prompts.md §7` |
| Travel | 已接线（round 6 / 无人场景） | `rol_activity_naxos_travel.dds` | `empty Aegean volcanic coast at dusk, black rock, sea cliffs, unoccupied boat` |
| Location | 已接线（round 6 / 无人场景） | `rol_activity_naxos_location.dds` | `empty black-stone Aegean sanctuary terrace, gold geometry, equipment only` |
| `0990` Arrival | 已接线（无人场景） | `rol_event_naxos_0990_arrival.dds` | `Empty sea-cliff entrance, sealed door, black stone and cold Aegean light; see rol_rival_legacy_image_prompts.md §7` |
| `1000` Antechamber | 已接线（无人场景） | `rol_event_naxos_1000_antechamber.dds` | `Empty black-gold geometric doors and braziers, no imperial figures; see rol_rival_legacy_image_prompts.md §7` |
| `1002` Verification | 已接线（无人场景） | `rol_event_naxos_1002_verification.dds` | `Empty mechanism hall and testing altar; see rol_rival_legacy_image_prompts.md §7` |
| `1003` Custodes | 已接线（无人场景） | `rol_event_naxos_1003_custodes.dds` | `Empty sealed custodes gate, stored spears and geometric seals; see rol_rival_legacy_image_prompts.md §7` |
| `1001` Terminal | 已接线（无人场景） | `rol_event_naxos_1001_terminal.dds` | `Empty skylit sanctuary with covered dais; see rol_rival_legacy_image_prompts.md §7` |
| `1090` Summary | 已接线（无人场景） | `rol_event_naxos_1090_summary.dds` | `Empty sanctuary with banners, weapon racks and covered display table; see rol_rival_legacy_image_prompts.md §7` |

### 5.4 Sevilla / Astrolabe

| 场景 | 状态 | 文件 | Prompt |
|---|---|---|---|
| Discovery | 已接线（round 7 / 无人场景） | `rol_event_sevilla_discovery.dds` | `empty maritime discovery room, covered instrument, blank parchment, salt mist` |
| Travel | 已接线（round 6 / 无人场景） | `rol_activity_sevilla_travel.dds` | `empty Atlantic travel seascape, unoccupied sailing ship, storm clouds, no crew` |
| Location | 已接线（round 6 / 无人场景） | `rol_activity_sevilla_location.dds` | `empty medieval Atlantic harbor, stone quay, furled ship, ropes and chests` |
| `0990` Quays | 已接线（round 7 / 无人场景） | `rol_event_sevilla_0990_quays.dds` | `empty Triana quays, furled ships, lanterns and cargo crates` |
| `1000` Smugglers | 已接线（round 7 / 无人场景） | `rol_event_sevilla_1000_smugglers.dds` | `empty hidden cove, unoccupied boats, sealed crates, sea cave` |
| `1002` Stormwall | 已接线（round 7 / 无人场景） | `rol_event_sevilla_1002_stormwall.dds` | `empty storm wall, black ocean vortex, purple lightning` |
| `1001` Terminal | 已接线（round 7 / 无人场景） | `rol_event_sevilla_1001_terminal.dds` | `empty mirror sea, circular brass geometry, pale horizon` |
| `1090` Summary | 已接线（round 7 / 无人场景） | `rol_event_sevilla_1090_summary.dds` | `empty return harbor, covered navigation table, dawn mist` |

### 5.5 Carthage / Ash-Forged Mask

| 场景 | 状态 | 文件 | Prompt |
|---|---|---|---|
| Discovery | 已接线（round 7 / 无人场景） | `rol_event_carthage_discovery.dds` | `empty black-sand Punic discovery, buried entrance, bronze tools, cold stars` |
| Travel | 已接线（round 6 / 无人场景） | `rol_activity_carthage_travel.dds` | `empty black-sand desert route, cold stars, distant ruins, no caravan or animals` |
| Location | 已接线（round 6 / 无人场景） | `rol_activity_carthage_location.dds` | `empty black-sand sanctuary approach, buried Punic ruins, bronze tools, no figures` |
| `0990` Arrival | 已接线（round 7 / 无人场景） | `rol_event_carthage_0990_arrival.dds` | `empty buried Carthaginian arrival, black dunes, stone threshold, cold night` |
| `1000` Desert | 已接线（旧版保留 / 无需重生图） | `rol_event_carthage_1000_desert.dds` | `black desert under freezing stars, empty ancient charts and tools, cursed salt and ash, Carthaginian ruins in the distance; preserve the usable legacy scene` |
| `1002` Ash Temple | 已接线（round 7 / 无人场景） | `rol_event_carthage_1002_ash_temple.dds` | `empty buried ash temple, fractured columns, starlight, bronze braziers` |
| `1001` Terminal | 已接线（round 7 / 无人场景） | `rol_event_carthage_1001_terminal.dds` | `empty black-sand terminal chamber, covered dais, cold starlight` |
| `1090` Summary | 已接线（round 7 / 无人场景） | `rol_event_carthage_1090_summary.dds` | `empty Carthaginian record room, covered table, desert dawn` |

### 5.6 Legend Circle / 四链总揭示

| 场景 | 状态 | 文件 | Prompt |
|---|---|---|---|
| `rol_legend_circle.0001` | 已接线（round 7 / 无人场景） | `rol_event_legend_circle_revelation.dds` | `empty circular observatory, five unoccupied pedestals, restrained blue-gold light` |

---

## 6) 当前状态审计（2026-10-06）

### 6.1 已接线的重点资源
- Rome 活动图标族已落地。
- Carthage 活动图标族、artifact 图标、整套 event/activity scene 占位资源已落地。
- 五条正式活动链都已接入统一筹备模块图标：`rol_option_expedition_preparation.dds`。
- Legend Circle 大事件背景已接线。

### 6.2 旧版资源保留项
- Munich、Naxos、Sevilla、Carthage 的活动图标族均已存在并通过 DDS 审计；当前没有因为“看起来旧”而重复生图。
- Sevilla artifact 图标已接入 `rol_astrolabe_of_ocean.dds`。
- `@rol_legendary_icon!` 已接入 `rol_legendary_icon.dds`。

### 6.3 当前缺口
- 当前 canonical 资源清单没有发现需要立即生成的新活动图标族；后续只有出现明确占位、缺失或场景冲突时才新增生图批次。

### 6.4 当前最稳妥的替换策略
- 已接线文件统一**同名覆盖**。
- 旧版已有且内容可用的文件直接保留，不为“看起来旧”而重复生成。
- 仅对明确的占位图、缺失图或与场景要求冲突的图补文件，再改 visual / GUI / basename 接线。
- 每次生图前先对照本清单和现有 DDS，避免覆盖已经完成的旧版资源。
- 活动图标透明问题先看 alpha 是否真实存在，再清 `gfx` 缓存，不要只看导出格式名。

### 6.5 当前新增视觉基线
- Munich artifact 专用图标：`rol_nibelung_star_sphere.dds`
- Carthage 事件背景 key 已补齐到 `common/event_backgrounds/rol_event_backgrounds.txt`
- `rol_legendary_icon.dds` 需保持：`60x60`、真透明背景、大金星 + 两颗环绕小星

