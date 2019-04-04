#!/usr/bin/env python3

from atlas import Atlas
import json
import argparse

username = ''
password = ''
api_url = ''

parser = argparse.ArgumentParser()

parser.add_argument("--email")

parser.parse_args()
args = parser.parse_args()

def load_credentials(file='credentials.json'):
    global data, username, password, api_url
    with open(file, 'r') as f:
        data = json.load(f)
        username = data['username']
        password = data['password']
        api_url = data['api']

def init_atlas(debug=False):
    global atlas, username, password, api_url
    load_credentials()
    atlas = Atlas(username, password, api_url, verify_credentials=False, debug=debug)


def pretty_format(results):
	for hit in results["hits"]["hits"]:
		breach_name = hit["_index"]
		breach_data = hit["_source"]

		print("\n# %s" % (breach_name))

		for key in breach_data:
			if key != "":
				print("%s: %s" % (key, str(breach_data[key]).strip()))


init_atlas(debug=False)

if args.email:
	print("[*] Searching Atlas for %s" % args.email.strip())
	results = atlas.search_email_addresses(email_address=args.email, size=100)
	pretty_format(results)