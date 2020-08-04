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
    "surface_liquid": "Water",
    "core_liquid": "Lava",
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
            "is_new_color": True,
            "exist_on_perm": True,
            "exist_via_transform": None,
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
