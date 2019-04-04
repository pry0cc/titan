#!/usr/bin/env python3

from atlas import Atlas
import json
import click

username = ''
password = ''
api_url = ''


def init_atlas(debug=False):
    global atlas, username, password, api_url
    load_credentials()
    atlas = Atlas(username, password, api_url, verify_credentials=False, debug=debug)


@click.group()
def entry_point():
    pass


@click.command()
@click.option('--count', default=100, help='The maximum amount of records to return')
@click.option('--verbose', is_flag=True)
@click.argument('email')
def search_email(email, count, verbose):
    """Search for email addresses matching the given input"""

    init_atlas(debug=verbose)
    results = atlas.search_email_addresses(email_address=email, size=count)
    print(results)


@click.option('--file', default="credentials.json", help="The file path to credentials.json")
def load_credentials(file='credentials.json'):
    global data, username, password, api_url
    with open(file, 'r') as f:
        data = json.load(f)
        username = data['username']
        password = data['password']
        api_url = data['api']


entry_point.add_command(search_email)

if __name__ == '__main__':
    entry_point()
