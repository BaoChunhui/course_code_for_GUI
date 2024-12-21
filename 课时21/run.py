from PySide6 import QtWidgets, QtCore

from vnpy.event import EventEngine, Event
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import TickData, ContractData, SubscribeRequest, OrderRequest
from vnpy.trader.event import EVENT_TICK
from vnpy.trader.utility import load_json
from vnpy.trader.constant import Exchange, Direction, Offset, OrderType

from vnpy_tts import TtsGateway as Gateway

gateway_name: str = Gateway.default_name

setting: set = {
    "用户名": "6358",
    "密码": "123456",
    "经纪商代码": "",
    "交易服务器": "121.37.80.177:20002",
    "行情服务器": "121.37.80.177:20004",
    "产品名称": "",
    "授权编码": ""
}

class TradingWidget(QtWidgets.QWidget):
    """交易控件"""
    
    def __init__(self, main_engine: MainEngine) -> None:
        """构造函数"""
        super().__init__()
        
        self.main_engine = main_engine
        
        self.init_ui()
        
    def init_ui(self) -> None:
        """初始化界面"""
        self.symbol_line = QtWidgets.QLineEdit()
        self.symbol_line.returnPressed.connect(self.update_symbol)
        
        self.exchange_combo = QtWidgets.QComboBox()
        self.exchange_combo.addItems([
            Exchange.CFFEX.value,
            Exchange.SHFE.value,
            Exchange.DCE.value,
            Exchange.CZCE.value
        ])
        
        self.direction_combo = QtWidgets.QComboBox()
        self.direction_combo.addItems([
            Direction.LONG.value,
            Direction.SHORT.value
        ])
        
        self.offset_combo = QtWidgets.QComboBox()
        self.offset_combo.addItems([
            Offset.OPEN.value,
            Offset.CLOSE.value,
            Offset.CLOSETODAY.value,
            Offset.CLOSEYESTERDAY.value
        ])
        
        self.price_spin = QtWidgets.QDoubleSpinBox()
        self.price_spin.setDecimals(3) # 设置成三位小数
        self.price_spin.setMinimum(1) # 设置下限
        self.price_spin.setMaximum(1000000) # 设置上限
        
        
        self.volume_spin = QtWidgets.QSpinBox()
        self.volume_spin.setSuffix("手") # 设置后缀
        self.volume_spin.setRange(1, 1000) # 设置范围
        
        button = QtWidgets.QPushButton("下单")
        button.clicked.connect(self.send_order)
        
        form = QtWidgets.QFormLayout()
        form.addRow("代码", self.symbol_line)
        form.addRow("交易所", self.exchange_combo)
        form.addRow("方向", self.direction_combo)
        form.addRow("开平", self.offset_combo)
        form.addRow("价格", self.price_spin)
        form.addRow("数量", self.volume_spin)
        form.addRow(button)
        
        self.setLayout(form)
        
    def send_order(self) -> None:
        """发送委托"""
        symbol = self.symbol_line.text()
        exchange = Exchange(self.exchange_combo.currentText())
        direction = Direction(self.direction_combo.currentText())
        offset = Offset(self.offset_combo.currentText())
        price = self.price_spin.value()
        volume = self.volume_spin.value()
        order_type = OrderType.LIMIT
        
        # 确认合约存在
        vt_symbol = f"{symbol}.{exchange.value}"
        contract = self.main_engine.get_contract(vt_symbol)
        if not contract:
            return
        
        # 发送委托请求
        req = OrderRequest(
            symbol=symbol,
            exchange=exchange,
            direction=direction,
            type=order_type,
            volume=volume,
            price=price,
            offset=offset
        )
        
        self.main_engine.send_order(req, contract.gateway_name)
        
    def update_symbol(self) -> None:
        """更新交易代码"""
        symbol = self.symbol_line.text()
        exchange_str = self.exchange_combo.currentText()
        vt_symbol = f"{symbol}.{exchange_str}"
        
        contract = self.main_engine.get_contract(vt_symbol)
        if contract:
            print("查询合约成功")
            self.price_spin.setSingleStep(contract.pricetick)
            self.volume_spin.setSingleStep(contract.min_volume)
        
class MainWidget(QtWidgets.QWidget):
    """主体组件"""
    
    # 在类中直接定义signal成员变量，而非__init__构造函数中
    signal = QtCore.Signal(Event)
    
    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """构造函数"""
        super().__init__()
        
        self.main_engine = main_engine
        self.event_engine = event_engine
        
        self.ticks = {}
        
        self.init_ui()
        self.register_event()
        
    def init_ui(self) -> None:
        """初始化界面"""
        # 创建控件
        self.edit = QtWidgets.QTextEdit()
        self.line = QtWidgets.QLineEdit()
        self.button = QtWidgets.QPushButton("订阅")
        
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
        
        # 网格布局
        grid = QtWidgets.QGridLayout()
        grid.addWidget(label, 0, 0, 1, 3)
        grid.addWidget(self.line, 1, 0)
        grid.addWidget(self.combo, 1, 1)
        grid.addWidget(self.button, 1, 2)
        grid.addWidget(self.edit, 2, 0, 1, 3)  # 第二行，第0列，占一行，占3列
        
        # 垂直布局
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addWidget(self.trading_widget)
        
        self.setLayout(vbox)
        
    def register_event(self) -> None:
        """注册事件监听"""
        # 绑定信号
        self.signal.connect(self.process_tick_event)
        
        # 注册监听
        self.event_engine.register(EVENT_TICK, self.signal.emit)
        
    def process_tick_event(self, event: Event) -> None:
        """处理行情数据"""
        tick: TickData = event.data
        self.ticks[tick.vt_symbol] = tick
        
        text = ""
        for t in self.ticks.values():
            text += f"{t.vt_symbol}\tbid:{t.bid_price_1}\task:{t.ask_price_1}\n"
            
        self.edit.setText(text)
        
    def subscribe(self) -> None:
        """订阅合约行情"""
        # 获取合约
        symbol: str = self.line.text()
        exchange_str = self.combo.currentText()
        vt_symbol: str = f"{symbol}.{exchange_str}"
        
        # 查询合约数据
        contract: ContractData = self.main_engine.get_contract(vt_symbol)
        if not contract:
            print(f"合约{vt_symbol}不存在")
            return
        
        req = SubscribeRequest(contract.symbol, contract.exchange)
        self.main_engine.subscribe(req, contract.gateway_name)
        

def run() -> None:
    """主程序入口"""
    # Qt应用（事件循环）
    qapp = QtWidgets.QApplication([])
    
    # 创建主引擎
    event_engine: EventEngine = EventEngine()
    main_engine: MainEngine = MainEngine(event_engine)
    main_engine.add_gateway(Gateway)
    
    # 创建控件
    widget = MainWidget(main_engine, event_engine)
    widget.show()
    
    # 连接交易接口
    main_engine.connect(setting, gateway_name)
    
    # 运行应用
    qapp.exec()

    # 关闭引擎
    main_engine.close()

if __name__ == '__main__':
    run()
