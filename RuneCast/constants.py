ORES = [
    "Copper ore", "Tin ore", "Iron ore", "Coal",
    "Mithril ore", "Adamantite ore", "Runite ore",
    "Luminite", "Orichalcite ore", "Drakolith",
    "Banite ore", "Light animica", "Dark animica"
]

STONE_SPIRITS = [
    "Copper stone spirit", "Tin stone spirit", "Iron stone spirit", "Coal stone spirit",
    "Mithril stone spirit", "Adamantite stone spirit", "Runite stone spirit",
    "Luminite stone spirit", "Orichalcite stone spirit", "Drakolith stone spirit",
    "Banite stone spirit", "Light animica stone spirit", "Dark animica stone spirit"
]

PRECURSOR_BARS = [
    "Bronze bar", "Iron bar", "Steel bar", "Mithril bar",
    "Adamant bar", "Rune bar", "Orikalkum bar",
    "Necronium bar", "Bane bar", "Elder rune bar"
]

INTERMEDIATE_BARS = [
    "Concentrated alloy bar",
    "Enriched alloy bar",
    "Immaculate alloy bar",
]

CORE_ITEM = ["Glorious bar"]

ITEM_GROUPS = {
    1: CORE_ITEM,
    2: INTERMEDIATE_BARS,
    3: PRECURSOR_BARS,
    4: STONE_SPIRITS,
    5: ORES,
}


def get_items_by_depth(depth):
    items = []
    for d in range(1, int(depth) + 1):
        items.extend(ITEM_GROUPS.get(d, []))
    return items
