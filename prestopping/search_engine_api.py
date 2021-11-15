import requests
import os, sys
from PIL import Image
from io import BytesIO
from IPython.display import clear_output
import shutil
import time
import math

def main():
    subscription_key = "3691f68199d14ba99baf4c7f06d0c8a4"
    assert subscription_key

    search_url = "https://api.bing.microsoft.com/v7.0/images/search"
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}

    if len(sys.argv) != 4:
        print("Wrong input arguments")
        sys.exit()

    count = int(sys.argv[2])
    label = sys.argv[1]
    save_path = sys.argv[3]
    pages = math.ceil(count / 150)

    parent_dir = save_path
    querys = [label]

    for page in range(pages):
        for query in querys:
            path = os.path.join(parent_dir, query)
            if os.path.exists(path) == False:
                os.makedirs(path)
            
            page_count = 0
            if count > 150:
                page_count = 150
                count = count - 150
            else:
                page_count = count

            params  = {"q": query + " closeup", "license": "public", "imageType": "photo", "count": str(page_count) , "offset" : str(page*150)}
            response = requests.get(search_url, headers=headers, params=params)
            response.raise_for_status()
            search_results = response.json()

            thumbnail_urls = [img["thumbnailUrl"] for img in search_results["value"][:page_count]]
            for i in range(page_count):
                image_data = requests.get(thumbnail_urls[i])
                image_data.raise_for_status()
                image = Image.open(BytesIO(image_data.content))
                image.save(path + "\\" + query + str(i + (page*150)) + ".jpg")

if __name__ == '__main__':
    print(sys.argv)
    main()