# Website about Films

It is a **Django-based movie watching platform** that allows users to browse, search, and interact with movies and actors. 
Users can leave ratings, manage favorite lists, view rating movies, and explore other users' preferences. 
The project includes several additional features such as caching, pagination, user authentication with Google, 
Celery task management for background operations, parsing films and actors into the database, tests, and Docker to simplify set-up.

---

## Site Functionality:
- View information about **films and actors**
- Add **movies** and **actors** to favorites, and leave reviews/ratings
- User profile functionality, as well as the ability to view other users' profiles and their ratings on movies
- **Search** and **sort** by different queries
- Page showcasing the **most active users**
- Authorization via **email** or **Google account**
- Parser using **Selenium** and **BeautifulSoup** to populate a database with information about movies and actors
- **Celery**, **Redis**, and **caching** for optimization
- **Docker** for easy setup
- Unit Tests for functionality validation

---

## Technologies:
- **Python**
- **Django**
- **Docker**
- **SQLite**
- **Celery**
- **Redis**
- **Selenium**
- **BeautifulSoup**
- **Flower**
- ... 

---
## Set-Up
bash
1) git clone https://github.com/Qermon/movie_website.git
2) In the root folder of the movie_website project you need to create a .env file and add SECRET_KEY with any code there
   Example: SECRET_KEY = '123'
3) docker-compose up --build
4) (Optional) Google registration on the website. In file .env add client_id and secret
   Example:
   SECRET_KEY = '123'
   cliend_id = 'your client_id'
   secret = 'your secret'
