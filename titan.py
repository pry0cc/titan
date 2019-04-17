#!/usr/bin/env python3

from atlas import Atlas
import json
import argparse
import sys
import crayons
import os

username = ''
password = ''
api_url = ''

parser = argparse.ArgumentParser(description='Titan is a query program for querying an ELK stack with for password dumps and breach data.')

parser.add_argument("--email")
parser.add_argument("--password")
parser.add_argument("--ip")
parser.add_argument("--format")
parser.add_argument("--domain")
parser.add_argument("--domains")
parser.add_argument("--username")
parser.add_argument("--size")
parser.add_argument("--output")
parser.add_argument("--provision")
parser.add_argument("--debug", default=False)

parser.parse_args()
args = parser.parse_args()

def load_credentials(files=['credentials.json','~/.titan']):
	global data, username, password, api_url
	loaded = False
	for file in files:
		if os.path.isfile(os.path.expanduser(file)):
			try:
				with open(os.path.expanduser(file), 'r') as f:
					data = json.load(f)
					username = data['username']
					password = data['password']
					api_url = data['api']
					loaded = True
			except:
				print(crayons.red("[-] Something went terribly wrong while attempting to read config, do you have a config?"))
	if not loaded:
		print(crayons.red("[-] No config file detected, please make one before proceeding"))
		sys.exit()

def init_atlas(debug=False):
	global atlas, username, password, api_url
	load_credentials()
	atlas = Atlas(username, password, api_url, verify_credentials=False, debug=debug)


def format_data(results, format_type):
	if format_type == "per_breach":
		for hit in results["hits"]["hits"]:
			breach_name = hit["_index"]
			breach_data = hit["_source"]

			print(crayons.red("\n# %s" % (breach_name)))

			for key in breach_data:
				if key != "":
					print("%s: %s" % (key, str(breach_data[key]).strip()))
	elif format_type == "just_emails":
		for hit in results["hits"]["hits"]:
			if "emailAddress" in hit["_source"]:
				email = hit["_source"]["emailAddress"]
			else:
				email = hit["_source"]["username"]
			breach = hit["_index"]
			print("%s: %s" % (breach, email))
	elif format_type == "json":
		for hit in results["hits"]["hits"]:
			breach_name = hit["_index"]
			data = hit["_source"]
			data["breach"] = breach_name
			print(data)
	elif format_type == "unique_json":
		data = {}
		for hit in results["hits"]["hits"]:
			breach_data = hit["_source"]

			for key in breach_data:
				if key != "":
					if not key in data:
						data[key] = breach_data[key]
					else:
						if data[key] != breach_data[key] and not isinstance(data[key], list):
							temp = data[key]
							data[key] = [temp, breach_data[key]]
						elif data[key] != breach_data[key] and isinstance(data[key], list):
							if not breach_data[key] in data[key]:
								data[key].append(breach_data[key])

		print(data)
	elif format_type == "unique":
		data = {}
		for hit in results["hits"]["hits"]:
			breach_data = hit["_source"]

			for key in breach_data:
				if key != "":
					if not key in data:
						data[key] = breach_data[key]
					else:
						if data[key] != breach_data[key] and not isinstance(data[key], list):
							temp = data[key]
							data[key] = [temp, breach_data[key]]
						elif data[key] != breach_data[key] and isinstance(data[key], list):
							if not breach_data[key] in data[key]:
								data[key].append(breach_data[key])

		print("")
		for key in data:
			if data[key] != "":
				print("%s: %s" % (key, str(data[key]).strip()))

