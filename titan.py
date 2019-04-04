#!/usr/bin/env python3

from atlas import Atlas
import json

with open("credientials.json", "r") as read_file:
    data = json.load(read_file)

print(data)

atlas = Atlas(data["username"], data["password"], data["api"] ,verify_credentials=False, debug=True)

atlas.search_email_addresses('hello@me.com')