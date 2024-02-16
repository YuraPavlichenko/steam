import requests
from xml.etree import ElementTree


# url = "https://steamcommunity.com/groups/Natus-Vincere/memberslistxml/?xml=1&p=2"

# response = requests.get(url)
# tree = ElementTree.fromstring(response.content)

# for member in tree.findall("./members/steamID64"):
#     print(member.text)


# for child in tree:
#     print(child.tag, child.attrib)
    

# a = response.json()
# print(response.json())
# print(response.text)

# a = "https://steamcommunity.com/groups/Natus-Vincere/memberslistxml/?xml=1&p=2"


a = "http://steamcommunity.com/inventory/76561198215117679/730/2?l=english&count=5000"

response = requests.get(a)
print(response.status_code)
print(response.json())