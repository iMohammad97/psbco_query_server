import json
import random
import string
import urllib.parse

import requests
from fastapi import FastAPI, Header
from requests_ntlm import HttpNtlmAuth
from starlette.middleware.cors import CORSMiddleware


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

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://5.34.197.188:5000",
    "http://5.34.197.188",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/v1/sendSMS/")
def update_item(*, template: str = Header(None),
                param1: str = Header(None),
                receptor: str = Header(None)):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "apikey": "dOt7P76LO65JfohHNf7oKDv++WWjAHOGAPLRikV7DL8"
    }

    req_url = "https://api.smsapp.ir/v2/send/verify"
    payload = {'type': 1, 'template': template, 'param1': param1, 'receptor': receptor}
    # payload = "type=1¶m1=&receptor=" + str(receptor) + "&template=" + str(template)

    r = requests.post(req_url, headers=headers, data=json.dumps(payload))
    req_response_json = r.json()
    print(req_response_json)

    return {"status": r.status_code, "response": req_response_json}


@app.get("/customerlist/subset")
def read_agents_subsets_list(*,
                             username: str = Header(None),
                             password: str = Header(None),
                             filter: str = Header(None)):
    domain = "psbco.org"
    site_url = "http://sp.psbco.org/"

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
    endpoint_uri = "_api/web/lists/getbytitle('CustomerList')/items" + filter
    if result:  # login successfully
        result = auth_object.sharepoint_get_request(endpoint_uri)
        if result.status_code == requests.codes.ok:
            if len(result.json()['d']['results']) == 0:
                return {"status": 404, "error_type": "no such item", "error_result": "no result"}
            else:
                json_result = result.json()['d']['results']
                return {"status": 200, "count": len(result.json()['d']['results']), "item": json_result}
        return {"status": result.status_code, "error_type": "no such item", "error_result": "no result"}
    else:
        return result


@app.get("/customermidlist/sales")
def read_agents_mid_sales_list(*,
                               username: str = Header(None),
                               password: str = Header(None),
                               filter: str = Header(None)):
    domain = "psbco.org"
    site_url = "http://sp.psbco.org/"

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
    endpoint_uri = "_api/web/lists/getbytitle('CustomerSalesMidList')/items" + filter
    if result:  # login successfully
        result = auth_object.sharepoint_get_request(endpoint_uri)
        if result.status_code == requests.codes.ok:
            if len(result.json()['d']['results']) == 0:
                return {"status": 404, "error_type": "no such item", "error_result": "no result"}
            else:
                json_result = result.json()['d']['results']
                return {"status": 200, "count": len(result.json()['d']['results']), "item": json_result}
        return {"status": result.status_code, "error_type": "no such item", "error_result": "no result"}
    else:
        return result


