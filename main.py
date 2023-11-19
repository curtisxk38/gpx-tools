import argparse
import gpxpy.gpx as gpxpy
import gpxpy as gpx_parser
import datetime
import sys
import math
from pathlib import Path

METERS_IN_MILE = 1609.34

from typing import *


def split(points, chunk_size):
    for i in range(0, len(points), chunk_size):
        yield points[i:i + chunk_size]

def process(gpx_file: str, distance: int, files: int) -> None:
    gpx_path = Path(gpx_file)
    print(f"Opening {gpx_file}")
    with open(gpx_path) as f:
        gpx = gpx_parser.parse(f)

    # we assume there is only 1 track
    track = gpx.tracks[0]
    segment = track.segments[0]

    if files is not None:
        segments = []
        num_points = len(segment.points)
        for chunk in split(segment.points, math.ceil(num_points / files)):
            segments.append(gpxpy.GPXTrackSegment(chunk))

    elif distance is not None:
        segments = []
        # extremely naive implementation
        # assumes points are evenly distributed along length of segment
        length = segment.length_2d() # length in meters
        length = length / METERS_IN_MILE
        points_per_mile = len(segment.points) / length
        chunk_size = math.ceil(points_per_mile * distance)
        for chunk in split(segment.points, chunk_size):
            segments.append(gpxpy.GPXTrackSegment(chunk))

    for index, segment in enumerate(segments):
        clone = gpx.clone()
        clone.tracks[0].segments = [segment]
        new_path = gpx_path.parent.joinpath(f"split-{index+1}-{gpx_path.name}")
        with open(new_path, "w") as f:
            f.write(clone.to_xml())
            print(f"Saved {new_path}")

    

def main() -> None:
    parser = argparse.ArgumentParser(description='Split GPX file')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--files', type=int,  help='Split split track into multiple files')
    group.add_argument('-d', '--distance', type=int, help='Split track into tracks of this distance (miles) each')
    parser.add_argument('gpx_files', metavar='gpx', type=str, default='', nargs='*', help='GPX file')
    args = parser.parse_args()

    gpx_files = args.gpx_files
    distance = args.distance
    files = args.files

    for gpx_file in gpx_files:
        process(gpx_file, distance, files)

if __name__ == "__main__":
    main()