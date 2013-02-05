#Cocaine-flow over HTTP#

Под **COCAINE_API_SERVER** понимается адрес:порт, запущенного cocaine-flow

## Работа с учетными записями ##
Идентификация пользователя осуществляется по секретному токену, который присваивается пользователя при регистрации. 
Для некоторых операций (см. далее) необходимо передавать этот токен в HTTP запросе.

### Регистрация
 
  + Url: *COCAINE_API_SERVER/register*
  + HTTP-метод: *POST*
  + Параметры: *username* и *password*  

Пример:  
    `curl "http://COCAINE_API_SERVER/register" -d "username=TESTUSER&password=TEST"`

### Получение token для пользователя

  + Url: *COCAINE_API_SERVER/token*
  + HTTP-метод: *POST*
  + Параметры: *username* и *password*

Пример:  
    `curl "http://COCAINE_API_SERVER/token" -d "username=TESTUSER&password=TEST"`

## Упавление хостами

### Получить список хостов:
Позволяет посмотреть набор кластеров и входящих в них хостов, участвующих в облаке.

  + Url: *COCAINE_API_SERVER/hosts*
  + HTTP-метод: *GET*
  + Параметры: *username* и *password*

Пример:  
    `wget -qO - "http:/COCAINE_API_SERVER/hosts"`
