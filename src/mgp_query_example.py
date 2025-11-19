#!/usr/bin/env python3

import requests
import json
import sys

from getpass import getpass

PROTOCOL = "https"
HOSTNAME = "mathgenealogy.org"
PORT = "8000"

# Function to prompt on the console for the user's
# email address and password to use to log in to
# the MGP API. Password is not shown on console
# while the user types it.
def getlogin():
    print("Enter email used for MGP authentication:",end=" ",file=sys.stderr)
    email = input()
    password = getpass()
    return {'email': email, 'password': password}

# Function to log in to the MGP API and get a JWT for authentication.
# authdata is a dict with key email set to the user's email address
# and key password set to the user's password.
# If login is successful, returns a JSON object with key token set
# to the JWT.
# If login is unsuccessful, raises RuntimeError.
def login(authdata):
    r = requests.post(f"{PROTOCOL}://{HOSTNAME}:{PORT}/login", authdata)
    if r.ok:
        r.close()
        return r.json()
    else:
        r.close()
        raise RuntimeError("Failed to authenticate")

# Function to do a query against the MGP API. Returns a string with
# the query result if the query was successfully executed. Raises
# RuntimeError if there is an error.

# endpoint is a string (beginning with /) such as "/api/v2/MGP/acad"
# referring to an API endpoint

# token is a dict with key token containing a JWT.
# The return value from login() is the best way to get this.

# params is a dict structured to contain the GET parameters.
# For example, if quering /api/v2/MGP/acad, params could be
# {'id': '1969'}. 
def doquery(endpoint,token,params):
    headers = {'x-access-token': token['token']}
    r = requests.get(f"{PROTOCOL}://{HOSTNAME}:{PORT}{endpoint}",headers = headers, params = params)
    if r.ok:
        r.close()
        return r.text
    else:
        r.close()
        raise RuntimeError("Error executing query")


# User modifications can be made here in this portion of the script.
# This is what is run when calling ./mgp.py on the command line.
# Alternatively, import the functions above into your own python
# script and write code similar to what is given here as the example.
if __name__ == '__main__':
    authdata = getlogin()
    token = login(authdata)

    # Example for results coming back as JSON
    querydata = {'id': '1969'}
    endpoint = '/api/v2/MGP/acad'
    acad = json.loads(doquery(endpoint,token,querydata))
    print(acad['MGP_academic']['given_name'])

    # Example for calling the search endpoint
    # We do NOT recommend supplying all fields, but the full
    # structure is provided for reference. The example searches
    # only using a family name and given name
    # searchparams = { 'family_name' : family_name,
    #                      'given_name' : given_name,
    #                      'other_names' : other_names,
    #                      'school' : school,
    #                      'year' : year,
    #                      'thesis' : thesis,
    #                      'country' : country,
    #                      'msc' : msc
    #                      }
    searchparams = { 'family_name' : 'Keller',
                         'given_name' : 'M',
                         'format' : 'csv'
                         }
    endpoint = '/api/v2/MGP/search'

    # To get CSV, run the query with searchparams as above
    search_csv = doquery(endpoint,token,searchparams)
    print(search_csv)

    # To just get a list of IDs as JSON, we make a change.
    # The JSON result is the default.
    searchparams['format'] = 'json'
    acad_list = json.loads(doquery(endpoint,token,searchparams))
    # In practice, you would iterate over this list and call /api/v2/MGP/acad
    # to retrieve more information on each individual.
    print(acad_list)
    
    # Example for results coming back as CSV
    querydata = {'id': '1969', 'format': 'CSV', 'window' : '5'}
    endpoint = '/api/v2/MGP/siblings'
    siblings = doquery(endpoint,token,querydata)
    print(siblings)

# Available endpoints:
# /api/v2/MGP/acad - Get info about a specific person (use id parameter)
# /api/v2/MGP/search - Search for people (use family_name, given_name, etc.)
# /api/v2/MGP/siblings - Get academic siblings (use id and window parameters)
    
