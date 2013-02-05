# Cocaine-flow-setup

Эта утилита позволяет произвести первоначальную настройку Cocaine-flow. Настройка производится в режиме вопрос-ответ.
В скобках указывается "значение по умолчанию"

Запускаем:
```bash
python cocaine-flow-setup
```
Путь к каталогу, где будет расположен файл конфигурации:  
```bash
Installation path (default: /etc/cocaine-flow):
```
Имя дефолтного пользователя:  
```bash
Username (default: admin):
Password (default: password):
```
Тип стораджа:
```bash
Storage (default: elliptics):
```
Далее идет настройка стораджа.
Для **elliptics**:
```bash
Elliptics node (hostname[:port])  # хост и порт
Elliptics groups (default: 1,2,3) # список групп 
```
Для **mongo**:
```bash
Mongo hostname (default: localhost)   # хост с MongoDB
Mongo port (default: 27017)           # порт
Mongo db name (default: cocaine-flow) # имя базы в Mongo
Mongo replica set                     # имя репликасета, если есть
```
Далее запрашивается порт, по-которому будет доступен веб-интерфейс **cocaine-flow**:
```bash
Port (default: 5000)  # порт для доступа в веб-интерфейс
```

По результатам ответов будет произведена проверка подключения к стораджу, создание учетной записи и сгенерирован файл
настроек. Примерный вид:
```yaml
PORT: 5000
SECRET_KEY: <some-key>
UPLOAD_FOLDER: /tmp
ALLOWED_EXTENSIONS: [.gz]
STORAGE: elliptics
ELLIPTICS_GROUPS: [1, 2, 3]
ELLIPTICS_NODES: {elliptics-host.net: 1025}
MAX_CONTENT_LENGTH: 16777216
#STORAGE: mongo 
#MONGO_DBNAME: cocaine-flow 
#MONGO_HOST: mongo-host.net
#MONGO_PORT: 27017
```

Данный фалйл можно уточнять в последствии руками.
