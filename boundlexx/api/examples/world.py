from boundlexx.api.utils import get_base_url

WORLD_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/worlds/1/",
    "id": 251,
    "name": "aus3_t6_3",
    "display_name": "Typhuchis",
    "region": "aus",
    "tier": 6,
    "description": "WORLD_TYPE_RIFT",
    "size": 192,
    "world_type": "RIFT",
    "time_offset": "2020-07-14T12:01:11.160609Z",
    "is_sovereign": False,
    "is_perm": False,
    "is_creative": False,
    "is_locked": False,
    "is_public": True,
    "number_of_regions": 34,
    "start": "2020-07-26T21:40:35Z",
    "end": "2020-07-31T15:07:13Z",
    "atmosphere_color": "#b4d2ff",
    "water_color": "#c359ff",
}

WORLD_COLORS_EXAMPLE = {
    "world_url": f"{get_base_url()}/api/v1/worlds/10/",
    "block_colors": [
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10850/",
                "game_id": 10850,
                "string_id": "ITEM_TYPE_ASH_DEFAULT_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/66/",
                "game_id": 66,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/9555/",
                "game_id": 9555,
                "string_id": "ITEM_TYPE_CRYSTAL_GLEAM_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/33/",
                "game_id": 33,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/9838/",
                "game_id": 9838,
                "string_id": "ITEM_TYPE_FLORA_FLOWER_1",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/90/",
                "game_id": 90,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/9839/",
                "game_id": 9839,
                "string_id": "ITEM_TYPE_FLORA_FLOWER_2",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/244/",
                "game_id": 244,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/9840/",
                "game_id": 9840,
                "string_id": "ITEM_TYPE_FLORA_FLOWER_3",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/34/",
                "game_id": 34,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/9841/",
                "game_id": 9841,
                "string_id": "ITEM_TYPE_FLORA_FLOWER_4",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/210/",
                "game_id": 210,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10775/",
                "game_id": 10775,
                "string_id": "ITEM_TYPE_FLORA_PLANT_FIBROUS",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/67/",
                "game_id": 67,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10774/",
                "game_id": 10774,
                "string_id": "ITEM_TYPE_FLORA_PLANT_INKY",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/68/",
                "game_id": 68,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10788/",
                "game_id": 10788,
                "string_id": "ITEM_TYPE_FUNGUS_AMANITA",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/249/",
                "game_id": 249,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10789/",
                "game_id": 10789,
                "string_id": "ITEM_TYPE_FUNGUS_BRACKET",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/235/",
                "game_id": 235,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10790/",
                "game_id": 10790,
                "string_id": "ITEM_TYPE_FUNGUS_CORAL",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/8/",
                "game_id": 8,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10792/",
                "game_id": 10792,
                "string_id": "ITEM_TYPE_FUNGUS_DRIPPING",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/9/",
                "game_id": 9,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10793/",
                "game_id": 10793,
                "string_id": "ITEM_TYPE_FUNGUS_GLOWING",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/210/",
                "game_id": 210,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10791/",
                "game_id": 10791,
                "string_id": "ITEM_TYPE_FUNGUS_SCATTER",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/210/",
                "game_id": 210,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/3085/",
                "game_id": 3085,
                "string_id": "ITEM_TYPE_GRASS_BARBED_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/66/",
                "game_id": 66,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/6157/",
                "game_id": 6157,
                "string_id": "ITEM_TYPE_GRASS_GNARLED_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/68/",
                "game_id": 68,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/13/",
                "game_id": 13,
                "string_id": "ITEM_TYPE_GRASS_VERDANT_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/239/",
                "game_id": 239,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10814/",
                "game_id": 10814,
                "string_id": "ITEM_TYPE_GRAVEL_DEFAULT_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/114/",
                "game_id": 114,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10870/",
                "game_id": 10870,
                "string_id": "ITEM_TYPE_GROWTH_DEFAULT_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/127/",
                "game_id": 127,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10842/",
                "game_id": 10842,
                "string_id": "ITEM_TYPE_ICE_DEFAULT_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/160/",
                "game_id": 160,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10806/",
                "game_id": 10806,
                "string_id": "ITEM_TYPE_ICE_GLACIER_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/130/",
                "game_id": 130,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10866/",
                "game_id": 10866,
                "string_id": "ITEM_TYPE_MOULD_DEFAULT_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/9/",
                "game_id": 9,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10846/",
                "game_id": 10846,
                "string_id": "ITEM_TYPE_MUD_DEFAULT_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/238/",
                "game_id": 238,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10779/",
                "game_id": 10779,
                "string_id": "ITEM_TYPE_PLANT_ALOE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/235/",
                "game_id": 235,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10778/",
                "game_id": 10778,
                "string_id": "ITEM_TYPE_PLANT_CACTUS",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/56/",
                "game_id": 56,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10781/",
                "game_id": 10781,
                "string_id": "ITEM_TYPE_PLANT_FIDDLEHEAD",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/67/",
                "game_id": 67,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10776/",
                "game_id": 10776,
                "string_id": "ITEM_TYPE_PLANT_LOTUS",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/66/",
                "game_id": 66,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10780/",
                "game_id": 10780,
                "string_id": "ITEM_TYPE_PLANT_SNOWDROP",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/206/",
                "game_id": 206,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10777/",
                "game_id": 10777,
                "string_id": "ITEM_TYPE_PLANT_YUCCA",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/58/",
                "game_id": 58,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10798/",
                "game_id": 10798,
                "string_id": "ITEM_TYPE_ROCK_IGNEOUS_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/33/",
                "game_id": 33,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10794/",
                "game_id": 10794,
                "string_id": "ITEM_TYPE_ROCK_METAMORPHIC_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/52/",
                "game_id": 52,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10802/",
                "game_id": 10802,
                "string_id": "ITEM_TYPE_ROCK_SEDIMENTARY_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/85/",
                "game_id": 85,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10810/",
                "game_id": 10810,
                "string_id": "ITEM_TYPE_SAND_DEFAULT_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/105/",
                "game_id": 105,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/11588/",
                "game_id": 11588,
                "string_id": "ITEM_TYPE_SOIL_CLAY_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/249/",
                "game_id": 249,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/11592/",
                "game_id": 11592,
                "string_id": "ITEM_TYPE_SOIL_PEATY_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/8/",
                "game_id": 8,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/11584/",
                "game_id": 11584,
                "string_id": "ITEM_TYPE_SOIL_SILTY_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/59/",
                "game_id": 59,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10854/",
                "game_id": 10854,
                "string_id": "ITEM_TYPE_SPONGE_DEFAULT_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/131/",
                "game_id": 131,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10858/",
                "game_id": 10858,
                "string_id": "ITEM_TYPE_TANGLE_DEFAULT_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/68/",
                "game_id": 68,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10862/",
                "game_id": 10862,
                "string_id": "ITEM_TYPE_THORNS_DEFAULT_BASE",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/240/",
                "game_id": 240,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10830/",
                "game_id": 10830,
                "string_id": "ITEM_TYPE_WOOD_ANCIENT_TRUNK",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/64/",
                "game_id": 64,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10822/",
                "game_id": 10822,
                "string_id": "ITEM_TYPE_WOOD_EXOTIC_LEAVES",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/123/",
                "game_id": 123,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10818/",
                "game_id": 10818,
                "string_id": "ITEM_TYPE_WOOD_LUSH_LEAVES",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/125/",
                "game_id": 125,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10838/",
                "game_id": 10838,
                "string_id": "ITEM_TYPE_WOOD_LUSTROUS_TRUNK",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/7/",
                "game_id": 7,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10834/",
                "game_id": 10834,
                "string_id": "ITEM_TYPE_WOOD_TWISTED_TRUNK",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/129/",
                "game_id": 129,
            },
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10826/",
                "game_id": 10826,
                "string_id": "ITEM_TYPE_WOOD_WAXY_LEAVES",
            },
            "color": {
                "url": f"{get_base_url()}/api/v1/colors/210/",
                "game_id": 210,
            },
        },
    ],
}

