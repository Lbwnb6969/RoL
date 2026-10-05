# RoL 竞争者与圣物余响关键图片提示词

> 用途：交给 GPT 图片生成器制作新增事件背景。  
> 统一规格：`1592 x 848`，横向 `16:9`，无透明通道。  
> 最终格式：先输出高质量 PNG，再转换为 `DDS / BC1 (DXT1)`。  
> 风格基线：CK3 中世纪历史幻想事件绘景，写实厚涂、克制的传奇感，不做现代奇幻海报。

## 1. 通用生成要求

将下面这段附加在每条提示词末尾：

```text
Wide 16:9 event background for a medieval grand-strategy game, 1592x848 composition, historically grounded medieval dark-fantasy matte painting, realistic painterly texture, cinematic but restrained lighting, solemn atmosphere, detailed architecture and period objects, clear depth, no modern objects, no text, no letters, no logo, no watermark, no interface, no decorative frame. Keep the central 65 percent readable and uncluttered for event text; avoid important faces or objects at the extreme left and right edges. Do not imitate a specific living artist.
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
A tense encounter at a temporary medieval archaeological expedition camp at dusk. An ambiguous rival has just arrived beside a weathered map table, placing a sealed bundle of copied clues, fragments, and an aged route map before the expedition leader. In the background are pack animals, canvas shelters, lanterns, digging tools, guards, and distant ancient ruins. The rival's evidence looks persuasive but subtly suspicious. Mediterranean and Central European expedition details are blended carefully so the scene can serve several different relic quests. Suspicion, negotiation, and restrained danger; muted earth colors, iron gray, old gold, and warm lantern light. No relic itself is visible and no outcome is predetermined.
```

### 2.2 学者研究真品

- 对应事件：`rol_relic_legacy.0002`
- 建议文件名：`rol_event_relic_scholarly_study.dds`
- 构图目的：可同时容纳剑、星界球、星盘或面具中的任意一件，画面不要锁死具体圣物造型。

```text
A guarded medieval palace study prepared for the examination of a legendary relic. A valuable object rests beneath a partially opened dark cloth on a heavy oak table, its exact form deliberately obscured so it could be a sword, celestial sphere, astrolabe, or ceremonial mask. Scholars examine surrounding sketches, measuring cords, wax tablets, magnifying lenses, and historical records while armed household guards watch from a respectful distance. Candlelight and one shaft of cool daylight reveal dust and careful craftsmanship. The mood balances intellectual wonder with fear of damaging something irreplaceable; quiet prestige, no explosive magic.
```

### 2.3 真品更换主人

- 对应事件：`rol_relic_legacy.0003`
- 建议文件名：`rol_event_relic_new_owner.dds`
- 构图目的：表现传承、赠予或夺取后的新归属，不描绘具体取得方式。

```text
A solemn medieval great hall at first light, prepared for the formal acceptance of a legendary relic by a new owner. A long object-sized reliquary chest stands open on a low stone dais, but the relic inside is mostly hidden by rich folded cloth and reflected light, allowing the scene to represent several different artifacts. Old banners and extinguished candles suggest the previous owner's legacy; newly lit braziers and assembled witnesses mark the beginning of another chapter. The atmosphere is ceremonial, politically charged, and slightly uneasy rather than triumphant. A visual transition from shadowed past on one side to restrained golden dawn on the other.
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

## 6. 当前占位图与碎片远征提示词

代码阶段先复用 rol_event_rome_0990_arrival.dds 作为占位图。以下文件已经注册到 RoL 的背景键，后续生图完成后直接替换对应 DDS：

### 6.1 竞争者契约

- 文件：rol_event_rival_pact.dds
- 背景键：rol_bg_rival_pact

```text
A restrained medieval diplomatic chamber inside a temporary relic expedition headquarters. The expedition leader and an ambiguous rival stand on opposite sides of a scarred oak table covered with route maps, wax seals, shared notes, and a small open purse. A single lantern illuminates hands, maps, and the uneasy distance between the two figures; guards and expedition equipment remain soft in the background. The scene should communicate a practical pact between competitors, with shared credit and future distrust, without showing any specific relic.
```

### 6.2 圣物转手

- 文件：rol_event_relic_legacy_transfer.dds
- 背景键：rol_bg_relic_legacy_transfer

```text
A solemn medieval armory prepared for the transfer of an inherited legendary relic. A covered reliquary rests on a stone workbench between an old household banner and a newly prepared set of travel gear. Witnesses remain in shadow while a gloved hand reaches toward the covered object, leaving the exact artifact ambiguous. Warm forge light, dark iron, folded cloth, sealed documents, and a quiet sense of political succession; no visible writing, no explicit theft, no specific sword, sphere, astrolabe, or mask.
```

### 6.3 碎片远征

- 文件：rol_event_fragment_expedition.dds
- 背景键：rol_bg_fragment_expedition

```text
A compact medieval excavation at the mouth of a newly uncovered chamber. An expedition leader studies a fragment-sized piece of worked metal and stone beside measuring tools, rope, oil lamps, and a half-cleared threshold. The larger legendary relic is absent from the scene; only clues to a matching fragment appear. Narrow passage walls, dust, careful hands, and a small uncertain opening create the feeling of a dangerous short expedition. Neutral materials and lighting must keep the image compatible with a martial blade, celestial sphere, ocean astrolabe, or funerary mask.
```

### 6.4 碎片嵌合升级

- 文件：rol_event_fragment_upgrade.dds
- 背景键：rol_bg_fragment_upgrade

```text
A medieval reliquary workshop at the moment a recovered fragment is fitted into a legendary object hidden beneath a dark cloth. The fragment is visible only as a small distinctive piece locking into a larger silhouette, while the exact relic remains deliberately ambiguous. A scholar, craftsperson, and silent guard observe the alignment; chisels, clamps, wax, and old diagrams rest on the table. The mood is precise and consequential, with controlled golden light, no explosive magic, no readable writing, and enough calm central space for event text.
```

统一规格继续使用 1592 x 848、横向 16:9、无透明通道，最终转换为 DDS / BC1 (DXT1)。所有提示词都要求无文字、无徽标、无水印，并为中央事件文本保留清晰区域。
