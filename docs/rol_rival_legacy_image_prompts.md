# RoL 竞争者与圣物余响关键图片提示词

> 用途：交给 GPT 图片生成器制作新增事件背景。  
> 统一规格：`1592 x 848`，横向 `16:9`，无透明通道。  
> 最终格式：先输出高质量 PNG，再转换为 `DDS / BC1 (DXT1)`。  
> 风格基线：CK3 中世纪历史幻想事件绘景，写实厚涂、克制的传奇感，不做现代奇幻海报。

## 1. 通用生成要求

事件背景默认只画环境和道具，不生成人物、动物、尸体、雕像或人形图案。人物由 CK3 事件的 `left_portrait`、`right_portrait` 和 `window_characters` 叠加；背景要给这些肖像以及中央事件文字留出安静的负空间。若某张图确实需要表现人物动作，应单独作为角色插画处理，不要替换事件背景。

将下面这段附加在每条提示词末尾：

```text
Wide 16:9 event background for a medieval grand-strategy game, 1592x848 composition, historically grounded medieval dark-fantasy matte painting, realistic painterly texture, cinematic but restrained lighting, solemn atmosphere, detailed architecture and period objects, clear depth, no modern objects, no text, no letters, no logo, no watermark, no interface, no decorative frame. Keep the central 65 percent readable and uncluttered for event text; avoid important faces or objects at the extreme left and right edges. Do not imitate a specific living artist.
No people, no human figures, no animals, no corpses, no statues, no carved faces, no silhouettes, no hands, no footprints, and no reflections of people; the scene must be empty and ready for CK3 code-driven portraits to overlay.
```

统一负面约束：

```text
Avoid anime, cartoon, glossy mobile-game art, exaggerated high fantasy, oversized magical particles, neon colors, modern clothing, modern weapons, photorealistic photography, close-up portrait composition, readable writing, UI elements, borders, split panels, collage, excessive bloom, black crushed shadows.
```

## 2. 第一优先级

### 2.1 远征竞争者

- 对应事件：`rol_rival.1000`
- 建议文件名：`rol_event_rival_expedition.dds`
- 构图目的：兼容五条远征，不出现任何单一圣物，既可解释为同行宾客，也可解释为后来赶上的宫廷人物。

```text
A deserted temporary medieval archaeological expedition camp at dusk, moments after an unknown competitor left evidence on a weathered map table. A sealed bundle of copied clues, fragments, and an aged route map rests beside wax seals and measuring tools; the evidence looks persuasive but subtly suspicious. Canvas shelters, empty lantern stands, digging tools, coiled rope, and distant ancient ruins establish the expedition without showing a single person or animal. Mediterranean and Central European details are blended carefully so the scene can serve several relic quests. Suspicion, negotiation, and restrained danger; muted earth colors, iron gray, old gold, and warm lantern light. No relic itself is visible and no outcome is predetermined.
```

### 2.2 学者研究真品

- 对应事件：`rol_relic_legacy.0002`
- 建议文件名：`rol_event_relic_scholarly_study.dds`
- 构图目的：可同时容纳剑、星界球、星盘或面具中的任意一件，画面不要锁死具体圣物造型。

```text
An empty guarded medieval palace study prepared for the examination of a legendary relic. A valuable object rests beneath a partially opened dark cloth on a heavy oak table, its exact form deliberately obscured so it could be a sword, celestial sphere, astrolabe, or ceremonial mask. Surrounding sketches, measuring cords, wax tablets, magnifying lenses, sealed records, empty chairs, and a distant weapons rack show that scholars and guards were expected but have stepped away. Candlelight and one shaft of cool daylight reveal dust and careful craftsmanship. The mood balances intellectual wonder with fear of damaging something irreplaceable; quiet prestige, no explosive magic, no identifiable artifact silhouette.
```

### 2.3 真品更换主人

- 对应事件：`rol_relic_legacy.0003`
- 建议文件名：`rol_event_relic_new_owner.dds`
- 构图目的：表现传承、赠予或夺取后的新归属，不描绘具体取得方式。

```text
An empty solemn medieval great hall at first light, prepared for the formal acceptance of a legendary relic by a new owner. A long object-sized reliquary chest stands open on a low stone dais, but the relic inside is mostly hidden by rich folded cloth and reflected light, allowing the scene to represent several different artifacts. Old banners and extinguished candles suggest the previous owner's legacy; newly lit braziers, an unused ceremonial table, and a clear aisle mark the beginning of another chapter. The atmosphere is ceremonial, politically charged, and slightly uneasy rather than triumphant. A visual transition from shadowed past on one side to restrained golden dawn on the other, with no witnesses visible.
```

## 3. 第二优先级

### 3.1 圣物要求持有者践行传奇

- 对应事件：`rol_relic_legacy.0001`
- 建议文件名：`rol_event_relic_legendary_duty.dds`

