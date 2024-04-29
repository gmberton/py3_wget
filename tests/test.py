
import os

import pycksum
from py3_wget import download_file


tests_url_filename_cksum = [
    ("https://universityofadelaide.app.box.com/index.php?rm=box_download_shared_file&shared_name=zkfk1akpbo5318fzqmtvlpp7030ex4up&file_id=f_1424421870101",
      "summer.tar.gz", 0),
    ("https://universityofadelaide.app.box.com/index.php?rm=box_download_shared_file&shared_name=zkfk1akpbo5318fzqmtvlpp7030ex4up&file_id=f_1424424688104",
      "winter.tar.gz", 0),
    ("https://universityofadelaide.app.box.com/index.php?rm=box_download_shared_file&shared_name=zkfk1akpbo5318fzqmtvlpp7030ex4up&file_id=f_1424408901067",
      "cleanImageNames.txt", 1502666467),
    ("https://surfdrive.surf.nl/files/index.php/s/sbZRXzYe3l0v67W/download?path=%2F&files=SPEDTEST.zip",
      "SPEDTEST.zip", 0),
    ("https://data.4tu.nl/ndownloader/items/d2ee2551-986a-46bc-8540-b43f5b01ec4d/versions/4",
      "AmsterTime: A Visual Place Recognition Benchmark Dataset for Severe Domain Shift_4_all.zip", 0),
    ("http://www.ok.sc.e.titech.ac.jp/~torii/project/vlocalization/icons/reference_poses_598.zip",
      "reference_poses_598.zip", 0),
    ("https://zenodo.org/record/1243106/files/Eynsham.zip?download=1",
      "Eynsham.zip?download=1", 0),
    ("http://www.doc.ic.ac.uk/~ahanda/living_room_traj1_frei_png.tar.gz",
     "living_room_traj1_frei_png.tar.gz", 0),
    # ("https://www.cs.cornell.edu/projects/megadepth/dataset/MegaDepth_SfM/MegaDepth_SfM_v1.tar.xz",
    #   "MegaDepth_SfM_v1.tar.xz", 0)
]

for url, filename, cksum in tests_url_filename_cksum:
    download_file(url)
    assert os.path.exists(filename), f"{filename} does not exist"
    if cksum != 0:
        with open(filename) as file:
            assert pycksum.cksum(file) == cksum
