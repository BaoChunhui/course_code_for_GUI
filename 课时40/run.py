import ctypes
from pathlib import Path

from PySide6 import QtWidgets, QtGui
import qdarkstyle

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy_tts import TtsGateway as Gateway

from mainwindow import MainWindow

gateway_name: str = Gateway.default_name
        

def run() -> None:
    """主程序入口"""
    # Qt应用（事件循环）
    qapp = QtWidgets.QApplication([])
    
    # 设置全局默认字体
    font = QtGui.QFont("微软雅黑", 12)
    qapp.setFont(font)
    
    # 应用黑色皮肤
    qapp.setStyleSheet(qdarkstyle.load_stylesheet())
    
    # 应用Material皮肤
    # qt_material.apply_stylesheet(qapp, "light_blue.xml")
    
    # 获取ico文件绝对路径
    icon_path = Path(__file__).parent.joinpath("logo.ico")
    
    # 设置应用图标
    icon = QtGui.QIcon(str(icon_path))
    qapp.setWindowIcon(icon)
    
    # 设置进程id，否则任务栏图标无法显示
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("gui demo")
    
    # 创建主引擎
    event_engine: EventEngine = EventEngine()
    main_engine: MainEngine = MainEngine(event_engine)
    main_engine.add_gateway(Gateway)
    
    # 创建控件
    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()
    
    # 运行应用
    qapp.exec()


if __name__ == '__main__':
    run()
