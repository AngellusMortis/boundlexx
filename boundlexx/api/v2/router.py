from boundlexx.api.common.views import GameFileViewSet
from boundlexx.api.routers import APIDocsRouter
from boundlexx.api.v2 import views

API_DESCRIPTION = """
Boundless Lexicon API v2. Everything about the game Boundless.

Disclaimer: Boundlexx is an unoffical API for the game Boundless. There is no
affiliation with Wonderstruck Games.

The v2 API is designed for speed and efficently compared to
[v1](/api/v1/) which is designed for discoverability.
What this means is the `list` views for a lot of resources will return a
lot less data then their detail view. Generally `list` views only
return non-relational "essential" data. `retrieve` views will return all
of the data about that specific object.

Also, in many cases relational data has been stripped out. Now you only a
get a lookup key to that object and you need to call the other resource
endpoint for more data. The "general" idea is that the `list` of any of the
essential top level resources will be cached by the client to allow for rapid
look up.
"""

router = APIDocsRouter(API_DESCRIPTION, "v2")

router.register("blocks", views.BlockViewSet, basename="block")

router.register("colors", views.ColorViewSet, basename="color").register(
    "blocks",
    views.BlockColorViewSet,
    basename="color-blocks",
    parents_query_lookups=["color__game_id"],
)

router.register("emojis", views.EmojiViewSet, basename="emoji")
router.register("game-files", GameFileViewSet, basename="game-file")

item_viewset = router.register("items", views.ItemViewSet, basename="item")
item_viewset.register(
    "resource-counts",
    views.ItemResourceCountViewSet,
    basename="item-resource-count",
    parents_query_lookups=["item__game_id"],
)
item_viewset.register(
    "colors",
    views.ItemColorsViewSet,
    basename="item-colors",
    parents_query_lookups=["item__game_id"],
)
item_viewset.register(
    "resource-timeseries",
    views.ItemResourceWorldListViewSet,
    basename="item-resource-world",
    parents_query_lookups=["item__game_id"],
)
item_viewset.register(
    r"resource-timeseries/(?P<world_poll__world_id>\d+)",
    views.ItemResourceTimeseriesViewSet,
    basename="item-resource-timeseries",
    parents_query_lookups=["item__game_id"],
)

router.register("recipe-groups", views.RecipeGroupViewSet, basename="recipe-group")
router.register("recipes", views.RecipeViewSet, basename="recipe")

router.register("skill-groups", views.SkillGroupViewSet, basename="skill-group")
router.register("skills", views.SkillViewSet, basename="skill")

world_viewset = router.register("worlds", views.WorldViewSet, basename="world")
world_viewset.register(
    "distances",
    views.WorldDistanceViewSet,
    basename="world-distance",
    parents_query_lookups=["world_source__id"],
)
world_viewset.register(
    "polls",
    views.WorldPollViewSet,
    basename="world-poll",
    parents_query_lookups=["world_id"],
)
