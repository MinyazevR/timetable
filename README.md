# Timetable
Для того, чтобы реализовывать инструменты для работы с расписанием  СПБГУ, необходимо иметь данные с [`timetable`](https://timetable.spbu.ru/) в структурированном виде. Данный проект представляет из себя веб-краулер и базу данных, в которую переодически выгружаются данные с timetable. Для работы с расписанием предоставляются файлы в формате `.csv`. Расписание постоянно выгружается на месяц вперед(с учетом текущей недели). Также, можно упростить работу с базой данных и получить акутальное состояние базы данных с расписанием на месяц вперед. 

### Для этого необходимо:
* git clone https://github.com/MinyazevR/timetable.git
* pip install -r requirements.txt
* создать базу данных (дальше будет пример для PostgreSQL)
* создать в корневой директории файл config.py с единственной строкой: `DATABASE_URI = 'postgresql+asyncpg://<username>:<password>@localhost:<port>/<database_name>'`
* alembic upgrade head
* python3 main.py users
* python3 main.py events
