# Geocoder
Данное приложение, используя базу адресов OSM, может определить:
* координаты и полный адрес объекта РФ по части его адреса
* все строения находящиеся в заданном радиусе от указанного адреса

## Скачивание базы
`download_db.py`

## Usage
```
search.py [-h] [--nv] [--nc] [-r R] name_db address
```

- positional arguments:
  * `name_db` : имя базы данных
  * `address` : адрес желаемого здания

- optional arguments:
  * `-h, --help` : показать справочное сообщение и выйти
  * `--nv, --no-verbose` : вывод без информации об исправлении ошибок
  * `--nc, --no-corrected` : режим без исправления ошибок
  * `-r R` : радиус поиска

### Подробности реализации
Модули, отвечающие за сбор базы данных адресов, расположены в пакете `pretreatment`:
* `get_city_list.py` получает из системы OSM список всех городов РФ с их id и регионами, котороми они пренадлежат
и сохраняет в файл `cities_from_osm.txt`
* `preprocessor.py` принимает на вход txt-файл со списком городов, их id в системе OSM и регином
и название итоговой базы данных. Заполняет итоговую БД адресами из системы OSM, принадлежащим данным городам
* `kdtree.py` составляет kd-дерево всех адресов и записывает бинарное дерево в виде массива в файл
* `download_db.db` скачивает базу данных с Яндекс.Диска на локальный диск
* `kdsearch.py` осуществялет поиск адресов в радиусе по бинарному дервеву, записаному в файле
* `search.py` осуществялет поиск адреса по базе данных и вывод соответствующей информации