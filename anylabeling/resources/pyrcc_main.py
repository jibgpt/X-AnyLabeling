import sys

from PyQt5.pyrcc_main import main

# pyinstaller x-anylabeling-win-cpu.spec    打包exe

# resources.py就是资源文件
if __name__ == '__main__':
    # 设置命令行参数
    sys.argv = ['pyrcc5', 'resources.qrc', '-o', 'resources.py']
    main()
