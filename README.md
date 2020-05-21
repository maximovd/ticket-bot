## Telegram bot for receive ticket.

For the bot to work, it is required .env file in the project root.Place your tokens in this file.
You can find an example .env in the root of the project, called example-env.

There are two ways to deploy the bot:

1. Launch in the terminal using supervisor on Ubuntu.
2. Launch in the Docker container.

### 1. Launch in the terminal using supervisor on Ubuntu.

First, you need to make sure that your python version is ≥ 3.7:

```
$ python3 -V
```
If pip is not installed, install:
```
$ sudo apt update
$ sudo apt install python3-pip
```

If this is not the case, update the python version.

I use Poetry to work with dependencies on the dev machine, but you can use virtualenv on the server.

For install python-venv on Ubuntu, use this command: 
```
$ sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
$ sudo apt install -y python3-venv
```

Then you need to create a new environment:

```
$ mkdir myapp && cd myapp
$ python3 -m venv env
```
Then activate new venv:
```
$ source env/bin/activate

```
After activating v env, you need to install dependencies for the bot. While in the bot folder, run:
```
$ pip3 install -r requirements.txt
```
This command will install all dependencies for your venv.

After installing the dependencies, install and configure supervisor:
```
$ sudo apt install supervisor
```
The supervisor allows you to monitor the status of applications, stop, start, and restart them. First, we need to create a configuration file for your program, where we will describe the basic rules for restarting and logging. By default, you can use the file:
```
$ /etc/supervisor/supervisord.conf
```
Delete all the content and enter the following text:
```
[program:ticket-bot]
command=python bot.py
directory=/your-path/to/bot/
autorestart=true
```
If you haven't started the supervisor yet, run the command:
```
$ supervisord
```
Now you can say the supervisor to read the data from the config:
```
$ supervisorctl reread
```
To view the status of running processes, use the command:
```
$ supervisorctl status
```
The process called "ticket-bot “(the name is specified in the config) will be in the”STOPPED" state, launch it:
```
$ supervisorctl start
```
Now the bot should work.

### 2. Launch in Docker container.

To run the bot in the Docker container, you need to install docker and buld docker image, as the system I will use Ubuntu.
```
$ sudo apt install docker.io

```
Before creating a Dockerfile, you must edit It by filling it in with your own data

After build the docker image:
```
$ docker build -t ticket-bot ~/path-to-Dockerfile
```
After run docker image in container:
```
docker run ticket-bot 
```
Now the bot should work.