# Description
This is demo of task from freelance. This script work only with html request.
If you need more functionality like async, parse phone number, saving to
xls(xlsx) file format, please contact with me.

## Task
> Добрый день. Нужно собрать данные с сайта olx точка kz 
> 1. Брать нужно: урл, телефон , имя, область, город, район, категория + подкатегории.
> 2. Данные нужно выгружать в эксель построчно в колонки. 
> 3. Если в объявлении больше 1 номера, то следующие номера переносятся на строки ниже, а все данные из объявления просто копируются. 
> 4. Основные данные- это номера, удалять дубликаты нужно именно по номерам. 
> 5. Номера нужно приводить в единный формат начинаться они должны с семерки а не с +семь или восьмерки, и без каких-либо символов между цифрами. Пример на фото.

# Features
[x] - Get all links from main OLX page
[x] - Parse User ID
[x] - Parse User Name
[x] - Parse Title
[x] - Parse Location Region
[x] - Parse Location City
[x] - Parse Location Disctirct
[x] - Parse Location Category
[x] - Parse Location Sub Category
[x] - Format dict object for json
[x] - Save data to csv format file

# Install & Rub
## Install
```bash
python3 -m pip install pipenv
```

```bash
pipenv install --dev
```
## Run
```bash
pipenv run app.py
```

# ToDo
[] - refactor code
[] - tests
[] - project structure
[] - create docker
