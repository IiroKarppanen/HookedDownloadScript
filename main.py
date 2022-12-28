from get_urls import get_urls
from get_data import get_movies
from get_images import get_images
import os


os.system('cls')    

# Gather URLS

while True:
    try:
        minVotes = int(input("Enter minimum amount of votes for movie (lower count -> more movies): "))
        if ((len(str(minVotes)) < 4) or (len(str(minVotes)) > 7)):
            raise ValueError
        break
    except ValueError:
        print("Enter valid number")

        
os.system('cls')
result = get_urls(minVotes)

url_list = result[0]
id_list = result[1]


# Download data
os.system('cls')

get_movies(url_list, len(id_list))

# Download image urls
os.system('cls')

get_images(id_list)

print("\nDownload Complete!")





