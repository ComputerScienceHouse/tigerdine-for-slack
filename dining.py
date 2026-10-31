# TigerDine for Slack "dining.py"
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

from datetime import date
import requests


def get_dining_info() -> list[dict]:
    url = "https://www.rit.edu/feeds/mobile-app/dining-all.php"
    response = requests.get(url, timeout=5).json()
    return response


def get_locations_with_chefs(data: list[dict]) -> dict[list[str]]:
    locations_with_chefs: dict[list[str]] = {}

    date_str = date.today().strftime('%Y-%m-%d')

    for location in data:
        if location["visitingChefs"]:
            chefs: dict = location["visitingChefs"]
            for day in chefs.keys():
                if day == date_str:
                    found_chefs = []
                    for chef in chefs[date_str]:
                        found_chefs.append(chef)
                    locations_with_chefs[location["name"]] = found_chefs

    return locations_with_chefs


def get_food_truck_info() -> list[dict]:
    url = "https://www.rit.edu/dining/feeds/mobile-app/food-trucks.php"
    response = requests.get(url, timeout=5).json()
    return response


def get_trucks_with_availability(data: list[dict]) -> list[dict]:
    trucks_with_availability: list[dict] = []

    for truck in data:
        if truck["datesAvailable"]:
            trucks_with_availability.append(truck)

    return trucks_with_availability
