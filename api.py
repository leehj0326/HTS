# api.py
import requests
import os


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
        return []

    def get_chart_data(self, stock_name):
        return []

    def get_account_summary(self):
        """계좌 요약 정보 조회 (수익률 지표 세분화)"""
        if not self.check_connection():
            return {
                "account_no": "",
                "cash_balance": "0 원",
                "total_eval_amount": "0 원",
                "total_profit_loss": "0 원",
                "total_investment": "0 원",
                "today_realized_pnl": "0 원",
                "crdt_secu_rt": "100.0%",
                "eval_return_rate": "0.0%",
                "realized_return_rate": "0.0%",
                "today_total_return_rate": "0.0%"
            }

        account_no = ""
        cash_balance = "0 원"
        total_eval = "0"
        total_pl = "0"
        eval_rt = "0.0%"
        total_inv = "0"
        today_pnl = "0"
        crdt_rt = "100.0%"
        realized_rt = "0.0%"
        today_tot_rt = "0.0%"

        try:
            _, res_ka = self.request_api('ka00001', {})
            account_no = res_ka.get('acctNo', '')
        except Exception:
            pass

        try:
            _, res_kt1 = self.request_api('kt00001', {'qry_tp': '3'})
            entr = res_kt1.get('entr', '0')
            cash_balance = f"{int(entr):,} 원" if entr.isdigit() else f"{entr} 원"
        except Exception:
            pass

        try:
            _, res_kt18 = self.request_api('kt00018', {'qry_tp': '1', 'dmst_stex_tp': 'KRX'})
            total_eval = res_kt18.get('tot_evlt_amt', '0')
            total_pl = res_kt18.get('tot_evlt_pl', '0')
            eval_rt = res_kt18.get('tot_prft_rt', '0.0') + "%"
            total_inv = res_kt18.get('tot_puch_amt', '0')
            today_pnl = res_kt18.get('d2_prft_amt', '0')
        except Exception:
            pass

        try:
            _, res_kt5 = self.request_api('kt00005', {'qry_tp': '1'})
            crdt_rt = res_kt5.get('crdt_secu_rt', '100.0') + "%"
        except Exception:
            pass

        try:
            # 실현손익 기간별 총괄 (ka10074) -> 실현손익률
            _, res_pl = self.request_api('ka10074', {'qry_tp': '0'})
            realized_rt = res_pl.get('rlzt_prft_rt', '0.0') + "%"
        except Exception:
            pass

        try:
            # 당일 매매일지 (ka10170) -> 당일 총 수익률
            _, res_journal = self.request_api('ka10170', {'qry_tp': '0'})
            today_tot_rt = res_journal.get('tot_prft_rt', '0.0') + "%"
        except Exception:
            pass

        formatted_pnl = f"{int(total_pl):,} 원" if total_pl.lstrip('-').isdigit() else f"{total_pl} 원"

        return {
            "account_no": account_no,
            "cash_balance": cash_balance,
            "total_eval_amount": f"{int(total_eval):,} 원" if total_eval.isdigit() else f"{total_eval} 원",
            "total_profit_loss": formatted_pnl,
            "total_investment": f"{int(total_inv):,} 원" if total_inv.isdigit() else f"{total_inv} 원",
            "today_realized_pnl": f"{int(today_pnl):,} 원" if today_pnl.lstrip('-').isdigit() else "0 원",
            "crdt_secu_rt": crdt_rt,
            "eval_return_rate": eval_rt,
            "realized_return_rate": realized_rt,
            "today_total_return_rate": today_tot_rt
        }

    def get_deposit_detail(self):
        if not self.check_connection():
            return {}
        try:
            _, res_data = self.request_api('kt00001', {'qry_tp': '3'})
            return res_data
        except Exception:
            return {}

    def get_margin_orderable(self, stk_cd, uv):
        if not self.check_connection() or not stk_cd or not uv:
            return {}
        params = {
            'io_amt': '',
            'stk_cd': str(stk_cd),
            'trde_tp': '2',
            'trde_qty': '',
            'uv': str(uv),
            'exp_buy_unp': ''
        }
        try:
            _, res_data = self.request_api('kt00010', params)
            return res_data
        except Exception:
            return {}

    def get_credit_balance_detail(self):
        items = []
        if not self.check_connection():
            return items
        try:
            _, res_data = self.request_api('kt00005', {'qry_tp': '1'})
            for item in res_data.get('crdt_remn_dtl', []):
                items.append({
                    'stk_nm': item.get('stk_nm', '알수없음'),
                    'crdt_tp': item.get('crdt_tp_nm', '현금'),
                    'loan_dt': item.get('loan_dt', '-'),
                    'exp_dt': item.get('exp_dt', '-'),
                    'secu_rt': item.get('crdt_secu_rt', '100'),
                    'qty': item.get('rmnd_qty', '0'),
                    'eval_pl': item.get('evltv_prft', '0')
                })
        except Exception:
            pass
        return items

    def get_portfolio_holdings(self):
        items = []
        if not self.check_connection():
            return items
        try:
            _, res_data = self.request_api('kt00018', {'qry_tp': '1', 'dmst_stex_tp': 'KRX'})
            holdings = res_data.get('stk_bal_dtl', []) or res_data.get('output', [])
            for h in holdings:
                items.append({
                    'stk_nm': h.get('stk_nm', '알수없음'),
                    'qty': h.get('rmnd_qty', h.get('hldg_qty', '0')),
                    'puch_prc': h.get('puch_prc', '0'),
                    'now_prc': h.get('now_prc', h.get('prc', '0')),
                    'evlt_pl': h.get('evlt_pl', '0'),
                    'prft_rt': h.get('prft_rt', '0.0')
                })
        except Exception:
            pass
        return items

    def get_realized_pl_summary(self):
        if not self.check_connection():
            return {}
        try:
            _, res_data = self.request_api('ka10074', {'qry_tp': '0'})
            return res_data
        except Exception:
            return {}

    def get_realized_pl_details(self):
        items = []
        if not self.check_connection():
            return items
        try:
            _, res_data = self.request_api('ka10073', {'qry_tp': '0'})
            details = res_data.get('rlzt_prft_dtl', []) or res_data.get('output', [])
            for d in details:
                items.append({
                    'date': d.get('trde_dt', '-'),
                    'stk_nm': d.get('stk_nm', '알수없음'),
                    'buy_amt': d.get('puch_amt', '0'),
                    'sell_amt': d.get('sell_amt', '0'),
                    'rlzt_pl': d.get('rlzt_prft', '0'),
                    'prft_rt': d.get('prft_rt', '0.0'),
                    'fee': d.get('fee', '0'),
                    'tax': d.get('tax', '0')
                })
        except Exception:
            pass
        return items

    def get_daily_trading_journal(self):
        if not self.check_connection():
            return {}, []
        try:
            _, res_data = self.request_api('ka10170', {'qry_tp': '0'})
            summary = {
                'tot_rlzt_prft': res_data.get('tot_rlzt_prft', '0'),
                'tot_prft_rt': res_data.get('tot_prft_rt', '0.0'),
                'tot_fee_tax': str(int(res_data.get('tot_fee', '0') or 0) + int(res_data.get('tot_tax', '0') or 0)),
                'tot_sttl_amt': res_data.get('tot_sttl_amt', '0')
            }
            items = []
            details = res_data.get('miv_dtl', []) or res_data.get('output', [])
            for d in details:
                items.append({
                    'stk_nm': d.get('stk_nm', '알수없음'),
                    'buy_unp': d.get('puch_unp', '0'),
                    'sell_unp': d.get('sell_unp', '0'),
                    'buy_qty': d.get('buy_qty', '0'),
                    'sell_qty': d.get('sell_qty', '0'),
                    'rlzt_prft': d.get('rlzt_prft', '0'),
                    'prft_rt': d.get('prft_rt', '0.0'),
                    'fee': d.get('fee', '0'),
                    'tax': d.get('tax', '0')
                })
            return summary, items
        except Exception:
            return {}, []

    def get_trade_counts(self):
        unexecuted_count = 0
        executed_count = 0
        if not self.check_connection():
            return unexecuted_count, executed_count

        try:
            _, res_un = self.request_api('ka10075', {'qry_tp': '0'})
            un_list = res_un.get('acnt_unexec_dtl', [])
            unexecuted_count = len(un_list)
        except Exception:
            pass

        try:
            _, res_ex = self.request_api('ka10076', {'qry_tp': '0'})
            ex_list = res_ex.get('acnt_exec_dtl', [])
            executed_count = len(ex_list)
        except Exception:
            pass

        return unexecuted_count, executed_count

    def get_trade_history(self):
        items = []
        if not self.check_connection():
            return items

        try:
            _, res_un = self.request_api('ka10075', {'qry_tp': '0'})
            for item in res_un.get('acnt_unexec_dtl', []):
                stk_nm = item.get('stk_nm', '알수없음')
                price = item.get('ord_unp', '0')
                fmt_price = f"{int(price):,} 원" if price.isdigit() else f"{price} 원"
                items.append((stk_nm, fmt_price, "미체결"))
        except Exception:
            pass

        try:
            _, res_ex = self.request_api('ka10076', {'qry_tp': '0'})
            for item in res_ex.get('acnt_exec_dtl', []):
                stk_nm = item.get('stk_nm', '알수없음')
                price = item.get('exec_prc', '0')
                fmt_price = f"{int(price):,} 원" if price.isdigit() else f"{price} 원"
                items.append((stk_nm, fmt_price, "체결"))
        except Exception:
            pass

        return items

    def execute_order(self, stock_name, order_type, quantity):
        return False