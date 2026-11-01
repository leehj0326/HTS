# ui.py
import sys
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QSplitter, QLabel, QTextEdit, QMessageBox, QDialog, QFormLayout,
    QListWidget, QMenu, QAbstractItemView, QInputDialog, QRubberBand, QTabBar, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, QRectF, QPointF, QRect, QPoint, QMimeData, QSettings
from PySide6.QtGui import QPainter, QColor, QPen, QIntValidator, QDrag

from api import TradingAPIClient

DARK_STYLE = """
QMainWindow {
    background-color: #121212;
    color: #e0e0e0;
}
QWidget {
    background-color: #1e1e1e;
    color: #d4d4d4;
    font-family: 'Segoe UI', sans-serif;
    font-size: 10pt;
}
QLineEdit {
    background-color: #2d2d2d;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 6px;
    color: #ffffff;
}
QLineEdit:focus {
    border: 1px solid #007acc;
}
QPushButton {
    background-color: #2d2d2d;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 6px 12px;
    color: #ffffff;
}
QPushButton:hover {
    background-color: #353535;
    border: 1px solid #505050;
}
QPushButton:pressed {
    background-color: #007acc;
}
QPushButton#BuyButton {
    background-color: #ef5350;
    color: #ffffff;
    font-weight: bold;
    border-radius: 6px;
    font-size: 11pt;
}
QPushButton#BuyButton:hover {
    background-color: #f26d6a;
}
QPushButton#SellButton {
    background-color: #26a69a;
    color: #ffffff;
    font-weight: bold;
    border-radius: 6px;
    font-size: 11pt;
}
QPushButton#SellButton:hover {
    background-color: #33b8ab;
}
QTreeWidget {
    background-color: #161616;
    border: 1px solid #2d2d2d;
    selection-background-color: #264f78;
    outline: 0;
}
QTreeWidget::item {
    padding: 8px 6px;
    margin: 2px 4px;
    border-radius: 4px;
    border: 1px solid transparent;
}
QTreeWidget::item:hover {
    background-color: #222222;
    border: 1px solid #333333;
}
QTreeWidget::item:selected {
    background-color: #264f78;
    color: #ffffff;
}
QHeaderView::section {
    background-color: #252526;
    color: #cccccc;
    padding: 6px;
    border: 1px solid #2d2d2d;
}
QTabWidget::pane {
    border: 1px solid #2d2d2d;
    background-color: #1e1e1e;
}
QTabBar::tab {
    background-color: #2d2d2d;
    color: #858585;
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #1e1e1e;
    color: #ffffff;
    border-bottom: 2px solid #007acc;
}
QSplitter::handle {
    background-color: #2d2d2d;
}
QTextEdit {
    background-color: #181818;
    border: 1px solid #2d2d2d;
    color: #d4d4d4;
}
QTableWidget {
    background-color: #181818;
    border: 1px solid #2d2d2d;
    gridline-color: #2d2d2d;
}
QMenu {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3c3c3c;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px;
}
QMenu::item:selected {
    background-color: #007acc;
}
"""


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("키움 API 로그인")
        self.resize(400, 240)
        self.api_client = None

        self.settings = QSettings("KiwoomTrading", "AutoTrader")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("<b>키움 모의투자 API 로그인</b>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        self.app_key_input = QLineEdit()
        self.app_key_input.setPlaceholderText("App Key를 입력하세요")

        self.secret_key_input = QLineEdit()
        self.secret_key_input.setPlaceholderText("Secret Key를 입력하세요")
        self.secret_key_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow("App Key:", self.app_key_input)
        form_layout.addRow("Secret Key:", self.secret_key_input)
        layout.addLayout(form_layout)

        self.remember_checkbox = QCheckBox("정보 기억하기 (자동로그인)")
        layout.addWidget(self.remember_checkbox)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ef5350;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        login_btn = QPushButton("로그인 및 연동")
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)

        self.load_saved_credentials()

    def load_saved_credentials(self):
        remember = self.settings.value("remember", False, type=bool)
        if remember:
            self.remember_checkbox.setChecked(True)
            self.app_key_input.setText(self.settings.value("app_key", ""))
            self.secret_key_input.setText(self.settings.value("secret_key", ""))

    def handle_login(self):
        app_key = self.app_key_input.text().strip()
        secret_key = self.secret_key_input.text().strip()

        if not app_key or not secret_key:
            self.error_label.setText("App Key와 Secret Key를 모두 입력해주세요.")
            return

        client = TradingAPIClient(app_key, secret_key)
        if client.check_connection():
            if self.remember_checkbox.isChecked():
                self.settings.setValue("remember", True)
                self.settings.setValue("app_key", app_key)
                self.settings.setValue("secret_key", secret_key)
            else:
                self.settings.remove("remember")
                self.settings.remove("app_key")
                self.settings.remove("secret_key")

            self.api_client = client
            self.accept()
        else:
            self.error_label.setText("인증 실패: 키를 다시 확인하고 입력해주세요.")


