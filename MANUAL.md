#Cocaine-flow over HTTP#

Под **COCAINE_API_SERVER** понимается адрес:порт, запущенного **Cocaine-flow**

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

Пример:  
    `wget -qO - "http://COCAINE_API_SERVER/hosts"`

### Добавить хост:
Доступно только администратору. Необходимо указать token.
  + Url: *COCAINE_API_SERVER/hosts/<claster_name>/<hostname>*
  + HTTP-метод: *PUT* *POST*
  + Параметры: *token*

Пример:  
    `curl -X PUT "http://COCAINE_API_SERVER/hosts/TESTCLUSTER/TESTHOST?token=<admin's-token>"`
    
### Удалить хост:
Доступно только администратору. Необходимо указать token.
  + Url: *COCAINE_API_SERVER/hosts/<claster_name>/<hostname>*
  + HTTP-метод: *DELETE*
  + Параметры: *token*

Пример:  
    `curl -X DELETE "http://COCAINE_API_SERVER/hosts/TESTCLUSTER/TESTHOST?token=<admin's-token>"`
   
### Удалить кластер:
**ВНИМАНИЕ:** это удалит все хосты, входящие в этот кластер!  
Доступно только администратору. Необходимо указать token.

  + Url: *COCAINE_API_SERVER/hosts/<claster_name>*
  + HTTP-метод: *DELETE*
  + Параметры: *token*

Пример:  
    `curl -X DELETE "http://COCAINE_API_SERVER/hosts/TESTCLUSTER?token=<admin's-token>"`
   
