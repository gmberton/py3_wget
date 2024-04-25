
import re
import os
import time
import shutil
import requests
from tqdm import tqdm


def download_file(url, output_path=None, max_tries=5, block_size_bytes=1024, retry_seconds=2):
    
    for attempt_num in range(max_tries):  # In case of errors, try 'max_tries' times
        try:
            req = requests.get(url, stream=True)
            if output_path is None:
                if 'content-disposition' not in req.headers:
                    output_path = os.path.basename(url)
                elif len(re.findall("filename=\"(.+)\"", req.headers['content-disposition'])) != 0:
                    output_path = re.findall("filename=\"(.+)\"", req.headers['content-disposition'])[0]
                elif len(req.headers['content-disposition'].split("filename=")) != 0:
                    output_path = req.headers['content-disposition'].split("filename=")[1]
                else:
                    output_path = "unknown_filename"
            
            output_filename = os.path.basename(output_path)
            partial_filename = f"{output_filename}.part"
            if os.path.exists(output_path):
                print(f"File {output_path} already exists, I won't download it again")
                return
            
            total_size = int(req.headers.get('content-length', 0))  # Total size in bytes
            
            tqdm_bar = tqdm(total=total_size, desc=os.path.basename(output_path), unit='iB', unit_scale=True)
            with open(partial_filename, 'wb') as file:
                for data in req.iter_content(block_size_bytes):
                    tqdm_bar.update(len(data))
                    file.write(data)
            tqdm_bar.close()
            if total_size != 0 and tqdm_bar.n != total_size:
                print(tqdm_bar.n)
                print(total_size)
                raise RuntimeError("ERROR, something went wrong during download")
            break
        except (Exception, RuntimeError) as e:
            if os.path.exists(partial_filename):
                os.remove(partial_filename)
            print(e)
            print(f"I'll try again to download {output_path} in {retry_seconds**attempt_num} seconds")
            time.sleep(retry_seconds**attempt_num)
    else:
        raise RuntimeError(f"I tried {max_tries} times and I couldn't download {output_path} from {url}")
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    shutil.move(partial_filename, output_path)