class DepositDetailDialog(QDialog):
    def __init__(self, parent=None, api_client=None):
        super().__init__(parent)
        self.setWindowTitle("계좌 상세 및 정밀 잔고 조회")
        self.resize(750, 600)
        self.api_client = api_client

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("<b>[상세 자산 및 실현 현황]</b>"))
        summary_widget = QWidget()
        self.form_layout = QFormLayout(summary_widget)

        self.inv_lbl = QLabel("0 원")
        self.today_pnl_lbl = QLabel("0 원")
        self.entr_lbl = QLabel("0 원")
        self.ord_alow_lbl = QLabel("0 원")

        self.form_layout.addRow("총 투자원금(매입금액):", self.inv_lbl)
        self.form_layout.addRow("당일 실현손익:", self.today_pnl_lbl)
        self.form_layout.addRow("예수금:", self.entr_lbl)
        self.form_layout.addRow("주문 가능 금액:", self.ord_alow_lbl)
        layout.addWidget(summary_widget)

        layout.addWidget(QLabel("<b>[체결 잔고 정밀 조회 - 신용/대출 상세]</b>"))
        self.balance_table = QTableWidget(0, 7)
        self.balance_table.setHorizontalHeaderLabels(["종목명", "신용구분", "대출일", "만기일", "담보비율", "보유수량", "평가손익"])
        self.balance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.balance_table)

        close_btn = QPushButton("확인")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.load_data()

    def load_data(self):
        if not self.api_client:
            return

        summary = self.api_client.get_account_summary()
        self.inv_lbl.setText(summary.get('total_investment', '0 원'))
        self.today_pnl_lbl.setText(summary.get('today_realized_pnl', '0 원'))

        res_dep = self.api_client.get_deposit_detail()
        if res_dep:
            entr = res_dep.get('entr', '0')
            ord_amt = res_dep.get('ord_alow_amt', '0')
            self.entr_lbl.setText(f"{int(entr):,} 원" if entr.isdigit() else "0 원")
            self.ord_alow_lbl.setText(f"{int(ord_amt):,} 원" if ord_amt.isdigit() else "0 원")

        balance_items = self.api_client.get_credit_balance_detail()
        self.balance_table.setRowCount(len(balance_items))
        for row, item in enumerate(balance_items):
            self.balance_table.setItem(row, 0, QTableWidgetItem(item['stk_nm']))
            self.balance_table.setItem(row, 1, QTableWidgetItem(item['crdt_tp']))
            self.balance_table.setItem(row, 2, QTableWidgetItem(item['loan_dt']))
            self.balance_table.setItem(row, 3, QTableWidgetItem(item['exp_dt']))
            self.balance_table.setItem(row, 4, QTableWidgetItem(f"{item['secu_rt']}%"))
            self.balance_table.setItem(row, 5, QTableWidgetItem(f"{item['qty']}주"))
            self.balance_table.setItem(row, 6, QTableWidgetItem(f"{item['eval_pl']}원"))

            for col in range(7):
                self.balance_table.item(row, col).setTextAlignment(Qt.AlignCenter)


