from boundlexx.api.routers import APIDocsRouter
from boundlexx.api.v1 import views

router = APIDocsRouter()
router.register("colors", views.ColorViewSet, basename="color").register(
    "blocks",
    views.BlockColorViewSet,
    basename="color-blocks",
    parents_query_lookups=["color__game_id"],
)

router.register("emojis", views.EmojiViewSet, basename="emoji")
router.register("game-files", views.GameFileViewSet, basename="game-file")
router.register("blocks", views.BlockViewSet, basename="block")

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
