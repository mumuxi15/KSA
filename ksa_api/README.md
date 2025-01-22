# KSA_API

Everyday start

```bash
.venv\Scripts\activate
cd ksa_api\backend
python manage.py runserver
cd ksa_api\frontend
npm start
```

Backend Django Set Up

```python
django-admin startproject ksa_api#mkdir backend and move all files to backend
python manage.py startapp dashboard
pip install django-cors-headers  # solve CORS issues localhost:3000 and localhost:8000
python manage.py startapp shipping  #create a shipping app
python manage.py makemigrations shipping # update changes in shipping.models
python manage.py shell # exlore database APIbash
```



Frontend React Set Up

```shell
npx create-react-app frontendnpx
cd frontend
npm install axios
npm i react-router-dom
npm i react-bootstrap bootstrap
npm install react-icons 
npm install --save jquery
npm start
#  install css packages
npm install react-icons --save
npm install @mui/material @emotion/react @emotion/styled find filename in all sub directory 
```

Production Environment

Two environment: local, production.When switch, update below files

```python
change urls.py, wsgi.py, asgi.py, 'ksa_api.settings.local' to 'ksa_api.settings.production'
```

```

```
