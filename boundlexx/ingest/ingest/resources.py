import djclick as click

from boundlexx.boundless.models import (
    Block,
    Liquid,
    ResourceData,
    ResourceDataBestWorld,
)
from boundlexx.ingest.models import GameFile

RESOURCE_LIQUIDS = [
    48,  # Petrolim
    64,  # Resin
]


def _get_block_item(game_id, model):
    item = None

    if not game_id == 0:
        favorite = (
            model.objects.select_related("block_item").filter(game_id=game_id).first()
        )

        if favorite is not None:
            item = favorite.block_item

    return item


def _get_block(game_id):
    return _get_block_item(game_id, Block)


def _get_liquid(game_id):
    return _get_block_item(game_id, Liquid)


def _create_world_types(resource_data, created, data):
    world_types = []

    for world_type in resource_data["bestWorld"]["types"]:
        world_types.append(world_type.replace("_EXO", ""))

    if not created:
        new_world_types = set(world_types)
        actual_world_types = {
            r.world_type for r in ResourceDataBestWorld.objects.filter(data=data)
        }

        # delete existing
        ResourceDataBestWorld.objects.filter(
            data=data, world_type__in=list(actual_world_types - new_world_types)
        ).delete()

        world_types = list(new_world_types - actual_world_types)

    # create new:
    for world_type in world_types:
        ResourceDataBestWorld.objects.create(data=data, world_type=world_type)


def _create_resource_liquids():
    for game_id in RESOURCE_LIQUIDS:
        liquid = Liquid.objects.get(game_id=game_id)

        if not liquid.block_item.is_resource:
            liquid.block_item.is_resource = True
            liquid.block_item.save()


def run():
    resourcetiers = GameFile.objects.get(
        folder="assets/archetypes", filename="resourcetiers.json"
    ).content

    compiled_resource_profiles = GameFile.objects.get(
        folder="server/assets/archetypes", filename="compiledresourceprofiles.msgpack"
    ).content["resourceData"]

    _create_resource_liquids()

    data_created = 0
    click.echo("Creating Resource Data...")
    with click.progressbar(resourcetiers.items()) as pbar:
        for block_name, resource_data in pbar:
            block = Block.objects.select_related("block_item").get(name=block_name)

            resource_profile = None
            is_embedded = False
            if str(block.game_id) in compiled_resource_profiles["blockResources"]:
                is_embedded = True
                resource_profile = compiled_resource_profiles["blockResources"][
                    str(block.game_id)
                ]
            else:
                resource_profile = compiled_resource_profiles["surfaceResources"][
                    str(block.game_id)
                ]

            if not block.block_item.is_resource:
                block.block_item.is_resource = True
                block.block_item.save()

            args = {
                "is_embedded": is_embedded,
                "exo_only": resource_data.get("exoOnly", False),
                "max_tier": resource_data["maxTier"],
                "min_tier": resource_data["minTier"],
                "best_max_tier": resource_data["bestWorld"]["maxTier"],
                "best_min_tier": resource_data["bestWorld"]["minTier"],
                "shape": resource_profile["shape"],
                "size_max": resource_profile["sizeMax"],
                "size_min": resource_profile["sizeMin"],
                "altitude_max": resource_profile["altitudeMax"],
                "altitude_min": resource_profile["altitudeMin"],
                "distance_max": resource_profile.get("distanceMax"),
                "distance_min": resource_profile.get("distanceMin"),
                "cave_weighting": resource_profile["caveWeighting"],
                "size_skew_to_min": resource_profile["sizeSkewToMin"],
                "blocks_above_max": resource_profile["blocksAboveMax"],
                "blocks_above_min": resource_profile["blocksAboveMin"],
                "liquid_above_max": resource_profile["liquidAboveMax"],
                "liquid_above_min": resource_profile["liquidAboveMin"],
                "noise_frequency": resource_profile.get("noiseFrequency"),
                "noise_threshold": resource_profile.get("noiseThreshold"),
                "liquid_favorite": _get_liquid(resource_profile["liquidFavourite"]),
                "three_d_weighting": resource_profile["threeDWeighting"],
                "surface_favorite": _get_block(resource_profile["surfaceFavourite"]),
                "surface_weighting": resource_profile["surfaceWeighting"],
                "altitude_best_lower": resource_profile["altitudeBestLower"],
                "altitude_best_upper": resource_profile["altitudeBestUpper"],
                "distance_best_lower": resource_profile.get("distanceBestLower"),
                "distance_best_upper": resource_profile.get("distanceBestUpper"),
                "blocks_above_best_lower": resource_profile["blocksAboveBestLower"],
                "blocks_above_best_upper": resource_profile["blocksAboveBestUpper"],
                "liquid_above_best_upper": resource_profile["liquidAboveBestUpper"],
                "liquid_above_best_lower": resource_profile["liquidAboveBestLower"],
                "liquid_second_favorite": _get_liquid(
                    resource_profile["liquidSecondFavourite"]
                ),
                "surface_second_favorite": _get_block(
                    resource_profile["surfaceSecondFavourite"]
                ),
            }

            data, created = ResourceData.objects.get_or_create(
                item=block.block_item, defaults=args
            )
            _create_world_types(resource_data, created, data)

            for attr, value in args.items():
                setattr(data, attr, value)
            data.save()

            if created:
                data_created += 1

    click.echo(f"{data_created} Resource data created")
