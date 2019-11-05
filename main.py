from fastapi import FastAPI, Header
import requests
from requests_ntlm import HttpNtlmAuth
import urllib.parse
import random, string


# Creating a class for Authentication
class UserAuthentication:

    def __init__(self, username, password, domain, site_url):
        self.__username = username
        self.__password = password
        self.__domain = domain
        self.__site_url = site_url
        self.__ntlm_auth = None

    def sharepoint_get_request(self, endpoint_uri):
        headers = {
            'accept': 'application/json;odata=verbose',
            'content-type': 'application/json;odata=verbose',
            'odata': 'verbose',
            'X-RequestForceAuthentication': 'true'
        }
        url = urllib.parse.urljoin(self.__site_url, endpoint_uri)
        result = requests.get(url, auth=self.__ntlm_auth, headers=headers, verify=False)
        return result

    def authenticate(self):
        login_user = self.__domain + "\\" + self.__username  # username example: winntdomain/dibyaranjan
        user_auth = HttpNtlmAuth(login_user, self.__password)
        self.__ntlm_auth = user_auth

        # Create header for the http request
        my_headers = {
            'accept': 'application/json;odata=verbose',
            'content-type': 'application/json;odata=verbose',
            'odata': 'verbose',
            'X-RequestForceAuthentication': 'true'
        }

        # Sending http get request to the sharepoint site
        result = requests.get(self.__site_url, auth=user_auth, headers=my_headers, verify=False)
        # Requests ignore verifying the SSL certificates if you set verify to False

        # Checking the status code of the requests
        if result.status_code == requests.codes.ok:  # Value of requests.codes.ok is 200
            return True
        else:
            result.raise_for_status()


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/batteryitems/")
def read_item(*, username: str = Header(None),
              password: str = Header(None),
              domain: str = Header(None),
              site_url: str = Header(None),
              endpoint_uri: str = Header(None),
              is_check_query: str = Header(None),
              filter: str = Header(None),
              battery_serial: str = Header(None)):
    auth_object = UserAuthentication(username, password, domain, site_url)
    result = auth_object.authenticate()

    ActivationCode = ''.join(random.choices(string.digits, k=10))
    # We want to extract all the list presents in the site
    if result:  # login successfully
        if is_check_query == '1':
            endpoint_uri += filter
            result = auth_object.sharepoint_get_request(endpoint_uri)
            if result.status_code == requests.codes.ok:
                if len(result.json()['d']['results']) == 0:
                    return {"status": 404, "error_type": "no such item", "error_result": "no result"}
                if is_check_query == '1':
                    json_result = result.json()['d']['results'][0]
                    ActivationCode = ''.join(random.choices(string.digits, k=10))
                    if json_result['isActive'] != "1":
                        return {"status": 200, "item": json_result, "ActivationCode": ActivationCode}
                    return {"status": 200, "item": json_result}
            return {"status": result.status_code, "error_type": "no such item", "error_result": "no result"}
        return json_result


@app.get("/batteryitems/mybatteries")
def find_batteries(*, username: str = Header(None),
                   password: str = Header(None),
                   domain: str = Header(None),
                   site_url: str = Header(None),
                   endpoint_uri: str = Header(None),
                   is_check_query: str = Header(None),
                   phone_number: str = Header(None)):
    auth_object = UserAuthentication(username, password, domain, site_url)
    result = auth_object.authenticate()

    items = []
    # We want to extract all the list presents in the site
    if result:  # login successfully
        result = auth_object.sharepoint_get_request(endpoint_uri)
        if result.status_code == requests.codes.ok:
            json_result = result.json()['d']['results']
            if is_check_query == '1':
                for element in json_result:
                    if element['ActivatorTelId'] == phone_number:
                        items.append(element)
                return {"status": 200, "item": items}
            return json_result
        else:
            return {"status": "error on items", "error_type": "no items in list", "error_result": result}
    else:  # login unsuccessfully
        return {"status": "error on auth", "error_type": "failed auth", "error_result": result}


