
## Запуск и установка.

### 1 .Clone/Fork получите репозиторий и создайте venv
                    
**Windows**
          
```bash
git clone https://github.com/Cycl1k/TestTelethon.git
cd TestTelethon
py -3 -m venv venv

```
          
**macOS/Linux**
          
```bash
git clone https://github.com/Cycl1k/TestTelethon.git
cd TestTelethon
python3 -m venv venv

```

### 2 .Активируйте venv
          
**Windows** 

```venv\Scripts\activate```
          
**macOS/Linux**

```. venv/bin/activate```
or
```source venv/bin/activate```

### 3 .Установите зависимости

Установка windows/macOS/Linux

```
pip install -r requirements.txt
```
# P.S. Иногда не устанавливается Flask и Flaks_login в этом случаи устнавливаем их в ручную
```
pip install flask flask_login
```
### 4 .Миграция и создания БД

```python manage.py```

### 5. Конфигурационный файл

Для запуска необходимо создать config.ini файл с текстом:
```
[Telegram]
api_id = <api id>
api_hash = <api hash>
``` 
Данные можно пулучить на https://my.telegram.org

### 6. Запуск приложения

**Для linux и macOS**
Make the run file executable by running the code

```chmod 777 run```

Then start the application by executing the run file

```./run```

**На windows**
```
set FLASK_APP=routes
flask run
```

---------------

## О веб приложении 
# Web

'/' - базовая страница с авторизацией
'/loginn' - авторизация
'/register' - регистрация
'/qrcode' - созание QR-кода по содержимому запроса
'/tg' - авторизация по QR коду в телеграм
'/get_me' - Информация об аккаунте, под которым авторизовались
'/chat' - информция о доступных чатах
'/chats' - посление 50 сообщений + возможность отправки сообщения
'/wb' - возвращает 10 найденных товаров на wildberries

# Комментарии

Так как не понятно, куда нужно было отправлять запрос "wild:любой товар" превратил его в API POST запрос без тела или GET запрос, что возращает страницу с ссылками

 


