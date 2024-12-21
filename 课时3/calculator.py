from PySide6 import QtWidgets


class CalculatorWidget(QtWidgets.QWidget):
    """计算器窗口"""
    
    def __init__(self) -> None:
        """构造函数"""
        super().__init__()
        
        self.output = QtWidgets.QTextEdit()  # 输出文本框
        self.input = QtWidgets.QLineEdit()  # 输入文本框
        self.input.returnPressed.connect(self.calculate)  # 回车执行计算
        
        vbox = QtWidgets.QVBoxLayout()  # 垂直控件布局
        vbox.addWidget(self.output)
        vbox.addWidget(self.input)
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
    