@app.get("/batteryitems/update/")
def update_item(*, username: str = Header(None),
                password: str = Header(None),
                site_url: str = Header(None),
                endpoint_uri: str = Header(None),
                item_id: str = Header(None),
                is_active: str = Header(None),
                activator_tel: str = Header(None),
                activation_date: str = Header(None),
                activation_history: str = Header(None),
                activation_code: str = Header(None),
                metadata_type: str = Header(None)):
    sharepoint_contextinfo_url = site_url + '_api/contextinfo'

    headers = {
        "Accept": "application/json; odata=verbose",
        "Content-Type": "application/json; odata=verbose",
        "odata": "verbose",
        "X-RequestForceAuthentication": "true"
    }

    auth = HttpNtlmAuth(username, password)

    # First of all get the context info
    r = requests.post(sharepoint_contextinfo_url, auth=auth, headers=headers, verify=False)
    form_digest_value = r.json()['d']['GetContextWebInformation']['FormDigestValue']

    api_page = site_url + endpoint_uri + "GetItemById(%s)" % item_id
    update_headers = {
        "Accept": "application/json; odata=verbose",
        "Content-Type": "application/json; odata=verbose",
        "odata": "verbose",
        "X-RequestForceAuthentication": "true",
        "X-RequestDigest": form_digest_value,
        "IF-MATCH": "*",
        "X-HTTP-Method": "MERGE"
    }

    ActivationCode = ''.join(random.choices(string.digits, k=10))

    payload = {"isActive": is_active,
               "ActivationDate": activation_date,
               "ActivatorTelId": activator_tel,
               "ActivationType": "اپلیکیشن",
               "ActivationCode": ActivationCode,
               "ActivationHistory": activation_history,
               "__metadata": {"type": metadata_type}
               }

    r = requests.post(api_page, json=payload, auth=auth, headers=update_headers, verify=False)

    return {"status": r.status_code}


@app.get("/batteryitems/update/new_battery")
def update_item(*, username: str = Header(None),
                password: str = Header(None),
                site_url: str = Header(None),
                endpoint_uri: str = Header(None),
                packing_date: str = Header(None),
                gurranty_end_date: str = Header(None),
                battery_serial: str = Header(None)):
    sharepoint_contextinfo_url = site_url + '_api/contextinfo'

    headers = {
        "Accept": "application/json; odata=verbose",
        "Content-Type": "application/json; odata=verbose",
        "odata": "verbose",
        "X-RequestForceAuthentication": "true"
    }

    auth = HttpNtlmAuth(username, password)

    # First of all get the context info
    r = requests.post(sharepoint_contextinfo_url, auth=auth, headers=headers, verify=False)
    form_digest_value = r.json()['d']['GetContextWebInformation']['FormDigestValue']

    api_page = site_url + endpoint_uri

    update_headers = {
        "Accept": "application/json; odata=verbose",
        "Content-Type": "application/json; odata=verbose",
        "odata": "verbose",
        "X-RequestForceAuthentication": "true",
        "X-RequestDigest": form_digest_value,
        # "IF-MATCH": "*",
        # "X-HTTP-Method": "MERGE"
    }

    payload = {'__metadata': {'type': 'SP.Data.BatteryListTestListItem'},
               'BatterySerial': battery_serial,
               'PackingDate': packing_date,
               'GurrantyEndDate': gurranty_end_date,
               'Title': 'New Item by Application'}

    r = requests.post(api_page, json=payload, auth=auth, headers=update_headers, verify=False)
    ActivationCode = ''.join(random.choices(string.digits, k=10))

    return {"status": r.status_code, "ActivationCode": ActivationCode, "item": r.json()['d']}


