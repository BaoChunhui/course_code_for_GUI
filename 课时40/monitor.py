from PySide6 import QtWidgets, QtCore, QtGui
from typing import Dict
from datetime import datetime
from enum import Enum

from vnpy.event import EventEngine, Event
from vnpy.trader.event import EVENT_TICK, EVENT_LOG, EVENT_ORDER, EVENT_TRADE, EVENT_ACCOUNT, EVENT_POSITION
from vnpy.trader.object import TickData


class TickCell(QtWidgets.QTableWidgetItem):
    """Tick盘口监控表格单元"""
    
    def __init__(self, text: str = "") -> None:
        """构造函数"""
        super().__init__(text)
        
        font = QtGui.QFont("微软雅黑", 14)
        self.setFont(font)
        
        self.setTextAlignment(QtCore.Qt.AlignCenter)
        
        self.setBackground(QtGui.QColor("yellow"))
        
        if "多" in text:
            self.setForeground(QtGui.QColor("red"))
        elif "空" in text:
            self.setForeground(QtGui.QColor("green"))
            
            
class TickMonitor(QtWidgets.QTabWidget):
    """Tick盘口监控控件"""
    
    signal = QtCore.Signal(Event)
    
    def __init__(self, event_engine: EventEngine) -> None:
        """构造函数"""
        super().__init__()
        
        self.event_engine = event_engine
        
        self.ticks = {}
        self.tables = {}
        
        self.register_event()
        
    def get_table(self, vt_symbol: str) -> QtWidgets.QTableWidget:
        """初始化界面"""
        table = self.tables.get(vt_symbol, None)
        if table:
            return table
        
        # 创建表格
        table = QtWidgets.QTableWidget()
        self.tables[vt_symbol] = table
        self.addTab(table, vt_symbol)
        
        # 表头列表
        labels = ["代码", "最新价", "信息"]
        
        # 设置列数
        table.setColumnCount(len(labels))
         
        # 设置水平表头
        table.setHorizontalHeaderLabels(labels)
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        # 关闭垂直表头
        table.verticalHeader().setVisible(False)
        
        # 禁用表格编辑
        table.setEditTriggers(table.NoEditTriggers)
        
        return table
        
    def register_event(self) -> None:
        """处理Tick事件"""
        self.signal.connect(self.process_tick_event)
        self.event_engine.register(EVENT_TICK, self.signal.emit)
        
    def process_tick_event(self, event: Event) -> None:
        """处理Tick事件"""
        tick: TickData = event.data
        last_tick: TickData = self.ticks.get(tick.vt_symbol, None)
        self.ticks[tick.vt_symbol] = tick
        
        if not last_tick:
            return
        
        # 获取该合约的表格
        table = self.get_table(tick.vt_symbol)
        
        # 计算持仓变化
        oi_change: int = tick.open_interest - last_tick.open_interest
        
        if oi_change > 0:
            oi_str = "开"
        elif oi_change < 0:
            oi_str = "平"
        else:
            oi_str = "换"
            
        # 计算方向变化
        if tick.last_price >= last_tick.ask_price_1:
            direction_str = "多"
        elif tick.last_price <= last_tick.bid_price_1:
            direction_str = "空"
        else:
            direction_str = "双"
            
        # 获取当前行数
        row = table.rowCount()
        
        # 在尾部插入行（从索引0开始）
        table.insertRow(row)

        # 创建单元格
        # symbol_cell = QtWidgets.QTableWidgetItem(tick.vt_symbol)
        # price_cell = QtWidgets.QTableWidgetItem(str(tick.last_price))
        # info_cell = QtWidgets.QTableWidgetItem(f"{direction_str}{oi_str}")
        
        # 设置字体
        # font = QtGui.QFont("微软雅黑", 14)
        
        # symbol_cell.setFont(font)
        # price_cell.setFont(font)
        # info_cell.setFont(font)
        
        # 设置对齐
        # symbol_cell.setTextAlignment(QtCore.Qt.AlignCenter)
        # price_cell.setTextAlignment(QtCore.Qt.AlignCenter)
        # info_cell.setTextAlignment(QtCore.Qt.AlignCenter)
        
        # 设置背景颜色
        # symbol_cell.setBackground(QtGui.QColor("yellow"))
        # price_cell.setBackground(QtGui.QColor("yellow"))
        # info_cell.setBackground(QtGui.QColor("yellow"))
        
        # 设置字体颜色
        # if direction_str == "多":
        #     info_cell.setForeground(QtGui.QColor("red"))
        # elif direction_str == "空":
        #     info_cell.setForeground(QtGui.QColor("green"))
            
        # 使用自定义单元格
        symbol_cell = TickCell(tick.vt_symbol)
        price_cell = TickCell(str(tick.last_price))
        info_cell = TickCell(f"{direction_str}{oi_str}")

        # 设置单元格
        table.setItem(row, 0, symbol_cell)
        table.setItem(row, 1, price_cell)
        table.setItem(row, 2, info_cell)
        
        # 滚动到底部
        table.scrollToBottom()
        
        
class MonitorCell(QtWidgets.QTableWidgetItem):
    """通用监控表格单元格"""
    
    def __init__(self, content: object = None) -> None:
        """构造函数"""
        super().__init__()
        
        font = QtGui.QFont("微软雅黑", 12)
        self.setFont(font)
        
        self.setTextAlignment(QtCore.Qt.AlignCenter)
        
        if content:
            self.set_content(content)   
        
    def set_content(self, content: object) -> None:
        """设置内容"""
        if type(content) in {float, int}:
            content = str(content)
        elif isinstance(content, Enum):
            content = content.value
        elif isinstance(content, datetime):
            content = content.strftime("%H:%M:%S")
        
        self.setText(content)

        
