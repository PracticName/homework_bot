# Бот-ассистент
## Описание
Telegram-бот, который обращается к __API__ сервиса __Практикум.Домашка__ и узнает статус вашей домашней работы: взята ли ваша домашка в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку:
- раз в 6 минут опрашивает __API__ сервис __Практикум.Домашка__ и проверяет статус отправленной на ревью домашней работы;
- при обновлении статуса анализирует ответ API и отправляет вам соответствующее уведомление в Telegram;
- логироует свою работу и сообщает вам о важных проблемах сообщением в Telegram.

Константа ```RETRY_PERIOD``` отвечает за период опроса __API__ сервиса __Практикум.Домашка__

Функция ```main()```: в ней описана основная логика работы программы. Все остальные функции запускаются из неё. Последовательность действий в общем виде такая:
1. Сделать запрос к API.
2. Проверить ответ.
3. Если есть обновления — получить статус работы из обновления и отправить сообщение в Telegram.
4. Подождать некоторое время и вернуться в пункт 1.

Функция ```check_tokens()``` проверяет доступность переменных окружения, которые необходимы для работы программы. Если отсутствует хотя бы одна переменная окружения — продолжать работу бота нет смысла.

Функция ```get_api_answer()``` делает запрос к единственному эндпоинту API-сервиса <https://practicum.yandex.ru/api/user_api/homework_statuses/>. В качестве параметра в функцию передается временная метка. В случае успешного запроса вернет ответ API, приведя его из формата JSON к типам данных Python.

Функция ```check_response()``` проверяет ответ API на соответствие документации __API__ сервиса __Практикум.Домашка__. В качестве параметра функция получает ответ API, приведенный к типам данных Python.

Функция ```parse_status()``` извлекает из информации о конкретной домашней работе статус этой работы. В качестве параметра функция получает только один элемент из списка домашних работ. В случае успеха, функция возвращает подготовленную для отправки в Telegram строку, содержащую один из вердиктов словаря ```HOMEWORK_VERDICTS```

Функция ```send_message()``` отправляет сообщение в Telegram чат, определяемый переменной окружения ```TELEGRAM_CHAT_ID```. Принимает на вход два параметра: экземпляр класса ```Bot``` и строку с текстом сообщения.

_Логирование_
Каждое сообщение в журнале логов состояит из:
- даты и времени события,
- уровня важности события,
- описания события,
- номер строки в том файле, из которого сообщение отправлено в лог,
- имя функции, из которой отправлено сообщение в лог.
Например:
```
2024-05-23 13:00:15,900, ERROR, Сбой в работе программы: HTTP response code отличный от 200., 140, main
```

## Как запустить проект
1. Cделать форк и клонируйте репозиторий <https://github.com/PracticName/homework_bot>
2. Cоздать и активировать виртуальное окружение:
Windows
```
python -m venv venv
source venv/Scripts/activate
```
Linux/macOS
```
python3 -m venv venv
source venv/bin/activate
```
3. Обновить PIP
Windows
```
python -m pip install --upgrade pip
```
Linux/macOS
```
python3 -m pip install --upgrade pip
```
4. Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
5. Создать Бота зарегестрировать и настроить его; подробная документация <https://core.telegram.org/bots/api>
6. Создайте файл ```.env``` в корне проекта и заполните его
```
P_TOKEN = <Ваш_token_Практикум.Домашка>
T_TOKEN = <Ваш_token_бота>
T_CHAT_ID = <Ваш_telegram_id>
```
Получить токен API __Практикум.Домашка__ можно по адресу: <https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a>.
7. Запустить проект:
Windows
```
python homework.py 
```
Linux/macOS
```
python3 homework.py 
```
## Стек
1. Python 3.9
2. requests
3. pytest
4. python-dotenv
5. python-telegram-bot

## Примеры ответов API Практикум.Домашка
В список ```homeworks``` попадают работы, которым был присвоен статус за период от ```from_date``` до настоящего момента. С помощью метки времени можно управлять содержанием этого списка: 
при ```from_date = 0``` в этот список попадут все ваши домашние работы;
при ```from_date```, равном "минуту назад", велик шанс получить пустой список;
при других значениях этого параметра в списке будет ограниченный перечень домашних работ.

```
{
   "homeworks":[
      {
         "id":124,
         "status":"rejected",
         "homework_name":"username__hw_python_oop.zip",
         "reviewer_comment":"Код не по PEP8, нужно исправить",
         "date_updated":"2020-02-13T16:42:47Z",
         "lesson_name":"Итоговый проект"
      },
      {
         "id":123,
         "status":"approved",
         "homework_name":"username__hw_test.zip",
         "reviewer_comment":"Всё нравится",
         "date_updated":"2020-02-11T14:40:57Z",
         "lesson_name":"Тестовый проект"
      },

      ...

   ],
   "current_date":1581604970
} 
```
Если за выбранный интервал времени ни у одной из домашних работ не появился новый статус — список работ будет пуст:
{
   "homeworks":[],
   "current_date":1634074965
}
Если в качестве параметра ```from_date``` в запросе будет передано что-то неожиданное для сервиса, то API вернёт ответ с кодом 400:
```
{
   "code": "UnknownError",
   "error": {"error": "Wrong from_date format"}
}
```
А в случае запроса с недействительным или некорректным токеном, API вернёт ответ с кодом 401. Сам ответ будет содержать следующую информацию:
```
{
   "code": "not_authenticated",
   "message": "Учетные данные не были предоставлены.",
   "source": "__response__"
}
```
## Статусы домашней работы
Статус домашки (значение из ответа API по ключу ```status```) может быть трёх типов:
- ```reviewing```: работа взята в ревью;
- ```approved```: ревью успешно пройдено;
- ```rejected```: в работе есть ошибки, нужно поправить.
Если домашку ещё не взяли в работу — её не будет в выдаче.  

## Автор
Агеев Алексей