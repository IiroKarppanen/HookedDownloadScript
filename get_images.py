def get_images(id_list):

    import concurrent.futures
    import requests
    from bs4 import BeautifulSoup
    import json
    from tqdm import tqdm
    import os
    from PIL import Image
    import sys

    Image.MAX_IMAGE_PIXELS = None

    HEADERS ={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

    image_list = []
    poster_list = []
    title_list = []

    print("Downloading image urls (3/3)")
    pbar = tqdm(total=len(id_list)) # Init pbar
    

    def download_image(id):
        
        try:

            # Download posters and images

            url = 'https://www.imdb.com/title/' + str(id) + "/"

            resp = requests.get(url, headers=HEADERS)
            page = BeautifulSoup(resp.text, 'lxml')

            try:
                original_title = page.select('div.sc-dae4a1bc-0.gwBsXc')[0].text
                original_title = original_title.replace("Original title: ", "").strip()
            except:
                original_title = str(page.title.string[:-7])

            original_title = original_title.split("(", 1)[0]
            
            poster_url = page.select('img.ipc-image')[0]['src']

            url2 = f'https://www.imdb.com/title/{id}/mediaviewer'
            resp = requests.get(url2, headers=HEADERS)
            page2 = BeautifulSoup(resp.text, 'lxml')
            image_url = str(page2.find_all('img')[1]['src'])

            image_list.append(image_url)
            poster_list.append(poster_url)
            title_list.append(original_title)


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            global path_to_json
            # If image download fails remove movie entry from json file
            with open(path_to_json, encoding="utf8") as f:
                data = json.load(f)

            for item in data:
                if(item['movie_id'] == id):
                    data.pop(item)
                    break

        pbar.update(n=1) 

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(download_image, id_list)


    # Add titles and image_urls to json file

    with open('movies.json', encoding="utf8") as f:
        data = json.load(f)

    for (item, title, image, poster) in zip(data, title_list, image_list, poster_list):
        item['title'] = title
        item['image_url'] = image
        item['poster_url'] = poster

    with open('movies.json', 'w', encoding='utf-8') as file:
                    file.write(
                        '[' +
                        ',\n'.join(json.dumps(i, ensure_ascii=False) for i in data) +
                        ']\n')


    pbar.close()