WORLD_POLL_EXAMPLE = {
    "url": f"{get_base_url()}/api/v1/worlds/10/polls/3/",
    "id": 3,
    "leaderboard_url": f"{get_base_url()}/api/v1/worlds/10/polls/3/leaderboard/",  # noqa E501
    "resources_url": f"{get_base_url()}/api/v1/worlds/10/polls/3/resources/",
    "time": "2020-07-28T13:25:50.688813-04:00",
    "world": {
        "url": f"{get_base_url()}/api/v1/worlds/10/",
        "id": 10,
        "display_name": "Serpensarindi",
    },
    "player_count": 1,
    "beacon_count": 787,
    "plot_count": 44478,
    "total_prestige": 66227813,
}

WORLD_POLL_LEADERBOARD_EXAMPLE = {
    "world_poll_id": 3,
    "world_poll_url": f"{get_base_url()}/api/v1/worlds/10/polls/3/",
    "leaderboard": [
        {
            "world_rank": 1,
            "guild_tag": "Lynx",
            "mayor_name": "Comet Squadron",
            "name": ":#bright yellow: Sardonyx",
            "prestige": 12876131,
        },
        {
            "world_rank": 2,
            "guild_tag": "Shinra ",
            "mayor_name": "Shinra Corp.",
            "name": ":#black:New :#2AE9E6:Midgar",
            "prestige": 11668659,
        },
        {
            "world_rank": 3,
            "guild_tag": "Lynx",
            "mayor_name": "Comet Squadron",
            "name": ":#bright yellow:Sardonyx",
            "prestige": 11273078,
        },
        {
            "world_rank": 4,
            "guild_tag": "Shinra ",
            "mayor_name": "Shinra Corp.",
            "name": ":#black:New :#2ea9e6:Midgar",
            "prestige": 4829815,
        },
        {
            "world_rank": 5,
            "guild_tag": "Hell",
            "mayor_name": "Hellsing",
            "name": "Gleamdustry",
            "prestige": 4324847,
        },
    ],
}

