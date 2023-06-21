from requests_html import HTMLSession
import re
import json
import os
import requests
from urllib.parse import urlparse
import pandas as pd
from tqdm import tqdm

def download_image(url ,save_path, pid_number, image_number, chunk_size=128):
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    
    r = requests.get(url,  stream=True)
    if r.status_code == 404:
        return "no file lol"
    else:
        a = urlparse(url)
    
        # get orignal file name
        f_name = os.path.basename(a.path)
        new_name = str(pid_number) + "_" + str(image_number) + "." + f_name.split(".")[-1]
    
    with open(save_path + "/" + new_name, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)
    return save_path + "/" + new_name


# main scraper , opens page and get data from json in script tag
def scraper(sku, prod_url, df, index):
    s = HTMLSession()
    url = prod_url
    r = s.get(url)
    
    regex_pattern = r'window\.__myx\s*=\s*({.*?})</script>'
    match = re.search(regex_pattern, r.text)

    if match:
        json_string = match.group(1)
        json_object = json.loads(json_string)

        try:
            images = json_object.get("pdpData").get("media").get("albums")[0].get("images")
            for i, img in enumerate(images):
                img_url = img.get("src")
                download_image(img_url,"images",sku,i+1)
                df.at[index, f'Image {i+1}'] = img_url
        except:
            pass
        return df
    

df = pd.read_excel("Myntra PID.xlsx")

for index, row in tqdm(df.iterrows(), total=df.shape[0]):
    pid = row.get("PID")
    url = row.get("Myntra Link")
    # print(url)
    scraper(str(pid), url, df, index)

df.to_csv("results.csv" , index=False)