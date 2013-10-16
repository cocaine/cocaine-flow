"""
1. Make tempdir
2. git clone
3. extract commits
4. language specific deploy
5. make app info
6. make tar.gz
7. save data
8. save commits
9. save app info
"""

def upload(request, response):
    req = yield request.read()

    response.write("OK")
    response.close()