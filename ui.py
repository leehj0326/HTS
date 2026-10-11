# ui.py
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QSplitter, QLabel, QTextEdit, QMessageBox, QDialog, QFormLayout,
    QListWidget, QMenu, QAbstractItemView, QInputDialog, QRubberBand, QTabBar, QCheckBox
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


class MyAccountDialog(QDialog):
    def __init__(self, parent=None, current_user_name="사용자", api_client=None):
        super().__init__(parent)
        self.setWindowTitle("내 계좌 정보")
        self.resize(450, 300)
        self.user_name = current_user_name
        self.api_client = api_client

        self.is_connected = self.api_client.check_connection() if self.api_client else False

        self.raw_account_no = ""
        self.cash_balance = "0 원"
        self.total_pnl = "0 원 (0%)"

        if self.api_client and self.is_connected:
            data = self.api_client.get_account_summary()
            self.raw_account_no = data.get('account_no', '')
            self.cash_balance = data.get('cash_balance', '0 원')
            self.total_pnl = data.get('total_profit_loss', '0 원 (0%)')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # 상단: 타이틀 및 연동 확인 UI 뱃지
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

        # 1. 이름
        user_layout = QHBoxLayout()
        self.user_label = QLabel(f"<b>{self.user_name}</b>")
        change_name_btn = QPushButton("이름 변경")
        change_name_btn.setFixedWidth(80)
        change_name_btn.clicked.connect(self.change_user_name)
        user_layout.addWidget(self.user_label)
        user_layout.addWidget(change_name_btn)
        user_layout.addStretch()

        # 2. 계좌번호 (뒤 4자리 마스킹 + 누르고 있을 때 보기 버튼)
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

        # 3. 현금잔고
        self.cash_label = QLabel(f"<b>{self.cash_balance}</b>")

        # 4. 평가손익 (금액, %)
        self.total_pnl_label = QLabel(f"<b>{self.total_pnl}</b>")

        form_layout.addRow("이름:", user_layout)
        form_layout.addRow("계좌번호:", account_layout)
        form_layout.addRow("현금잔고:", self.cash_label)
        form_layout.addRow("평가손익:", self.total_pnl_label)

        layout.addLayout(form_layout)
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
        self.current_user_name = "사용자"
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

        self.my_btn = QPushButton("my")
        self.my_btn.clicked.connect(self.open_my_dialog)

        top_layout.addLayout(search_container, 3)
        top_layout.addWidget(self.search_btn)
        top_layout.addStretch(5)
        top_layout.addWidget(self.my_btn)
        main_layout.addLayout(top_layout)

        body_splitter = QSplitter(Qt.Horizontal)

        self.tree_widget = SelectionTreeWidget(self)
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

        def create_group_node(parent, text):
            node = QTreeWidgetItem(parent, [text])
            node.setFlags(node.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
            node.setBackground(0, QColor("#1c1c1c"))
            return node

        create_group_node(self.tree_widget, "기본 그룹")
        self.tree_widget.expandAll()
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
            elif item and is_group and action == add_sub_action:
                name, ok = QInputDialog.getText(self, "하위 그룹 추가", "하위 그룹 이름을 입력하세요:")
                if ok and name.strip():
                    new_item = QTreeWidgetItem(item, [name.strip()])
                    new_item.setFlags(
                        new_item.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
                    new_item.setBackground(0, QColor("#1c1c1c"))
                    item.setExpanded(True)
            elif action == delete_action:
                parent = item.parent()
                if parent:
                    parent.removeChild(item)
                else:
                    idx = self.tree_widget.indexOfTopLevelItem(item)
                    if idx != -1:
                        self.tree_widget.takeTopLevelItem(idx)
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