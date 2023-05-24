from dataclasses import field, fields
import string
from traceback import print_tb
from typing import Dict
#from winreg import QueryInfoKey
import requests

import re
import mechanicalsoup
import html
import urllib.parse

from urllib.parse import urlparse
from urllib.parse import parse_qs

BASE_URL = "https://rest40.bullhornstaffing.com/rest-services"


class BullHornAdapter:
    def __init__(self, client_id: string, client_secret: string) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.session_token = ""
        super().__init__()

    def get_code(self, client_id: string) -> string:
        browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')

        browser.open(
            "https://universal.bullhornstaffing.com/universal-login/login")
        browser.select_form('#login-form')

        response = browser.submit_selected()
        print("Response")
        print(response.text)

        print("URL")
        print(browser.get_url())

        """browser.open(
            "https://rest.bullhornstaffing.com/oauth/authorize?client_id=f8a61111-51a6-42c4-8e1f-08dd9dc2f463&response_type=code&action=Login&username=captivateiq.api&password=+>2T=bK6qTtrU>$[&state=demo")

        print("Request")
        new_url = browser.get_url()
        parsed_url = urlparse(new_url)
        captured_value = parse_qs(parsed_url.query)['code'][0]
        print(captured_value)"""
        flag =False
        while(flag == False):
            print('while(flag == False):')
            browser.open("https://rest.bullhornstaffing.com/oauth/authorize?client_id=f8a61111-51a6-42c4-8e1f-08dd9dc2f463&response_type=code&action=Login&username=captivateiq.api&password=BhCiq2022!*&state=demo")
            print("Request")
            new_url = browser.get_url()
            print('new_url',new_url)
            parsed_url = urlparse(new_url)
            try: 
                captured_value = parse_qs(parsed_url.query)['code'][0]
                print('Captured Value',captured_value)    
                flag= True #cambiar a 
            except:
                print("parsed_url error",parsed_url)
                code_value= False

        return captured_value

    def get_access_token(self, code: string) -> string:
        url = 'https://auth.bullhornstaffing.com/oauth/token?grant_type=authorization_code&code={}&client_id={}&client_secret={}'.format(
            code, self.client_id, self.client_secret)
        response = requests.request("POST", url, headers={}, data={})
        json_response = response.json()
        print(json_response)
        return json_response["access_token"]

    def get_session_token(self, access_token):
        url = 'https://rest.bullhornstaffing.com/rest-services/login?version=*&access_token={}'.format(
            access_token)
        response = requests.request("POST", url, headers={}, data={})
        json_response = response.json()
        self.session_token = json_response["BhRestToken"]
        return json_response["BhRestToken"]

    # TODO we need the make the request to refresh the token.
    #token
    def refresh_token(self, access_token: string) -> string:
        url = 'https://auth.bullhornstaffing.com/oauth/token?grant_type=refresh_token&refresh_token={}&client_id={}&client_secret={}'.format(
            access_token, self.client_id, self.client_secret)
        response = requests.request("POST", url, headers={}, data={})
        json_response = response.json()
        return json_response["access_token"]
    
    #contract
    def get_contracts_billable(self, period_Search):
        #https://rest40.bullhornstaffing.com/rest-services/4hz0p/query/BillableCharge?where=periodEndDate='2022-05-14'&fields=placement(id,employmentType)&count=500&orderBy=placement.id
        query = "periodEndDate='{}'".format(period_Search)
        fields = "placement(id,employmentType)&count=500&orderBy=placement.id"
        url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/query/BillableCharge?where={}&fields={}".format(query,fields)
        #url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/query/PayableCharge?where=(placement.id>73700)AND(placement.id<73720)AND(periodEndDate='2022-06-04')&fields={}".format(fields)            
        print(url)
        payload = {}
        headers = {
            'BhRestToken': self.session_token
            }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()
        contracts = json_response['data']
        while json_response['count'] ==500:
            placement_id = json_response['data'][499]['placement']['id']
            query = "periodEndDate='{}'AND(placement.id>{})".format(period_Search,placement_id)
            url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/query/BillableCharge?where={}&fields={}".format(query,fields)
            #url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/query/PayableCharge?where=(placement.id>73690)AND(periodEndDate='2022-06-04')&fields={}".format(fields)            
            print(url)
            response = requests.request("GET", url, headers=headers, data=payload)
            json_response = response.json()
            contracts = json_response['data'] +contracts
        return contracts

    def get_contracts_payable(self, period_Search):
        query ="periodEndDate='{}'".format(period_Search)
        fields = "placement(id,employmentType)&count=500&orderBy=placement.id"
        url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/query/PayableCharge?where={}&fields={}".format(query,fields)
        print(url)
        payload = {}
        headers = {
            'BhRestToken': self.session_token
            }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()
        contracts = json_response['data']
        while json_response['count'] ==500:
            placement_id = json_response['data'][499]['placement']['id']
            query = "periodEndDate='{}'AND(placement.id>{})".format(period_Search,placement_id)
            url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/query/PayableCharge?where={}&fields={}".format(query,fields)
            #url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/query/PayableCharge?where=(placement.id>73690)AND(periodEndDate='2022-06-04')&fields={}".format(fields)            
            print(url)
            response = requests.request("GET", url, headers=headers, data=payload)
            json_response = response.json()
            contracts = json_response['data'] +contracts
        #print("get_contracts_payable",contracts)
        return contracts

        

        

    """def get_contracts_modified(self,  date_added):
        query = "(dateAdded>{})AND((placement.employmentType='Contract')OR(placement.employmentType='Direct Hire'))".format(date_added)
        #query = "(dateAdded>{})".format(date_added)
        fields = "placement(id, employmentType)&count=500&orderBy=dateAdded"
        url = 'https://rest40.bullhornstaffing.com/rest-services/4hz0p/query/PayableCharge?where={}&fields={}'.format(query,fields)
        payload = {}
        headers = {
            'BhRestToken': self.session_token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()
        return json_response['data']"""

    # borrar
    """def searh_feed_contract(self, date_added, date_last_modified):
        query = "((dateAdded>{})OR(dateLastModified>{}))AND(status='Approved')AND((employmentType='Direct Hire')OR(employmentType='Contract'))".format(
            date_added, date_last_modified)
        fields = "id,candidate(owner),jobOrder(clientCorporation,title),dateBegin,employmentType,workWeekStart,customText5,commissions(commissionPercentage,role,user)"
        url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/query/Placement?where={}&fields={}".format(
            query, fields)

        payload = {}
        headers = {
            'BhRestToken': self.session_token
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()

        return json_response["data"]"""

    def period_id(self, placementID):

        url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/query/BillableCharge?where=placement={}&fields=id,periodEndDate".format(
            placementID)
        payload = {}
        headers = {
            'BhRestToken': self.session_token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()
        return json_response['data'][0]['id']

    def general_data(self, placementID):
        fields = "id,candidate(owner),jobOrder(clientCorporation,title),dateBegin,employmentType,workWeekStart,customText5,commissions(commissionPercentage,role,user)"
        url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/entity/Placement/{}?&fields={}".format(
            placementID, fields)
        payload = {}
        headers = {
            'BhRestToken': self.session_token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()
        return json_response["data"]

    def earn_codes(self, placementID):
        fields = "id,placementRateCardLineGroups[500]"
        url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/query/PlacementRateCard?where=placement={}&fields={}".format(
            placementID, fields)
        payload = {}
        headers = {
            'BhRestToken': self.session_token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()
        return json_response["data"]

    def id_payable_charge(self, placementID,periodEndDate):
        query ="(placement={})AND(periodEndDate='{}')".format(placementID,periodEndDate)
        fields = "id,placement(id)"
        url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/query/PayableCharge?where={}&fields={}".format(
            query, fields)
        payload = {}
        headers = {
            'BhRestToken': self.session_token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()
        id_payable_list = []
        try:
            for item  in json_response['data']:
                id_payable_list.append(item['id'])
            #print(payableID)
            return id_payable_list
        except:
            #print(payableID)
            
            return id_payable_list

        """try:
            id_payable = json_response['data'][0]['id']
            return id_payable
        except:
            return 0"""
    
    def id_billable_charge(self, placementID,periodEndDate):
        query ="(placement={})AND(periodEndDate='{}')".format(placementID,periodEndDate)
        fields = "id,placement(id)"
        url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/query/PayableCharge?where={}&fields={}".format(
            query, fields)
        payload = {}
        headers = {
            'BhRestToken': self.session_token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()
        try:
            id_payable = json_response['data'][0]['id']
            return id_payable
        except:
            return 0
    
    
    def get_hours_data(self, id_payable):
        fields = "periodEndDate,payableTransactions[500](quantity,earnCode(code))"
        url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/entity/PayableCharge/{}?fields={}".format(
            id_payable, fields)
        payload = {}
        headers = {
            'BhRestToken': self.session_token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()
        #print(json_response)
        return json_response['data']
    
    """def get_hours_data_billable(self, id_payable):
        fields = "periodEndDate,payableTransactions[500](quantity,earnCode(code))"
        url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/entity/BillableCharge/{}?fields={}".format(
            id_payable, fields)
        payload = {}
        headers = {
            'BhRestToken': self.session_token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()
        #print(json_response)
        return json_response['data']"""

    def get_billable_charge(self, placement_id):
        query = "placement={}".format(placement_id)
        fields = "placement(id,candidate(owner),jobOrder(clientCorporation,title),dateBegin,employmentType,workWeekStart),periodEndDate,billMasters(billMastersearh_feed_contractactions(quantity),earnCode(earnCodeTypeLookup))"
        url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/query/BillableCharge?where={}&fields={}".format(query,
                                                                                                                       fields)

        payload = {}
        headers = {
            'BhRestToken': self.session_token
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()

        return json_response["data"]

    def get_exported_transactions(self,id_payable):
        fields= "id,periodEndDate,exportedTransactions[500](id,quantity,earnCode(code))"
        url = 'https://rest40.bullhornstaffing.com/rest-services/4hz0p/entity/PayableCharge/{}?fields={}'.format(id_payable, fields)
        payload = {}
        headers = {
            'BhRestToken': self.session_token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()
        return json_response['data']

    """def get_exported_transactions_billable(self,id_payable):
        fields= "id,periodEndDate,exportedTransactions[500](id,quantity,earnCode(code))"
        url = 'https://rest40.bullhornstaffing.com/rest-services/4hz0p/entity/BillableCharge/{}?fields={}'.format(id_payable, fields)
        payload = {}
        headers = {
            'BhRestToken': self.session_token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()
        return json_response['data']
    """
    
    def get_rate_card(self, placement_id):
        query = "placement={}".format(placement_id)
        fields = "id,placementRateCardLineGroups(id)"
        url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/query/PlacementRateCard?where={}&fields={}".format(query,
                                                                                                                          fields)

        payload = {}
        headers = {
            'BhRestToken': self.session_token
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()

        return json_response["data"]

    

    def search_direct_hires(self, placementID):
        fields = "id,candidate(owner),commissions(commissionPercentage,role,user,dateAdded),employmentType,jobOrder(clientCorporation,title),daysGuaranteed,dateBegin,flatFee,status,customText14"
        print(placementID)
        url = "https://rest40.bullhornstaffing.com/rest-services/4hz0p/entity/Placement/{}?&fields={}".format(placementID,fields)
        
        
        payload = {}
        headers = {
            'BhRestToken': self.session_token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()
        return json_response["data"]
