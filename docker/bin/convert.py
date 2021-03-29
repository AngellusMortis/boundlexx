#!/usr/bin/env python3.7

import sys

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


def make_sphere(img, out_path, projection="ortho", lon_0=0, lat_0=0, resolution="l"):
    projection = "ortho"
    basemap = Basemap(
        projection=projection, lon_0=lon_0, lat_0=lat_0, resolution=resolution
    )
    basemap.warpimage(img)
    plt.savefig(out_path, transparent=True)


if __name__ == "__main__":
    make_sphere(sys.argv[1], sys.argv[2], lon_0=30, lat_0=-5)
