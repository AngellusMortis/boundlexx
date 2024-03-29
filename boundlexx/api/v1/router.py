from boundlexx.api.common.views import ExportedFileViewSet, GameFileViewSet
from boundlexx.api.routers import APIDocsRouter
from boundlexx.api.v1 import views

API_DESCRIPTION = """
Boundless Lexicon API. Everything about the game Boundless.

Disclaimer: Boundlexx is an unoffical API for the game Boundless. There is no
affiliation with Wonderstruck Games.

This API is designed to be _relatively_ user friendly so you can always go to
any API URL and you should get a nice browsable API view for the endpoint. It
is also designed to give as much information as possible upfront and force you
to filter it down to just the information you need/want. As such every endpoint
has various filters avaiable to make use of if too much data is coming back for
you.

The API provides a nice "browsable API" view for each endpoint that allows you
to interact with the endpoint. It will show you all of the avaiable filters,
formats, etc. Because the API is kind of heavily cached by a CDN, this **format
is _not_ the default**. If you would like to use it, simply add `?format=api`
to the end of any endpoint to get it.

The API is also designed to give you as much data as avaiable, so you might
be getting more then you need. It is expected you use filters to trim down the
response content to only what you want back. The browsable API has all the
possible filters for each endpoint as does this OpenAPI spec. The OpenAPI spec
may extra filters that do not work on specific endpoints as there is a bit of
drift between the generation of the API vs. the generation of the docs that
have not been resolved yet (Sorry!).

**NOTE ABOUT WEB APPLICATIONS**: v1 is not optimized for Web apps. It does not
have the nessarcary CORS headers so it cannot be used inside of XHR requests in
a Javascript application. It can still be used for non Web applications as the
usuability and discoverbility is very useful. For Web apps, please see [v2](/api/v2/).
"""

router = APIDocsRouter(API_DESCRIPTION, "v1")

router.register("blocks", views.BlockViewSet, basename="block")

router.register("colors", views.ColorViewSet, basename="color").register(
    "blocks",
    views.BlockColorViewSet,
    basename="color-blocks",
    parents_query_lookups=["color__game_id"],
)

router.register("emojis", views.EmojiViewSet, basename="emoji")
router.register("exports", ExportedFileViewSet, basename="export")
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

router.register("metals", views.MetalViewSet, basename="metal")

router.register("recipe-groups", views.RecipeGroupViewSet, basename="recipe-group")
router.register("recipes", views.RecipeViewSet, basename="recipe")

router.register("skill-groups", views.SkillGroupViewSet, basename="skill-group")
router.register("skills", views.SkillViewSet, basename="skill")

world_viewset = router.register("worlds", views.WorldViewSet, basename="world")
world_viewset.register(
    "polls",
    views.WorldPollViewSet,
    basename="world-poll",
    parents_query_lookups=["world_id"],
)
world_viewset.register(
    "distances",
    views.WorldDistanceViewSet,
    basename="world-distance",
    parents_query_lookups=["world_source__id"],
)