class TradeHistoryDialog(QDialog):
    def __init__(self, parent=None, api_client=None):
        super().__init__(parent)
        self.setWindowTitle("체결 / 미체결 통합 내역 조회")
        self.resize(500, 400)
        self.api_client = api_client

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("<b>[당일 체결 및 미체결 현황]</b>"))

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["종목 이름", "가격", "체결/미체결"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        close_btn = QPushButton("확인")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.load_data()

    def load_data(self):
        if not self.api_client:
            return

        items = self.api_client.get_trade_history()
        self.table.setRowCount(len(items))
        for row, (stk_nm, price, status) in enumerate(items):
            item_name = QTableWidgetItem(stk_nm)
            item_price = QTableWidgetItem(price)
            item_status = QTableWidgetItem(status)

            item_name.setTextAlignment(Qt.AlignCenter)
            item_price.setTextAlignment(Qt.AlignCenter)
            item_status.setTextAlignment(Qt.AlignCenter)

            if status == "체결":
                item_status.setForeground(QColor("#26a69a"))
            else:
                item_status.setForeground(QColor("#ef5350"))

            self.table.setItem(row, 0, item_name)
            self.table.setItem(row, 1, item_price)
            self.table.setItem(row, 2, item_status)


class PortfolioDialog(QDialog):
    def __init__(self, parent=None, api_client=None):
        super().__init__(parent)
        self.setWindowTitle("보유종목 잔고 상세 조회")
        self.resize(650, 450)
        self.api_client = api_client

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("<b>[보유종목 잔고 현황]</b>"))

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["종목명", "보유수량", "매입단가", "현재가", "평가손익", "수익률"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        close_btn = QPushButton("확인")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.load_data()

    def load_data(self):
        if not self.api_client:
            return

        items = self.api_client.get_portfolio_holdings()
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            name_item = QTableWidgetItem(item['stk_nm'])
            qty_item = QTableWidgetItem(f"{int(item['qty']):,} 주" if str(item['qty']).isdigit() else f"{item['qty']} 주")
            puch_item = QTableWidgetItem(
                f"{int(item['puch_prc']):,} 원" if str(item['puch_prc']).isdigit() else f"{item['puch_prc']} 원")
            now_item = QTableWidgetItem(
                f"{int(item['now_prc']):,} 원" if str(item['now_prc']).isdigit() else f"{item['now_prc']} 원")

            pl_val = str(item['evlt_pl'])
            pl_str = f"{int(pl_val):,} 원" if pl_val.lstrip('-').isdigit() else f"{pl_val} 원"
            pl_item = QTableWidgetItem(pl_str)

            rt_item = QTableWidgetItem(f"{item['prft_rt']}%")

            for col, itm in enumerate([name_item, qty_item, puch_item, now_item, pl_item, rt_item]):
                itm.setTextAlignment(Qt.AlignCenter)
                if col in [4, 5]:
                    val_str = itm.text().replace(',', '').replace(' 원', '').replace('%', '')
                    try:
                        fval = float(val_str)
                        if fval > 0:
                            itm.setForeground(QColor("#ef5350"))
                        elif fval < 0:
                            itm.setForeground(QColor("#26a69a"))
                    except ValueError:
                        pass
                self.table.setItem(row, col, itm)


class RealizedPLDialog(QDialog):
    def __init__(self, parent=None, api_client=None):
        super().__init__(parent)
        self.setWindowTitle("실현손익 및 세부 통계 조회")
        self.resize(800, 550)
        self.api_client = api_client

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("<b>[기간별 총괄 손익 요약]</b>"))
        summary_widget = QWidget()
        self.form_layout = QFormLayout(summary_widget)

        self.tot_buy_lbl = QLabel("0 원")
        self.tot_sell_lbl = QLabel("0 원")
        self.tot_pl_lbl = QLabel("0 원")
        self.tot_fee_lbl = QLabel("0 원")
        self.tot_tax_lbl = QLabel("0 원")

        self.form_layout.addRow("총 매수금액:", self.tot_buy_lbl)
        self.form_layout.addRow("총 매도금액:", self.tot_sell_lbl)
        self.form_layout.addRow("실현손익:", self.tot_pl_lbl)
        self.form_layout.addRow("매매수수료:", self.tot_fee_lbl)
        self.form_layout.addRow("매매세금:", self.tot_tax_lbl)
        layout.addWidget(summary_widget)

        layout.addWidget(QLabel("<b>[일자별·종목별 세부 손익 및 수익률 통계]</b>"))
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["거래일자", "종목명", "매수금액", "매도금액", "실현손익", "수익률", "수수료/세금"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        close_btn = QPushButton("확인")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.load_data()

    def load_data(self):
        if not self.api_client:
            return

        summary = self.api_client.get_realized_pl_summary()
        if summary:
            b_amt = summary.get('tot_puch_amt', '0')
            s_amt = summary.get('tot_sell_amt', '0')
            p_amt = summary.get('tot_rlzt_prft', '0')
            f_amt = summary.get('tot_fee', '0')
            t_amt = summary.get('tot_tax', '0')

            self.tot_buy_lbl.setText(f"{int(b_amt):,} 원" if b_amt.isdigit() else "0 원")
            self.tot_sell_lbl.setText(f"{int(s_amt):,} 원" if s_amt.isdigit() else "0 원")
            self.tot_pl_lbl.setText(f"{int(p_amt):,} 원" if p_amt.lstrip('-').isdigit() else "0 원")
            self.tot_fee_lbl.setText(f"{int(f_amt):,} 원" if f_amt.isdigit() else "0 원")
            self.tot_tax_lbl.setText(f"{int(t_amt):,} 원" if t_amt.isdigit() else "0 원")

        items = self.api_client.get_realized_pl_details()
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            date_item = QTableWidgetItem(item['date'])
            name_item = QTableWidgetItem(item['stk_nm'])

            b_str = item['buy_amt']
            buy_item = QTableWidgetItem(f"{int(b_str):,} 원" if b_str.isdigit() else f"{b_str} 원")

            s_str = item['sell_amt']
            sell_item = QTableWidgetItem(f"{int(s_str):,} 원" if s_str.isdigit() else f"{s_str} 원")

            pl_str = item['rlzt_pl']
            pl_item = QTableWidgetItem(f"{int(pl_str):,} 원" if pl_str.lstrip('-').isdigit() else f"{pl_str} 원")

            rt_item = QTableWidgetItem(f"{item['prft_rt']}%")
            fee_tax_item = QTableWidgetItem(f"수수료 {item['fee']} / 세금 {item['tax']}")

            for col, itm in enumerate([date_item, name_item, buy_item, sell_item, pl_item, rt_item, fee_tax_item]):
                itm.setTextAlignment(Qt.AlignCenter)
                if col == 4:
                    val_str = itm.text().replace(',', '').replace(' 원', '')
                    try:
                        fval = float(val_str)
                        if fval > 0:
                            itm.setForeground(QColor("#ef5350"))
                        elif fval < 0:
                            itm.setForeground(QColor("#26a69a"))
                    except ValueError:
                        pass
                self.table.setItem(row, col, itm)


class DailyJournalDialog(QDialog):
    def __init__(self, parent=None, api_client=None):
        super().__init__(parent)
        self.setWindowTitle("당일 매매일지 조회")
        self.resize(850, 600)
        self.api_client = api_client

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("<b>[당일 총괄 매매 요약]</b>"))
        summary_widget = QWidget()
        self.form_layout = QFormLayout(summary_widget)

        self.tot_pl_lbl = QLabel("0 원")
        self.tot_rt_lbl = QLabel("0.0%")
        self.tot_fee_tax_lbl = QLabel("0 원")
        self.tot_sttl_lbl = QLabel("0 원")

        self.form_layout.addRow("총 손익금액:", self.tot_pl_lbl)
        self.form_layout.addRow("총 수익률:", self.tot_rt_lbl)
        self.form_layout.addRow("총 매매수수료/세금:", self.tot_fee_tax_lbl)
        self.form_layout.addRow("총 정산금액:", self.tot_sttl_lbl)
        layout.addWidget(summary_widget)

        layout.addWidget(QLabel("<b>[종목별 상세 매매일지 목록]</b>"))
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["종목명", "매수평균가", "매도평균가", "매수수량", "매도수량", "실현손익금", "수익률", "수수료/세금"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        close_btn = QPushButton("확인")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.load_data()

    def load_data(self):
        if not self.api_client:
            return

        summary, items = self.api_client.get_daily_trading_journal()

        pl_val = summary.get('tot_rlzt_prft', '0')
        rt_val = summary.get('tot_prft_rt', '0.0')
        ft_val = summary.get('tot_fee_tax', '0')
        st_val = summary.get('tot_sttl_amt', '0')

        self.tot_pl_lbl.setText(f"{int(pl_val):,} 원" if pl_val.lstrip('-').isdigit() else f"{pl_val} 원")
        self.tot_rt_lbl.setText(f"{rt_val}%")
        self.tot_fee_tax_lbl.setText(f"{int(ft_val):,} 원" if ft_val.isdigit() else f"{ft_val} 원")
        self.tot_sttl_lbl.setText(f"{int(st_val):,} 원" if st_val.lstrip('-').isdigit() else f"{st_val} 원")

        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            name_item = QTableWidgetItem(item['stk_nm'])

            b_unp = item['buy_unp']
            buy_unp_item = QTableWidgetItem(f"{int(b_unp):,} 원" if b_unp.isdigit() else f"{b_unp} 원")

            s_unp = item['sell_unp']
            sell_unp_item = QTableWidgetItem(f"{int(s_unp):,} 원" if s_unp.isdigit() else f"{s_unp} 원")

            b_qty = item['buy_qty']
            buy_qty_item = QTableWidgetItem(f"{int(b_qty):,} 주" if b_qty.isdigit() else f"{b_qty} 주")

            s_qty = item['sell_qty']
            sell_qty_item = QTableWidgetItem(f"{int(s_qty):,} 주" if s_qty.isdigit() else f"{s_qty} 주")

            pl_str = item['rlzt_prft']
            pl_item = QTableWidgetItem(f"{int(pl_str):,} 원" if pl_str.lstrip('-').isdigit() else f"{pl_str} 원")

            rt_item = QTableWidgetItem(f"{item['prft_rt']}%")
            fee_tax_item = QTableWidgetItem(f"수수료 {item['fee']} / 세금 {item['tax']}")

            for col, itm in enumerate(
                    [name_item, buy_unp_item, sell_unp_item, buy_qty_item, sell_qty_item, pl_item, rt_item,
                     fee_tax_item]):
                itm.setTextAlignment(Qt.AlignCenter)
                if col in [5, 6]:
                    val_str = itm.text().replace(',', '').replace(' 원', '').replace('%', '')
                    try:
                        fval = float(val_str)
                        if fval > 0:
                            itm.setForeground(QColor("#ef5350"))
                        elif fval < 0:
                            itm.setForeground(QColor("#26a69a"))
                    except ValueError:
                        pass
                self.table.setItem(row, col, itm)


class MyAccountDialog(QDialog):
    def __init__(self, parent=None, current_user_name="사용자", api_client=None):
        super().__init__(parent)
        self.setWindowTitle("내 계좌 정보")
        self.resize(480, 600)
        self.user_name = current_user_name
        self.api_client = api_client
        self.settings = QSettings("KiwoomTrading", "AutoTrader")

        self.is_connected = self.api_client.check_connection() if self.api_client else False

        self.raw_account_no = ""
        self.cash_balance = "0 원"
        self.total_pnl = "0 원"
        self.total_eval = "0 원"
        self.crdt_secu_rt = "100.0%"
        self.eval_return_rate = "0.0%"
        self.realized_return_rate = "0.0%"
        self.today_total_return_rate = "0.0%"
        unexec, exec_cnt = 0, 0

        if self.api_client and self.is_connected:
            data = self.api_client.get_account_summary()
            self.raw_account_no = data.get('account_no', '')
            self.cash_balance = data.get('cash_balance', '0 원')
            self.total_pnl = data.get('total_profit_loss', '0 원')
            self.total_eval = data.get('total_eval_amount', '0 원')
            self.crdt_secu_rt = data.get('crdt_secu_rt', '100.0%')
            self.eval_return_rate = data.get('eval_return_rate', '0.0%')
            self.realized_return_rate = data.get('realized_return_rate', '0.0%')
            self.today_total_return_rate = data.get('today_total_return_rate', '0.0%')
            unexec, exec_cnt = self.api_client.get_trade_counts()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        top_bar_layout = QHBoxLayout()
        dialog_title = QLabel("<b>[내 계좌 정보]</b>")

        self.status_badge = QLabel()
        self.status_badge.setAlignment(Qt.AlignCenter)
        self.status_badge.setFixedSize(65, 26)
        self.update_status_badge()

        top_bar_layout.addWidget(dialog_title)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.status_badge)
        layout.addLayout(top_bar_layout)

        form_layout = QFormLayout()

        user_layout = QHBoxLayout()
        self.user_label = QLabel(f"<b>{self.user_name}</b>")
        change_name_btn = QPushButton("이름 변경")
        change_name_btn.setFixedWidth(80)
        change_name_btn.clicked.connect(self.change_user_name)
        user_layout.addWidget(self.user_label)
        user_layout.addWidget(change_name_btn)
        user_layout.addStretch()

        account_layout = QHBoxLayout()
        masked_acc = self.mask_account(self.raw_account_no)
        self.account_label = QLabel(f"<b>{masked_acc}</b>")

        self.show_acc_btn = QPushButton("보기")
        self.show_acc_btn.setFixedWidth(50)
        self.show_acc_btn.pressed.connect(lambda: self.account_label.setText(f"<b>{self.raw_account_no}</b>"))
        self.show_acc_btn.released.connect(
            lambda: self.account_label.setText(f"<b>{self.mask_account(self.raw_account_no)}</b>"))

        account_layout.addWidget(self.account_label)
        account_layout.addWidget(self.show_acc_btn)
        account_layout.addStretch()

        form_layout.addRow("이름:", user_layout)
        form_layout.addRow("계좌번호:", account_layout)

        layout.addLayout(form_layout)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(8)

        def create_card(title, value_str):
            card = QFrame()
            card.setStyleSheet("background-color: #181818; border: 1px solid #2d2d2d; border-radius: 4px;")
            l = QVBoxLayout(card)
            l.setContentsMargins(10, 8, 10, 8)
            l.setSpacing(2)
            l.addWidget(QLabel(f"<font color='#858585' size='2'>{title}</font>"))
            l.addWidget(QLabel(f"<b>{value_str}</b>"))
            return card

        grid_layout.addWidget(create_card("계좌 현금", self.cash_balance), 0, 0)
        grid_layout.addWidget(create_card("총 평가금액", self.total_eval), 0, 1)
        grid_layout.addWidget(create_card("평가손익", self.total_pnl), 1, 0)
        grid_layout.addWidget(create_card("평가손익률", self.eval_return_rate), 1, 1)
        grid_layout.addWidget(create_card("당일 총 수익률", self.today_total_return_rate), 2, 0)
        grid_layout.addWidget(create_card("실현손익률", self.realized_return_rate), 2, 1)
        grid_layout.addWidget(create_card("신용담보비율", self.crdt_secu_rt), 3, 0)
        grid_layout.addWidget(create_card("체결 / 미체결", f"체결 {exec_cnt} | 미체결 {unexec}"), 3, 1)

        layout.addLayout(grid_layout)
        layout.addStretch()

        close_btn = QPushButton("확인")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def mask_account(self, acc_no):
        if not acc_no or len(acc_no) <= 4:
            return "****"
        return acc_no[:-4] + "****"

    def update_status_badge(self):
        if self.is_connected:
            self.status_badge.setText("연동 O")
            self.status_badge.setStyleSheet("""
                background-color: #1b3b2b;
                color: #2ecc71;
                border: 1px solid #2ecc71;
                border-radius: 6px;
                font-weight: bold;
                font-size: 9pt;
            """)
        else:
            self.status_badge.setText("연동 X")
            self.status_badge.setStyleSheet("""
                background-color: #3b1b1b;
                color: #e74c3c;
                border: 1px solid #e74c3c;
                border-radius: 6px;
                font-weight: bold;
                font-size: 9pt;
            """)

    def change_user_name(self):
        new_name, ok = QInputDialog.getText(self, "사용자 이름 변경", "사용할 이름을 입력하세요:", text=self.user_name)
        if ok and new_name.strip():
            self.user_name = new_name.strip()
            self.user_label.setText(f"<b>{self.user_name}</b>")
            self.settings.setValue("user_name", self.user_name)


class DraggableTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.drag_start_pos = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            if (event.pos() - self.drag_start_pos).manhattanLength() > QApplication.startDragDistance():
                index = self.tabAt(self.drag_start_pos)
                if index != -1:
                    tab_text = self.tabText(index)
                    drag = QDrag(self)
                    mime_data = QMimeData()
                    mime_data.setText(tab_text)
                    drag.setMimeData(mime_data)
                    drag.exec(Qt.CopyAction | Qt.MoveAction)
                    return
        super().mouseMoveEvent(event)


class SelectionTreeWidget(QTreeWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.is_dragging = False
        self.initial_selection = []
        self.setAcceptDrops(True)
        self.settings = QSettings("KiwoomTrading", "AutoTrader")

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasText():
            stock_name = event.mimeData().text().strip()
            item = self.itemAt(event.position().toPoint())
            target_group = item if (item and self.main_window.is_group_item(item)) else (
                item.parent() if item else None)
            if target_group:
                new_stock = QTreeWidgetItem(target_group, [stock_name])
                new_stock.setFlags(
                    (new_stock.flags() & ~Qt.ItemIsEditable) | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
                new_stock.setBackground(0, QColor("#181818"))
                target_group.setExpanded(True)
                event.acceptProposedAction()
                self.main_window.save_tree_state()
                return
        super().dropEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.position().toPoint())
            if not item:
                self.origin = event.position().toPoint()
                self.is_dragging = True
                self.initial_selection = self.selectedItems()
                self.rubberBand.setGeometry(QRect(self.origin, QPoint()))
                self.rubberBand.show()
                if not (event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)):
                    self.clearSelection()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_dragging and (event.buttons() & Qt.LeftButton):
            current_pos = event.position().toPoint()
            rect = QRect(self.origin, current_pos).normalized()
            self.rubberBand.setGeometry(rect)
            if not (event.modifiers() & Qt.ControlModifier):
                self.clearSelection()
            for item in self.initial_selection:
                item.setSelected(True)
            for i in range(self.topLevelItemCount()):
                self._check_item_in_rect(self.topLevelItem(i), rect)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.rubberBand.hide()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.is_dragging:
            self.is_dragging = False
            self.rubberBand.hide()
            self.clearSelection()
            for item in self.initial_selection:
                item.setSelected(True)
            event.accept()
            return
        elif event.key() == Qt.Key_Delete:
            for item in self.selectedItems():
                parent = item.parent()
                if parent:
                    parent.removeChild(item)
                else:
                    idx = self.indexOfTopLevelItem(item)
                    if idx != -1:
                        self.takeTopLevelItem(idx)
            event.accept()
            self.main_window.save_tree_state()
            return
        super().keyPressEvent(event)

    def _check_item_in_rect(self, item, rect):
        index = self.indexFromItem(item)
        if index.isValid() and rect.intersects(self.visualRect(index)):
            item.setSelected(True)
        for i in range(item.childCount()):
            self._check_item_in_rect(item.child(i), rect)


