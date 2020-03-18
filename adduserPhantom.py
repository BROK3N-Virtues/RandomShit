import urllib3
import requests
import re
from collections import OrderedDict
from bs4 import BeautifulSoup
import json
import sys
import getopt
import array

#Disable https certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#initial variables
username = "admin"
password = "password1"
newuser = "whitecelladmin"
newpass = "white"
targetfile = ""
phantom_url = ""

headers = OrderedDict()
headers['Host'] =  phantom_url
headers['User-Agent'] = "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0" 
headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
headers['Accept-Language'] = "en-US,en;q=0.5"
headers['Accept-Encoding'] = "gzip, deflate"
headers['Connection'] = "close"
headers['Upgrade-Insecure-Requests'] = "1"


#cookies = OrderedDict()
def usage():
    print "Phantom User Add"
    print
    print "Usage: python addPhantomUser.py"
    print "-t --target  - target web server"
    print "-i --targetfile - target input file"
    print "-u --newuser - user to add to phantom"
    print "-p --newpass - password for new user"
    print "-a --admin - admin username"
    print "-c --cred - admin creds"
    sys.exit(0)


def adduser():
    global username
    global password
    global newuser
    global newpass
    global targetfile
    global phantom_url

    csrftoken = ""
    csrfmiddlewaretoken = ""
    cookies = OrderedDict()
    loginheaders = OrderedDict()
    new_user_data = OrderedDict()
    newuserheaders = OrderedDict()
    login_url = "https://" + phantom_url + "/login?next=/"
    actual_login_url = "https://" + phantom_url + "/login"
    newuser_url = "https://" + phantom_url + "/rest/ph_user"

    headers = OrderedDict()
    headers['Host'] =  phantom_url
    headers['User-Agent'] = "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0" 
    headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    headers['Accept-Language'] = "en-US,en;q=0.5"
    headers['Accept-Encoding'] = "gzip, deflate"
    headers['Connection'] = "close"
    headers['Upgrade-Insecure-Requests'] = "1"
    
    # This request GETs phantom log in page and starts the session. 
    s = requests.Session()
    s.headers.update(headers)
    try:
        login_page_get_request = s.get(login_url, verify=False)
    except requests.exceptions.RequestException as e:
        print e
        return
    for c in login_page_get_request.cookies:
        cookies[c.name] = c.value
        #print "My cookies are: " + c.name + "=" + c.value

    # Below is a bunch of ways to fail to scrape something out with re.search
    # FML I wasted a bunch of time failing to figure it out properly
    # We also need to parse this GET response html and obtain the csrf parameter.
    # csrf is required for POST request later that will actually log us in.
    #result = re.search('(?=value=\')[^\s]*',login_page_get_request.text)
    #result = re.search(r"(?=value=')[^\s]*",login_page_get_request.text)
    #print result
    #cval = result.group(0)
    #print cval[7:-1]

    # Parse the ET respone html to obtain the csrfmiddlewaretoken
    # this token is required for the POST request to login.
    soup = BeautifulSoup(login_page_get_request.text, 'html.parser')
    #print soup.form.input['value']
    csrfmiddlewaretoken = soup.form.input['value']

    # Now let's log in.
    # Data for log in POST
    initial_login_data = OrderedDict()
    initial_login_data['csrfmiddlewaretoken'] = csrfmiddlewaretoken
    initial_login_data['username'] = username
    initial_login_data['password'] = password

    #change our headers for the post parameters
    #without the proper referer the post request will fail
    loginheaders['Host'] =  phantom_url
    loginheaders['User-Agent'] = "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0" 
    loginheaders['Accept'] = "application/json, text/javascript, */*; q=0.01"
    loginheaders['Accept-Language'] = "en-US,en;q=0.5"
    loginheaders['Accept-Encoding'] = "gzip, deflate"
    loginheaders['Referer'] = login_url
    loginheaders['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
    loginheaders['X-Requested-With'] = "XMLHttpRequest"
    loginheaders['Connection'] = "close"
    loginheaders['Upgrade-Insecure-Requests'] = "1"

    # Log in POST request is here
    login_page_post_request = s.post(actual_login_url, data=initial_login_data, headers=loginheaders, cookies=cookies)
    for c in login_page_post_request.cookies:
        cookies[c.name] = c.value
    #print login_page_post_request.text
    csrftoken = cookies['csrftoken']

    new_user_data = OrderedDict()
    new_user_data['username'] = newuser
    new_user_data['password'] = newpass
    new_user_data['first_name']= "WhiteCell"
    new_user_data['last_name'] = "Administrator"
    new_user_data['time_zone'] = "America/New_York"
    new_user_data['roles'] = ["1"]
    new_user_data['type'] = "normal"
    new_user_data['prevent_login'] = "false"

    newuserheaders['Host'] =  phantom_url
    newuserheaders['User-Agent'] = "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0" 
    newuserheaders['Accept'] = "application/json, text/plain, */*"
    newuserheaders['Accept-Language'] = "en-US,en;q=0.5"
    newuserheaders['Accept-Encoding'] = "gzip, deflate"
    newuserheaders['Referer'] = "https://" + phantom_url + "/admin/users"
    newuserheaders['Cache-Control'] = "no-cache, no-store, must-revalidate"
    newuserheaders['Content-Type'] = "application/json"
    newuserheaders['X-CSRFToken'] = csrftoken
    newuserheaders['Connection'] = "close"

    #print json.dumps(new_user_data)
    add_user_post_request = s.post(newuser_url, data=json.dumps(new_user_data), headers=newuserheaders, cookies=cookies)
    #print add_user_post_request
    #print add_user_post_request.text
    #soup2 = BeautifulSoup(add_user_post_request.text, 'html.parser')
    #authresult = soup2.failed
    #print json.loads(str(soup.text))
    #print(soup2.prettify())
    result2 = re.search(r"authentication failure",add_user_post_request.text)
    if result2:
        print "Login has failed"
        return
    else:
        print "You may now login to " + phantom_url + " with the username " + newuser + " and password " + newpass + "."

def main():
    global newuser
    global newpass
    global username
    global password
    global targetfile
    global phantom_url
    
    ips = []
    test = ""

    #Print usage if no arguments provided
    if not len(sys.argv[1:]):
        usage()

    # Read the commandline options
    try:
        opts, args = getopt.getopt(sys.argv[1:],"ht:i:u:p:a:c:", ["help","target","targetfile","newuser","newpass","admin","cred"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    # Actions based on option selected
    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-t","--target"):
            ips.append(a)
        elif o in ("-i","--targetfile"):
            for line in open(a).readlines():
                ips.append(line.rstrip())
        elif o in ("-u","--newuser"):
            newuser = a
        elif o in ("-p","--newpass"):
            newpass = a
        elif o in ("-a","--admin"):
            username = a
        elif o in ("-c","--cred"):
            password = a
        else:
                assert False,"Unhandled, Option"
   
    # Call the add user function for each IP address
    for ip in ips:
        phantom_url = ip
        adduser()

main()
