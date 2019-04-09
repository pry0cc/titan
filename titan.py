#!/usr/bin/env python3

from atlas import Atlas
import json
import argparse

username = ''
password = ''
api_url = ''

parser = argparse.ArgumentParser()

parser.add_argument("--email")
parser.add_argument("--password")
parser.add_argument("--ip")
parser.add_argument("--domain")
parser.add_argument("--domains")
parser.add_argument("--username")
parser.add_argument("--debug", default=False)

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


def pretty_format(results, format_type):
	if format_type == "per_breach":
		for hit in results["hits"]["hits"]:
			breach_name = hit["_index"]
			breach_data = hit["_source"]

			print("\n# %s" % (breach_name))

			for key in breach_data:
				if key != "":
					print("%s: %s" % (key, str(breach_data[key]).strip()))
	elif format_type == "just_emails":
		for hit in results["hits"]["hits"]:
			email = hit["_source"]["emailAddress"]
			breach = hit["_index"]
			print("%s: %s" % (breach, email))


init_atlas(debug=args.debug)

if args.email:
	print("[*] Searching Atlas for %s" % args.email.strip())
	results = atlas.search_email_addresses(email_address=args.email, size=100)
	pretty_format(results, "per_breach")
elif args.domains:
	domains = args.domains.split(",")

	print("[*] Searching Atlas for %i domains" % len(domains))
	for domain in domains:
		domain = '"' + domain + '"'
		results = atlas.search_email_addresses(email_address=domain, size=100)
		pretty_format(results, "per_breach")
elif args.domain:
	domain = args.domain
	print("[*] Searching Atlas for %s" % domain)
	domain = '"' + domain + '"'
	results = atlas.search_email_addresses(email_address=domain, size=100)
	pretty_format(results, "per_breach")
elif args.password:
	print("[*] Searching Atlas for emails using the password: %s" % args.password.strip())
	results = atlas.search_passwords(password=args.password, size=100)
	pretty_format(results, "just_emails")