@app.get("/customermidlist/services")
def read_agents_mid_services_list(*,
                                  username: str = Header(None),
                                  password: str = Header(None),
                                  filter: str = Header(None)):
    domain = "psbco.org"
    site_url = "http://sp.psbco.org/"

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
    endpoint_uri = "_api/web/lists/getbytitle('CustomerReplaceMidList')/items" + filter
    if result:  # login successfully
        result = auth_object.sharepoint_get_request(endpoint_uri)
        if result.status_code == requests.codes.ok:
            if len(result.json()['d']['results']) == 0:
                print(result.json()['d']['results'])
                return {"status": 404, "error_type": "no such item", "error_result": "no result"}
            else:
                json_result = result.json()['d']['results']
                return {"status": 200, "count": len(result.json()['d']['results']), "item": json_result}
        return {"status": result.status_code, "error_type": "no such item", "error_result": "no result"}
    else:
        return result


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
        return result.json


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

    endpoint_uri += "?$select=ActivatorTelId,*&$filter=ActivatorTelId eq " + "'" + phone_number + "'"
    items = []
    # We want to extract all the list presents in the site
    if result:  # login successfully
        result = auth_object.sharepoint_get_request(endpoint_uri)
        if result.status_code == requests.codes.ok:
            json_result = result.json()['d']['results']
            if is_check_query == '1':
                # for element in json_result:
                #     # if element['ActivatorTelId'] == phone_number:
                #     items.append(element)
                return {"status": 200, "item": json_result}
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

    payload = {'__metadata': {'type': 'SP.Data.BatteryListListItem'},
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
                               mode: str = Header(None),
                               item_Id: str = Header(None),
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

    if filter is not None:
        if mode is not None:
            if mode == '1':
                filter = "$select=CustomerName/CustomerName,CustomerID/Name,*&$expand=CustomerName,CustomerID&$orderby=Modified desc&$filter=(CustomerID/ID eq " + item_Id + ")and(Status eq \'اتمام حمل\')"
            elif mode == '2':
                filter = "$select=CustomerName/CustomerName,CustomerID/Name,*&$expand=CustomerName,CustomerID&$orderby=Modified desc&$filter=(CustomerID/ID eq " + item_Id + ")and(Status eq \'در صف تولید\')"
            elif mode == '3':
                filter = "$select=CustomerName/CustomerName,CustomerID/Name,*&$expand=CustomerName,CustomerID&$orderby=Modified desc&$filter=(CustomerID/ID eq " + item_Id + ")and(Status eq \'در انتظار صدور پیش فاکتور\')"
            elif mode == '4':
                filter = "$select=CustomerName/CustomerName,CustomerID/Name,*&$expand=CustomerName,CustomerID&$orderby=Modified desc&$filter=(CustomerID/ID eq " + item_Id + ")and(Status eq \'در انتظار تعیین تاریخ حمل\')"
            elif mode == '5':
                filter = "$select=CustomerName/CustomerName,CustomerID/Name,*&$expand=CustomerName,CustomerID&$orderby=Modified desc&$filter=(CustomerID/ID eq " + item_Id + ")and(Status eq \'در انتظار تایید مالی\')"
            elif mode == '6':
                filter = "$select=CustomerName/CustomerName,CustomerID/Name,*&$expand=CustomerName,CustomerID&$orderby=Modified desc&$filter=(CustomerID/ID eq " + item_Id + ")and(Status eq \'در انتظار تایید پرداخت\')"
            elif mode == '7':
                filter = "$select=CustomerName/CustomerName,CustomerID/Name,*&$expand=CustomerName,CustomerID&$orderby=Modified desc&$filter=(CustomerID/ID eq " + item_Id + ")and(Status eq \'آماده حمل\')"
            elif mode == '8':
                filter = "$select=CustomerName/CustomerName,CustomerID/Name,*&$expand=CustomerName,CustomerID&$orderby=Modified desc&$filter=(CustomerID/ID eq " + item_Id + ")and(Status eq \'در انتظار تایید پیش فاکتور\')"
            elif mode == '0':
                filter = "$select=CustomerName/CustomerName,CustomerID/Name,*&$expand=CustomerName,CustomerID&$orderby=Modified desc&$filter=CustomerID/ID eq " + item_Id

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
                return {"status": 200, "count": len(result.json()['d']['results']), "item": json_result}
            else:
                result = auth_object.sharepoint_get_request(endpoint_uri + "?" + filter)
                if len(result.json()['d']['results']) == 0:
                    return {"status": 404, "error_type": "no such item", "error_result": "no result"}
                json_result = result.json()['d']['results']
                return {"status": 200, "count": len(result.json()['d']['results']), "item": json_result}

        return {"status": result.status_code, "error_type": "no such item", "error_result": "no result"}
    else:
        return result


@app.get("/batteryitems/agents_check")
def read_agents_usernames(*,
                          username: str = Header(None),
                          password: str = Header(None),
                          domain: str = Header(None),
                          site_url: str = Header(None),
                          version_by_pass: str = Header(None)):
    if version_by_pass == 'pass1':
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
                filter_CustomerList = "_api/web/lists/getbytitle('CustomerList')/items?$select=CustomerLoginID/ID,*&$expand=CustomerLoginID&$filter=CustomerLoginID/ID eq " + str(
                    json_result['Id'])
                resultName = auth_object.sharepoint_get_request(filter_CustomerList)
                name_json = ''
                if len(resultName.json()['d']['results']) == 0:
                    name_json = 'nullclient'
                else:
                    name_json = resultName.json()['d']['results'][0]['CustomerName']
                return {"status": 200, "item": json_result, "cliname": name_json,
                        "fullitem": resultName.json()['d']['results'][0]}
            return {"status": result.status_code, "error_type": "no such item", "error_result": "no result"}
        else:
            return {"status": "fail", "result": result}
    else:
        return {"status": "fail", "result": "version_error"}


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

    payload = {'__metadata': {'type': 'SP.Data.BatteryListListItem'},
               'BatterySerial': battery_serial,
               'PackingDate': packing_date,
               'GurrantyEndDate': gurranty_end_date,
               'Title': 'New Item by Application'}

    r = requests.post(api_page, json=payload, auth=auth, headers=update_headers, verify=False)
    ActivationCode = ''.join(random.choices(string.digits, k=10))

    return {"status": r.status_code, "ActivationCode": ActivationCode, "item": r.json()['d']}


@app.get("/batteryitems/agents_sales_details")
def read_agents_sales_requests(*,
                               username: str = Header(None),
                               password: str = Header(None),
                               domain: str = Header(None),
                               site_url: str = Header(None),
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
    endpoint_uri = "_api/web/lists/getbytitle('SalesDetails')/items" + "?" + filter
    if result:  # login successfully
        result = auth_object.sharepoint_get_request(endpoint_uri)
        if result.status_code == requests.codes.ok:
            if len(result.json()['d']['results']) == 0:
                return {"status": 404, "error_type": "no such item", "error_result": "no result"}
            else:
                json_result = result.json()['d']['results']
                return {"status": 200, "item": json_result}
        return {"status": result.status_code, "error_type": "no such item", "error_result": "no result"}
    else:
        return result


@app.get("/batteryitems/agents_services")
def read_agents_services_requests(*,
                                  username: str = Header(None),
                                  password: str = Header(None),
                                  domain: str = Header(None),
                                  site_url: str = Header(None),
                                  mode: str = Header(None),
                                  item_Id: str = Header(None),
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

    if filter is not None:
        if mode is not None:
            if mode == '1':
                filter = "$select=ReplacedBYUserName/ID,ReplacedBYUserName/Title,*&$expand=ReplacedBYUserName&$filter=(ReplacedBYUserName/ID eq " + item_Id + ")and(Status eq \'تایید\')"
            elif mode == '2':
                filter = "$select=ReplacedBYUserName/ID,ReplacedBYUserName/Title,*&$expand=ReplacedBYUserName&$filter=(ReplacedBYUserName/ID eq " + item_Id + ")and(Status eq \'تایید ارفاقی\')"
            elif mode == '3':
                filter = "$select=ReplacedBYUserName/ID,ReplacedBYUserName/Title,*&$expand=ReplacedBYUserName&$filter=(ReplacedBYUserName/ID eq " + item_Id + ")and(Status eq \'تایید شده\')"
            elif mode == '4':
                filter = "$select=ReplacedBYUserName/ID,ReplacedBYUserName/Title,*&$expand=ReplacedBYUserName&$filter=(ReplacedBYUserName/ID eq " + item_Id + ")and(Status eq \'در انتظار ارسال به کارخانه\')"
            elif mode == '5':
                filter = "$select=ReplacedBYUserName/ID,ReplacedBYUserName/Title,*&$expand=ReplacedBYUserName&$filter=(ReplacedBYUserName/ID eq " + item_Id + ")and(Status eq \'در حال بررسی\')"
            elif mode == '6':
                filter = "$select=ReplacedBYUserName/ID,ReplacedBYUserName/Title,*&$expand=ReplacedBYUserName&$filter=(ReplacedBYUserName/ID eq " + item_Id + ")and(Status eq \'در راه کارخانه\')"
            elif mode == '7':
                filter = "$select=ReplacedBYUserName/ID,ReplacedBYUserName/Title,*&$expand=ReplacedBYUserName&$filter=(ReplacedBYUserName/ID eq " + item_Id + ")and(Status eq \'نیاز به شارژ\')"
            elif mode == '0':
                filter = "$select=ReplacedBYUserName/ID,ReplacedBYUserName/Title,*&$expand=ReplacedBYUserName&$filter=ReplacedBYUserName/ID eq " + item_Id

    # First of all get the context info
    r = requests.post(sharepoint_contextinfo_url, auth=auth, headers=headers, verify=False)

    form_digest_value = r.json()['d']['GetContextWebInformation']['FormDigestValue']

    # We want to extract all the list presents in the site
    endpoint_uri = "_api/web/lists/getbytitle('CustomerGurrantyRequest')/items"
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


@app.get("/batteryitems/agents_services_details")
def read_agents_sales_requests(*,
                               username: str = Header(None),
                               password: str = Header(None),
                               domain: str = Header(None),
                               site_url: str = Header(None),
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
    endpoint_uri = "_api/web/lists/getbytitle('CustomerGurrantyRequest')/items" + "?" + "$select=DeffectedBatterySerial/BatterySerial,ReplaceBatterySerial/BatterySerial,ReplaceOstan/Title0,ReplaceShahr/Title0,*&$expand=DeffectedBatterySerial,ReplaceOstan,ReplaceShahr,ReplaceBatterySerial"
    endpoint_uri = endpoint_uri + filter
    if result:  # login successfully
        result = auth_object.sharepoint_get_request(endpoint_uri)
        if result.status_code == requests.codes.ok:
            if len(result.json()['d']['results']) == 0:
                return {"status": 404, "error_type": "no such item", "error_result": "no result"}
            else:
                json_result = result.json()['d']['results']
                return {"status": 200, "item": json_result}
        return {"status": result.status_code, "error_type": "no such item", "error_result": "no result"}
    else:
        return result


@app.get("/batteryitems/multi_query")
def read_item_multi_query(*, username: str = Header(None),
                          password: str = Header(None),
                          domain: str = Header(None),
                          site_url: str = Header(None),
                          endpoint_uri: str = Header(None),
                          is_check_query: str = Header(None),
                          filter: str = Header(None)):
    filter1 = "_api/web/lists/getbytitle('BatteryReplaceReason')/items?$select=ID,ReplaceReason"
    filter2 = "_api/web/lists(guid'ec9e53c8-e181-448c-add2-2c3a6f981866')/items?$select=ID,Title0"
    # filter3 = "_api/web/lists(guid'fb73bd0a-fe5c-46e1-936a-842f916f7cd2')/items?$select=ID,Title0,PK_OstanId&$$expand=PK_Ostan,&$filter=PK_Ostan/ID eq "+

    auth_object = UserAuthentication(username, password, domain, site_url)
    result = auth_object.authenticate()
    return_result = {}

    # We want to extract all the list presents in the site
    if result:  # login successfully
        if is_check_query == '1':
            endpoint_uri_result = endpoint_uri
            endpoint_uri_result += filter
            result = auth_object.sharepoint_get_request(endpoint_uri_result)
            result_ReplaceReason = auth_object.sharepoint_get_request(filter1)
            result_Ostan = auth_object.sharepoint_get_request(filter2)
            result_Shahrestan = auth_object.sharepoint_get_request(endpoint_uri)
            if result.status_code == requests.codes.ok:
                if len(result.json()['d']['results']) == 0:
                    return_result = {"status": 404, "error_type": "no such item", "error_result": "no result"}
                if is_check_query == '1':
                    json_result = result.json()['d']['results'][0]
                    json_result1 = result_ReplaceReason.json()['d']['results']
                    json_result2 = result_Ostan.json()['d']['results']
                    ActivationCode = ''.join(random.choices(string.digits, k=10))
                    if json_result['isActive'] != "1":
                        return_result = {"status": 200,
                                         "item": json_result,
                                         "ActivationCode": ActivationCode,
                                         "replace_reasons": json_result1,
                                         "ostans": json_result2}
                    return_result = {"status": 200,
                                     "item": json_result,
                                     "replace_reasons": json_result1,
                                     "ostans": json_result2}
            else:
                return_result = {"status": result.status_code, "error_type": "no such item",
                                 "error_result": "no result"}
    return return_result


@app.get("/batteryitems/city_query")
def read_item_multi_query(*, username: str = Header(None),
                          password: str = Header(None),
                          domain: str = Header(None),
                          site_url: str = Header(None),
                          ostan_id: str = Header(None)):
    filter3 = "_api/web/lists(guid'fb73bd0a-fe5c-46e1-936a-842f916f7cd2')/items?$select=ID,Title0,PK_OstanId&$$expand=PK_Ostan,&$filter=PK_Ostan/ID eq "

    auth_object = UserAuthentication(username, password, domain, site_url)
    result = auth_object.authenticate()
    return_result = {}
    # We want to extract all the list presents in the site
    if result:  # login successfully
        result = auth_object.sharepoint_get_request(filter3 + ostan_id)
        if result.status_code == requests.codes.ok:
            result = result.json()['d']['results']
            return_result = {"status": 200,
                             "item": result}
        else:
            return_result = {"status": result.status_code, "error_type": "no such item",
                             "error_result": "no result"}
    return return_result


@app.get("/batteryitems/update/new_service")
def update_item(*, username: str = Header(None),
                password: str = Header(None),
                site_url: str = Header(None),
                endpoint_uri: str = Header(None),
                replace_ostan_id: str = Header(None),
                replace_shahr_id: str = Header(None),
                replace_reason_id: str = Header(None),
                sales_date: str = Header(None),
                replace_date: str = Header(None),
                indicator_status: str = Header(None),
                app_status: str = Header(None),
                first_voltage: str = Header(None),
                second_voltage: str = Header(None),
                replace_by_id: str = Header(None),
                deffected_battery_serial_id: str = Header(None),
                replace_battery_serial_id: str = Header(None),
                replaced_by_username_id: str = Header(None)):
    sharepoint_contextinfo_url = site_url + '_api/contextinfo'

    filter_CustomerList = "_api/web/lists/getbytitle('CustomerList')/items?$select=CustomerLoginID/ID,*&$expand=CustomerLoginID&$filter=CustomerLoginID/ID eq " + replace_by_id

    auth_object = UserAuthentication(username, password, 'psbco.org', site_url)
    result = auth_object.authenticate()
    return_result = {}

    # get user's id in CustomerList
    customer_result = auth_object.sharepoint_get_request(filter_CustomerList)

    idd = customer_result.json()['d']['results'][0]['ID']

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

    payload = {'__metadata': {'type': 'SP.Data.CustomerGurrantyRequestListItem'},
               'ReplaceOstanId': replace_ostan_id,
               'ReplaceShahrId': replace_shahr_id,
               'ReplaceReasonId': replace_reason_id,
               'SalesDate': sales_date,
               'ReplaceDate': replace_date,
               'ReplaceById': idd,
               'AppStatus': app_status,
               'AppIndicator': indicator_status,
               'OData__x0031_stVoltage': first_voltage,
               'OData__x0032_ndVoltage': second_voltage,
               'DeffectedBatterySerialId': deffected_battery_serial_id,
               'ReplaceBatterySerialId': replace_battery_serial_id,
               'ReplacedBYUserNameId': replaced_by_username_id,
               'SubmitBy': 'PWA'}

    r = requests.post(api_page, json=payload, auth=auth, headers=update_headers, verify=False)
    ActivationCode = ''.join(random.choices(string.digits, k=10))

    return {"status": r.status_code, "ActivationCode": ActivationCode, "item": r.json()}


@app.get("/batteryitems/provinces_query")
def read_item_multi_query(*, username: str = Header(None),
                          password: str = Header(None),
                          domain: str = Header(None),
                          site_url: str = Header(None),
                          endpoint_uri: str = Header(None),
                          is_check_query: str = Header(None),
                          filter: str = Header(None)):
    filter2 = "_api/web/lists(guid'ec9e53c8-e181-448c-add2-2c3a6f981866')/items?$select=ID,Title0"

    auth_object = UserAuthentication(username, password, domain, site_url)
    result = auth_object.authenticate()
    return_result = {}

    # We want to extract all the list presents in the site
    if result:  # login successfully
        if is_check_query == '1':
            provinces_result = auth_object.sharepoint_get_request(filter2)
            if provinces_result.status_code == requests.codes.ok:
                if len(provinces_result.json()['d']['results']) == 0:
                    return_result = {"status": 404, "error_type": "no such item", "error_result": "no result"}
                if is_check_query == '1':
                    json_result2 = provinces_result.json()['d']['results']
                    return_result = {"status": 200,
                                     "provinces": json_result2}
            else:
                return_result = {"status": result.status_code, "error_type": "no such item",
                                 "error_result": "no result"}
    return return_result


@app.get("/batteryitems/provinces_query")
def read_item_multi_query(*, username: str = Header(None),
                          password: str = Header(None),
                          domain: str = Header(None),
                          site_url: str = Header(None),
                          endpoint_uri: str = Header(None),
                          is_check_query: str = Header(None),
                          filter: str = Header(None)):
    filter2 = "_api/web/lists(guid'ec9e53c8-e181-448c-add2-2c3a6f981866')/items?$select=ID,Title0"

    auth_object = UserAuthentication(username, password, domain, site_url)
    result = auth_object.authenticate()
    return_result = {}

    # We want to extract all the list presents in the site
    if result:  # login successfully
        if is_check_query == '1':
            provinces_result = auth_object.sharepoint_get_request(filter2)
            if provinces_result.status_code == requests.codes.ok:
                if len(provinces_result.json()['d']['results']) == 0:
                    return_result = {"status": 404, "error_type": "no such item", "error_result": "no result"}
                if is_check_query == '1':
                    json_result2 = provinces_result.json()['d']['results']
                    return_result = {"status": 200,
                                     "provinces": json_result2}
            else:
                return_result = {"status": result.status_code, "error_type": "no such item",
                                 "error_result": "no result"}
    return return_result


@app.get("/batteryitems/assign_query")
def read_item_multi_query(*, username: str = Header(None),
                          password: str = Header(None),
                          domain: str = Header(None),
                          site_url: str = Header(None),
                          item_id: str = Header(None),
                          filter: str = Header(None)):
    filter2 = "_api/web/lists/getbytitle('CustomerAssignaedQTY')/items?$filter=CustomerName/ID eq "
    filter_CustomerList = "_api/web/lists/getbytitle('CustomerList')/items?$select=CustomerLoginID/ID,*&$expand=CustomerLoginID&$filter=CustomerLoginID/ID eq " + item_id

    auth_object = UserAuthentication(username, password, domain, site_url)
    result = auth_object.authenticate()
    return_result = {}

    # get user's id in CustomerList
    customer_result = auth_object.sharepoint_get_request(filter_CustomerList)

    id = customer_result.json()['d']['results'][0]['ID']

    # We want to extract all the list presents in the site
    if result:  # login successfully
        assign_result = auth_object.sharepoint_get_request(filter2 + str(id))
        if assign_result.status_code == requests.codes.ok:
            if len(assign_result.json()['d']['results']) == 0:
                return_result = {"status": 404, "error_type": "no such item", "error_result": "no result"}
            else:
                json_result2 = assign_result.json()['d']['results']
                return_result = {"status": 200,
                                 "assigns": json_result2}
        else:
            return_result = {"status": id, "error_type": "no such item",
                             "error_result": "no result"}
    return return_result


@app.get("/batteryitems/multi_products_query")
def read_item_multi_query(*, username: str = Header(None),
                          password: str = Header(None),
                          domain: str = Header(None),
                          site_url: str = Header(None)):
    filter1 = "_api/web/lists/getbytitle('productList')/items"
    filter2 = "_api/web/lists/getbytitle('brandList')/items"

    auth_object = UserAuthentication(username, password, domain, site_url)
    result = auth_object.authenticate()
    return_result = {}

    # get user's id in CustomerList
    filter1_result = auth_object.sharepoint_get_request(filter1)
    filter2_result = auth_object.sharepoint_get_request(filter2)

    # id = customer_result.json()['d']['results'][0]['ID']

    # We want to extract all the list presents in the site
    if result:  # login successfully
        if (filter1_result.status_code == requests.codes.ok) and (filter2_result.status_code == requests.codes.ok):
            json_result1 = filter1_result.json()['d']['results']
            json_result2 = filter2_result.json()['d']['results']
            return_result = {"status": 200,
                             "products": json_result1,
                             "brands": json_result2}
        else:
            return_result = {"status": filter1_result.status_code, "error_type": "no such item",
                             "error_result": "no result"}
    return return_result


@app.get("/batteryitems/update/new_sales")
def update_item(*, username: str = Header(None),
                password: str = Header(None),
                site_url: str = Header(None),
                # Header
                status: str = Header(None),
                ship_ostan_id: str = Header(None),
                ship_city_id: str = Header(None),
                ship_address: str = Header(None),
                customer_name_id: str = Header(None),
                assign_id: str = Header(None),
                # Details
                product_name_id: str = Header(None),
                product_brand_id: str = Header(None),
                request_qty: str = Header(None),
                count: str = Header(None),
                deliver_to_customer: str = Header(None)):
    sharepoint_contextinfo_url = site_url + '_api/contextinfo'

    filter_CustomerList = "_api/web/lists/getbytitle('CustomerList')/items?$select=CustomerLoginID/ID,*&$expand=CustomerLoginID&$filter=CustomerLoginID/ID eq " + customer_name_id

    auth_object = UserAuthentication(username, password, 'psbco.org', site_url)
    result = auth_object.authenticate()
    return_result = {}

    # get user's id in CustomerList
    customer_result = auth_object.sharepoint_get_request(filter_CustomerList)

    idd = customer_result.json()['d']['results'][0]['ID']

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

    endpoint_uri = "_api/web/lists/getbytitle('salesheader')/items"
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

    print(deliver_to_customer)

    payload = {'__metadata': {'type': 'SP.Data.SalesHeaderListItem'},
               'Status': 'در انتظار صدور پیش فاکتور',
               'ShipOstanId': ship_ostan_id,
               'ShipCityId': ship_city_id,
               'ShipAddress': ship_address,
               'AssignedListIDId': assign_id,
               'CustomerNameId': idd,
               'DeliverTo': deliver_to_customer, }

    r = requests.post(api_page, json=payload, auth=auth, headers=update_headers, verify=False)

    m = []
    parent_id = str(r.json()['d']['ID'])
    # Details
    product_name_id = product_name_id.split("-")
    product_brand_id = product_brand_id.split("-")
    request_qty = request_qty.split("-")
    if r.status_code == 201:
        for i in range(int(count)):
            g = requests.post(sharepoint_contextinfo_url, auth=auth, headers=headers, verify=False)
            form_digest_value = g.json()['d']['GetContextWebInformation']['FormDigestValue']

            endpoint_uri = "_api/web/lists/getbytitle('salesdetails')/items"
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

            payload = {'__metadata': {'type': 'SP.Data.SalesDetailsListItem'},
                       'Parent_ID': parent_id,
                       'ProductNameId': int(product_name_id[i]),
                       'RequestedQTY': int(request_qty[i]),
                       'ProductBrandId': int(product_brand_id[i]),
                       }

            g = requests.post(api_page, json=payload, auth=auth, headers=update_headers, verify=False)
            m.append(g.json()['d'])
    return {"status": [r.status_code], "items": {"header": r.json()['d'], "details": m}}


@app.get("/batteryitems/access_query/")
def read_item_multi_query(*, username: str = Header(None),
                          password: str = Header(None),
                          domain: str = Header(None),
                          site_url: str = Header(None),
                          phone: str = Header(None)):
    filter2 = "_api/web/lists/getbytitle('AppAccessList')/items?$filter=MobileNumber eq '" + phone + "'"

    auth_object = UserAuthentication(username, password, domain, site_url)
    result = auth_object.authenticate()
    return_result = {}

    # We want to extract all the list presents in the site
    if result:  # login successfully
        access_result = auth_object.sharepoint_get_request(filter2)
        if access_result.status_code == requests.codes.ok:
            if len(access_result.json()['d']['results']) == 0:
                return_result = {"status": 404, "error_type": "no such item", "error_result": "no result"}
            else:
                json_result2 = access_result.json()['d']['results']
                return_result = {"status": 200,
                                 "assigns": json_result2}
        else:
            return_result = {"status": access_result.status_code, "error_type": "server no such item",
                             "error_result": "no result"}
    return return_result


@app.get("/batteryitems/app_access_list/")
def app_access_list(*, username: str = Header(None),
                    password: str = Header(None),
                    domain: str = Header(None),
                    site_url: str = Header(None),
                    endpoint_uri: str = Header(None),
                    phone_number: str = Header(None)):
    auth_object = UserAuthentication(username, password, domain, site_url)
    result = auth_object.authenticate()

    endpoint_uri += "?$select=MobileNumber,*&$filter=MobileNumber eq " + "'" + phone_number + "'"
    # We want to extract all the list presents in the site
    if result:  # login successfully
        result = auth_object.sharepoint_get_request(endpoint_uri)
        if result.status_code == requests.codes.ok:
            json_result = result.json()['d']['results']
            return {"status": 200, "item": json_result}
        else:
            return {"status": "error on items", "error_type": "failed on request processing", "error_result": result}
    else:  # login unsuccessfully
        return {"status": "error on auth", "error_type": "failed auth", "error_result": result}
