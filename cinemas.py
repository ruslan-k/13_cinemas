import random
from time import sleep

import requests
from bs4 import BeautifulSoup

NUM_OF_DISPLAYED_MOVIES = 10
AFISHA_MOVIE_LIST_URL = 'http://www.afisha.ru/msk/schedule_cinema/'
KINOPOISK_URL = 'https://www.kinopoisk.ru/index.php'
PARSE_TIMEOUT = 10
MOVIE_THEATERS_THRESHOLD = 5
USER_AGENTS = [
    "Opera/9.80 (Windows NT 5.1; U; cs) Presto/2.2.15 Version/10.10",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_8; zh-tw) AppleWebKit/533.16 (KHTML, like Gecko) Version/5.0 Safari/533.16"
    "Mozilla/5.0 (X11; U; Linux x86_64; en-us) AppleWebKit/531.2+ (KHTML, like Gecko) Version/5.0 Safari/531.2+"
]


def fetch_afisha_page():
    request = requests.get(AFISHA_MOVIE_LIST_URL)
    afisha_html = request.content
    return afisha_html


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    movie_divs = soup.find_all('div', {'class': 'object'})
    movies_with_num_of_theaters = {}
    for movie_div in movie_divs:
        title = movie_div.find('h3', {'class': 'usetags'}).text
        num_of_movie_theaters = len(movie_div.find_all('td', {'class': 'b-td-item'}))
        if num_of_movie_theaters > MOVIE_THEATERS_THRESHOLD:
            movies_with_num_of_theaters[title] = num_of_movie_theaters
    movies = [title for title, num in movies_with_num_of_theaters.items()]
    return movies


def fetch_movie_info(movie_title):
    print('Processing title: {}'.format(movie_title))
    header = {'User-Agent': random.choice(USER_AGENTS)}
    request_params = {"first": "yes", "kp_query": movie_title}
    request = requests.get(KINOPOISK_URL, headers=header, params=request_params)
    sleep(PARSE_TIMEOUT)
    soup = BeautifulSoup(request.content, 'html.parser')

    movie_rating_tag = soup.find('span', {'class': 'rating_ball'})
    if movie_rating_tag:
        movie_rating = float(movie_rating_tag.text)
    else:
        movie_rating = 0

    num_of_votes_tag = soup.find('span', {'class': 'ratingCount'})
    if num_of_votes_tag:
        num_of_votes = int(num_of_votes_tag.text.replace(' ', ''))
    else:
        num_of_votes = 0

    return dict(title=movie_title, rating=movie_rating, num_votes=num_of_votes)


def output_movies_to_console(movies):
    movies_infos_list = [fetch_movie_info(movie) for movie in movies]
    sorted_movies_by_rating = sorted(movies_infos_list, key=lambda movie_info: movie_info['rating'], reverse=True)
    top_movies = sorted_movies_by_rating[:NUM_OF_DISPLAYED_MOVIES]
    print('\nTop {} popular movies on afisha.ru:'.format(NUM_OF_DISPLAYED_MOVIES))
    for movie in top_movies:
        print('Title: "{title}", rating: {rating}, number of votes: {num_votes}'.format(title=movie['title'],
                                                                                     rating=movie['rating'],
                                                                                     num_votes=movie['num_votes']))


if __name__ == '__main__':
    afisha_page = fetch_afisha_page()
    movies = parse_afisha_list(afisha_page)
    output_movies_to_console(movies)