class CandleChartWidget(QWidget):
    def __init__(self, stock_name, api_client, parent=None):
        super().__init__(parent)
        self.stock_name = stock_name
        self.api_client = api_client
        self.candles = []
        self.load_data()

    def load_data(self):
        self.candles = self.api_client.get_chart_data(self.stock_name)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width, height = self.width(), self.height()
        painter.fillRect(0, 0, width, height, QColor("#141414"))

        if not self.candles:
            painter.setPen(QColor("#777777"))
            painter.drawText(QRectF(0, 0, width, height), Qt.AlignCenter, f"{self.stock_name} 데이터 없음")
            return

        min_p = min(c['low'] for c in self.candles)
        max_p = max(c['high'] for c in self.candles)
        p_range = max_p - min_p if max_p != min_p else 1

        margin_t, margin_b, margin_r, margin_l = 10, 10, 60, 10
        chart_h = (height - (margin_t + margin_b)) * 0.75

        avail_w = width - (margin_l + margin_r)
        c_width = max(3, avail_w / len(self.candles) - 4)

        for i, c in enumerate(self.candles):
            x = margin_l + i * (avail_w / len(self.candles)) + c_width / 2
            y_open = margin_t + chart_h * (1.0 - (c['open'] - min_p) / p_range)
            y_close = margin_t + chart_h * (1.0 - (c['close'] - min_p) / p_range)
            y_high = margin_t + chart_h * (1.0 - (c['high'] - min_p) / p_range)
            y_low = margin_t + chart_h * (1.0 - (c['low'] - min_p) / p_range)

            color = QColor("#ef5350") if c['close'] >= c['open'] else QColor("#26a69a")
            painter.setPen(QPen(color, 1))
            painter.drawLine(QPointF(x, y_high), QPointF(x, y_low))
            painter.fillRect(QRectF(x - c_width / 2, min(y_open, y_close), c_width, max(1.0, abs(y_close - y_open))),
                             color)


