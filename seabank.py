import requests
import json
import time
import hashlib

# from smart_otp import get_smart_otp
class SeaBank:
    def __init__(self, username, password, account_number):
        self.file = f"data/{username}.txt"
        self.password = hashlib.sha256(password.encode()).hexdigest()
        self.username = username
        self.account_number = account_number
        self.id_token = ""
        self.username_id = ""
        self.is_login = False
        self.time_login = time.time()
        self.customer_id = ""
        if not self._file_exists():
            self.save_data()
        else:
            self.parse_data()
            self.password = hashlib.sha256(password.encode()).hexdigest()
            self.username = username
            self.account_number = account_number
            self.save_data()

    def _file_exists(self):
        try:
            with open(self.file, 'r'):
                return True
        except FileNotFoundError:
            return False

    def save_data(self):
        data = {
            'username': self.username,
            'password': self.password,
            'account_number': self.account_number,
            'id_token': self.id_token,
            'username_id': self.username_id,
            'is_login': self.is_login,
            'time_login': self.time_login,
        }
        with open(self.file, 'w') as f:
            json.dump(data, f)

    def parse_data(self):
        with open(self.file, 'r') as f:
            data = json.load(f)
            self.username = data['username']
            self.password = data['password']
            self.account_number = data.get('account_number', '')
            self.customerId = data.get('customerId', '')
            self.id_token = data.get('id_token', '')
            self.username_id = data.get('username_id', '')
            self.is_login = data.get('is_login', '')
            self.time_login = data.get('time_login', '')

    def do_login(self):
        param = {
            "username": self.username,
            "password": self.password,
            "rememberMe": False,
            "context": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "channel": "SEAMOBILE3.0",
            "subChannel": "SEANET",
            "passwordType": "HASH",
            "captcha": None,
            "location": None,
            "longitude": None,
            "latitude": None,
            "ipAddress": None,
            "machineName": None,
            "machineType": None,
            "application": None,
            "version": None,
            "contextFull": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.100.0"
        }
        result = self.curl_post('https://ebankbackend.seanet.vn/canhan/api/authenticate-hash', param)
        
        if 'code' in result and result['code'] == '00':
            self.is_login = True
            result['success'] = True
            self.username_id = result['data']['username']
            self.id_token = result['data']['id_token']
            self.customer_id = result['data']['customerId']
            self.is_login = True
            self.time_login = time.time()
            self.save_data()
            
            return {
                'code': 200,
                'success': True,
                'message': "success",
                'data': result if result else ""
            }
        elif 'code' in result and result['code'] == 'BANKAPI-AUTHENAPI-50304':
            return {
            'code': 444,
            'success': False,
            'message': 'Tài khoản hoặc mật khẩu không đúng',
            'data': result if result else ""
            }
        elif 'code' in result and result['code'] == 'BANKAPI-AUTHENAPI-50305':
            return {
            'code': 404,
            'success': False,
            'message': 'Tài khoản không tồn tại',
            'data': result if result else ""
            }
        else:
            return {
                'code': 500,
                'success': False,
                'message': result['messageVi'] if 'messageVi' in result else result,
                "param": param,
                'data': result if result else ""
            }

    def format_date(self, date):
        date = date.split('/')
        return f"{date[2]}{date[1]}{date[0]}"

    def get_transactions(self, begin, end, account_number,limit=100):
        if not self.is_login or time.time() - self.time_login > 900:
            login = self.do_login()
            if 'success' not in login or not login['success']:
                return login
        begin = self.format_date(begin)
        end = self.format_date(end)
        param = {
            "accountID": account_number,
            "fromDate": begin,
            "toDate": end,
            "coCode": "",
            "language": "GB",
            "shortTitle": "",
            "currency": "",
            "productName": ""
        }
        history =  self.curl_post('https://ebankms1.seanet.vn/p03/api/p03-statement/get-trans-list-new', param, True)
        if 'code' in history and history['code'] == '00':
            if not history['data']:
                return {'code':200,'success': True, 'message': 'Thành công',
                            'data':{
                                'transactions':[],
                    }}
            records = history['data'][-limit:]
            history['data'] = records
            return {'code':200,'success': True, 'message': 'Thành công',
                    'data':{
                        'transactions':history['data'],
            }}
        return {'code':520,'success': True, 'message': 'Unknown error!',
                'data':history}
    def get_accounts(self):
        return self.curl_get('https://ebankms1.seanet.vn/p02/api/swib-enquiry/customer-accounts')
    def get_balance(self,account_number):
        if not self.is_login or time.time() - self.time_login > 900:
            login = self.do_login()
            if 'success' not in login or not login['success']:
                return login
            
        accounts_list = self.get_accounts()
        if 'data' in accounts_list and accounts_list['data']:
            for account in accounts_list['data']:        
                if account.get('accountID') == account_number:
                    return {'code':200,'success': True, 'message': 'Thành công',
                                    'data':{
                                        'account_number':account_number,
                                        'balance':int(account.get('availBal'))
                            }}
                else:
                    return {'code':404,'success': False, 'message': 'account_number not found!'} 
        else:
            self.is_login = False
            self.save_data()
            return {'code':520 ,'success': False, 'message': 'Unknown Error!','data':account} 
    def check_bank_name_out(self,bank_code,account_number):
        param = {
            "bankID": bank_code,
            "benAccount": account_number,
            "senderAccount": self.account_number
        }
        return self.curl_post('https://ebankms2.seanet.vn/p0405/api/common/enq-check-acc', param, True)
    
    def check_bank_name_in(self,account_number):
        return self.curl_post('https://ebankms2.seanet.vn/p0405/api/swib-enquiry/check-customer-info/'+str(account_number))
    
    def mapping_bank_code(self,bank_name):
        with open('banks.json','r', encoding='utf-8') as f:
            data = json.load(f)
        for bank in data['data']:
            if bank['shortName'].lower() == bank_name.lower():
                return bank['bin']
        return None
    def get_bank_name(self, ben_account_number, bank_name):
        if not self.is_login:
            login = self.do_login()
            if not login['success']:
                return login
        if 'bank_name' == 'SeABank':
            return self.check_bank_name_in(ben_account_number)
        else:
            bank_code = self.mapping_bank_code(bank_name)
            return self.check_bank_name_in(bank_code,ben_account_number)
    
    def get_list_bank(self):
        return self.curl_get('https://ebankms2.seanet.vn/p0405/api/get-list-bank')

    def curl_get(self, url):
        try:
            headers = self.header_null(True)
            # proxy_url = "http://103.189.75.146:40508"
            # proxy_username = "linhvudieu329"
            # proxy_password = "l0Ks3Jp"

            # Construct the proxy credentials
            # proxy_credentials = f"{proxy_username}:{proxy_password}"
            # proxy_auth = requests.auth.HTTPProxyAuth(proxy_username, proxy_password)

            # # Set up the proxy dictionary
            # proxies = {
            #     "http": f"http://{proxy_credentials}@{proxy_url}",
            #     "https": f"http://{proxy_credentials}@{proxy_url}"
            # }
            response = requests.get(url, headers=headers, timeout=60)
            result = response.json()
            return result
        except Exception as e:
            return False

    def curl_post(self, url, data=None, with_authen=False):
        try:
            headers = self.header_null(True)
            # proxy_url = "103.189.75.146:40508"
            # proxy_username = "linhvudieu329"
            # proxy_password = "l0Ks3Jp"

            # # Construct the proxy credentials
            # proxy_credentials = f"{proxy_username}:{proxy_password}"
            # proxy_auth = requests.auth.HTTPProxyAuth(proxy_username, proxy_password)

            # # Set up the proxy dictionary
            # proxies = {
            #     "http": f"http://{proxy_credentials}@{proxy_url}",
            #     "https": f"http://{proxy_credentials}@{proxy_url}"
            # }
            headers = self.header_null(with_authen)
            response = requests.post(url, headers=headers, json=data, timeout=60)
            result = response.json()
            return result
        except Exception as e:
            return False

    def header_null(self, with_authen=False):
        header = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://seanet.vn',
        'referer': 'https://seanet.vn/',
        'sec-ch-ua': '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'
        }
        if with_authen:
            header['Authorization'] = 'Bearer ' + self.id_token

        return header