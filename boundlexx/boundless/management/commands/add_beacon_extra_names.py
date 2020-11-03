import djclick as click

from boundlexx.boundless.models import BeaconScan, Color
from boundlexx.boundless.utils import html_name


@click.command()
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Clear existing",
)
def command(force):
    if force:
        BeaconScan.objects.all().update(text_name=None, html_name=None)

    colors = Color.objects.all()

    beacons = BeaconScan.objects.all()
    with click.progressbar(
        beacons.iterator(), length=beacons.count(), show_percent=True, show_pos=True
    ) as pbar:
        for beacon in pbar:
            if beacon.text_name is None:
                beacon.text_name = html_name(beacon.name, strip=True, colors=colors)
                beacon.html_name = html_name(beacon.name, colors=colors)
                beacon.save()
