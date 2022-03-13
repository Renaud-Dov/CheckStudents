## How to install and run this package

### Installation
#### Using Docker
To install this package, run the following command:
```bash
$ docker built . -t check_students
$ docker run -v  $(pwd)/database:/app/database/ --name discord-checkstudent -d check_students -e "DISCORD_TOKEN=<your-discord-token>"
```

#### Using your bash
````bash
$ pip install -r requirements.txt
$ export DISCORD_TOKEN=your_discord_token
$ python app.py
````