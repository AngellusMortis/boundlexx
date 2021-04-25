from datetime import timedelta

import djclick as click
from django.utils import timezone

from boundlexx.boundless.models import (
    BeaconScan,
    Color,
    ItemRequestBasketPrice,
    ItemShopStandPrice,
    LeaderboardRecord,
    Settlement,
    World,
)
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


def _shops(force, colors):
    click.echo("Clearing all shops...")
    cutoff = timezone.now() - timedelta(days=30)
    if force:
        ItemShopStandPrice.objects.filter(time__gte=cutoff).update(
            beacon_text_name=None, beacon_html_name=None
        )
        ItemRequestBasketPrice.objects.filter(time__gte=cutoff).update(
            beacon_text_name=None, beacon_html_name=None
        )

    click.echo("Doing Shop Stands...")
    stands = ItemShopStandPrice.objects.filter(time__gte=cutoff)
    with click.progressbar(
        stands.iterator(), length=stands.count(), show_percent=True, show_pos=True
    ) as pbar:
        for stand in pbar:
            stand.beacon_text_name = html_name(
                stand.beacon_name, strip=True, colors=colors
            )
            stand.beacon_html_name = html_name(stand.beacon_name, colors=colors)
            stand.save()

    click.echo("Doing Request Baskets...")
    baskets = ItemRequestBasketPrice.objects.filter(time__gte=cutoff)
    with click.progressbar(
        baskets.iterator(), length=baskets.count(), show_percent=True, show_pos=True
    ) as pbar:
        for basket in pbar:
            basket.beacon_text_name = html_name(
                basket.beacon_name, strip=True, colors=colors
            )
            basket.beacon_html_name = html_name(basket.beacon_name, colors=colors)
            basket.save()


def _leaderboards(force, colors):
    click.echo("Doing Leaderboards...")
    cutoff = timezone.now() - timedelta(days=7)
    if force:
        LeaderboardRecord.objects.filter(time__gte=cutoff).update(
            text_name=None, html_name=None
        )

    leaderboards = LeaderboardRecord.objects.filter(time__gte=cutoff)
    with click.progressbar(
        leaderboards.iterator(),
        length=leaderboards.count(),
        show_percent=True,
        show_pos=True,
    ) as pbar:
        for leaderboard in pbar:
            if leaderboard.name is not None and leaderboard.text_name is None:
                leaderboard.text_name = html_name(
                    leaderboard.name, strip=True, colors=colors
                )
                leaderboard.html_name = html_name(leaderboard.name, colors=colors)
                leaderboard.save()


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
    "-s",
    "--shops",
    "enable_shops",
    is_flag=True,
    help="Do shops",
)
@click.option(
    "-l",
    "--leaderboards",
    "enable_leaderboards",
    is_flag=True,
    help="Do leaderboards",
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

    if enable_leaderboards:
        _leaderboards(force, colors)

    if enable_shops:
        _shops(force, colors)
