# KSA

```bash
.venv\Scripts\activate
cd ksa_api\backend
python manage.py runserver
cd ksa_api\frontend
npm start
```

Django Command

```
python manage.py dumpdata 
```



Backend

```python
django-admin startproject ksa_api
#mkdir backend and move all files to backend
python manage.py startapp dashboard
pip install django-cors-headers  # solve cross-origin resource sharing CORS issues localhost:3000 and :8000 
```

start a new app

```bash
python manage.py startapp shipping  #create a shipping app
python manage.py makemigrations shipping # update changes in shipping.models
python manage.py shell # exlore database API
```

React set up env

```shell
npx create-react-app frontendnpx
cd frontend
npm install axios
npm i react-router-dom
npm i react-bootstrap bootstrap
npm install react-icons 
npm install --save jquery
npm start
# 
```

NPM Pakcages

```shell
npm uninstall @mantine/core @mantine/hooks
npm install react-icons --save
npm install @mui/material @emotion/react @emotion/styled

```

Bash 

```bash
dir /s /b /o:gn "setupProxy.js" # find filename in all sub directory 
```

Production

```python
change urls.py, wsgi.py, asgi.py, 'ksa_api.settings.local' to 'ksa_api.settings.production'
```



HTML

```html
    :{
        'ENGINE': 'django.db.backends.mysql',
        'CONN_STRING': os.getenv('DATABASE_URL')
    }
```

```

```


