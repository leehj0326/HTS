import requests
import json


class TradingAPIClient:
    def __init__(self, base_url="https://api.example.com", api_key="", secret_key=""):
        self.base_url = base_url
        self.api_key = api_key
        self.secret_key = secret_key
        self.headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }

    def get_stock_list(self):
        """1. 전체 종목 리스트 조회 (검색 자동완성용)"""
        # TODO: 실제 증권사 API 또는 백엔드 엔드포인트에 맞게 수정
        # response = requests.get(f"{self.base_url}/stocks", headers=self.headers)
        # return response.json()

        # 임시 기본 종목 반환 (연동 시 실제 API 데이터로 교체)
        return [
            "삼성전자", "SK하이닉스", "LG에너지솔루션",
            "셀트리온", "현대차", "NAVER", "카카오",
            "LG화학", "삼성바이오로직스", "기아", "POSCO홀딩스"
        ]

    def get_chart_data(self, stock_name):
        """2. 특정 종목의 캔들차트 데이터(시가/고가/저가/종가/거래량) 조회"""
        # TODO: 실제 API 연동
        # params = {"stock": stock_name}
        # response = requests.get(f"{self.base_url}/chart", headers=self.headers, params=params)
        # return response.json()

        import random
        candles = []
        base_price = 70000 if "삼성" in stock_name or "SK" in stock_name else 45000
        for _ in range(40):
            open_p = base_price + random.randint(-800, 800)
            close_p = open_p + random.randint(-1000, 1000)
            high_p = max(open_p, close_p) + random.randint(100, 500)
            low_p = min(open_p, close_p) - random.randint(100, 500)
            volume = random.randint(50000, 300000)
            candles.append({'open': open_p, 'high': high_p, 'low': low_p, 'close': close_p, 'volume': volume})
            base_price = close_p
        return candles

    def get_account_portfolio(self):
        """3. 내 자산 및 보유 종목 현황 조회"""
        # TODO: 실제 API 연동
        # response = requests.get(f"{self.base_url}/account", headers=self.headers)
        # return response.json()

        return {
            "user_name": "홍길동 (모의투자자)",
            "total_eval_amount": "12,450,000 원",
            "total_profit_loss": "+745,000 원 (+6.3%)",
            "portfolio": [
                ("삼성전자", "10주", "70,500원", "+65,000원 (+0.9%)", "보유중"),
                ("SK하이닉스", "5주", "152,000원", "+120,000원 (+1.5%)", "보유중"),
                ("LG에너지솔루션", "2주", "380,000원", "-15,000원 (-0.3%)", "체결완료")
            ]
        }

    def execute_order(self, stock_name, order_type, quantity):
        """4. 매수/매도 주문 전송"""
        # TODO: 실제 API 연동
        # payload = {"stock": stock_name, "type": order_type, "qty": quantity}
        # response = requests.post(f"{self.base_url}/order", headers=self.headers, json=payload)
        # return response.json()

        print(f"[API 전송] {stock_name} {quantity}주 {order_type} 주문 요청 완료")
        return True