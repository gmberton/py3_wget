
import os

from py3_wget import download_file


url_filename_cksum = [
    ("https://universityofadelaide.app.box.com/index.php?rm=box_download_shared_file&shared_name=zkfk1akpbo5318fzqmtvlpp7030ex4up&file_id=f_1424408901067",
      "tmp/cleanImageNames.txt",
      1502666467),
    ("https://universityofadelaide.app.box.com/index.php?rm=box_download_shared_file&shared_name=zkfk1akpbo5318fzqmtvlpp7030ex4up&file_id=f_1521702837314",
      "tmp/winter.tar.gz",
      3357613045),
    ("https://surfdrive.surf.nl/files/index.php/s/sbZRXzYe3l0v67W/download?path=%2F&files=SPEDTEST.zip",
      "tmp/SPEDTEST.zip",
      3708784116),
    ("https://data.4tu.nl/ndownloader/items/d2ee2551-986a-46bc-8540-b43f5b01ec4d/versions/4",
      "tmp/AmsterTime.zip",
      4085124150),
    ("http://www.ok.sc.e.titech.ac.jp/~torii/project/vlocalization/icons/reference_poses_598.zip",
      "tmp/reference_poses_598.zip",
      263063612),
    ("https://zenodo.org/record/1243106/files/Eynsham.zip?download=1",
      "tmp/Eynsham.zip",
      1581884634),
    ("http://www.doc.ic.ac.uk/~ahanda/living_room_traj1_frei_png.tar.gz",
      "tmp/living_room_traj1_frei_png.tar.gz",
      3041840781),
]

for url, filename, cksum in url_filename_cksum:
    download_file(url, filename, overwrite=True, cksum=cksum)
    assert os.path.exists(filename), f"{filename} does not exist"
