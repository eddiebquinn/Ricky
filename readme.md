# Ricky
A bot based on [RICO-bot](https://github.com/eddiebquinn/RICO-bot) to address the shortcomings of its predecessor. The main feature added is the ability to run on multiple servers. This was done to decentralise the nofap community and move away from centralised hub servers. While this bot inherits many of the original streak related features of its predecessor, it also strips away many features. The reason for this is because a lot of what the previous iteration was doing, could be done by many other bots in far better ways.

# Running
I would prefer you don't run an instance of this bot, just call the `!invite` command and it will give you a link to add to your server. The source code is here for the community to add to so we can grow this bot together, *however* if you so wish to run it, the instructions are below

1. **Make sure to get python 3.10 or higher**
This is required to run the bot
2. **Install dependencies**
You can easily install all required dependencies using the `requirements.txt` file located in the repo, to do this navigate into the directory and type `pip3 install -r requirements.txt`.
3. **Create the database in MySQL**
The bot itself is smart enough to make the tables in MySQL (provided they do not already exist) upon connection. All you need to do is create the database and schema
4. **Setup config file**
For operational security, the config file is included in the `.gitignore` file and thus is not viable within the repo. It is however required to run the bot, and thus you will find how to lay it out below.

```JSON
{
    "sql_connection_settings":{
        "username": "username",
        "password": "password",
        "host": "host",
        "database":"database"
    },
    "discord_api_settings":{
        "api_token":"api_token"
    }
}
```
5. **Running the bot**
As it currently stands, the main instance of the bot is run using [PM2](https://pm2.keymetrics.io/). This is not required, and in the long term it is likely we will move towards using a docker container. The bot doesn't take any arguments to start and can be launched using `python3 main.py` in the command line. 