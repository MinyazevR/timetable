# Timetable
Для того, чтобы реализовывать инструменты для работы с расписанием  СПБГУ, необходимо иметь данные с [`timetable`](https://timetable.spbu.ru/) в структурированном виде. Данный проект представляет из себя веб-краулер и базу данных, в которую переодически выгружаются данные с timetable. Для работы с расписанием предоставляются файлы в формате `.csv`. Расписание постоянно выгружается на месяц вперед(с учетом текущей недели). Также, можно упростить работу с базой данных и получить акутальное состояние базы данных с расписанием на месяц вперед. 
#### Prerequisites:
1. [Download and install Python](https://www.python.org/downloads/) (Version 3.x)
   
#### Для получения акутального состояния базы данных необходимо:
1. Склонировать этот репозиторий
```
git clone https://github.com/MinyazevR/timetable.git
```
2. Install requirements
```
pip install -r requirements.txt
```
3. Cоздать базу данных
4. Поменять файл config.py в корневой директории, установив DATABASE_URL. Пример для PostgreSQL:
```
DATABASE_URI = 'postgresql+asyncpg://<username>:<password>@localhost:<port>/<database_name>'
```
5. Обновить базу данных до актуального состояния(все миграции находятся в `migrations`)
```
alembic upgrade head
```
6. Заполнить таблицы, запустив main.py (запускать с аргументом events только после users, потому что таблицы, связанные с расписанием заполняются на основе таблиц, связанных с пользователями)
```
python3 main.py users
python3 main.py events
```
