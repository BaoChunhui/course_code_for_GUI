from PySide6 import QtWidgets

TEXT = ""

if __name__ == '__main__':
    # Qt 应用（事件循环）
    qapp = QtWidgets.QApplication([])
    
    # 创建控件
    edit = QtWidgets.QTextEdit()
    edit.show()
    
    # 设置初始文字
    edit.setText("Hello World!")
    
    # 全量设置（覆盖）
    edit.setText("Hello Again!")
    
    # 尾部追加
    edit.append("Hello Again!")
    
    # 清空内容
    # edit.clear()
    
    # 设置只读
    # edit.setReadOnly(True)
    
    # 设置颜色，影响的是后续内容，之前输入不受影响
    edit.setTextColor("red")
    
    # 设置字体
    edit.setFontFamily("宋体")
    
    # 设置字体
    edit.setFontPointSize(20)
    
    # 追加内容
    edit.append("自定义效果")
    
    # 运行应用
    qapp.exec()
