from PySide6 import QtWidgets


if __name__ == '__main__':
    # Qt应用（事件循环）
    qapp = QtWidgets.QApplication([])
    
    # 创建控件
    line = QtWidgets.QLineEdit()
    line.show()
    
    # 设置初始文字
    # line.setText("通用输入框")
    
    # 设置显示模式：setEchoMode
    # Normal：正常显示输入的内容
    line.setEchoMode(line.EchoMode.Normal)
    # NoEcho：不显示任何内容
    # line.setEchoMode(line.EchoMode.NoEcho)
    # Password：显示为密码覆盖字符
    # line.setEchoMode(line.EchoMode.Password)
    # PasswordEchoOnEdit：仅在输入瞬间显示字符
    # line.setEchoMode(line.EchoMode.PasswordEchoOnEdit)
    
    
    # 获取文字
    def print_text():
        content: str = line.text()
        print(f"当前文本框内容为：{content}")
        
    line.returnPressed.connect(print_text) # 当获取到回车键，就执行print_text函数
    
    # 设置内容自动补全
    data = ["开仓", "平仓", "平今", "平昨"]
    completer = QtWidgets.QCompleter(data)
    line.setCompleter(completer)
    
    # 运行应用
    qapp.exec()
