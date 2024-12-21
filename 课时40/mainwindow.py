from PySide6 import QtWidgets, QtCore, QtGui

from vnpy.event import EventEngine, Event
from vnpy.trader.engine import MainEngine
from vnpy.trader.constant import Exchange
from vnpy.trader.event import EVENT_LOG
from vnpy.trader.object import ContractData, SubscribeRequest

from monitor import (
    TickMonitor,
    MarketMonitor,
    OrderMonitor,
    TradeMonitor,
    PositionMonitor,
    AccountMonitor,
    LogMonitor
)
from widget import TradingWidget, FlashWidget, LoginDialog


class MainWindow(QtWidgets.QMainWindow):
    """主体组件"""
    
    signal_log = QtCore.Signal(Event)
    
    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """构造函数"""
        super().__init__()

        self.main_engine = main_engine
        self.event_engine = event_engine

        self.init_ui()
        self.register_event()
        
    def init_ui(self) -> None:
        """初始化界面"""
        # 设置窗口标题
        self.setWindowTitle("我的专属交易平台")
        
        # 顶部菜单栏
        menubar = self.menuBar()
        sys_menu = menubar.addMenu("系统")
        sys_menu.addAction("登录", self.show_login_dialog)
        
        sys_menu.addAction("测试", self.run_test)
        
        # 底部状态栏
        self.statusBar().showMessage("程序启动")
        
        # 创建控件     
        self.edit = QtWidgets.QTextEdit()
        self.line = QtWidgets.QLineEdit()
        self.button = QtWidgets.QPushButton("订阅")
        
        # stylesheet = "color:blue;background-color:orange"
        # self.button.setStyleSheet(stylesheet)
        
        self.tick_monitor = TickMonitor(self.event_engine)
        
        # 标签控件
        label = QtWidgets.QLabel()
        label.setText("市场行情监控")
        label.setAlignment(QtCore.Qt.AlignCenter)
        
        # 下拉框控件
        self.combo = QtWidgets.QComboBox()
        
        exchanges = [
            Exchange.CFFEX.value,
            Exchange.SHFE.value,
            Exchange.DCE.value,
            Exchange.CZCE.value,
        ]
        
        self.combo.addItems(exchanges) # 传入一个list
        
        # 绑定触发
        self.button.clicked.connect(self.subscribe)
        
        # 交易控件
        self.trading_widget = TradingWidget(self.main_engine)
        
        # 闪电下单控件
        self.flash_widget = FlashWidget(self.main_engine, self.event_engine)
        
        # 监控表格
        self.order_monitor = OrderMonitor(self.event_engine)
        self.trade_monitor = TradeMonitor(self.event_engine)
        self.position_monitor = PositionMonitor(self.event_engine)
        self.account_monitor = AccountMonitor(self.event_engine)
        self.market_monitor = MarketMonitor(self.event_engine)
        self.log_monitor = LogMonitor(self.event_engine)
        
        # 网格布局
        grid = QtWidgets.QGridLayout()
        grid.addWidget(label, 0, 0, 1, 2)
        grid.addWidget(self.line, 2, 0)
        grid.addWidget(self.combo, 2, 1)
        grid.addWidget(self.button, 2, 2)
        grid.addWidget(self.edit, 3, 0, 1, 3)  # 第二行，第0列，占一行，占3列
        
        # 垂直布局
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addWidget(self.trading_widget)
        vbox.addWidget(self.flash_widget)
        
        # 垂直布局2
        tab1 = QtWidgets.QTabWidget()
        tab1.addTab(self.market_monitor, "行情")
        
        tab2 = QtWidgets.QTabWidget()
        tab2.addTab(self.order_monitor, "委托")
        tab2.addTab(self.trade_monitor, "成交")
        tab2.addTab(self.position_monitor, "持仓")
        
        tab3 = QtWidgets.QTabWidget()
        tab3.addTab(self.account_monitor, "资金")
        tab3.setMaximumHeight(100)
        
        tab4 = QtWidgets.QTabWidget()
        tab4.addTab(self.log_monitor, "日志")
        
        vbox2 = QtWidgets.QVBoxLayout()
        vbox2.addWidget(tab1)
        vbox2.addWidget(tab2)
        vbox2.addWidget(tab3)
        vbox2.addWidget(tab4)
        
        # 水平布局
        hbox = QtWidgets.QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addLayout(vbox2)
        hbox.addWidget(self.tick_monitor)
        
        widget = QtWidgets.QWidget()
        widget.setLayout(hbox)
        self.setCentralWidget(widget)
        
    def register_event(self) -> None:
        """注册事件监听"""
        self.signal_log.connect(self.process_log_event)
        self.event_engine.register(EVENT_LOG, self.signal_log.emit)
        
    def subscribe(self) -> None:
        """订阅合约行情"""
        # 获取合约
        symbol: str = self.line.text()
        exchange_str = self.combo.currentText()
        vt_symbol: str = f"{symbol}.{exchange_str}"
        
        # 查询合约数据
        contract: ContractData = self.main_engine.get_contract(vt_symbol)
        if not contract:
            self.edit.append(f"找不到合约{vt_symbol}")
            return
        self.edit.append(f"订阅合约{vt_symbol}")
        
        req = SubscribeRequest(contract.symbol, contract.exchange)
        self.main_engine.subscribe(req, contract.gateway_name)
        
    def show_login_dialog(self) -> None:
        """显示连接登录控件"""
        login_dialog = LoginDialog(self.main_engine)
        # 执行exec后程序处于阻塞状态，必须取消或者执行
        n = login_dialog.exec()
        
        if n == login_dialog.Accepted:
            print("发起登录操作")
        else:
            print("取消登录操作")
        
    def process_log_event(self, event: Event) -> None:
        """处理日志事件"""
        log = event.data
        self.statusBar().showMessage(log.msg)
        
    def run_test(self) -> None:
        """运行功能测试"""
        # question/information/warning/critical
        n = QtWidgets.QMessageBox.warning(
            self,
            "信息提示框测试",
            "我们正在运行测试",
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Close | QtWidgets.QMessageBox.Cancel,
            QtWidgets.QMessageBox.Ok
        )
        
        print("信息提示框运行结果", n)
        
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """运行功能测试"""
        # 弹出信息框
        n = QtWidgets.QMessageBox.question(
            self,
            "关闭确认",
            "是否确认关闭交易系统",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        # 判断选择结果
        if n != QtWidgets.QMessageBox.Yes:
            event.ignore()
            return
        
        # 关闭main_engine
        self.main_engine.close()
        
        # 接受关闭事件
        event.accept()
