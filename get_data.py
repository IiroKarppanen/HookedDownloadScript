def get_movies(url_list, movie_amount):

    import concurrent.futures
    import requests
    from bs4 import BeautifulSoup
    import json
    import re
    from tqdm import tqdm
    import os
    import sys

    HEADERS ={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":
        "gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", 
        "Upgrade-Insecure-Requests":"1"}

    json_list = []
    id_list = []

    print("Downloading Movie Data (2/2)")
    pbar = tqdm(total=movie_amount) # Init pbar

    def iterateList(url):
            
        resp = requests.get(url, headers=HEADERS)
        content = BeautifulSoup(resp.text, 'lxml')

        movie_list = content.select('.lister-item-content')

        def downloadData(movie):
            try:

                header = movie.select('.lister-item-header')[0].get_text().strip()

                # Get movie id and append it to list
                id = movie.select('.lister-item-header')[0].find('a')['href']
                id = id.replace("/", "").replace("title", "").replace("?ref_=adv_li_tt", "").strip()

                if id not in id_list:
           
                    # Get movie release year
                    try:
                        year = int(header[-6:].replace("(", "").replace(")", ""))
                        start_year = year
                        end_year = year
                    except:
                        year = re.sub("[^0-9]", "", header[1:])
                        start_year = year[:4]
                        end_year = year[-4:]
                    

                    try:
                        age = movie.select('.certificate')[0].get_text().strip()
                    except:
                        age = "undefined"

                    try:
                        runtime = movie.select('.runtime')[0].get_text().strip()
                    except:
                        runtime = "undefined"


                    genres = []
                    
                    for genre in movie.select('.genre'):
                        genres.append(genre.text.strip())

                    genres = json.dumps(genres)

                    try:
                        metascore = content.select('.ratings-metascore')[0].get_text().strip()
                        metascore = int(re.search(r'\d+', metascore).group())
                    except:
                        metascore = 'undefined'

                    try:

                        list = movie.select('.sort-num_votes-visible')[0].findChildren('span')
                        
                        votes = list[1].get_text().strip().replace(",", "")
                        votes = int(votes)

                    except:
                        votes = 'undefined'
                    
                    try:

                        revenue = list[4].get_text().strip().replace("$", "")
                        # Convert from string with M or K letter to integer
                        if("M" in revenue):
                            revenue = revenue.replace("M", "")
                            revenue2 = int(float(revenue)) * 1000000
                        if("K" in revenue):
                            revenue = revenue.replace("K", "")
                            revenue2 = int(float(revenue)) * 1000
                    
                    except:
                        revenue2 = 'undefined'

                    cast = []
                    
                    actors = movie.select('p')[-2].get_text().strip()
                    cast.append(actors.split("Stars:",1)[1].strip().replace('\n', ''))
                    cast = json.dumps(cast, ensure_ascii=False)

                    #############################################################################################################

                    url = 'https://www.imdb.com/title/' + str(id) + "/"

                    resp = requests.get(url, headers=HEADERS)
                    page = BeautifulSoup(resp.text, 'lxml')

                    try:
                        original_title = page.select('div.sc-dae4a1bc-0.gwBsXc')[0].text
                        original_title = original_title.replace("Original title: ", "").strip()
                    except:
                        try:
                            original_title = str(page.title.string[:-7])
                        except:
                            raise Exception

                    original_title = original_title.split("(", 1)[0]
                    poster_url = page.select('img.ipc-image')[0]['src']

                    url2 = f'https://www.imdb.com/title/{id}/mediaviewer'
                    resp = requests.get(url2, headers=HEADERS)

                    page2 = BeautifulSoup(resp.text, 'lxml')
                    image_url = str(page2.find_all('img')[1]['src'])
                    
                                
                    data = {
                        "movie_id": id,
                        "start_year": int(start_year),
                        "end_year": int(end_year),
                        "age": age,
                        "plot": movie.select('.text-muted')[2].get_text().strip(),
                        "revenue": revenue2 ,
                        "rating": float(movie.select('.ratings-imdb-rating')[0].get_text().strip()),
                        "metascore": metascore,
                        "runtime": runtime,
                        "votes": int(votes),
                        "genres": genres,
                        "kind": "movie",
                        "ep_count": 0,
                        "cast": cast,
                        "title": original_title,
                        "poster_url": poster_url,
                        "image_url": image_url
                        }
                        
                    if id not in id_list:
                        json_list.append(data)
                        id_list.append(id)

                        # Save data to json file
                        with open("movies.json", 'w', encoding='utf-8') as file:
                            file.write(
                                '[' +
                                ',\n'.join(json.dumps(i, ensure_ascii=False) for i in json_list) +
                                ']\n')

                        pbar.update(n=1) 
                
            except Exception:
                exc_type, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                pass


        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(downloadData, movie_list)   


    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(iterateList, url_list)   

             