```text
A medieval ruler alone in a dim ceremonial chamber before a covered legendary relic displayed on a stone pedestal. Four understated symbolic motifs appear in the surrounding architecture without becoming literal objects: a Roman martial relief, a celestial star pattern, a carved maritime compass rose, and a Punic funerary motif. Courtiers wait as distant silhouettes beyond an archway, expecting the ruler to embody the relic's legend. The covered object remains ambiguous. Heavy responsibility, inherited myth, controlled red-gold and deep blue lighting, solemn and introspective rather than supernatural spectacle.
```

### 3.2 Naxos 誓卫检阅

- 对应事件：`rol_relic_legacy.0101`
- 建议文件名：`rol_event_naxos_guard_review.dds`

```text
A formal inspection of an elite medieval Aegean oath-guard in a black-stone coastal fortress courtyard. A small disciplined formation wears historically grounded Byzantine-inspired lamellar armor with restrained black-and-gold accents and carries long spears. Officers inspect equipment, shield alignment, and formation discipline while volcanic cliffs and a cold blue sea appear beyond the walls. The troops look rare, expensive, and formidable, not fantastical super-soldiers. Morning wind moves narrow ceremonial banners; hard sunlight, solemn military order, no combat.
```

### 3.3 Naxos 老兵请愿扩编

- 对应事件：`rol_relic_legacy.0102`
- 建议文件名：`rol_event_naxos_veteran_petition.dds`

```text
Inside a Byzantine-inspired island armory, several scarred veteran oath-guards present a petition to expand their ancient corps. On one side, a few immaculate old suits of black-and-gold lamellar armor and heirloom spears are arranged with ritual precision; on the other, unfinished armor, raw materials, empty weapon racks, and waiting young recruits show the cost and risk of expansion. The veterans are dignified and serious, not desperate. Warm forge light meets cool sea light, creating a visual choice between preserving an elite tradition and allowing it to grow.
```

### 3.4 Naxos 继承誓言

- 对应事件：`rol_relic_legacy.0103`
- 建议文件名：`rol_event_naxos_oath_inheritance.dds`

```text
A night oath ceremony in an ancient Aegean sanctuary after the death of a commander. Veteran guards kneel in disciplined formation before an undecorated successor standing at the foot of a black-stone dais. The predecessor's empty cloak, sealed helmet, and extinguished lamp rest nearby as respectful symbols of death; no corpse is shown. A new brazier waits to be lit beside an old fading flame. Byzantine-inspired architecture, volcanic stone, restrained gold, deep blue night, grief transformed into duty. The scene should leave open whether the successor accepts or refuses the oath.
```

## 4. 生成与筛选标准

每张建议让 GPT 生成 `3` 个构图版本，筛选时按以下顺序判断：

1. 场景是否一眼符合 CK3 中世纪事件背景，而不是卡牌插画或宣传海报。
2. 中央区域是否足够安静，事件文字覆盖后仍能阅读。
3. 是否没有生成可读文字、现代物件、UI、边框或水印。
4. 竞争者图是否能兼容五条远征；通用圣物图是否没有锁死某一件真品。
5. Naxos 士兵是否保持拜占庭/爱琴海历史幻想感，没有科幻盔甲或过度华丽金甲。
6. 暗部是否保留细节，转换 BC1 后不会变成整片黑色。

## 5. 建议生成顺序

1. `rol_event_rival_expedition.dds`
2. `rol_event_relic_scholarly_study.dds`
3. `rol_event_relic_new_owner.dds`
4. `rol_event_relic_legendary_duty.dds`
5. `rol_event_naxos_guard_review.dds`
6. `rol_event_naxos_veteran_petition.dds`
7. `rol_event_naxos_oath_inheritance.dds`

前三张覆盖面最高，应优先生成和筛选。图片完成后仍需另行注册 background key 并接入事件；仅放入 `gfx` 目录不会自动生效。

## 6. 当前已接入的竞争者、传承与碎片场景

以下资源已经注册到 RoL 的背景键并接入当前事件链。它们均按无人环境背景处理；旧版仍可用的资源继续保留，后续不重复调用生图 API，除非出现明确占位、缺失或场景冲突：

### 6.1 竞争者契约

- 文件：rol_event_rival_pact.dds
- 背景键：rol_bg_rival_pact

```text
An empty restrained medieval diplomatic chamber inside a temporary relic expedition headquarters. A scarred oak table holds route maps with no readable writing, wax seals, shared notes, two unopened travel satchels, and a small open purse. A single lantern illuminates the table while canvas walls, rolled maps, spare bedrolls, and expedition equipment recede into cool shadow. The scene communicates a practical pact between competitors through objects left ready for negotiation, with shared credit and future distrust, without showing any specific relic. No people, animals, hands, silhouettes, statues, or human-shaped shadows.
```

### 6.2 圣物转手

- 文件：rol_event_relic_legacy_transfer.dds
- 背景键：rol_bg_relic_legacy_transfer