def save_data(results, format_type):
	output = ""
	if format_type == "per_breach":
		for hit in results["hits"]["hits"]:
			breach_name = hit["_index"]
			breach_data = hit["_source"]

			output += "\n# %s\n" % (breach_name)

			for key in breach_data:
				if key != "":
					output += "%s: %s\n" % (key, str(breach_data[key]).strip())
	elif format_type == "just_emails":
		for hit in results["hits"]["hits"]:
			if "emailAddress" in hit["_source"]:
				email = hit["_source"]["emailAddress"]
			else:
				email = hit["_source"]["username"]
			breach = hit["_index"]
			output += "%s: %s\n" % (breach, email)
	elif format_type == "json":
		for hit in results["hits"]["hits"]:
			breach_name = hit["_index"]
			data = hit["_source"]
			data["breach"] = breach_name
			output += json.dumps(data) + "\n"
	elif format_type == "unique_json":
		data = {}
		for hit in results["hits"]["hits"]:
			breach_data = hit["_source"]

			for key in breach_data:
				if key != "":
					if not key in data:
						data[key] = breach_data[key]
					else:
						if data[key] != breach_data[key] and not isinstance(data[key], list):
							temp = data[key]
							data[key] = [temp, breach_data[key]]
						elif data[key] != breach_data[key] and isinstance(data[key], list):
							if not breach_data[key] in data[key]:
								data[key].append(breach_data[key])

		output += json.dumps(data) + "\n"
	elif format_type == "unique":
		data = {}
		for hit in results["hits"]["hits"]:
			breach_data = hit["_source"]

			for key in breach_data:
				if key != "":
					if not key in data:
						data[key] = breach_data[key]
					else:
						if data[key] != breach_data[key] and not isinstance(data[key], list):
							temp = data[key]
							data[key] = [temp, breach_data[key]]
						elif data[key] != breach_data[key] and isinstance(data[key], list):
							if not breach_data[key] in data[key]:
								data[key].append(breach_data[key])

		output += "\n"
		for key in data:
			if data[key] != "":
				output += "%s: %s\n" % (key, str(data[key]).strip())

	return output

init_atlas(debug=args.debug)

if args.email:
	print(crayons.blue("[*] Searching Atlas for %s" % args.email.strip()))
	results = atlas.search_email_addresses(email_address=args.email, size=100)

	data = ""

	if args.output:
		if args.format:
			data = save_data(results, args.format)
		else:
			data = save_data(results, "per_breach")

		f = open(args.output, "w+")
		for line in data:
			f.write(line)
		f.close()
		print(crayons.blue("[+] File saved to %s" % (args.output)))
	else:
		if args.format:
			format_data(results, args.format)
		else:
			format_data(results, "per_breach")
elif args.domains:
	domains = args.domains.split(",")

	print(crayons.blue("[*] Searching Atlas for %i domains" % len(domains)))
	for domain in domains:
		domain = '"' + domain + '"'
		results = atlas.search_email_addresses(email_address=domain, size=100)

	if args.output:
		data = ""
		if args.format:
			data = save_data(results, args.format)
		else:
			data = save_data(results, "per_breach")

		f = open(args.output, "w+")
		for line in data:
			f.write(line)
		f.close()
		print(crayons.blue("[+] File saved to %s" % (args.output)))
	else:
		if args.format:
			format_data(results, args.format)
		else:
			format_data(results, "per_breach")
elif args.domain:
	domain = args.domain
	print(crayons.blue("[*] Searching Atlas for %s" % domain))
	domain = '"' + domain + '"'
	results = atlas.search_email_addresses(email_address=domain, size=100)

	if args.output:
		data = ""
		if args.format:
			data = save_data(results, args.format)
		else:
			data = save_data(results, "per_breach")

		f = open(args.output, "w+")
		for line in data:
			f.write(line)
		f.close()
		print(crayons.blue("[+] File saved to %s" % (args.output)))
	else:
		if args.format:
			format_data(results, args.format)
		else:
			format_data(results, "per_breach")
elif args.password:
	print(crayons.blue("[*] Searching Atlas for emails using the password: %s" % args.password.strip()))
	results = atlas.search_passwords(password=args.password, size=100)
	
	if args.output:
		data = ""
		if args.format:
			data = save_data(results, args.format)
		else:
			data = save_data(results, "just_email")

		f = open(args.output, "w+")
		for line in data:
			f.write(line)
		f.close()
		print(crayons.blue("[+] File saved to %s" % (args.output)))
	else:
		if args.format:
			format_data(results, args.format)
		else:
			format_data(results, "just_email")
else:
	parser.print_help(sys.stderr)

