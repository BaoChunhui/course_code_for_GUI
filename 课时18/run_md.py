from pathlib import Path

from PySide6 import QtWidgets, QtCore, QtGui

from vnpy.event import EventEngine, Event
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import TickData, ContractData, SubscribeRequest
from vnpy.trader.event import EVENT_TICK

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

class DataWidget(QtWidgets.QWidget):
    """市场行情组件"""
    
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
        
        # label.setText("市场行情监控")
        # label.setNum(123)
        # png_path = Path(__file__).parent.joinpath("capital.png")
        # pixmap = QtGui.QPixmap(str(png_path))
        # label.setPixmap(pixmap.scaled(100, 100))
        
        # label.setAlignment(QtCore.Qt.AlignCenter)
        # label.setAlignment(QtCore.Qt.AlignRight)
        # label.setAlignment(QtCore.Qt.AlignLeft)
        
        # label.setWordWrap(True) # 自动换行
        
        # html = "<b>行情监控</b>"  # <b>和</b>之间的字体加粗
        # html = '<a style="color:red;">市场监控</a>' # 红色字体
        html = '<a href="www.vnpy.com">Veighna主页</a>' # 网页链接
        label.setText(html)

        label.setOpenExternalLinks(True) # 允许点击打开外部链接
        
        # 绑定触发
        self.button.clicked.connect(self.subscribe)
        
        # 网格布局
        layout = QtWidgets.QGridLayout()
        layout.addWidget(label, 0, 0, 1, 2)
        layout.addWidget(self.line, 1, 0)
        layout.addWidget(self.button, 1, 1)
        layout.addWidget(self.edit, 2, 0, 1, 2)  # 第二行，第一列，占一行，占两列
        self.setLayout(layout)
        
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
        # 获取合约代码
        vt_symbol: str = self.line.text()
        
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
    widget = DataWidget(main_engine, event_engine)
    widget.show()
    
    # 连接交易接口
    main_engine.connect(setting, gateway_name)
    
    # 运行应用
    qapp.exec()
    
    # 关闭引擎
    main_engine.close()


if __name__ == '__main__':
    run()