```text
An empty solemn medieval armory prepared for the transfer of an inherited legendary relic. A covered reliquary rests on a stone workbench between an old household banner and a newly prepared set of travel gear. An unused ceremonial stand, folded gloves, sealed documents with no readable writing, dark iron racks, and warm forge light communicate political succession without showing a hand or witness. The exact artifact remains ambiguous beneath the cloth; no explicit theft, no specific sword, sphere, astrolabe, or mask. No people, animals, statues, silhouettes, or human-shaped shadows.
```

### 6.3 碎片远征

- 文件：rol_event_fragment_expedition.dds
- 背景键：rol_bg_fragment_expedition

```text
A compact empty medieval excavation at the mouth of a newly uncovered chamber. A fragment-sized piece of worked metal and stone rests beside measuring tools, rope, oil lamps, chalk marks with no readable writing, and a half-cleared threshold. The larger legendary relic is absent; only clues to a matching fragment appear. Narrow passage walls, damp roots, dust, and a small uncertain opening create the feeling of a dangerous short expedition. Neutral materials and lighting keep the image compatible with a martial blade, celestial sphere, ocean astrolabe, or funerary mask. No people, animals, hands, footprints, statues, silhouettes, or human-shaped shadows.
```

### 6.4 碎片嵌合升级

- 文件：rol_event_fragment_upgrade.dds
- 背景键：rol_bg_fragment_upgrade

```text
A quiet empty medieval reliquary workshop prepared for fitting a recovered fragment into a legendary object hidden beneath a dark cloth. The fragment is visible only as a small distinctive piece beside clamps, chisels, wax, alignment cords, and old diagrams with no readable writing; the exact relic remains deliberately ambiguous. An unused work stool, covered tools, and a stone hearth suggest careful craftsmanship without showing any observer. The mood is precise and consequential, with controlled golden light, no explosive magic, and calm central space for event text. No people, animals, hands, statues, silhouettes, or human-shaped shadows.
```

统一规格继续使用 1592 x 848、横向 16:9、无透明通道，最终转换为 DDS / BC1 (DXT1)。所有提示词都要求无文字、无徽标、无水印，并为中央事件文本保留清晰区域。


## 7. Naxos / Thera 无人事件背景批次

Naxos 的事件背景统一使用黑色火山石、爱琴海海风、克制的旧金色几何纹样和冷灰蓝光。背景只画建筑、器物和光线，不画守卫、人物、雕像、盔甲人台或人形浮雕；守卫和继承者由事件代码叠加。建议文件名分别对应 `rol_event_naxos_*.dds`，最终规格为 `1592x848 / BC1(DXT1)`。

```text
An empty black-volcanic Aegean coastal ruin at first discovery: a weathered stairway descends from sea cliffs to a sealed underground doorway, with broken columns, salt mist, and restrained old-gold geometric marks on the stone. No readable writing and no statues. The place must feel ancient, guarded by architecture alone, and ready for CK3 event portraits to overlay.
```

```text
An empty sea-cliff entrance to an underground Thera sanctuary, with a curving black-stone stairway, a heavy sealed door, scattered volcanic rubble, one small oil lamp, and distant cold Aegean water. Use restrained gold trim and blue-gray storm light. No people, animals, guards, armor, statues, relief faces, or human-shaped shadows.
```

```text
An empty Naxos antechamber behind enormous black-and-gold geometric doors. Braziers burn on low stone stands; abstract sun and spear motifs are carved as simple non-human geometry, never as figures. The floor is dusty and symmetrical, the sacred pressure comes from scale and silence. No guards, statues, armor, portraits, or human silhouettes.
```

```text
An empty Thera terminal sanctuary with a raised stone dais beneath a circular skylight and restrained golden light. A covered reliquary or closed stone pedestal remains deliberately ambiguous; dark volcanic columns and sea-blue shadow frame the chamber. No throne occupant, statue, guardian, armor, human relief, animal, or human-shaped shadow.
```

```text
An empty verification hall inside a black-volcanic sanctuary, lined with ancient mechanical wheels, counterweights, channels, and a simple stone testing altar. Cold blue daylight meets a narrow warm beam; every motif is geometric and non-human. No people, guards, statues, armor, faces, or silhouettes.
```

```text
An empty custodes gate deep inside the Thera sanctuary: a monumental sealed door, rows of ceremonial spears stored on wall racks, extinguished braziers, and black-gold geometric seals. The sacred guard is implied by the locked architecture and abandoned equipment. No soldiers, armor mannequins, statues, relief faces, animals, or human shadows.
```

```text
An empty Naxos sanctuary after the relic expedition, with folded neutral banners, a cold hearth, orderly weapon racks, and a covered stone display table in a quiet black-stone hall. Pale sea light and one restrained brazier suggest closure without triumph. No armor displays shaped like bodies, no people, statues, portraits, or human silhouettes.
```
