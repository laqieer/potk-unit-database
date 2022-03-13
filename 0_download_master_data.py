# -*- coding:utf-8 -*-
# Python script to download only the assets necessary to extract unit data
# (Stats caps, skills, etc).
#
# Takes the paths.json file as an argument.
# Saves the downloaded assets into ./cache/
import os.path

from potk_unit_extractor.site import SiteManager

if __name__ == "__main__":
    import sys

    try:
        mgr = SiteManager(work='.', sources=os.path.dirname(__file__))
        mgr.download_to_cache(sys.argv[1])
    except ValueError as ex:
        print(ex, file=sys.stderr)
        exit(1)
