# py3_wget
A tool like wget for python, supporting a progress bar

Install with
```
pip install py3_wget
```

and use simply like
```
import py3_wget
py3_wget.download_file(
    url="https://universityofadelaide.app.box.com/index.php?rm=box_download_shared_file&shared_name=zkfk1akpbo5318fzqmtvlpp7030ex4up&file_id=f_1424424688104",
    output_path="winter.tar.gz"
)
```

### TODO list
- Improve tests
- Add possibility to resume from partial download
- Optionally pass cksum to downloader to ensure file is correctly downloaded
- Give option to turn off tqdm (silent download)
