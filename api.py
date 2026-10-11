# api.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()


class TradingAPIClient:
    def __init__(self, app_key='', secret_key=''):
        self.app_key = app_key
        self.secret_key = secret_key
        self.host = 'https://mockapi.kiwoom.com'
        self.token = None

        if not self.app_key or not self.secret_key:
            self.app_key = os.getenv('APP_KEY', '')
            self.secret_key = os.getenv('SECRET_KEY', '')

        if self.app_key and self.secret_key:
            self.authenticate(self.app_key, self.secret_key)

    def authenticate(self, app_key, secret_key):
        """토큰 발급 (fn_au10001)"""
        if not app_key or not secret_key:
            self.token = None
            return False

        url = self.host + '/oauth2/token'
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        data = {
            'grant_type': 'client_credentials',
            'appkey': app_key,
            'secretkey': secret_key
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                res_data = response.json()
                self.token = res_data.get('token')
                if self.token:
                    self.app_key = app_key
                    self.secret_key = secret_key
                    return True
        except Exception:
            pass

        self.token = None
        return False

    def check_connection(self):
        """토큰 발급 여부로 연동 상태 확인"""
        return bool(self.token and self.token.strip())

    def request_api(self, api_id, data, cont_yn='N', next_key=''):
        url = self.host + '/api/dostk/acnt'
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'authorization': f'Bearer {self.token}',
            'cont-yn': cont_yn,
            'next-key': next_key,
            'api-id': api_id
        }
        response = requests.post(url, headers=headers, json=data)
        return response, response.json()

    def get_stock_list(self):
        """종목 리스트 조회"""
        return []

    def get_chart_data(self, stock_name):
        """차트 데이터 조회"""
        return []

    def get_account_summary(self):
        """계좌번호, 현금잔고(예수금), 평가손익을 조회"""
        if not self.check_connection():
            return {
                "account_no": "",
                "cash_balance": "0 원",
                "total_profit_loss": "0 원 (0%)"
            }

        account_no = ""
        cash_balance = "0 원"
        total_pl = "0"
        total_rt = "0"

        try:
            # 1. 계좌번호 확인 (ka00001)
            _, res_ka = self.request_api('ka00001', {})
            account_no = res_ka.get('acctNo', '')
        except Exception:
            pass

        try:
            # 2. 예수금 확인 (kt00001)
            _, res_kt1 = self.request_api('kt00001', {'qry_tp': '3'})
            entr = res_kt1.get('entr', '0')
            cash_balance = f"{int(entr):,} 원" if entr.isdigit() else f"{entr} 원"
        except Exception:
            pass

        try:
            # 3. 잔고 확인 (kt00018) - 평가손익 및 수익률 추출용
            _, res_kt18 = self.request_api('kt00018', {'qry_tp': '1', 'dmst_stex_tp': 'KRX'})
            total_pl = res_kt18.get('tot_evlt_pl', '0')
            total_rt = res_kt18.get('tot_prft_rt', '0')
        except Exception:
            pass

        formatted_pnl = "0 원 (0.0%)"
        if total_pl.lstrip('-').isdigit():
            formatted_pnl = f"{int(total_pl):,} 원 ({total_rt}%)"
        else:
            formatted_pnl = f"{total_pl} 원 ({total_rt}%)"

        return {
            "account_no": account_no,
            "cash_balance": cash_balance,
            "total_profit_loss": formatted_pnl
        }

    def execute_order(self, stock_name, order_type, quantity):
        """주문 실행 API 연동 영역"""
        return False