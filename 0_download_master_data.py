# -*- coding:utf-8 -*-
# Python script to download only the assets necessary to extract unit data
# (Stats caps, skills, etc).
#
# Takes the paths.json file as an argument.
# Saves the downloaded assets into ./cache/
from potk_unit_extractor.site import download_to_cache

if __name__ == "__main__":
    import sys

    try:
        download_to_cache(sys.argv[1])
    except ValueError as ex:
        print(ex, file=sys.stderr)
        exit(1)
