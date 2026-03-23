# RoL 自定义背景图命名与生图 Prompt 清单

适用范围：当前四条正式主线（Rome / Munich / Naxos / Sevilla）的**扩展集**背景。

## 统一规则

- 最终导入目录：`C:\CK3Mods\RoL\gfx\interface\illustrations\event_scenes\`
- 推荐出图尺寸：`1592x848`
- 最终格式：`DDS / DXT1(BC1) / 无透明`
- 不要：文字、logo、水印、UI、近景大头角色
- 通用前缀（每张图都加在最前面）：

```text
16:9 widescreen CK3 event background, epic dark fantasy matte painting, highly detailed, cinematic lighting, atmospheric, no text, no logo, no watermark, no UI
```

> 说明：本批代码已先把同名 `.dds` 占位文件接入。你后续只要按下表**覆盖同名文件**即可，不需要再改脚本 key。

---

## Rome / Mars

| 场景 | 文件名 | 用法 / key | 生图补充 prompt |
|---|---|---|---|
| 发现事件 | `rol_event_rome_discovery.dds` | `rol_discovery_bg_rome` | ancient Roman underground passage, relief of Mars, crimson torchlight, cracked stone walls, lost legion relic aura |
| 活动旅途 | `rol_activity_rome_travel.dds` | Rome activity travel texture | night journey through Roman underground corridor, ranks of torches, damp stone walls, oppressive atmosphere |
| 活动地点 | `rol_activity_rome_location.dds` | Rome activity location texture | sealed catacomb main chamber, heavy stone gate, ritual fire and chains, Roman legion insignia |
| `0990` 抵达封印地宫 | `rol_event_rome_0990_arrival.dds` | `rol_bg_rome_0990_arrival` | sealed catacomb entrance, half-collapsed arch, iron gate with wax seals, braziers, tense pre-expedition mood |
| `1000` 深入地宫 | `rol_event_rome_1000_catacombs.dds` | `rol_bg_rome_1000_catacombs` | deep Palatine catacombs, broken statues, red dust haze, distant altar of Mars |
| `1002` 落石回廊 | `rol_event_rome_1002_collapse.dds` | `rol_bg_rome_1002_collapse` | narrow corridor with falling boulders, overturned torches, shattered dust, sudden danger |
| `1003` 血誓祭坛 | `rol_event_rome_1003_altar.dds` | `rol_bg_rome_1003_altar` | blood oath altar, stone offering table, crimson ritual markings, statue of Mars, solemn and mysterious |
| `1004` 禁卫残影 | `rol_event_rome_1004_guardians.dds` | `rol_bg_rome_1004_guardians` | underground war hall, ghostly praetorian formation, glowing crimson eyes, ancient Roman heavy armor silhouettes |
| `1001` 终局赐福 | `rol_event_rome_1001_terminal.dds` | `rol_success_bg_rome` | blessing of Mars, legendary blade floating above altar, red-gold divine light, war temple atmosphere |
| `1090` 远征结算 | `rol_event_rome_1090_summary.dds` | `rol_bg_rome_1090_summary` | Roman armory after expedition, relic on display, braziers and dark red war banners, victorious but solemn |

## Munich / Nibelung

| 场景 | 文件名 | 用法 / key | 生图补充 prompt |
|---|---|---|---|
| 发现事件 | `rol_event_munich_discovery.dds` | `rol_discovery_bg_munich` | Bavarian mountain omen, ancient stone gate buried in snow, pale starlight, cold mist |
| 活动旅途 | `rol_activity_munich_travel.dds` | Munich activity travel texture | expedition through Alpine blizzard trail, cold blue daylight, whipping snow, steep mountain ridge |
| 活动地点 | `rol_activity_munich_location.dds` | Munich activity location texture | frozen star crypt, frost-covered pillars, ancient sarcophagi, cold blue reflections |
| `0990` 星冢入口 | `rol_event_munich_0990_arrival.dds` | `rol_bg_munich_0990_arrival` | mouth of the star crypt, split ice gate, swirling snow fog, faint runic glow |
| `1000` 踏入极寒 | `rol_event_munich_1000_frost.dds` | `rol_bg_munich_1000_frost` | core frost corridor, giant frozen gate, chained ice, piercing blue-white light |
| `1002` 心灵深渊 | `rol_event_munich_1002_abyss.dds` | `rol_bg_munich_1002_abyss` | abyssal cavern with mirrored ice reflecting stars, cold violet illusions, eerie stillness |
| `1001` 星辰陨心 | `rol_event_munich_1001_terminal.dds` | `rol_success_bg_munich` | Nibelung star sphere floating above frozen dais, starlight raining down, ancient ice shrine |
| `1090` 远征结算 | `rol_event_munich_1090_summary.dds` | `rol_bg_munich_1090_summary` | quiet post-expedition snow camp beside star crypt, relic illuminating scrolls and frost, scholarly triumph |

## Naxos / Thera

| 场景 | 文件名 | 用法 / key | 生图补充 prompt |
|---|---|---|---|
| 发现事件 | `rol_event_naxos_discovery.dds` | `rol_discovery_bg_naxos` | Aegean volcanic island ruins, broken stairs descending underground, black rock and golden sacred traces |
| 活动旅途 | `rol_activity_naxos_travel.dds` | Naxos activity travel texture | approach to Thera volcanic sea cliffs, black volcanic stone, sea wind and embers, dusk light |
| 活动地点 | `rol_activity_naxos_location.dds` | Naxos activity location texture | underground palace of Thera, black-gold colonnades, ancient imperial statues, stern majesty |
| `0990` 抵达泰拉 | `rol_event_naxos_0990_arrival.dds` | `rol_bg_naxos_0990_arrival` | sea cliff entrance at Thera, stone stairway down into the earth, sea mist, lost palace ruins |
| `1000` 帝皇前厅 | `rol_event_naxos_1000_antechamber.dds` | `rol_bg_naxos_1000_antechamber` | gigantic black-gold doors, braziers before imperial icons, baroque techno-relic atmosphere, sacred pressure |
| `1002` 验证大厅 | `rol_event_naxos_1002_verification.dds` | `rol_bg_naxos_1002_verification` | long verification hall, ancient mechanisms and trial altar, cold golden light, ruthless order |
| `1003` 禁军守门阵列 | `rol_event_naxos_1003_custodes.dds` | `rol_bg_naxos_1003_custodes` | golden guardian silhouettes in formation, long polearms, impassable sacred gate, imperial holiness |
| `1001` 最终裁决 | `rol_event_naxos_1001_terminal.dds` | `rol_success_bg_naxos` | throne-like sanctuary, sacred gold light, elite guard insignia, final command bestowed |
| `1090` 远征结算 | `rol_event_naxos_1090_summary.dds` | `rol_bg_naxos_1090_summary` | underground sanctuary at rest, ritual wargear and banners, lingering glory, solemn closure |

## Sevilla / Astrolabe

| 场景 | 文件名 | 用法 / key | 生图补充 prompt |
|---|---|---|---|
| 发现事件 | `rol_event_sevilla_discovery.dds` | `rol_discovery_bg_sevilla` | magical sea chart spread across tavern table in old port of Sevilla, navigation tools, candlelight, salt mist |
| 活动旅途 | `rol_activity_sevilla_travel.dds` | Sevilla activity travel texture | forbidden ocean voyage, black waves, distant lightning, sailing ship charging into mist |
| 活动地点 | `rol_activity_sevilla_location.dds` | Sevilla activity location texture | quays of Triana, Iberian port, ropes and cargo crates, golden sea breeze at dawn |
| `0990` 特里亚纳码头 | `rol_event_sevilla_0990_quays.dds` | `rol_bg_sevilla_0990_quays` | old sailing ships and dock lanterns, busy harbor district, crates and mooring ropes, excitement before departure |
| `1000` 海峡走私者 | `rol_event_sevilla_1000_smugglers.dds` | `rol_bg_sevilla_1000_smugglers` | hidden cove, rough smugglers, weathered fast boats, warm lantern light and deep shadows, illicit deal atmosphere |
| `1002` 磁暴风墙 | `rol_event_sevilla_1002_stormwall.dds` | `rol_bg_sevilla_1002_stormwall` | magnetic storm wall at world’s edge, black sea vortex, purple-red sky, electromagnetic tempest, mad compass needles |
| `1001` 镜海星盘 | `rol_event_sevilla_1001_terminal.dds` | `rol_success_bg_sevilla` | perfectly calm mirror sea, glowing astrolabe floating above water, sacred blue-gold radiance, destiny of the age of exploration |
| `1090` 远征结算 | `rol_event_sevilla_1090_summary.dds` | `rol_bg_sevilla_1090_summary` | triumphant return to Sevilla harbor, astrolabe with navigation charts on display, dawn harbor, victorious expedition mood |

