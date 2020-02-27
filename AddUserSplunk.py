import urllib2
import requests
import re
from collections import OrderedDict

#initial variables
username = "admin"
password = "changeme"
return_to = "/en-US/"
set_has_logged_in = "false"

splunk_url = "http://192.168.177.129:8000"
login_url = splunk_url + "/en-US/account/login"


headers = OrderedDict()
headers['Host'] =  splunk_url
headers['User-Agent'] = "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0" 
headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
headers['Accept-Language'] = "en-US,en;q=0.5"
headers['Accept-Encoding'] = "gzip, deflate"
headers['Connection'] = "close"
headers['Upgrade-Insecure-Requests'] = "1"


cookies = OrderedDict()
# This request GETs Splunk log in page and starts the session. 
s = requests.Session()
s.headers.update(headers)
login_page_get_request = s.get(login_url)
for c in login_page_get_request.cookies:
    cookies[c.name] = c.value

# We also need to parse this GET response html and obtain the cval parameter.
# cval is required for POST request later that will actually log us in.
result = re.search('"cval":(.*),"time":', login_page_get_request.text)
cval = result.group(1)

# Now let's log in.

# Data for log in POST
initial_login_data = OrderedDict()
initial_login_data['cval'] = cval
initial_login_data['username'] = username
initial_login_data['password'] = password
initial_login_data['return_to'] = return_to
initial_login_data['set_has_logged_in'] = set_has_logged_in

# Log in POST request is here
login_page_post_request = s.post(login_url, data=initial_login_data, headers= headers, cookies= cookies)
for c in login_page_post_request.cookies:
    cookies[c.name] = c.value

new_user_data = OrderedDict()
new_user_data['output_mode'] = "json"
new_user_data['force-change-pass'] = "0"
new_user_data['defaultApp']= "launcher"
new_user_data['roles'] = "admin"
new_user_data['password'] = "brok3ntest"
new_user_data['name'] = "ISSM_whitecell5"

headers2 = OrderedDict()
headers2['Host'] =  splunk_url
headers2['User-Agent'] = "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0" 
headers2['Accept'] = "text/javascript, text/html, application/xml, text/xml, */*"
headers2['Accept-Language'] = "en-US,en;q=0.5"
headers2['Accept-Encoding'] = "gzip, deflate"
headers2['X-Splunk-Form-Key'] = cookies['splunkweb_csrf_token_8000']
headers2['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
headers2['X-Requested-With'] = "XMLHttpRequest"
headers2['Connection'] = "close"

user_mgmt_url = splunk_url + "/en-US/splunkd/__raw/servicesNS/nobody/search/authentication/users"
add_user_post_request = s.post(user_mgmt_url, data=new_user_data, headers= headers2, cookies=cookies)
