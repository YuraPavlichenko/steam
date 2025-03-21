import json
import requests
from xml.etree import ElementTree
import time
import sqlite3
import inspect
from datetime import datetime


def check_status_code(status_code):
    if status_code != 200:
        print(f"WRONG STATUS CODE {status_code}")
        return False
    else:
        return True

def check_visibility_status(user_id):
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=19934F4774B44AF4D2D31C83122ECDC3&steamids={user_id}"
    response = requests.get(url)
    
    if not check_status_code(response.status_code):
        print(f"Current Line: {inspect.currentframe().f_lineno}")

    visibility_status = response.json()["response"]["players"][0]["communityvisibilitystate"]
    if visibility_status == 1:
        return False
    elif visibility_status == 3:
        return True


def check_profile_level(user_id):
    url = f"http://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key=19934F4774B44AF4D2D31C83122ECDC3&steamid={user_id}"

    response = requests.get(url)
    if not check_status_code(response.status_code):
        print(f"Current Line: {inspect.currentframe().f_lineno}")

    print(response.json(), user_id)
    try:
        user_level = response.json()["response"]["player_level"]
        if user_level == 0 or user_level < 5:
            return True
        else:
            return False
    except:
        pass


def write_json_to_file(user_id):
    url = f"http://steamcommunity.com/inventory/{user_id}/730/2?l=english&count=5000"
    response = requests.get(url)
    if not check_status_code(response.status_code):
        print(f"Current Line: {inspect.currentframe().f_lineno}")

    #print(response.status_code)

    if response.status_code != 200:
        return False
    
    try:
        with open('json_response.txt', "w", encoding="utf-8", errors="ignore") as file:
            file.write(response.text)
            return True
    except:
        print("Error:", response.status_code)
        return False

#write_json_to_file("76561199430670235")

def get_data_from_file():
    with open('json_response.txt', 'r', errors="ignore") as file:
        dict_of_items = json.load(file)
        return dict_of_items


list_of_classid = []
def create_list_of_classid():
    dict_of_items = get_data_from_file()
    
    for item in dict_of_items["assets"]:
        list_of_classid.append(item["classid"])
    
    return list_of_classid


cases = {}
def get_name_and_amount():
    cases.clear()
    dict_of_items = get_data_from_file()

    for item in dict_of_items["descriptions"]:
        item_name = item["market_name"]
        item_classid = item["classid"]

        if "Case" in item_name:
            cases[item_name] = list_of_classid.count(item_classid)


def get_id_of_group_members():
    url = "https://steamcommunity.com/groups/Natus-Vincere/memberslistxml/?xml=1&p=758"
    response = requests.get(url)
    if not check_status_code(response.status_code):
        print(f"Current Line: {inspect.currentframe().f_lineno}")

    tree = ElementTree.fromstring(response.content)

    try:
        for member in tree.findall("./members/steamID64"):
            user_id = member.text
            if check_visibility_status(user_id):
                if check_profile_level(user_id):
                    if write_json_to_file(user_id):
                        get_data_from_file()
                        create_list_of_classid()
                        get_name_and_amount()
                        calculate_total_amount_of_cases(user_id)
            time.sleep(3)
    except Exception as Error:
        print("This happend in 89 line")
        print(Error)


def log_message(message, log_file="log.txt"):
    """Appends a message to the log file with a timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def calculate_total_amount_of_cases(user_id):
    total_cases_price = calculate_total_cost(cases)
    total_amount_of_cases = sum(cases.values())
    #print(total_amount_of_cases)
    if total_amount_of_cases > 0:
        print(f"User {user_id} has such amount of cases {total_amount_of_cases} that costs {total_cases_price}")
        log_message(f"User {user_id} has such amount of cases {total_amount_of_cases} that costs {total_cases_price}")
        write_to_db(user_id, total_amount_of_cases, total_cases_price)
        return True
    else:
        print(f"User {user_id} don`t match requirements")
        return False


def calculate_total_cost(cases: dict) -> float:
    #print("Started calculating")
    list_of_keys = list(cases.keys())
    total_cost = 0

    for key in list_of_keys:
        case_name = key
        #print(case_name)
        url = "http://steamcommunity.com/market/priceoverview/"
        params = {
            "appid": 730,
            "currency": 3,
            "market_hash_name": f"{case_name}"
        }
        response = requests.get(url, params=params)
        if not check_status_code(response.status_code):
            print(f"Current Line: {inspect.currentframe().f_lineno}")

        item_price = response.json()["median_price"]
        item_price = item_price.replace(",", ".")
        item_price = item_price.replace("€", "")
        item_price = item_price.replace("-", "")
        total_cost += float(item_price) * cases[key]
        #print(total_cost)
        time.sleep(1)

    return total_cost


def write_to_db(user_id, amount_of_cases, total_cases_price):
    try:
        sqliteConnection = sqlite3.connect('myproject/db.sqlite3')
        cursor = sqliteConnection.cursor()

        sqlite_insert_query = f"""INSERT INTO steam_requester_user (id, amount_of_cases, is_traded, total_cases_price) 
                                VALUES (?, ?, ?, ?)"""

        data_tuple = (user_id, amount_of_cases, False, total_cases_price)

        cursor.execute(sqlite_insert_query, data_tuple)
        sqliteConnection.commit()
        #print("Record inserted successfully into the table.")
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table:", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #print("The SQLite connection is closed.")


get_id_of_group_members()
#write_to_db(12, 12)