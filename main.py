import concurrent.futures
import requests
from bs4 import BeautifulSoup
import json
import re
from tqdm import tqdm
import os
from PIL import Image
import sys

Image.MAX_IMAGE_PIXELS = None

HEADERS ={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

genres = [
    "Adventure",
    "Animation",
    "Biography",
    "Comedy",
    "Crime",
    "Drama",
    "Family",
    "Fantasy",
    "Film-Noir",
    "History",
    "Horror",
    "Music",
    "Musical",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Sport",
    "Thriller",
    "War",
    "Western"
]

pages = [1,51,101,151,201,251,301,351,401,451,501,551,601,651,701,751,801,851,901,951,1001]

url_list = []
id_list = []
image_list = []
title_list = []
json_list = []

current_directory = os.getcwd()
path_to_json = os.path.join(current_directory, 'movies.json')

minVotes = 0

while True:
    try:
        minVotes = int(input("Enter minimum amount of IMBd votes for movie(lower count = more movies): "))
    except ValueError:
        print("Invalid input")
        continue
    else:
        break

os.system('cls')

print("Preparing download (1/3)...")

LENGTH = int(len(genres))
pbar = tqdm(total=LENGTH) # Init pbar

movie_amount = 0

def get_urls(genre):

    global movie_amount
    global bpar
    global minVotes

    pages = [1,251,501,753,751,1001,1251,1501,1751,2001,2251,2501,2751,3001,3251,3501,3751,4001]
    
    url = "https://www.imdb.com/search/title/?title_type=feature,tv_movie,tv_series&num_votes={},&genres={}&sort=user_rating&count=250"
    url = url.format(minVotes, genre)

    resp = requests.get(url, headers=HEADERS)
    content = BeautifulSoup(resp.text, 'lxml')
    amount = content.find('div', attrs=('class', 'desc')).find('span').text
    
    try:
        amount = amount[amount.index("of") + len("of"):]
        amount = int(''.join(x for x in amount if x.isdigit()))
    except:
        try:
            amount = int(''.join(x for x in amount if x.isdigit()))
        except:
            amount = 0
    movie_amount += amount
   
    for page in pages:
        if page >= amount:
            break
        url = "https://www.imdb.com/search/title/?title_type=feature,tv_movie,tv_series&num_votes={},&genres={}&sort=user_rating,desc&start={}&count=250t"
        formated_url = url.format(minVotes, genre, page)
        url_list.append(formated_url)

    pbar.update(n=1) 


def get_movies(url):

    global bpar, url_list, json_list, id_list
        
    resp = requests.get(url, headers=HEADERS)
    content = BeautifulSoup(resp.text, 'lxml')

    for movie in content.select('.lister-item-content'):

        try:

            header = movie.select('.lister-item-header')[0].get_text().strip()

            # Get movie id and append it to list
            a = movie.select('.lister-item-header')[0].find('a')['href']
            a = a.replace("/", "").replace("title", "").replace("?ref_=adv_li_tt", "").strip()
            id = a

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
                metascore = 0

            try:

                list = movie.select('.sort-num_votes-visible')[0].findChildren('span')
                
                votes = list[1].get_text().strip().replace(",", "")
                votes = int(votes)

            except:
                votes = 0
                continue

            
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
                revenue = 0
                continue

            cast = []
            
            actors = movie.select('p')[-2].get_text().strip()
            cast.append(actors.split("Stars:",1)[1].strip().replace('\n', ''))
            cast = json.dumps(cast, ensure_ascii=False)
                         
            data = {
                "movie_id": id,
                "start_year": start_year,
                "end_year": end_year,
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
                }
                
            json_list.append(data)
            id_list.append(id)

            # Save data to json file
            global path_to_json
            with open(path_to_json, 'w', encoding='utf-8') as file:
                file.write(
                    '[' +
                    ',\n'.join(json.dumps(i, ensure_ascii=False) for i in json_list) +
                    ']\n')
            
            pbar.update(n=1) 

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            pass


def get_images(id):

    try:

        # Download posters and images

        url = 'https://www.imdb.com/title/' + str(id) + "/"

        response = requests.get(url)
        page = BeautifulSoup(response.text, 'lxml')

        try:
            original_title = page.select('div.sc-dae4a1bc-0.gwBsXc')[0].text
            original_title = original_title.replace("Original title: ", "").strip()
        except:
            original_title = str(page.title.string[:-7])

        original_title = original_title.split("(", 1)[0]
        
        image_url = page.select('img.ipc-image')[0]['src']
        img_data = requests.get(image_url).content 

        file = f'{id}.jpg'
        current_directory = os.getcwd()
        location = os.path.join(current_directory, '/posters')
        dpath = os.path.join(location, file)
        print(dpath)

        with open(dpath, 'wb') as handler: 
            handler.write(img_data) 

        url2 = f'https://www.imdb.com/title/{id}/mediaviewer'

        response = requests.get(url2)
        page2 = BeautifulSoup(response.text, 'lxml')

        image_url =str(page2.find_all('img')[0]['src'])

        image_list.append(image_url)
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
    executor.map(get_urls, genres)

pbar.close()
print("Downloading movie data (2/3)...")
pbar = tqdm(total=movie_amount) # Init pbar

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(get_movies, url_list)

#Delete duplicates before downloading images
with open(path_to_json, encoding="utf8") as f:
  data = json.load(f)

unique = { each['movie_id'] : each for each in data }.values()

with open(path_to_json, 'w', encoding='utf-8') as file:
            file.write(
                '[' +
                ',\n'.join(json.dumps(i, ensure_ascii=False) for i in unique) +
                ']\n')

id_list = sorted(set(id_list))

pbar.close()
print("Downloading movie images (3/3)...")
pbar = tqdm(total=len(id_list)) # Init pbar

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(get_images, id_list)


# Add titles and image_urls to json file

with open('movies.json', encoding="utf8") as f:
  data = json.load(f)

for (item, title, url) in zip(data, title_list, image_list):
    item['title'] = title
    item['image_url'] = url

with open('movies.json', 'w', encoding='utf-8') as file:
                file.write(
                    '[' +
                    ',\n'.join(json.dumps(i, ensure_ascii=False) for i in data) +
                    ']\n')
   

pbar.close()
print("\nDownload Complete!")

