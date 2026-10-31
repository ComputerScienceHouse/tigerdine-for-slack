# TigerDine for Slack "bot.py"
# Copyright (C) 2026 Campbell Bagley

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from dining import *

import os
import time
from datetime import date, datetime

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Because config.json didn't really make sense for this one.
load_dotenv()

# If there's no token provided, then exit.
token = os.environ.get("SLACKBOT_TOKEN")
if token == "":
    print("No Slack bot token was found! Please set the SLACKBOT_TOKEN environment variable.")
    exit()

client = WebClient(token=os.environ.get("SLACKBOT_TOKEN"))


def send_message_to_slack(message: str):
    try:
        channel_id = os.environ.get("SLACKBOT_LUNCH_CHANNEL")
        if type(channel_id) is None:
            print(f"No channel ID was found! Please set the SLACKBOT_LUNCH_CHANNEL environment variable.")
            return
        response = client.chat_postMessage(
            channel=str(channel_id),  # We're already made sure it can't be None so cast it to shut PyCharm up.
            text=message,
            unfurl_links=False
        )
        print(response)
    except SlackApiError as e:
        print(f"An error occurred while sending message: {e}")


def get_data_and_send():
    # ======================
    # Today's Visiting Chefs
    # ======================
    dining_data = get_dining_info()
    locations_with_chefs = get_locations_with_chefs(dining_data)

    if not locations_with_chefs:
        slack_str = "No visiting chefs are on campus today!\n"

    else:
        slack_str = "Here are today's visiting chefs:\n"
        for key in locations_with_chefs.keys():
            slack_str += f"*{key}*\n"
            for location in locations_with_chefs[key]:
                start_time = datetime.strptime(location["startTime"], "%H:%M").strftime("%I:%M %p")
                end_time = datetime.strptime(location["endTime"], "%H:%M").strftime("%I:%M %p")
                slack_str += f"  - *{location["name"]}* ({start_time} - {end_time})\n"
                if location["description"] != "":
                    slack_str += f"      {location["description"]}\n"

    send_message_to_slack(slack_str)

    # ===================
    # Today's Food Trucks
    # ===================
    truck_data = get_food_truck_info()
    trucks_with_availability = get_trucks_with_availability(truck_data)
    date_str = date.today().strftime('%Y-%m-%d')

    if trucks_with_availability:
        slack_str = "Food trucks are on campus today!\n"
        for truck in trucks_with_availability:
            for d in truck["datesAvailable"]:
                if d["date"] == date_str:
                    start_time = datetime.strptime(d["startTime"], "%H:%M:00").strftime("%I:%M %p")
                    end_time = datetime.strptime(d["endTime"], "%H:%M:00").strftime("%I:%M %p")
                    slack_str += f"- *{truck["title"]}* ({start_time} - {end_time}) @ <{d["url"]}|{d["urlTitle"]}>\n"
                    if truck["description"] != "":
                        slack_str += f"    {truck["description"]}\n"

        send_message_to_slack(slack_str)


def main():
    print(f"Bot started up at {datetime.now().strftime('%H:%M')}")
    print(f"Message scheduled to send at "
          f"{os.environ.get("SLACKBOT_SCHEDULED_HOUR")}:{os.environ.get("SLACKBOT_SCHEDULED_MINUTE")} "
          f"({os.environ.get("SLACKBOT_UTC_OFFSET")}:00 offset) daily")

    if os.environ.get("SLACKBOT_INSTANT_MODE"):
        print("Instant mode is on! Sending now...")
        get_data_and_send()

    while True:
        cur_time = datetime.now()
        utc_offset = int(str(os.environ.get("SLACKBOT_UTC_OFFSET")))
        scheduled_hour = int(str(os.environ.get("SLACKBOT_SCHEDULED_HOUR")))
        scheduled_minute = int(str(os.environ.get("SLACKBOT_SCHEDULED_MINUTE")))

        if (int(cur_time.strftime("%H")) - utc_offset == scheduled_hour
                and cur_time.minute == scheduled_minute):
            print("it's time!")
            get_data_and_send()
        time.sleep(60)


if __name__ == "__main__":
    main()
