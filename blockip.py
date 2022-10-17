import sys
from xml.dom.expatbuilder import parseString
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtWidgets
from IPy import IP
import paramiko
import time
import re
import os
import icoico
import block_ip_2_ui

username = 'xxxx'
password = 'xxxx'


#正则表达式，用于匹配IP
pattern_ip =re.compile(r'\d{1,3}(\.\d{1,3}){3}')
running_time = time.strftime('%Y-%m-%d %H:%M:%S')

#白名单地址
ip_msg = '''
x.x.x.

        '''

#白名单地址段
ip_msg+='\n'.join([str(i) for i in IP('x.x.x.0/24')])
ip_allow_list = ip_msg.split()



def action(cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='1x.x.x.x',   #防火墙地址
                                username=username, 
                                password=password,
                                compress=True)
    conn = ssh.invoke_shell()
    time.sleep(0.5)
    conn.send('config vdom\n')
    time.sleep(0.2)
    conn.send('edit Internet_FW\n')
    time.sleep(0.2)
    conn.send(f'{cmd}\n')
    time.sleep(0.2)
    print('操作完成。')
    ssh.close()

def blockIp():
    ui.textBrowser.setText("")
    input_ip = ui.plainTextEdit.toPlainText()
    ip_list = input_ip.split("\n")
    ip_filte_list = []
    ip_error = []
    for ip in ip_list:
        ip = ip.strip()#去除ip地址中的空格
        ip1 = pattern_ip.search(ip)
        if ip1:
            ip_check = ip.split('.')
            if ip in ip_allow_list:
                ip_error.append(ip)

                print(ip+"为白名单ip，已剔除")
                ui.textBrowser.append(ip+"为白名单ip，已剔除")
                ui.textBrowser.lineWrapMode()
                continue
            elif ip_check[0] == '10' or (ip_check[0] == '192' and ip_check[1] == '168') or (ip_check[0] == '172' and int(ip_check[1]) in range(16,32)):
                #print(f'{ip}为内网IP，不封堵')
                ui.textBrowser.append('输入存在的内网IP未封堵')
                ui.textBrowser.lineWrapMode()
                continue
            ip_filte_list.append(ip)
            cmd = f'diagnose user quarantine add src4 {ip} 0 admin'
            try:
            
                action(cmd)
                ui.textBrowser.append(ip+'封堵完成，记录保存在block.log')
                ui.textBrowser.lineWrapMode()
                with open('block.log','a+') as f:
                    for ip in ip_filte_list:
                        f.write(f'{ip:<18}')
                        f.write(f'{running_time}\n')
            except:
                ui.textBrowser.append("网络不通或登录失败")
        else:
            ui.textBrowser.setText("ip错误,请检查")
    ui.plainTextEdit.clear()
            

def unBlockIp():
    ui.textBrowser.setText("")
    input_ip = ui.plainTextEdit.toPlainText()
    ip_list = input_ip.split("\n")
    ip_filte_list = []
    ip_error = []
    for ip in ip_list:
        ip = ip.strip()
        ip1 = pattern_ip.search(ip)
        if ip1:
            if ip in ip_allow_list:
                ip_error.append(ip)

                print(ip+"为白名单ip，未做封禁，无需解封")
                ui.textBrowser.append(ip+"为白名单ip，未做封禁，无需解封")
                ui.textBrowser.lineWrapMode()
                continue
            else:
                ip_filte_list.append(ip)
                cmd = f'diagnose user quarantine delete src4 {ip}'
                try:
                    action(cmd)
                    ui.textBrowser.append(ip+'解封完成完成，记录保存在unblock.log')
                    ui.textBrowser.lineWrapMode()
                    with open('unblock.log','a+') as f:
                        for ip in ip_filte_list:
                            f.write(f'{ip:<18}')
                            f.write(f'{running_time}\n')
                except:
                    ui.textBrowser.append("网络不通或登录失败")
                
        else:
            ui.textBrowser.append("ip错误,请检查")
    ui.plainTextEdit.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = block_ip_2_ui.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    ui.pushButton.clicked.connect(blockIp)
    ui.pushButton_2.clicked.connect(unBlockIp)
    sys.exit(app.exec_())