class TradingUI(QMainWindow):
    def __init__(self, api_client):
        super().__init__()
        self.setWindowTitle("파일 박스형 관심종목 트레이딩 프로그램")
        self.resize(1250, 800)
        self.showMaximized()

        self.api_client = api_client
        self.settings = QSettings("KiwoomTrading", "AutoTrader")
        self.current_user_name = self.settings.value("user_name", "사용자")
        self.stock_list = self.api_client.get_stock_list()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)

        top_layout = QHBoxLayout()
        search_container = QVBoxLayout()
        search_container.setSpacing(0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("종목명을 입력하세요")
        self.search_input.textEdited.connect(self.on_text_edited)
        self.search_input.returnPressed.connect(self.on_search)

        self.suggestion_list = QListWidget(self)
        self.suggestion_list.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.suggestion_list.hide()
        self.suggestion_list.itemClicked.connect(self.on_suggestion_clicked)

        search_container.addWidget(self.search_input)

        self.search_btn = QPushButton("검색")
        self.search_btn.clicked.connect(self.on_search)

        top_layout.addLayout(search_container, 3)
        top_layout.addWidget(self.search_btn)
        top_layout.addStretch(5)

        self.detail_btn = QPushButton("계좌 현금 및 증거금 상세 조회")
        self.detail_btn.clicked.connect(self.open_detail_dialog_from_main)
        top_layout.addWidget(self.detail_btn)

        self.history_btn = QPushButton("체결 / 미체결 내역 조회")
        self.history_btn.clicked.connect(self.open_trade_history_dialog)
        top_layout.addWidget(self.history_btn)

        self.portfolio_btn = QPushButton("보유종목 잔고 조회")
        self.portfolio_btn.clicked.connect(self.open_portfolio_dialog)
        top_layout.addWidget(self.portfolio_btn)

        self.realized_pl_btn = QPushButton("실현손익 및 통계 조회")
        self.realized_pl_btn.clicked.connect(self.open_realized_pl_dialog)
        top_layout.addWidget(self.realized_pl_btn)

        self.daily_journal_btn = QPushButton("당일 매매일지 조회")
        self.daily_journal_btn.clicked.connect(self.open_daily_journal_dialog)
        top_layout.addWidget(self.daily_journal_btn)

        self.my_btn = QPushButton("my")
        self.my_btn.setFixedSize(45, 32)
        self.my_btn.clicked.connect(self.open_my_dialog)
        top_layout.addWidget(self.my_btn)

        main_layout.addLayout(top_layout)

        body_splitter = QSplitter(Qt.Horizontal)

        self.tree_widget = SelectionTreeWidget(self, self)
        self.tree_widget.setHeaderLabel("관심 그룹 박스")
        self.tree_widget.setIndentation(24)
        self.tree_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree_widget.setExpandsOnDoubleClick(False)
        self.tree_widget.setDragEnabled(True)
        self.tree_widget.setAcceptDrops(True)
        self.tree_widget.setDropIndicatorShown(True)
        self.tree_widget.setDragDropMode(QTreeWidget.InternalMove)
        self.tree_widget.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.show_tree_context_menu)
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        self.tree_widget.itemChanged.connect(lambda item, col: self.save_tree_state())

        self.load_tree_state()
        body_splitter.addWidget(self.tree_widget)

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(DraggableTabBar(self.tab_widget))
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        right_layout.addWidget(self.tab_widget)
        body_splitter.addWidget(right_container)
        body_splitter.setSizes([280, 970])
        main_layout.addWidget(body_splitter)

    def save_tree_state(self):
        """트리 위젯의 전체 구조를 JSON으로 직렬화하여 QSettings에 저장"""

        def serialize_item(item):
            children = [serialize_item(item.child(i)) for i in range(item.childCount())]
            return {
                "text": item.text(0),
                "is_stock": self.is_stock_item(item),
                "children": children
            }

        root_items = []
        for i in range(self.tree_widget.topLevelItemCount()):
            root_items.append(serialize_item(self.tree_widget.topLevelItem(i)))

        try:
            json_str = json.dumps(root_items, ensure_ascii=False)
            self.settings.setValue("tree_state", json_str)
        except Exception:
            pass

    def load_tree_state(self):
        """저장된 트리 구조를 불러와 복원"""
        json_str = self.settings.value("tree_state", "")
        if not json_str:
            # 기본값 설정
            default_node = QTreeWidgetItem(self.tree_widget, ["기본 그룹"])
            default_node.setFlags(
                default_node.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
            default_node.setBackground(0, QColor("#1c1c1c"))
            self.tree_widget.expandAll()
            return

        try:
            root_items = json.loads(json_str)
            self.tree_widget.clear()

            def deserialize_item(parent, data):
                text = data.get("text", "그룹")
                is_stock = data.get("is_stock", False)
                node = QTreeWidgetItem(parent, [text])
                if is_stock:
                    node.setFlags((node.flags() & ~Qt.ItemIsEditable) | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
                    node.setBackground(0, QColor("#181818"))
                else:
                    node.setFlags(node.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
                    node.setBackground(0, QColor("#1c1c1c"))

                for child_data in data.get("children", []):
                    deserialize_item(node, child_data)

            for data in root_items:
                deserialize_item(self.tree_widget, data)

            self.tree_widget.expandAll()
        except Exception:
            default_node = QTreeWidgetItem(self.tree_widget, ["기본 그룹"])
            default_node.setFlags(
                default_node.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
            default_node.setBackground(0, QColor("#1c1c1c"))
            self.tree_widget.expandAll()

    def is_group_item(self, item):
        return item.childCount() > 0 or item.parent() is None or not self.is_stock_item(item)

    def show_tree_context_menu(self, pos):
        item = self.tree_widget.itemAt(pos)
        menu = QMenu(self)
        if item:
            is_group = self.is_group_item(item)
            if is_group:
                rename_action = menu.addAction("그룹 이름 변경")
                curr_title = self.tab_widget.tabText(
                    self.tab_widget.currentIndex()) if self.tab_widget.count() > 0 else ""
                add_stock_action = menu.addAction(f"이 그룹에 '{curr_title}' 추가") if curr_title else None
                add_sub_action = menu.addAction("하위 그룹 추가")
            delete_action = menu.addAction("삭제")

            action = menu.exec(self.tree_widget.mapToGlobal(pos))
            if item and is_group and action == rename_action:
                self.tree_widget.editItem(item, 0)
            elif item and is_group and add_stock_action and action == add_stock_action:
                new_stock = QTreeWidgetItem(item, [curr_title])
                new_stock.setFlags(
                    (new_stock.flags() & ~Qt.ItemIsEditable) | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
                new_stock.setBackground(0, QColor("#181818"))
                item.setExpanded(True)
                self.save_tree_state()
            elif item and is_group and action == add_sub_action:
                name, ok = QInputDialog.getText(self, "하위 그룹 추가", "하위 그룹 이름을 입력하세요:")
                if ok and name.strip():
                    new_item = QTreeWidgetItem(item, [name.strip()])
                    new_item.setFlags(
                        new_item.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
                    new_item.setBackground(0, QColor("#1c1c1c"))
                    item.setExpanded(True)
                    self.save_tree_state()
            elif action == delete_action:
                parent = item.parent()
                if parent:
                    parent.removeChild(item)
                else:
                    idx = self.tree_widget.indexOfTopLevelItem(item)
                    if idx != -1:
                        self.tree_widget.takeTopLevelItem(idx)
                self.save_tree_state()
        else:
            new_group_action = menu.addAction("새 파일 박스(그룹) 만들기")
            action = menu.exec(self.tree_widget.mapToGlobal(pos))
            if action == new_group_action:
                name, ok = QInputDialog.getText(self, "새 그룹 만들기", "새 그룹 이름을 입력하세요:")
                if ok and name.strip():
                    new_item = QTreeWidgetItem(self.tree_widget, [name.strip()])
                    new_item.setFlags(
                        new_item.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
                    new_item.setBackground(0, QColor("#1c1c1c"))
                    self.save_tree_state()

    def is_stock_item(self, item):
        return item.childCount() == 0 and item.parent() is not None and not (item.flags() & Qt.ItemIsEditable)

    def on_tree_item_clicked(self, item, column):
        if self.is_stock_item(item):
            stock_name = item.text(column).strip()
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabText(i) == stock_name:
                    self.tab_widget.setCurrentIndex(i)
                    return
            self.add_trading_tab(stock_name)

    def add_trading_tab(self, title):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(4, 4, 4, 4)

        main_splitter = QSplitter(Qt.Horizontal)
        left_splitter = QSplitter(Qt.Vertical)

        candle_widget = CandleChartWidget(title, self.api_client)
        left_splitter.addWidget(candle_widget)

        bottom_widget = QWidget()
        b_layout = QHBoxLayout(bottom_widget)
        b_layout.setContentsMargins(0, 4, 0, 0)

        memo_text = QTextEdit()
        memo_text.setPlaceholderText(f"{title} 투자 메모를 입력하세요...")

        history_text = QTextEdit()
        history_text.setReadOnly(True)

        b_layout.addWidget(memo_text, 1)
        b_layout.addWidget(history_text, 1)
        left_splitter.addWidget(bottom_widget)
        left_splitter.setSizes([500, 180])
        main_splitter.addWidget(left_splitter)

        right_splitter = QSplitter(Qt.Vertical)

        info_text = QTextEdit()
        info_text.setReadOnly(True)
        right_splitter.addWidget(info_text)

        order_widget = QWidget()
        o_layout = QVBoxLayout(order_widget)
        o_layout.setContentsMargins(4, 4, 4, 4)
        o_layout.addWidget(QLabel("<b>간편 주문</b>"))

        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("수량:"))
        qty_input = QLineEdit("1")
        qty_input.setAlignment(Qt.AlignCenter)
        qty_input.setValidator(QIntValidator(1, 9999, self))
        qty_layout.addWidget(qty_input)

        minus_btn, plus_btn = QPushButton("-"), QPushButton("+")
        minus_btn.setFixedWidth(35)
        plus_btn.setFixedWidth(35)
        minus_btn.clicked.connect(lambda: qty_input.setText(str(max(1, int(qty_input.text() or 1) - 1))))
        plus_btn.clicked.connect(lambda: qty_input.setText(str(int(qty_input.text() or 1) + 1)))

        qty_layout.addWidget(minus_btn)
        qty_layout.addWidget(plus_btn)
        o_layout.addLayout(qty_layout)

        btn_layout = QHBoxLayout()
        buy_btn = QPushButton(f"{title} 매수")
        buy_btn.setObjectName("BuyButton")
        buy_btn.clicked.connect(lambda: self.on_trade_executed(title, "매수", qty_input.text()))

        sell_btn = QPushButton(f"{title} 매도")
        sell_btn.setObjectName("SellButton")
        sell_btn.clicked.connect(lambda: self.on_trade_executed(title, "매도", qty_input.text()))

        btn_layout.addWidget(buy_btn)
        btn_layout.addWidget(sell_btn)
        o_layout.addLayout(btn_layout)

        right_splitter.addWidget(order_widget)
        right_splitter.setSizes([460, 220])
        main_splitter.addWidget(right_splitter)

        main_splitter.setSizes([750, 250])
        layout.addWidget(main_splitter)

        self.tab_widget.addTab(tab, title)
        self.tab_widget.setCurrentWidget(tab)

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)

    def on_text_edited(self, text):
        text = text.strip()
        if not text:
            self.suggestion_list.hide()
            return
        matched = [s for s in self.stock_list if text.lower() in s.lower()]
        if matched:
            self.suggestion_list.clear()
            for item in matched:
                self.suggestion_list.addItem(item)
            pos = self.search_input.mapToGlobal(QPointF(0, self.search_input.height()).toPoint())
            self.suggestion_list.setGeometry(pos.x(), pos.y(), self.search_input.width(),
                                             min(120, len(matched) * 25 + 10))
            self.suggestion_list.show()
        else:
            self.suggestion_list.hide()

    def on_suggestion_clicked(self, item):
        self.search_input.setText(item.text())
        self.suggestion_list.hide()
        self.on_search()

    def on_search(self):
        self.suggestion_list.hide()
        keyword = self.search_input.text().strip()
        if keyword:
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabText(i) == keyword:
                    self.tab_widget.setCurrentIndex(i)
                    self.search_input.clear()
                    return
            self.add_trading_tab(keyword)
            self.search_input.clear()

    def open_my_dialog(self):
        dialog = MyAccountDialog(self, current_user_name=self.current_user_name, api_client=self.api_client)
        dialog.exec()
        self.current_user_name = dialog.user_name

    def open_detail_dialog_from_main(self):
        dialog = DepositDetailDialog(self, api_client=self.api_client)
        dialog.exec()

    def open_trade_history_dialog(self):
        dialog = TradeHistoryDialog(self, api_client=self.api_client)
        dialog.exec()

    def open_portfolio_dialog(self):
        dialog = PortfolioDialog(self, api_client=self.api_client)
        dialog.exec()

    def open_realized_pl_dialog(self):
        dialog = RealizedPLDialog(self, api_client=self.api_client)
        dialog.exec()

    def open_daily_journal_dialog(self):
        dialog = DailyJournalDialog(self, api_client=self.api_client)
        dialog.exec()

    def on_trade_executed(self, stock_name, action_type, qty):
        success = self.api_client.execute_order(stock_name, action_type, int(qty))
        if success:
            color_tag = "red" if action_type == "매수" else "teal"
            QMessageBox.information(self, "주문 완료",
                                    f"[{stock_name}] {qty}주 <font color='{color_tag}'><b>{action_type}</b></font> 주문이 API를 통해 정상 전송되었습니다.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)

    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.Accepted and login_dialog.api_client:
        main_window = TradingUI(login_dialog.api_client)
        main_window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)