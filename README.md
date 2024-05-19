# Цифровой прорыв: Сезон ИИ, УФО Челябинск

## Кейс: РЖД "Анализатор служебных переговоров"
## Навигация по репозиторию
* research - папка с jupyter notebook с изучением, обработкой данных, подгрузкой и инференсом моделей
* backend-fastapi - папка с файлами backend'а
* fronthack - папка с файлами frontend'a
* langfuse - папка с файлами open source платформы мониторинга llm моделей langfuse
---
## Backend Deployment 
### Требования:
* Docker
### Команды:
```commandline
cd backhacks
docker build -t my-python-app .
docker run -d -p 8000:8000 my-python-app
```
### Итог:
Поднят backend по адресу `http://127.0.0.1:8000/`

## Frontend deployment 
### Требования:
* Docker
### Команды:
```commandline
cd fronthack 
docker build -t my-react-app .
docker run -p 5138:3000 my-react-app
```
### Итог:
Поднят frontend по адресу `http://localhost:5138/`
<br>**Переходите этой ссылке и пользуйтесь сервисом!**

## Langfuse deployment
### Требования:
* Docker
* Docker compose
### Команды:
```commandline
cd langfuse
docker-compose up
```
### Итог:
Поднят langfuse по адресу `http://127.0.0.1:3000/`
<br>**Переходите этой ссылке и пользуйтесь сервисом!**
### Подключение к backend
В langfuse перейти во вкладку settings -> Create new API key
Вставить сгенерированные ключи в `backend-fastapi/app.py` в:
```python
langfuse = Langfuse(
    secret_key="sk-lf-8b25f1cf-eb14-4676-85aa-ad163b91582c",
    public_key="pk-lf-dfb47137-da23-46fd-a273-e99deb59fb32",
    host="http://localhost:3000"
)
```

Заметим, что это API ключи для **ЛОКАЛЬНО** поднятого open-source сервиса.
<br>Никакие проприетарные интеграции не используются в проекте.
<br>Проект в состоянии работать **без интернета** после первоначального запуска.

---
## Команда: ProDUCKtion
* Артём Гордеев
* Дамадан Шавлуков
* Вячеслав Исаев
* Александр Куличенко