@app.get("/batteryitems/agents_sales")
def read_agents_sales_requests(*,
                               username: str = Header(None),
                               password: str = Header(None),
                               domain: str = Header(None),
                               site_url: str = Header(None),
                               endpoint_uri: str = Header(None),
                               filter: str = Header(None)):
    auth_object = UserAuthentication(username, password, domain, site_url)
    result = auth_object.authenticate()
    sharepoint_contextinfo_url = site_url + '/_api/contextinfo'

    auth = HttpNtlmAuth(username, password)

    headers = {
        "Accept": "application/json; odata=verbose",
        "Content-Type": "application/json; odata=verbose",
        "odata": "verbose",
        "X-RequestForceAuthentication": "true"
    }

    # First of all get the context info
    r = requests.post(sharepoint_contextinfo_url, auth=auth, headers=headers, verify=False)

    form_digest_value = r.json()['d']['GetContextWebInformation']['FormDigestValue']

    # We want to extract all the list presents in the site
    endpoint_uri = "_api/web/lists/getbytitle('SalesHeader')/items"
    if result:  # login successfully
        result = auth_object.sharepoint_get_request(endpoint_uri)
        if result.status_code == requests.codes.ok:
            if len(result.json()['d']['results']) == 0:
                return {"status": 404, "error_type": "no such item", "error_result": "no result"}
            if filter == None:
                json_result = result.json()['d']['results']
                return {"status": 200, "item": json_result}
            else:
                result = auth_object.sharepoint_get_request(endpoint_uri + "?" + filter)
                if len(result.json()['d']['results']) == 0:
                    return {"status": 404, "error_type": "no such item", "error_result": "no result"}
                json_result = result.json()['d']['results']
                return {"status": 200, "item": json_result}

        return {"status": result.status_code, "error_type": "no such item", "error_result": "no result"}
    else:
        return result


@app.get("/batteryitems/agents_check")
def read_agents_usernames(*,
                               username: str = Header(None),
                               password: str = Header(None),
                               domain: str = Header(None),
                               site_url: str = Header(None)):
    auth_object = UserAuthentication(username, password, domain, site_url)
    result = auth_object.authenticate()
    sharepoint_contextinfo_url = site_url + '/_api/contextinfo'

    auth = HttpNtlmAuth(username, password)

    headers = {
        "Accept": "application/json; odata=verbose",
        "Content-Type": "application/json; odata=verbose",
        "odata": "verbose",
        "X-RequestForceAuthentication": "true"
    }

    # First of all get the context info
    r = requests.post(sharepoint_contextinfo_url, auth=auth, headers=headers, verify=False)

    form_digest_value = r.json()['d']['GetContextWebInformation']['FormDigestValue']

    # We want to extract all the list presents in the site
    endpoint_uri = "/_api/web/currentUser"
    if result:  # login successfully
        result = auth_object.sharepoint_get_request(endpoint_uri)
        if result.status_code == requests.codes.ok:
            json_result = result.json()['d']
            return {"status": 200, "item": json_result}
        return {"status": result.status_code, "error_type": "no such item", "error_result": "no result"}
    else:
        return {"status": "fail", "result": result}


@app.get("/batteryitems/agents_sales_request")
def read_agents_sales_requests(*,
                               username: str = Header(None),
                               password: str = Header(None),
                               domain: str = Header(None),
                               site_url: str = Header(None),
                               endpoint_uri: str = Header(None)):
    sharepoint_contextinfo_url = site_url + '_api/contextinfo'

    headers = {
        "Accept": "application/json; odata=verbose",
        "Content-Type": "application/json; odata=verbose",
        "odata": "verbose",
        "X-RequestForceAuthentication": "true"
    }

    auth = HttpNtlmAuth(username, password)

    # First of all get the context info
    r = requests.post(sharepoint_contextinfo_url, auth=auth, headers=headers, verify=False)
    form_digest_value = r.json()['d']['GetContextWebInformation']['FormDigestValue']

    api_page = site_url + endpoint_uri

    update_headers = {
        "Accept": "application/json; odata=verbose",
        "Content-Type": "application/json; odata=verbose",
        "odata": "verbose",
        "X-RequestForceAuthentication": "true",
        "X-RequestDigest": form_digest_value,
        # "IF-MATCH": "*",
        # "X-HTTP-Method": "MERGE"
    }

    payload = {'__metadata': {'type': 'SP.Data.BatteryListTestListItem'},
               'BatterySerial': battery_serial,
               'PackingDate': packing_date,
               'GurrantyEndDate': gurranty_end_date,
               'Title': 'New Item by Application'}

    r = requests.post(api_page, json=payload, auth=auth, headers=update_headers, verify=False)
    ActivationCode = ''.join(random.choices(string.digits, k=10))

    return {"status": r.status_code, "ActivationCode": ActivationCode, "item": r.json()['d']}
