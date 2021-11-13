## How to install and run this package
### Configuration
Edit `config.json`
````json
{
  "token": "COPY YOUR DISCORD BOT TOKEN HERE"
}
````
### Installation
#### Using Docker
To install this package, run the following command:
```bash
$ docker built . -t check_students
$ docker run -v  $(pwd)/database:/app/database/ --name discord-checkstudent -d check_students
```

#### Using your bash
````bash
$ pip install -r requirements.txt
$ python app.py
````