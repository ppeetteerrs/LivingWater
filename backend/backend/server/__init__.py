VERSION = "3.0"

SETTINGS = {
    "ADMIN_WEIGHTS_RATIO": [10, 5, 1],
    "DICT_DB_PATH": "server/backend/db_files/dictionary.db",
    "VERSES_DB_PATH": "server/backend/db_files/verses.db",
    "PARAMS": {
        "TF_a_zero": 1,
        "TF_a_inf": 0.15,  # Curvature Parameter
        "TF_a_n": 0.2,  # Maximum Penalty for low Rarity among Verses
        "TF_n": 1,

        # Useless ATM
        "RPIV_a_zero": 0.98,  # Maximum Penalty for low Relative Popularity In Verse
        "RPIV_a_inf": 1.1,  # Curvature Parameter
        "RPIV_a_n": 1,
        "RPIV_n": 1,

        "RPAV_a_zero": 0.95,  # Maximum Penalty for low Relative Popularity Across Verses
        "RPAV_a_inf": 1.1,  # Curvature Parameter
        "RPAV_a_n": 1,
        "RPAV_n": 1,

        # Matched bonus
        "MB_a_zero": 0,  # Maximum Penalty for not matching any word
        "MB_a_inf": 49 / 40,  # if a_half = m, a_inf = m^2/(2m-1)
        "MB_a_n": 0.8,
        "MB_n": 0.5,
    }
}

__all__ = ["VERSION", "SETTINGS"]
