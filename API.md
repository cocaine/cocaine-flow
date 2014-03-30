# Flow REST API
To use all handlers except `Auth` you should set token in `Authorization` header (See examples).

## Auth

### Signup
 + url: `/flow/v1/signup`
 + method: **POST**
 + args:
   * name - username
   * password - password

```(bash)
curl -XPOST "http://localhost:9000/flow/v1/signup" --data "name=dummy&password=qwerty"
```

### Signin
 + url: `/flow/v1/signin`
 + method: **POST**
 + args: 
 	* name
 	* password

```(bash)
curl -XPOST "http://localhost:9000/flow/v1/signin" --data "name=dummy&password=qwerty"
```

### Generate token
 + url: `/flow/v1/gentoken`
 + method: **POST**
 + args: 
 	* name
 	* password

```(bash)
curl -XPOST "http://localhost:9000/flow/v1/gentoken" --data "name=dummy&password=qwerty"
# You could save token.
tok=$(curl -sXPOST "http://localhost:9000/flow/v1/gentoken" --data "name=dummy&password=qwerty")
```

## Profiles

### List
 + url: `"/flow/v1/profiles`
 + method: **GET**

```(bash)
curl "http://localhost:9000/flow/v1/profiles" -H "Authorization: $tok"
```

### Read
 + url: `/flow/v1/profiles/(.+)`
 + method: **GET**

```(bash)
curl "http://localhost:9000/flow/v1/profiles/profilename" -H "Authorization: $tok"
```

### Upload
 + url: `/flow/v1/profiles/(.+)`
 + method: **PUT**, **POST**

```(bash)
curl -XPUT "http://localhost:9000/flow/v1/profiles/ZZZ2" -H "Authorization: $tok" --data-binary "{\"pool-limit\": 2}"
```

### Remove
 + url: `/flow/v1/profiles/(.+)`
 + method: **DELETE**

```(bash)
curl -XDELETE "http://localhost:9000/flow/v1/profiles/ZZZ2" -H "Authorization: $tok"
```

## Runlists

### List
 + url: `/flow/v1/runlists`
 + method: **GET**

```(bash)
curl "http://localhost:9000/flow/v1/runlists" -H "Authorization: $tok"
```

## Hosts

### List
 + url: `/flow/v1/hosts`
 + method: **GET**

```(bash)
curl "http://localhost:9000/flow/v1/hosts" -H "Authorization: $tok"
```

### Add host
 + url: `/flow/v1/hosts/(.+)`
 + method: **PUT**, **POST**

```(bash)
curl -XPUT "http://localhost:9000/flow/v1/hosts/localhost" -H "Authorization: $tok"
```

### Remove host
 + url: `/flow/v1/hosts/(.+)`
 + method: **DELETE**

```(bash)
curl -XDELETE "http://localhost:9000/flow/v1/hosts/localhost" -H "Authorization: $tok"
```

## Routing groups

### List
 + url: `/flow/v1/groups`
 + method: **GET**
```(bash)
curl "http://localhost:9000/flow/v1/groups" -H "Authorization: $tok"
```

### View
 + url: `/flow/v1/groups/([^/]+)`
 + method: **GET**
```(bash)
curl "http://localhost:9000/flow/v1/groups/TEST" -H "Authorization: $tok"
```

### Create
 + url: `/flow/v1/groups/([^/]+)`
 + method: **PUT**, **POST**
```(bash)
curl -XPUT "http://localhost:9000/flow/v1/groups/TEST" -H "Authorization: $tok"
```

### Remove
 + url: `/flow/v1/groups/([^/]+)`
 + method: **DELETE**
```(bash)
curl -XDELETE "http://localhost:9000/flow/v1/groups/TEST" -H "Authorization: $tok"
```

### Push application
 + url: `/flow/v1/groups/([^/]+)/(.+)`
 + method: **PUT**
 + args:
    * weight - integer value
```(bash)
curl -XPUT "http://localhost:9000/flow/v1/groups/TEST/myapp?weight=1" -H "Authorization: $tok"
```

### Pop application
 + url: `/flow/v1/groups/([^/]+)/(.+)`
 + method: **DELETE**

```(bash)
curl -XDELETE "http://localhost:9000/flow/v1/groups/TEST/myapp" -H "Authorization: $tok"
```

## Apps

### List
 + url: `/flow/v1/apps`
 + method: **GET**
```(bash)
curl "http://localhost:9000/flow/v1/apps" -H "Authorization: $tok"
```

### Info
  + url: `/flow/v1/apps/<app>/<version>`
  + method: **GET**
```(bash)
curl "http://localhost:9000/flow/v1/apps/a/1" -H "Authorization: $tok"
```

### Upload
  + url: `/flow/v1/apps/<app>/<version>`
  + method: **POST**
  + body: tar-archive with application
```(bash)
curl -XPOST "http://localhost:9000/flow/v1/apps/testapp/1" -H "Authorization: $tok" --data-binary @testapp.tar.gz
```

### Deploy application
  + url: `/flow/v1/deployapp/<app>/<version>`
  + method: **POST**
  + args:
     * profile
  	 * runlist
  	 * weight: default value 0
```(bash)
curl -XPOST "http://localhost:9000/flow/v1/deployapp/testapp/1?profile=TEST&runlist=TEST&weight=100" -H "Authorization: $tok"
```

### Start application
  + url: `/flow/v1/startapp/<app>/<version>`
  + method: **POST**
  + args:
  	 * profile
```(bash)
curl -XPOST "http://localhost:9000/flow/v1/startapp/testapp/1?profile=TEST" -H "Authorization: $tok"
```

### Stop application
  + url:  `/flow/v1/stopapp/<app>/<version>`
  + method: **POST**
```(bash)
curl -XPOST "http://localhost:9000/flow/v1/stopapp/testapp/1" -H "Authorization: $tok"
```

## Utils

### Ping
  + url: `/flow/ping`
  + method: **GET**