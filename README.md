# py3_wget

A tool like wget for python, supporting a (optional) progress bar, cksum, timeout, retry failed download.

### Basic example
![Demo](assets/e1.gif)

### Recovering from download errors
If errors occur, py3_wget re-runs the download

### Overwrite
Already existing files won't be downloaded by default
![Demo](assets/e3.gif)

### Cksum, MD5, SHA256
py3_wget can automatically check the correctness of the download through cksum, MD5 or SHA256
![Demo](assets/e4.gif)

## Install
Install with
```
pip install py3_wget
```

## Parameters
```
py3_wget.download_file(
    url,
    output_path=None,
    overwrite=False,
    verbose=True,
    cksum=None,
    md5=None,
    sha256=None,
    max_tries=5,
    block_size_bytes=8192,
    retry_seconds=2,
    timeout_seconds=60,
)
```

### TODO list
- [ ] Optionally resume from partial download
- [x] Optionally pass cksum to downloader to ensure file is correctly downloaded
- [x] Optionally turn off tqdm (silent download)
- [x] Optionally set timeout for download request
