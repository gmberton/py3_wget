import os
import re
import time
import shutil
import hashlib
from tqdm import tqdm
from urllib.request import urlopen

from .cksum import compute_cksum


def download_file(
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
    timeout=60,
):
    """Download a file given its URL. If the download doesn't end well, it will be re-tried.

    Parameters
    ----------
    url : str
    output_path : str, if the path contains inexistent dirs (e.g. dir/to/file) they will be created.
        If None it will be derived from URL.
    overwrite : bool, if to overwrite the file in case it already exists. Default: False.
    verbose : bool, if True prints statements and show tqdm loop. Default: True.
    cksum : int, if not None then check that the file cksum corresponds. Raise RuntimeError if it doesn't.
    md5 : str, if not None then check that the file md5 corresponds. Raise RuntimeError if it doesn't.
    sha256 : str, if not None then check that the file sha256 corresponds. Raise RuntimeError if it doesn't.
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
    
    validate_download_params(
        url, output_path, overwrite, verbose, cksum, md5, sha256, max_tries, block_size_bytes, retry_seconds, timeout
    )
    
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

                total_size = int(headers.get("content-length", 0))  # Total size in bytes
                _download(response, output_path, total_size, partial_filename, verbose, block_size_bytes)
            break

        except (Exception, RuntimeError, OSError) as e:
            # Timeout error is raised as OSError
            if "partial_filename" in locals() and os.path.exists(partial_filename):
                os.remove(partial_filename)
            printf(e)
            printf(
                f"{num_attempt} / {max_tries}) I'll try again to download {output_path} in {retry_seconds**num_attempt} seconds"
            )
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

    if md5 is not None:
        with open(output_path, "rb") as file:
            computed_md5 = hashlib.md5(file.read()).hexdigest()
        if computed_md5 != md5:
            raise RuntimeError(f"The MD5 cksum for file {output_path} should be {md5} but it is {computed_md5}")

    if sha256 is not None:
        with open(output_path, "rb") as file:
            computed_sha256 = hashlib.sha256(file.read()).hexdigest()
        if computed_sha256 != sha256:
            raise RuntimeError(
                f"The SHA256 cksum for file {output_path} should be {sha256} but it is {computed_sha256}"
            )


def _get_output_path(headers, url, output_path):
    if output_path is None:
        if "content-disposition" not in headers:
            output_path = os.path.basename(url)
        elif len(re.findall('filename="(.+)"', headers["content-disposition"])) != 0:
            output_path = re.findall('filename="(.+)"', headers["content-disposition"])[0]
        elif len(headers["content-disposition"].split("filename=")) != 0:
            output_path = headers["content-disposition"].split("filename=")[1]
        else:
            output_path = "unknown_filename"
    output_filename = os.path.basename(output_path)
    partial_filename = f"{output_filename}.part"
    return output_path, partial_filename


def _download(response, output_path, total_size, partial_filename, verbose, block_size_bytes):
    tqdm_bar = tqdm(
        total=total_size, desc=os.path.basename(output_path), unit="iB", unit_scale=True, disable=not verbose
    )
    with open(partial_filename, "wb") as file:
        while True:
            block = response.read(block_size_bytes)
            if not block:
                break
            file.write(block)
            tqdm_bar.update(len(block))
        tqdm_bar.close()


def validate_download_params(url, output_path, overwrite, verbose, cksum, md5, sha256, max_tries, block_size_bytes, retry_seconds, timeout):
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        raise ValueError("The URL must be a string starting with 'http://' or 'https://'.")
    
    if output_path is not None and not isinstance(output_path, str):
        raise ValueError("The output_path must be a string or None.")
    
    if not isinstance(overwrite, bool):
        raise ValueError("The overwrite parameter must be a boolean.")
    
    if not isinstance(verbose, bool):
        raise ValueError("The verbose parameter must be a boolean.")
    
    if cksum is not None and not isinstance(cksum, int):
        raise ValueError("The cksum parameter must be an integer or None.")
    
    if md5 is not None and not re.fullmatch(r"[a-fA-F0-9]{32}", md5):
        raise ValueError("The md5 parameter must be a 32-character hexadecimal string or None.")
    
    if sha256 is not None and not re.fullmatch(r"[a-fA-F0-9]{64}", sha256):
        raise ValueError("The sha256 parameter must be a 64-character hexadecimal string or None.")
    
    if not isinstance(max_tries, int) or max_tries <= 0:
        raise ValueError("The max_tries parameter must be a positive integer.")
    
    if not isinstance(block_size_bytes, int) or block_size_bytes <= 0:
        raise ValueError("The block_size_bytes parameter must be a positive integer.")
    
    if not isinstance(retry_seconds, int) or retry_seconds <= 0:
        raise ValueError("The retry_seconds parameter must be a positive integer.")
    
    if not isinstance(timeout, int) or timeout <= 0:
        raise ValueError("The timeout parameter must be a positive integer.")


