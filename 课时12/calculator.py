from PySide6 import QtWidgets, QtGui


class CalculatorWidget(QtWidgets.QWidget):
    """计算器窗口"""
    
    def __init__(self) -> None:
        """构造函数"""
        super().__init__()
        
        self.output = QtWidgets.QTextEdit()  # 输出文本框
        self.input = QtWidgets.QLineEdit()  # 输入文本框
        self.input.returnPressed.connect(self.calculate)  # 回车执行计算
        
        calculate_button = QtWidgets.QPushButton("计算")  # 计算按钮
        calculate_button.clicked.connect(self.calculate)  # 点击执行计算
        calculate_button.setIcon(QtGui.QIcon("calculator.ico"))  # 设置图标
        
        clear_button = QtWidgets.QPushButton("清空")  #清空按钮
        clear_button.clicked.connect(self.input.clear)  # 点击清空输入
        clear_button.clicked.connect(self.output.clear)  # 点击清空输出
        clear_button.setIcon(QtGui.QIcon("clear.ico"))  # 设置图标
        
        
        vbox = QtWidgets.QVBoxLayout()  # 垂直控件布局
        vbox.addWidget(self.output)
        vbox.addWidget(self.input)
        vbox.addWidget(calculate_button)
        vbox.addWidget(clear_button)
        self.setLayout(vbox)
        
    def calculate(self) -> None:
        """执行计算"""
        text: str = self.input.text()  # 获取输入文字
        
        try:
            result = eval(text)  # 把字符串当代码来执行
            self.output.append(f"{text} = {result}")
        except Exception:
            self.output.append(f"{text} 表达式错误")

        
if __name__ == '__main__':
    qapp = QtWidgets.QApplication([])  # Qt应用（事件循环）
    
    widget = CalculatorWidget()  # 创建窗口
    widget.show()  # 显示窗口
    
    qapp.exec()  # 运行应用
    
