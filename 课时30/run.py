from functools import partial

from PySide6 import QtWidgets

def run() -> None:
    """主程序入口"""
    # Qt应用（事件循环）
    qapp = QtWidgets.QApplication([])
    
    # 创建两个控件
    edit1 = QtWidgets.QTextEdit()
    edit1.append("1号编辑框")
    
    edit2 = QtWidgets.QTextEdit()
    edit2.append("2号编辑框")
    
    # 创建标签页
    tab = QtWidgets.QTabWidget()
    
    # 添加到标签页
    tab.addTab(edit1, "1号")
    tab.addTab(edit2, "2号")
    
    # 设置标签形状
    tab.setTabShape(tab.TabShape.Rounded)
    
    # 设置标签位置
    tab.setTabPosition(tab.TabPosition.South)
    
    # 设置可移动
    tab.setMovable(True)
    
    # 创建移除按钮
    button = QtWidgets.QPushButton("移除")
    button.clicked.connect(partial(tab.removeTab, 0))
    
    # 创建整合控件
    vbox = QtWidgets.QVBoxLayout()
    vbox.addWidget(button)
    vbox.addWidget(tab)
    
    widget = QtWidgets.QWidget()
    widget.setLayout(vbox)
    widget.show()
    
    # 运行
    qapp.exec()
    
if __name__ == '__main__':
    run()