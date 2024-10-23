from glob import glob
from pathlib import Path

from custom_components.tank_level.process_image import process_image

for file in sorted(glob("/home/sheid/Nextcloud/Öltank/*.jpg")):
    print(Path(file).stem, end="\t")
    try:
        print(process_image(file))
    except ValueError as e:
        print(e)
