"""Constants for the Cyclus library."""

from enum import IntEnum

HOST = "cyclusnv.nl"


class WasteType(IntEnum):
    """Waste stream types as defined by Cyclus NV.

    Canonical IDs match the top-level afvalstroom IDs returned by the API.
    Gouda-specific child IDs are mapped to their canonical parent via _missing_.
    """

    GFT = 1
    RESIDUAL_WASTE = 2
    PAPER = 3
    CONSTRUCTION_WASTE = 5
    ELECTRICAL_APPLIANCES = 6
    GLASS = 7
    THRIFT_STORE = 8
    LARGE_HOUSEHOLD_WASTE = 9
    HAZARDOUS_WASTE = 10
    TEXTILES = 11
    ASBESTOS = 12
    RECYCLING_CENTER = 13
    PMD = 14
    NOTIFICATION_FORM = 756
    MOBILE_RECYCLING_CENTER = 757
    CHRISTMAS_TREES = 758
    GARDEN_WASTE = 760
    DEMOLITION_COMPANY = 763

    @classmethod
    def _missing_(cls, value: object) -> "WasteType | None":
        """Map Gouda-specific child IDs to their canonical parent."""
        _gouda_map: dict[int, WasteType] = {
            129: cls.GFT,
            491: cls.RESIDUAL_WASTE,
            385: cls.PAPER,
            638: cls.CONSTRUCTION_WASTE,
            183: cls.GLASS,
            335: cls.THRIFT_STORE,
            231: cls.LARGE_HOUSEHOLD_WASTE,
            285: cls.HAZARDOUS_WASTE,
            588: cls.TEXTILES,
            75: cls.ASBESTOS,
            22: cls.RECYCLING_CENTER,
            439: cls.PMD,
            748: cls.MOBILE_RECYCLING_CENTER,
            727: cls.CHRISTMAS_TREES,
            538: cls.GARDEN_WASTE,
        }
        if isinstance(value, int):
            return _gouda_map.get(value)
        return None
