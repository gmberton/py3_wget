
import re
import os
import time
import shutil
from tqdm import tqdm
from urllib.request import urlopen

from .cksum import compute_cksum


def download_file(url, output_path=None, overwrite=False, verbose=True, cksum=None,
                  max_tries=5, block_size_bytes=8192, retry_seconds=2, timeout=60):
    """Download a file given its URL. If the download doesn't end well, it will be re-tried.

    Parameters
    ----------
    url : str
    output_path : str, if the path contains inexistent dirs (e.g. dir/to/file) they will be created.
        If None it will be derived from URL.
    overwrite : bool, if to overwrite the file in case it already exists. Default: False.
    verbose : bool, if True prints statements and show tqdm loop. Default: True.
    cksum : int, if not None then check that the file cksum corresponds. Raise RuntimeError if it doesn't.
    max_tries : int, how many time to retry downloading file in case of errors. Default: 5.
    block_size_bytes : int, block size (in bytes) for downloadng. Default: 8192.
    retry_seconds : int, how long to wait after each failed download. Wait time is retry_seconds**num_attempt,
        so keep a small number. Default: 2.
    timeout : int, timeout for urllib request in seconds. Default: 60.

    Raises
    ------
    RuntimeError
        In case of wrong cksum or any download issues.

    Returns
    -------
    None.

    """
    # Is there a cleaner solution to turn off prints?
    if not verbose:
        printf = lambda x: x
    else:
        printf = print
    
    for num_attempt in range(max_tries):  # In case of errors, re-try up to 'max_tries' times
        try:
            with urlopen(url, timeout=timeout) as response:
                headers = response.headers
                output_path, partial_filename = _get_output_path(headers, url, output_path)
                
                if os.path.exists(output_path):
                    if overwrite:
                        os.remove(output_path)
                    else:
                        printf(f"File {output_path} already exists, I won't download it again")
                        return
                
                total_size = int(headers.get('content-length', 0))  # Total size in bytes
                _download(response, output_path, total_size, partial_filename, verbose, block_size_bytes)
            break
        
        except (Exception, RuntimeError, OSError) as e:
            # Timeout error is raised as OSError
            if "partial_filename" in locals() and os.path.exists(partial_filename):
                os.remove(partial_filename)
            printf(e)
            printf(f"{num_attempt} / {max_tries}) I'll try again to download {output_path} in {retry_seconds**num_attempt} seconds")
            time.sleep(retry_seconds**num_attempt)
    else:
        raise RuntimeError(f"I tried {max_tries} times and I couldn't download {output_path} from {url}")
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    shutil.move(partial_filename, output_path)
    
    if cksum is not None:
        with open(output_path, "rb") as file:
            computed_cksum = compute_cksum(file)
        if computed_cksum != cksum:
            raise RuntimeError(f"The cksum for file {output_path} should be {cksum} but it is {computed_cksum}")


def _get_output_path(headers, url, output_path):
    if output_path is None:
        if 'content-disposition' not in headers:
            output_path = os.path.basename(url)
        elif len(re.findall("filename=\"(.+)\"", headers['content-disposition'])) != 0:
            output_path = re.findall("filename=\"(.+)\"", headers['content-disposition'])[0]
        elif len(headers['content-disposition'].split("filename=")) != 0:
            output_path = headers['content-disposition'].split("filename=")[1]
        else:
            output_path = "unknown_filename"
    output_filename = os.path.basename(output_path)
    partial_filename = f"{output_filename}.part"
    return output_path, partial_filename


def _download(response, output_path, total_size, partial_filename, verbose, block_size_bytes):
    tqdm_bar = tqdm(total=total_size, desc=os.path.basename(output_path), unit='iB', unit_scale=True, disable=not verbose)
    with open(partial_filename, 'wb') as file:
        while True:
            block = response.read(block_size_bytes)
            if not block:
                break
            file.write(block)
            tqdm_bar.update(len(block))
        tqdm_bar.close()
