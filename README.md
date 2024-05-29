# py3_wget
A tool like wget for python, supporting a (optional) progress bar, cksum, timeout, retry failed download.

Install with
```
pip install py3_wget
```

and use as simply as (for example)
```
import py3_wget
py3_wget.download_file(
    url="https://zenodo.org/record/1243106/files/Eynsham.zip?download=1",
    output_path="Eynsham.zip"
)
```

### TODO list
- [ ] Optionally resume from partial download
- [x] Optionally pass cksum to downloader to ensure file is correctly downloaded
- [x] Optionally turn off tqdm (silent download)
- [x] Optionally set timeout for download request
