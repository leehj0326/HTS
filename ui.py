import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QSplitter, QLabel, QTextEdit, QMessageBox, QDialog, QFormLayout,
    QListWidget, QMenu, QAbstractItemView, QTableWidget, QTableWidgetItem, QHeaderView,
    QInputDialog, QRubberBand, QTabBar
)
from PySide6.QtCore import Qt, QRectF, QPointF, QRect, QPoint, QMimeData
from PySide6.QtGui import QPainter, QColor, QPen, QIntValidator, QDrag

# 파일 박스 및 토스 스타일을 반영한 다크 테마 QSS
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
QTreeWidget::drop-indicator {
    background-color: #007acc;
    height: 2px;
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
QTabBar::tab:hover {
    background-color: #353535;
    color: #ffffff;
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

            target_group = None
            if item:
                if self.main_window.is_group_item(item):
                    target_group = item
                else:
                    target_group = item.parent()

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
                top_item = self.topLevelItem(i)
                self._check_item_in_rect(top_item, rect)
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
            selected_items = self.selectedItems()
            if selected_items:
                for item in selected_items:
                    parent = item.parent()
                    if parent:
                        parent.removeChild(item)
                    else:
                        index = self.indexOfTopLevelItem(item)
                        if index != -1:
                            self.takeTopLevelItem(index)
                event.accept()
                return
        super().keyPressEvent(event)

    def _check_item_in_rect(self, item, rect):
        index = self.indexFromItem(item)
        if index.isValid():
            visual_rect = self.visualRect(index)
            if rect.intersects(visual_rect):
                item.setSelected(True)
        for i in range(item.childCount()):
            self._check_item_in_rect(item.child(i), rect)


class CandleChartWidget(QWidget):
    def __init__(self, stock_name, parent=None):
        super().__init__(parent)
        self.stock_name = stock_name
        self.candles = []

    def set_candles(self, candle_data):
        self.candles = candle_data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width = self.width()
        height = self.height()
        painter.fillRect(0, 0, width, height, QColor("#141414"))

        if not self.candles:
            painter.setPen(QColor("#777777"))
            painter.drawText(QRectF(0, 0, width, height), Qt.AlignCenter, "데이터가 없습니다. API 연동을 진행하세요.")
            return


class MyAccountDialog(QDialog):
    def __init__(self, parent=None, current_user_name="사용자"):
        super().__init__(parent)
        self.setWindowTitle("내 자산 및 보유 종목 현황")
        self.resize(600, 450)
        self.user_name = current_user_name

        layout = QVBoxLayout(self)

        summary_widget = QWidget()
        summary_layout = QFormLayout(summary_widget)

        # 사용자 이름 레이아웃 및 변경 버튼 구성
        user_layout = QHBoxLayout()
        self.user_label = QLabel(f"<b>{self.user_name}</b>")
        change_name_btn = QPushButton("이름 변경")
        change_name_btn.setFixedWidth(80)
        change_name_btn.clicked.connect(self.change_user_name)
        user_layout.addWidget(self.user_label)
        user_layout.addWidget(change_name_btn)
        user_layout.addStretch()

        self.total_asset_label = QLabel("<b>- 원</b>")
        self.total_pnl_label = QLabel("<b>-</b>")

        summary_layout.addRow("사용자:", user_layout)
        summary_layout.addRow("총평가금액:", self.total_asset_label)
        summary_layout.addRow("총평가손익:", self.total_pnl_label)
        layout.addWidget(summary_widget)

        layout.addWidget(QLabel("<b>[보유 주식 및 체결 내역]</b>"))

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["종목명", "보유수량", "매입단가", "평가손익", "상태"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        close_btn = QPushButton("확인")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def change_user_name(self):
        new_name, ok = QInputDialog.getText(self, "사용자 이름 변경", "사용할 이름을 입력하세요:", text=self.user_name)
        if ok and new_name.strip():
            self.user_name = new_name.strip()
            self.user_label.setText(f"<b>{self.user_name}</b>")
            # 메인 윈도우 창 등과 연동이 필요할 경우 여기서 처리 가능

    def set_account_data(self, user_info, portfolio_list):
        pass


class TradingUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("파일 박스형 관심종목 트레이딩 프로그램")
        self.resize(1250, 800)
        self.showMaximized()

        self.current_user_name = "사용자"  # 초기 지정 전 이름

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)

        self.stock_list = []

        # 1. 상단 영역
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

        # 2. 본문 영역
        body_splitter = QSplitter(Qt.Horizontal)

        # 2-1. 좌측 트리 영역
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

        # 2-2. 우측 영역 (상단 탭)
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
                current_tab_title = self.tab_widget.tabText(
                    self.tab_widget.currentIndex()) if self.tab_widget.count() > 0 else ""
                add_current_stock_action = None
                if current_tab_title:
                    add_current_stock_action = menu.addAction(f"이 그룹에 '{current_tab_title}' 추가")
                add_sub_action = menu.addAction("하위 그룹 추가")

            delete_action = menu.addAction("삭제")

            action = menu.exec(self.tree_widget.mapToGlobal(pos))

            if item and is_group and action == rename_action:
                self.tree_widget.editItem(item, 0)
            elif item and is_group and add_current_stock_action and action == add_current_stock_action:
                new_stock = QTreeWidgetItem(item, [current_tab_title])
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
                    index = self.tree_widget.indexOfTopLevelItem(item)
                    if index != -1:
                        self.tree_widget.takeTopLevelItem(index)
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

        main_content_splitter = QSplitter(Qt.Horizontal)
        left_sub_splitter = QSplitter(Qt.Vertical)

        candle_widget = CandleChartWidget(title)
        left_sub_splitter.addWidget(candle_widget)

        bottom_info_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_info_widget)
        bottom_layout.setContentsMargins(0, 4, 0, 0)

        memo_container = QVBoxLayout()
        memo_container.setContentsMargins(0, 0, 0, 0)
        memo_container.addWidget(QLabel("<b>종목 메모 / 특이사항</b>"))
        memo_text = QTextEdit()
        memo_text.setPlaceholderText(f"{title}에 대한 투자 포인트나 메모를 입력하세요...")
        memo_container.addWidget(memo_text)

        history_container = QVBoxLayout()
        history_container.setContentsMargins(0, 0, 0, 0)
        history_container.addWidget(QLabel("<b>최근 체결 / 매수·매도 현황</b>"))
        history_text = QTextEdit()
        history_text.setReadOnly(True)
        history_text.setPlainText("API 연동 대기 중...")
        history_container.addWidget(history_text)

        bottom_layout.addLayout(memo_container, 1)
        bottom_layout.addLayout(history_container, 1)

        left_sub_splitter.addWidget(bottom_info_widget)
        left_sub_splitter.setSizes([500, 180])
        main_content_splitter.addWidget(left_sub_splitter)

        right_sub_splitter = QSplitter(Qt.Vertical)

        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.addWidget(QLabel("<b>호가 정보</b>"))
        info_text = QTextEdit("API 연동 대기 중...")
        info_text.setReadOnly(True)
        info_layout.addWidget(info_text)
        right_sub_splitter.addWidget(info_widget)

        order_widget = QWidget()
        order_layout = QVBoxLayout(order_widget)
        order_layout.setContentsMargins(4, 4, 4, 4)
        order_layout.addWidget(QLabel("<b>간편 주문</b>"))

        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("수량:"))

        qty_input = QLineEdit("1")
        qty_input.setAlignment(Qt.AlignCenter)
        qty_input.setValidator(QIntValidator(1, 9999, self))
        qty_layout.addWidget(qty_input)

        minus_btn = QPushButton("-")
        plus_btn = QPushButton("+")
        minus_btn.setFixedWidth(35)
        plus_btn.setFixedWidth(35)

        def decrease_qty():
            val = max(1, int(qty_input.text() or 1) - 1)
            qty_input.setText(str(val))

        def increase_qty():
            val = int(qty_input.text() or 1) + 1
            qty_input.setText(str(val))

        minus_btn.clicked.connect(decrease_qty)
        plus_btn.clicked.connect(increase_qty)

        qty_layout.addWidget(minus_btn)
        qty_layout.addWidget(plus_btn)
        order_layout.addLayout(qty_layout)

        btn_layout = QHBoxLayout()
        buy_btn = QPushButton(f"{title} 매수")
        buy_btn.setObjectName("BuyButton")
        buy_btn.clicked.connect(lambda: self.on_trade_executed(title, "매수", qty_input.text()))

        sell_btn = QPushButton(f"{title} 매도")
        sell_btn.setObjectName("SellButton")
        sell_btn.clicked.connect(lambda: self.on_trade_executed(title, "매도", qty_input.text()))

        btn_layout.addWidget(buy_btn)
        btn_layout.addWidget(sell_btn)
        order_layout.addLayout(btn_layout)

        right_sub_splitter.addWidget(order_widget)
        right_sub_splitter.setSizes([460, 220])
        main_content_splitter.addWidget(right_sub_splitter)

        main_content_splitter.setSizes([750, 250])
        layout.addWidget(main_content_splitter)

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
        dialog = MyAccountDialog(self, current_user_name=self.current_user_name)
        dialog.exec()
        # 다이얼로그에서 변경된 이름을 메인 창에 반영
        self.current_user_name = dialog.user_name

    def on_trade_executed(self, stock_name, action_type, qty):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    window = TradingUI()
    window.show()
    sys.exit(app.exec())