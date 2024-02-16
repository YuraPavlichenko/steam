import json
import requests
from xml.etree import ElementTree
import time
import sqlite3


def check_visibility_status(user_id):
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=19934F4774B44AF4D2D31C83122ECDC3&steamids={user_id}"
    response = requests.get(url)
    visibility_status = response.json()["response"]["players"][0]["communityvisibilitystate"]
    if visibility_status != 1:
        return True
    elif visibility_status == 3:
        return False

def check_profile_level(user_id):
    url = f"http://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key=19934F4774B44AF4D2D31C83122ECDC3&steamid={user_id}"

    response = requests.get(url)
    print(response.json(), user_id)
    try:
        user_level = response.json()["response"]["player_level"]
        if user_level > 0:
            return False
        else:
            return True
    except:
        pass


def write_json_to_file(user_id):
    url = f"http://steamcommunity.com/inventory/{user_id}/730/2?l=english&count=5000"
    response = requests.get(url)

    if response.status_code == 200:
        with open('json_response.txt', "w", encoding="utf-8") as file:
            file.write(response.text)
    else:
        print("Error:", response.status_code)


def get_data_from_file():
    with open('json_response.txt', 'r') as file:
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

        if "case" in item_name.lower():
            cases[item_name.lower()] = list_of_classid.count(item_classid)


def get_id_of_group_members():
    url = "https://steamcommunity.com/groups/Natus-Vincere/memberslistxml/?xml=1&p=6"
    response = requests.get(url)
    tree = ElementTree.fromstring(response.content)

    for member in tree.findall("./members/steamID64"):
        user_id = member.text
        if check_visibility_status(user_id):
            if check_profile_level(user_id):
                write_json_to_file(user_id)
                get_data_from_file()
                create_list_of_classid()
                get_name_and_amount()
                calculate_total_amount_of_cases(user_id)
        time.sleep(1)



def calculate_total_amount_of_cases(user_id):
    total_amount_of_cases = sum(cases.values())
    #print(total_amount_of_cases)
    if total_amount_of_cases > 2:
        print(f"User {user_id} has such amount of cases {total_amount_of_cases}")
        write_to_db(user_id, total_amount_of_cases)
        return True
    else:
        print(f"User {user_id} don`t match requirements")
        return False


def write_to_db(user_id, amount_of_cases):
    try:
        sqliteConnection = sqlite3.connect('myproject/db.sqlite3')
        cursor = sqliteConnection.cursor()

        sqlite_insert_query = f"""INSERT INTO steam_requester_user (id, amount_of_cases, is_traded) 
                                VALUES (?, ?, ?)"""

        data_tuple = (user_id, amount_of_cases, False)

        cursor.execute(sqlite_insert_query, data_tuple)
        sqliteConnection.commit()
        print("Record inserted successfully into the table.")
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table:", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed.")


get_id_of_group_members()
#write_to_db(12, 12)