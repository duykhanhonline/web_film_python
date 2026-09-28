from dataclasses import dataclass


@dataclass(frozen=True)
class SlotSize:
    desktop: tuple[int, int]
    mobile: tuple[int, int]


# Fixed sizes reserve space so the layout never shifts. Keep in sync with .ad-slot in input.css.
SLOT_SIZES = {
    "ad-billboard": SlotSize(desktop=(970, 250), mobile=(320, 100)),
    "ad-infeed": SlotSize(desktop=(728, 90), mobile=(320, 100)),
    "ad-sidebar": SlotSize(desktop=(300, 250), mobile=(300, 250)),
}
