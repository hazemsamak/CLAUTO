import requests
from webexteamsbot import TeamsBot
from webexteamsbot.models import Response
import json
import os

# Note: Formatting in Webex Teams uses **text** for bold and *text* for italic

if __name__ == "__main__":
        
    # Set Webex Teams bot data fromn json file
    script_dir = os.path.dirname(__file__)
    bot_file = "{}\\bot.json".format(script_dir)
    with open(bot_file) as data_file:
        bot_json = json.load(data_file)
        bot_url = bot_json["bot_url"]
        bot_token = bot_json["bot_token"]
        bot_email = bot_json["bot_email"]
        bot_name = bot_json["bot_name"]

    # Create bot instance; Setting debug on
    bot = TeamsBot(
        bot_name,
        teams_bot_token = bot_token,
        teams_bot_url = bot_url,
        teams_bot_email = bot_email,
        debug = True
    )

    # Start bot using ngrok
    bot.run(host="0.0.0.0", port=5000)
