import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
import django
django.setup()

import re
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from film.models import Actors, MovieActor, Movies

"""
Цей скрипт здійснює парсинг даних з сайту IMDb для отримання інформації про фільми та акторів. 
Використовуються бібліотеки Selenium для автоматизації браузера, BeautifulSoup для аналізу HTML-коду, 
та requests для виконання HTTP-запитів. Дані отримуються з веб-сторінки IMDb, зберігаються у локальний HTML файл 
і потім аналізуються для отримання деталей про фільми та зберігається в базі даних Django в моделях. 
"""


def get_data(url):
    chromedriver_path = 'C:\\Users\\averb\\PycharmProjects\\djangoProject\\chromedriver.exe'
    options = Options()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    options.add_argument("Accept-Language: en-US,en;q=0.9")

    service = Service(chromedriver_path)
    browser = webdriver.Chrome(service=service, options=options)

    if os.path.getsize('save_script.html') == 0:
        try:
            browser.get(url)
            time.sleep(5)
            page_source = browser.page_source

            with open('save_script.html', 'w', encoding='utf-8') as file:
                file.write(page_source)
                print("Page source saved successfully.")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.quit()
    else:
        pass

    with open('save_script.html', 'r', encoding='utf-8') as file:
        src = file.read()
        soup = BeautifulSoup(src, 'lxml')
        movies = soup.find_all('li', class_="ipc-metadata-list-summary-item sc-4929eaf6-0 DLYcv cli-parent")
        movie_urls = ['https://www.imdb.com' + movie.find('a').get('href') for movie in movies]

        return movie_urls


def get_movie_details(movie_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    response = requests.get(movie_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    title = soup.find('span', class_="hero__primary-text").text
    release_date = None
    release_date_element = soup.find('a', attrs={'href': lambda x: x and 'releaseinfo' in x})

    duration_element = soup.find('li', attrs={'data-testid': 'title-techspec_runtime'})
    duration = duration_element.find('div',
                                     class_="ipc-metadata-list-item__content-container").get_text() if duration_element else None

    rating2 = soup.find('span', class_="sc-d541859f-1 imUuxf").text
    genres = soup.find('div', class_="ipc-chip-list__scroller").text
    genre = ', '.join(set(re.findall(r'[A-Z][a-z]*', genres)))

    description = soup.find('span', class_="sc-3ac15c8d-2 fXTzFP").text
    directors = soup.find('a', class_="ipc-metadata-list-item__list-content-item "
                                      "ipc-metadata-list-item__list-content-item--link").text

    writers_header = soup.find(string="Writers")
    if writers_header:
        writers_section = writers_header.find_next('ul', class_="ipc-inline-list ipc-inline-list--show-dividers ipc-inline-list--inline"
                                                                " ipc-metadata-list-item__list-content baseAlt")
        writers = [li.get_text(strip=True) for li in writers_section.find_all('li')] if writers_section else []
    else:
        writers = []

    if release_date_element:
        release_date = release_date_element.text.strip()

    image = soup.find('img', class_="ipc-image").get('src')
    roles = soup.find_all('span', class_="sc-cd7dc4b7-4 zVTic")

    actor_names = []
    descrip_actors = []
    image_actors = []

    actors = soup.find_all('div', class_="sc-cd7dc4b7-7 vCane")
    actor_urls = ['https://www.imdb.com' + actor.find('a').get('href') for actor in actors]

    for actor_url in actor_urls:
        actor_response = requests.get(actor_url, headers=headers)
        actor_soup = BeautifulSoup(actor_response.text, 'lxml')
        name_span = actor_soup.find('span', class_="hero__primary-text")
        descrip = actor_soup.find('div', class_="ipc-html-content-inner-div")
        images_actors = actor_soup.find('img', class_="ipc-image").get('src')

        if name_span:
            actor_names.append(name_span.text.strip())
        if descrip:
            descrip_text = descrip.text.replace('\n', ' ').replace('\\n', ' ').strip()
            descrip_actors.append(descrip_text)
        if images_actors:
            image_actors.append(images_actors)

    return title, genre, description, release_date, image, rating2, directors, writers, actor_names, descrip_actors, image_actors, roles, duration

# def main():
#     movie_urls = get_data('https://www.imdb.com/chart/top/?ref_=nv_mv_250')
#
#     for movie_url in movie_urls:
#         title, genre, *_ = get_movie_details(movie_url)
#
#         Movies.objects.update_or_create(
#             title=title,
#             defaults={
#                 'genre': genre,
#             }
#         )
#
#
# if __name__ == "__main__":
#     main()


def main():
    movie_urls = get_data('https://www.imdb.com/chart/top/?ref_=nv_mv_250')

    for movie_url in movie_urls:
        (title, genre, description, release_date, image, rating2, directors, writers,
         actor_names, descrip_actors, image_actors, roles, duration) = get_movie_details(movie_url)
        release_year = None
        if release_date:
            match = re.search(r'\d{4}', release_date)
            if match:
                release_year = int(match.group())

        movie, created = Movies.objects.get_or_create(
            title=title,
            defaults={
                'genre': genre,
                'description': description,
                'release_date': release_year,
                'image': image,
                'rating2': rating2,
                'directors': directors,
                'writers': ', '.join(writers),
                'duration': duration
            }
        )

        for actor_name, descrip, actor_image, role in zip(actor_names, descrip_actors, image_actors, roles):
            actor, actor_created = Actors.objects.get_or_create(
                actor_names=actor_name,
                defaults={
                    'descrip_actors': descrip,
                    'image_actors': actor_image
                }
            )

            MovieActor.objects.get_or_create(
                movie=movie,
                actor=actor,
                defaults={'role': role.text if role else None}
            )


if __name__ == "__main__":
    main()
