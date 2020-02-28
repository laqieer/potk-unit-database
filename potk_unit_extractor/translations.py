from potk_unit_extractor.model import UnitTagKind, UnitTagDesc

TAGS = {
    (UnitTagKind.LARGE, 2):
        UnitTagDesc(
            name="Phantom of the School",
            short_label_name="School",
            description="Also known as Gaku Units",
        ),
    (UnitTagKind.LARGE, 3):
        UnitTagDesc(
            name="Earth",
            short_label_name="Earth",
            description="Earth mode Units",
        ),
    (UnitTagKind.LARGE, 4):
        UnitTagDesc(
            name="Phantom of Love",
            short_label_name="PoL",
            description="Also know as SS/Swimsuit Units",
        ),
    (UnitTagKind.LARGE, 5):
        UnitTagDesc(
            name="Lost Ragnarok",
            short_label_name="LR",
            description="Units from the Lost Ragnarok Chapter",
        ),
    (UnitTagKind.LARGE, 6):
        UnitTagDesc(
            name="Elysium",
            short_label_name="OG",
            description="Units from the Heaven Chapter, Also known as Elysium",
        ),
    (UnitTagKind.LARGE, 7):
        UnitTagDesc(
            name="Integral Noah",
            short_label_name="IN",
            description="Units from the Integral Noah Chapter",
        ),

    (UnitTagKind.SMALL, 2):
        UnitTagDesc(
            name="Collaboration",
            short_label_name="Collab",
            description="Units from Collaboration Events",
        ),
    (UnitTagKind.SMALL, 7):
        UnitTagDesc(
            name="Holy Pool Kingdom",
            short_label_name="Pool",
            description="Units from the Holy Pool Kingdom Faction in the "
                        "PoL story",
        ),
    (UnitTagKind.SMALL, 8):
        UnitTagDesc(
            name="Beach Empire",
            short_label_name="Beach",
            description="Units from the Beach Empire Faction in the PoL story",
        ),
    (UnitTagKind.SMALL, 9):
        UnitTagDesc(
            name="Jungle Union",
            short_label_name="Jungle",
            description="Units from the Jungle Union Faction in the PoL story",
        ),
    (UnitTagKind.SMALL, 10):
        UnitTagDesc(
            name="Harmonia Pontificate",
            short_label_name="Harmonia",
            description="Units from the Harmonia Pontificate Faction in the "
                        "Lost Ragnarok story",
        ),
    (UnitTagKind.SMALL, 11):
        UnitTagDesc(
            name="Chaos Lion Empire",
            short_label_name="Chaos",
            description="Units from the Chaos Lion Empire Faction in the "
                        "Lost Ragnarok story",
        ),
    (UnitTagKind.SMALL, 12):
        UnitTagDesc(
            name="Treisema Republic",
            short_label_name="Treisema",
            description="Units from the Treisema Republic Faction in the "
                        "Lost Ragnarok story",
        ),
    (UnitTagKind.SMALL, 13):
        UnitTagDesc(
            name="Tyrhelm",
            short_label_name="Tyrhelm",
            description="Units from the Tyrhelm Faction in the "
                        "Lost Ragnarok story",
        ),
    (UnitTagKind.SMALL, 14):
        UnitTagDesc(
            name="Tagatame Collaboration",
            short_label_name="Taga",
            description="Units from Tagatame game, also developed by Gumi. "
                        "The game is also known as The Alchemist Code "
                        "in English.",
        ),
    (UnitTagKind.SMALL, 15):
        UnitTagDesc(
            name="Shinobi Nightmare Collaboration",
            short_label_name="Shinobina",
            description="Units from (former) Shinobi Nightmare game, "
                        "also developed by Gumi. "
                        "As of 2020, they game is closed, "
                        "but units may still be used in PotK",
        ),
    (UnitTagKind.SMALL, 16):
        UnitTagDesc(
            name="Command Killers",
            short_label_name="CK",
            description="Units from the Command Killers Faction, featured in "
                        "both Lost Ragnarok and Integral Noah Chapters",
        ),
    (UnitTagKind.SMALL, 17):
        UnitTagDesc(
            name="Integral Killers",
            short_label_name="IK",
            description="One of the factions featured in the "
                        "Integral Noah Chapter",
        ),
    (UnitTagKind.SMALL, 18):
        UnitTagDesc(
            name="Imitate Killers",
            short_label_name="ImK",
            description="One of the factions featured in the "
                        "Integral Noah Chapter",
        ),

    (UnitTagKind.CLOTHING, 2):
        UnitTagDesc(
            name="New Year",
            short_label_name="NY",
            description="Units released on New Year's Events",
        ),
    (UnitTagKind.CLOTHING, 3):
        UnitTagDesc(
            name="Valentines",
            short_label_name="Val",
            description="Units released on Valentine's Day Events",
        ),
    (UnitTagKind.CLOTHING, 4):
        UnitTagDesc(
            name="Wedding",
            short_label_name="Wed",
            description="Units released on Wedding Events",
        ),
    (UnitTagKind.CLOTHING, 5):
        UnitTagDesc(
            name="Swimsuit",
            short_label_name="SS",
            description="Units wearing Swimsuits",
        ),
    (UnitTagKind.CLOTHING, 6):
        UnitTagDesc(
            name="Halloween",
            short_label_name="Hallo",
            description="Units released on Halloween Events",
        ),
    (UnitTagKind.CLOTHING, 7):
        UnitTagDesc(
            name="Christmas",
            short_label_name="Xmas",
            description="Units released on Christmas Events",
        ),
    (UnitTagKind.CLOTHING, 8):
        UnitTagDesc(
            name="Black Killers",
            short_label_name="BK",
            description="Black Killers variants of the 1st Killers",
        ),
    (UnitTagKind.CLOTHING, 9):
        UnitTagDesc(
            name="Gym Suit",
            short_label_name="Gym",
            description="Units wearing Gym Suits",
        ),
    (UnitTagKind.CLOTHING, 10):
        UnitTagDesc(
            name="School Uniform",
            short_label_name="JK",
            description="Units wearing School Uniforms",
        ),
    (UnitTagKind.CLOTHING, 11):
        UnitTagDesc(
            name="Maid Uniform",
            short_label_name="Maid",
            description="Units wearing Maid Uniforms",
        ),
    (UnitTagKind.CLOTHING, 12):
        UnitTagDesc(
            name="Collaboration Cosplay",
            short_label_name="Cosplay",
            description="Units in Cosplay from a Collaboration Event",
        ),
    (UnitTagKind.CLOTHING, 13):
        UnitTagDesc(
            name="Yukata",
            short_label_name="Yukata",
            description="Units wearing an Yukata",
        ),
    (UnitTagKind.CLOTHING, 14):
        UnitTagDesc(
            name="Easter",
            short_label_name="Easter",
            description="Units released on Easter Events",
        ),
    (UnitTagKind.CLOTHING, 15):
        UnitTagDesc(
            name="Karma Killers",
            short_label_name="Karma",
            description="Units from the Karma Killers group from the "
                        "Chaos Lion Empire in the Lost Ragnarok story",
        ),
    (UnitTagKind.CLOTHING, 16):
        UnitTagDesc(
            name="Saint Killers",
            short_label_name="Saint",
            description="Units from the Saint Killers group from the "
                        "Harmonia Pontificate in the Lost Ragnarok story",
        ),
    (UnitTagKind.CLOTHING, 17):
        UnitTagDesc(
            name="Order Killers",
            short_label_name="Order",
            description="Units from the Order Killers group from the "
                        "Treisema Republic in the Lost Ragnarok story",
        ),
    (UnitTagKind.CLOTHING, 18):
        UnitTagDesc(
            name="Fatom Killers",
            short_label_name="Fatom",
            description="\"Excessive\" version of the units, launched/updated "
                        "as an recurring April 1st joke",
        ),
    (UnitTagKind.CLOTHING, 19):
        UnitTagDesc(
            name="Disruptors",
            short_label_name="DP",
            description="Units from the Disruptors Faction in the "
                        "Lost Ragnarok story",
        ),
    (UnitTagKind.CLOTHING, 20):
        UnitTagDesc(
            name="God Killers",
            short_label_name="GK",
            description="The leaders of each major faction in the "
                        "Lost Ragnarok story",
        ),

    (UnitTagKind.GENERATION, 2):
        UnitTagDesc(
            name="First Killers",
            short_label_name="1st",
            description="Units from the First Generation",
        ),
    (UnitTagKind.GENERATION, 3):
        UnitTagDesc(
            name="Sevenths Killers",
            short_label_name="7th",
            description="Units from the Seventh Generation",
        ),
    (UnitTagKind.GENERATION, 4):
        UnitTagDesc(
            name="Ancient Killers",
            short_label_name="Ancient",
            description="Units from Ancient Killers Generation",
        ),
}

# TODO Load from a yaml file?
SKILLS = {}
