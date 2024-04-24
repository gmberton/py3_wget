
import os
import time
import shutil
import requests
from tqdm import tqdm

RETRY_SECONDS = 2


def download_file(url, output_path, max_tries=10):
    tmp_filename = os.path.join(f".tmp_{int(time.time()*1000)}")
    if os.path.exists(output_path):
        print(f"File {output_path} already exists, I won't download it again")
        return
    
    for attempt_num in range(max_tries):  # In case of errors, try 'max_tries' times
        try:
            req = requests.get(url, stream=True)
            total_size = int(req.headers.get('content-length', 0))  # Total size in bytes
            block_size = 1024  # 1 KB
            tqdm_bar = tqdm(total=total_size, desc=os.path.basename(output_path),
                            unit='iB', unit_scale=True)
            with open(tmp_filename, 'wb') as f:
                for data in req.iter_content(block_size):
                    tqdm_bar.update(len(data))
                    f.write(data)
            tqdm_bar.close()
            if total_size != 0 and tqdm_bar.n != total_size:
                print(tqdm_bar.n)
                print(total_size)
                raise RuntimeError("ERROR, something went wrong during download")
            break
        except (Exception, RuntimeError) as e:
            if os.path.exists(tmp_filename): os.remove(tmp_filename)
            print(e)
            print(f"I'll try again to download {output_path} in {RETRY_SECONDS**attempt_num} seconds")
            time.sleep(RETRY_SECONDS**attempt_num)
    else:
        raise RuntimeError(f"I tried {max_tries} times and I couldn't download {output_path} from {url}")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    shutil.move(tmp_filename, output_path)
