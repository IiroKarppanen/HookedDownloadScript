def get_urls(minVotes):

    import concurrent.futures
    import requests
    from bs4 import BeautifulSoup
    from tqdm import tqdm
    import os

    HEADERS ={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":
    "gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", 
    "Upgrade-Insecure-Requests":"1"}

    genres = ["Adventure", "Animation", "Biography", "Comedy", "Crime", "Drama", "Family", "Fantasy", "Film-Noir", "History", "Horror",
    "Music", "Musical", "Mystery", "Romance", "Sci-Fi", "Sport", "Thriller", "War", "Western"]

    url_list = []
    id_list = []

    print("Preparing Download (1/2)")
    pbar = tqdm(total=len(genres))

    def save_url(genre):
        
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

        max_amount_in_page = 1

        while max_amount_in_page < amount:
            url = "https://www.imdb.com/search/title/?title_type=feature,tv_movie,tv_series&num_votes={},&genres={}&sort=user_rating,desc&start={}&count=250t"
            formated_url = url.format(minVotes, genre, max_amount_in_page)
            url_list.append(formated_url)
            max_amount_in_page += 50

        pbar.update(n=1) 


    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(save_url, genres)

    pbar.close()
    os.system('cls')
    print("Preparing Download (1/3)")
    pbar = tqdm(total=len(url_list))


    def delete_duplicates(url):
        resp = requests.get(url, headers=HEADERS)
        content = BeautifulSoup(resp.text, 'lxml')

        for movie in content.select('.lister-item-content'):

            # Get movie id and append it to list
            id = movie.select('.lister-item-header')[0].find('a')['href']
            id = id.replace("/", "").replace("title", "").replace("?ref_=adv_li_tt", "").strip()
            id_list.append(id)

        pbar.update(n=1) 



    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(delete_duplicates, url_list)


    id_list = list(set(id_list))


    pbar.close()

    return url_list, id_list