WORLD_POLL_RESOURCES_EXAMPLE = {
    "world_poll_id": 3,
    "world_poll_url": f"{get_base_url()}/api/v1/worlds/10/polls/3/",
    "resources": [
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/32803/",
                "game_id": 32803,
                "string_id": "ITEM_TYPE_ITEM_ROUGH_DIAMOND",
            },
            "count": 404887,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/32807/",
                "game_id": 32807,
                "string_id": "ITEM_TYPE_ITEM_ROUGH_RUBY",
            },
            "count": 37081,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/32785/",
                "game_id": 32785,
                "string_id": "ITEM_TYPE_ITEM_ORE_COPPER",
            },
            "count": 5109321,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/32787/",
                "game_id": 32787,
                "string_id": "ITEM_TYPE_ITEM_ORE_IRON",
            },
            "count": 15844635,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/32788/",
                "game_id": 32788,
                "string_id": "ITEM_TYPE_ITEM_ORE_SILVER",
            },
            "count": 1744395,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/32786/",
                "game_id": 32786,
                "string_id": "ITEM_TYPE_ITEM_ORE_GOLD",
            },
            "count": 788732,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/32789/",
                "game_id": 32789,
                "string_id": "ITEM_TYPE_ITEM_ORE_TITANIUM",
            },
            "count": 826501,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/32779/",
                "game_id": 32779,
                "string_id": "ITEM_TYPE_ITEM_COAL_SOFT",
            },
            "count": 6351450,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/32777/",
                "game_id": 32777,
                "string_id": "ITEM_TYPE_ITEM_COAL_BASE",
            },
            "count": 10427628,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/32778/",
                "game_id": 32778,
                "string_id": "ITEM_TYPE_ITEM_COAL_HARD",
            },
            "count": 2091034,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/33081/",
                "game_id": 33081,
                "string_id": "ITEM_TYPE_ITEM_FOSSIL_SMALL",
            },
            "count": 812497,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/33082/",
                "game_id": 33082,
                "string_id": "ITEM_TYPE_ITEM_FOSSIL_MEDIUM",
            },
            "count": 2542078,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/33083/",
                "game_id": 33083,
                "string_id": "ITEM_TYPE_ITEM_FOSSIL_LARGE",
            },
            "count": 1300306,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/33080/",
                "game_id": 33080,
                "string_id": "ITEM_TYPE_ITEM_ANCIENTTECHNOLOGY_FRAGMENT",
            },
            "count": 2598451,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/33078/",
                "game_id": 33078,
                "string_id": "ITEM_TYPE_ITEM_ANCIENTTECHNOLOGY_COMPONENT",
            },
            "count": 3420117,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/33079/",
                "game_id": 33079,
                "string_id": "ITEM_TYPE_ITEM_ANCIENTTECHNOLOGY_DEVICE",
            },
            "count": 219288,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10775/",
                "game_id": 10775,
                "string_id": "ITEM_TYPE_FLORA_PLANT_FIBROUS",
            },
            "count": 512,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10777/",
                "game_id": 10777,
                "string_id": "ITEM_TYPE_PLANT_YUCCA",
            },
            "count": 8247,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10778/",
                "game_id": 10778,
                "string_id": "ITEM_TYPE_PLANT_CACTUS",
            },
            "count": 5878,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10781/",
                "game_id": 10781,
                "string_id": "ITEM_TYPE_PLANT_FIDDLEHEAD",
            },
            "count": 2639,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10782/",
                "game_id": 10782,
                "string_id": "ITEM_TYPE_ROCK_BOULDER",
            },
            "count": 107001,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10783/",
                "game_id": 10783,
                "string_id": "ITEM_TYPE_ROCK_TALL",
            },
            "count": 22044,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10784/",
                "game_id": 10784,
                "string_id": "ITEM_TYPE_ROCK_STACK",
            },
            "count": 31523,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10786/",
                "game_id": 10786,
                "string_id": "ITEM_TYPE_ROCK_SHARD",
            },
            "count": 8088,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10787/",
                "game_id": 10787,
                "string_id": "ITEM_TYPE_ROCK_STALAGMITE",
            },
            "count": 7093,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10788/",
                "game_id": 10788,
                "string_id": "ITEM_TYPE_FUNGUS_AMANITA",
            },
            "count": 2326,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10789/",
                "game_id": 10789,
                "string_id": "ITEM_TYPE_FUNGUS_BRACKET",
            },
            "count": 1968,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10791/",
                "game_id": 10791,
                "string_id": "ITEM_TYPE_FUNGUS_SCATTER",
            },
            "count": 4527,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/10793/",
                "game_id": 10793,
                "string_id": "ITEM_TYPE_FUNGUS_GLOWING",
            },
            "count": 661,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/11642/",
                "game_id": 11642,
                "string_id": "ITEM_TYPE_CROP_BERRY",
            },
            "count": 4575,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/11641/",
                "game_id": 11641,
                "string_id": "ITEM_TYPE_CROP_NUTS",
            },
            "count": 647,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/11635/",
                "game_id": 11635,
                "string_id": "ITEM_TYPE_CROP_TUBER",
            },
            "count": 20814,
        },
        {
            "item": {
                "url": f"{get_base_url()}/api/v1/items/11645/",
                "game_id": 11645,
                "string_id": "ITEM_TYPE_CROP_FUEL",
            },
            "count": 4419,
        },
    ],
}
