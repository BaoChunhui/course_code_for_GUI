from time import sleep

from PySide6 import QtWidgets

from vnpy.event import EventEngine, Event
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import TickData, SubscribeRequest
from vnpy.trader.constant import Exchange
from vnpy.trader.event import EVENT_TICK

from vnpy_tts import TtsGateway as Gateway
# from vnpy_ctp import CtpGateway as Gateway


gateway_name: str = Gateway.default_name

setting: set = {
    "用户名": "",
    "密码": "",
    "经纪商代码": "",
    "交易服务器": "121.37.80.177:20002",
    "行情服务器": "121.37.80.177:20004",
    "产品名称": "",
    "授权编码": ""
}

    
def run() -> None:
    """主程序入口"""
    # Qt应用（事件循环）
    qapp = QtWidgets.QApplication([])
    
    # 创建控件
    edit = QtWidgets.QTextEdit()
    edit.show()
    
    # 创建事件引擎的对象，传入主引擎中创建主引擎，然后在主引擎中添加Gateway，创建主引擎成功
    event_engine: EventEngine = EventEngine()
    main_engine: MainEngine = MainEngine(event_engine)
    main_engine.add_gateway(Gateway)
    edit.append("创建主引擎成功")
    
    # 定义行情打印函数
    def print_tick(event: Event) -> None:
        """打印行情数据"""
        tick: TickData = event.data
        edit.append(str(tick))
    
    # 注册行情事件监听，如果tick数据到达这个类型的事件发生，则调用上面定义的print_tick函数
    event_engine.register(EVENT_TICK, print_tick)
    edit.append("注册行情事件监听")
    
    # 用主引擎连接柜台
    main_engine.connect(setting, gateway_name)
    edit.append("连接交易接口")
    
    sleep(5)
    
    # 创建SubscribeRequest类的对象，传入main_engine.subscribe中订阅行情
    req = SubscribeRequest("rb2306", Exchange.SHFE)
    main_engine.subscribe(req, gateway_name)
    edit.append(f"订阅行情推送{req.vt_symbol}")
    
    # 运行应用，同时也具有阻塞线程的作用
    qapp.exec()
    
    # 阻塞线程，直到遇到一个键盘上的输入
    # input()
    
    # 关闭主引擎
    main_engine.close()

    
if __name__ == '__main__':
    run()
