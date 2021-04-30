import djclick as click

from boundlexx.boundless.models import BeaconScan, Color, Settlement, World
from boundlexx.boundless.utils import calculate_extra_names, html_name


def _beacons(force, colors):
    click.echo("Doing Beacon Scans...")
    if force:
        BeaconScan.objects.all().update(text_name=None, html_name=None)

    beacons = BeaconScan.objects.all()
    with click.progressbar(
        beacons.iterator(), length=beacons.count(), show_percent=True, show_pos=True
    ) as pbar:
        for beacon in pbar:
            if beacon.name is not None and beacon.text_name is None:
                beacon.text_name = html_name(beacon.name, strip=True, colors=colors)
                beacon.html_name = html_name(beacon.name, colors=colors)
                beacon.save()


def _worlds(force, colors):
    click.echo("Doing Worlds...")
    if force:
        World.objects.all().update(text_name=None, html_name=None, sort_name=None)

    worlds = World.objects.all()
    with click.progressbar(
        worlds.iterator(), length=worlds.count(), show_percent=True, show_pos=True
    ) as pbar:
        for world in pbar:
            world = calculate_extra_names(world, world.display_name, colors=colors)
            world.save()


def _settlements(force, colors):
    click.echo("Doing Settlements...")
    if force:
        Settlement.objects.all().update(text_name=None, html_name=None)

    settlements = Settlement.objects.all()
    with click.progressbar(
        settlements.iterator(),
        length=settlements.count(),
        show_percent=True,
        show_pos=True,
    ) as pbar:
        for settlement in pbar:
            if settlement.name is not None and settlement.text_name is None:
                settlement.text_name = html_name(
                    settlement.name, strip=True, colors=colors
                )
                settlement.html_name = html_name(settlement.name, colors=colors)
                settlement.save()


@click.command()
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Clear existing",
)
@click.option(
    "-b",
    "--beacons",
    "enable_beacons",
    is_flag=True,
    help="Do beacons",
)
@click.option(
    "-w",
    "--worlds",
    "enable_worlds",
    is_flag=True,
    help="Do worlds",
)
@click.option(
    "-t",
    "--settlements",
    "enable_settlements",
    is_flag=True,
    help="Do enable_settlements",
)
def command(  # pylint: disable=too-many-arguments
    force,
    enable_beacons,
    enable_worlds,
    enable_shops,
    enable_leaderboards,
    enable_settlements,
):
    if (
        not enable_beacons
        and not enable_worlds
        and not enable_shops
        and not enable_leaderboards
        and not enable_settlements
    ):
        enable_beacons = True
        enable_shops = True
        enable_worlds = True
        enable_leaderboards = True
        enable_settlements = True

    colors = Color.objects.all()

    if enable_worlds:
        _worlds(force, colors)

    if enable_settlements:
        _settlements(force, colors)

    if enable_beacons:
        _beacons(force, colors)