class BaseMonitor(QtWidgets.QTableWidget):
    """通用数据监控控件"""
    
    signal = QtCore.Signal(Event)
    
    headers: Dict[str, str] = {}
    event_type: str = ""
    data_key: str = ""
    
    def __init__(self, event_engine: EventEngine) -> None:
        """构造函数"""
        super().__init__()
        
        self.event_engine = event_engine
        
        self.cells: Dict[str, Dict(str, QtWidgets.QTableWidgetItem)] = {}
        
        self.init_ui()
        self.register_event()
        
    def init_ui(self) -> None:
        """初始化界面"""
        # 表头列表
        labels = list(self.headers.keys())
        
        # 设置列数
        self.setColumnCount(len(labels))
        
        # 设置水平表头
        self.setHorizontalHeaderLabels(labels)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        # 关闭垂直表头
        self.verticalHeader().setVisible(False)
        
        # 禁用表格编辑
        self.setEditTriggers(self.NoEditTriggers)
        
        # 设置最窄宽度
        self.setMinimumWidth(1200)
        
    def register_event(self) -> None:
        """注册事件监听"""
        self.signal.connect(self.process_event)
        self.event_engine.register(self.event_type, self.signal.emit)
        
    def process_event(self, event: Event) -> None:
        """处理事件"""
        data: object = event.data
        
        # 如果配置了主键，则采用刷新更新
        if self.data_key:
            key: str = getattr(data, self.data_key)
            
            # 如果是新的数据
            if key not in self.cells:
                self.insert_new_row(key, data)
            else:
                self.update_old_row(key, data)
        else:
            self.insert_new_row("", data)
        
    def insert_new_row(self, key: str, data: object) -> None:
        """插入新的一行"""
        # 在头部插入行
        self.insertRow(0)
        
        # 添加单元格
        cells = {}
            
        for colume, field_name in enumerate(self.headers.values()):
            field_value: object = getattr(data, field_name)
            cell: MonitorCell = MonitorCell(field_value)
            self.setItem(0, colume, cell)
            cells[field_name] = cell
                
        self.cells[key] = cells
        
    def update_old_row(self, key: str, data: object) -> None:
        """更新老的一行"""
        cells = self.cells[key]
            
        for field_name, cell in cells.items():
            field_value: object = getattr(data, field_name)
            cell.set_content(field_value)
            
            
class OrderMonitor(BaseMonitor):
    """简化实现的委托监控控件"""
    headers: Dict[str, str] = {
        "代码": "symbol",
        "交易所": "exchange",
        "委托号": "orderid",
        "类别": "type",
        "方向": "direction",
        "开平": "offset",
        "价格": "price",
        "数量": "volume",
        "成交": "traded",
        "状态": "status",
        "时间": "datetime",
        "来源": "reference"
    }
    event_type: str = EVENT_ORDER
    data_key: str = "vt_orderid"
    
    
class TradeMonitor(BaseMonitor):
    """成交监控控件"""
    headers: Dict[str, str] = {
        "代码": "symbol",
        "交易所": "exchange",
        "委托号": "orderid",
        "成交号": "tradeid",
        "方向": "direction",
        "开平": "offset",
        "价格": "price",
        "数量": "volume",
        "时间": "datetime"
    }
    event_type: str = EVENT_TRADE
    data_key: str = "vt_orderid"


class PositionMonitor(BaseMonitor):
    """持仓监控控件"""
    headers: Dict[str, str] = {
        "代码": "symbol",
        "交易所": "exchange",
        "方向": "direction",
        "数量": "volume",
        "昨仓": "yd_volume",
        "冻结": "frozen",
        "均价": "price",
        "盈亏": "pnl",
    }
    event_type: str = EVENT_POSITION
    data_key: str = "vt_positionid"
    
    
class AccountMonitor(BaseMonitor):
    """资金监控控件"""
    headers: Dict[str, str] = {
        "账户": "accountid",
        "资金": "balance",
        "冻结": "frozen",
        "可用": "available"
    }
    event_type: str = EVENT_ACCOUNT
    data_key: str = "vt_accountid"
    
    
class LogMonitor(BaseMonitor):
    """日志监控控件"""
    headers: Dict[str, str] = {
        "时间": "time",
        "内容": "msg"
    }
    event_type: str = EVENT_LOG
    
    def __init__(self, event_engine: EventEngine) -> None:
        super().__init__(event_engine)
        
        self.horizontalHeader().setSectionResizeMode(0, self.horizontalHeader().ResizeToContents)
    
    
class MarketMonitor(BaseMonitor):
    """行情监控控件"""
    headers: Dict[str, str] = {
        "代码": "symbol",
        "交易所": "exchange",
        "时间": "datetime",
        "成交量": "volume",
        "成交额": "turnover",
        "持仓量": "open_interest",
        "最新价": "last_price",
        "开盘价": "open_price",
        "最高价": "high_price",
        "最低价": "low_price",
        "买量": "bid_volume_1",
        "买价": "bid_price_1",
        "卖价": "ask_price_1",
        "卖量": "ask_volume_1"
    }
    event_type: str = EVENT_TICK
    data_key: str = "vt_symbol"
