#! /usr/bin/python
# coding:utf-8
import Tkinter as tk
import turtle as t
import socket
import time
from threading import Thread

"""
////////////////////////////////////////////////////////////////////
//                          _ooOoo_                               //
//                         o8888888o                              //
//                         88" . "88                              //
//                         (| ^_^ |)                              //
//                         O\  =  /O                              //
//                      ____/`---'\____                           //
//                    .'  \\|     |//  `.                         //
//                   /  \\|||  :  |||//  \                        //
//                  /  _||||| -:- |||||-  \                       //
//                  |   | \\\  -  /// |   |                       //
//                  | \_|  ''\---/''  |   |                       //
//                  \  .-\__  `-`  ___/-. /                       //
//                ___`. .'  /--.--\  `. . ___                     //
//              ."" '<  `.___\_<|>_/___.'  >'"".                  //
//            | | :  `- \`.;`\ _ /`;.`/ - ` : | |                 //
//            \  \ `-.   \_ __\ /__ _/   .-` /  /                 //
//      ========`-.____`-.___\_____/___.-`____.-'========         //
//                           `=---='                              //
//      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        //
//         佛祖保佑       永无BUG     永不修改                       //
////////////////////////////////////////////////////////////////////
"""
flight_ip_address = '192.168.29.178'
flight_ip_port = 9093
# 无人机先建立tcp server，此时连接,按键启动另一端
# 子线程接收数据不为空
# 客户端套街字
tcp_client_socket = None


# 连接
def connect_flight():
    global tcp_client_socket
    tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcp_client_socket.connect((flight_ip_address, flight_ip_port))
        connect_status.set('    连接状态:    已连接')
    except:
        connect_status.set('    连接状态:    连接失败')


# 总航程
total_distance = [0]
recv_x = recv_y = None


# 接收数据
def receive_data():
    global total_distance, recv_x, recv_y
    # 等待tcp连接
    while True:
        if tcp_client_socket is not None:
            break
    send_w_num = [0] * 12
    # 发送命令1:请求数据
    while True:
        # 发送内容
        send_content = '1'
        # 编码
        send_data = send_content.encode()
        # 3.发送数据
        # 发送数据
        tcp_client_socket.send(send_data)
        # 4.接收数据
        # 1024:每次最大接受字节数
        recv_max = tcp_client_socket.recv(1024)
        # 对二进制数据进行解码
        recv_content = recv_max.decode()
        recv_data = str(recv_content)
        # 对数据进行处理
        # x y z
        # w 拐弯
        recv_data_split = recv_data.split()
        recv_x = float(recv_data_split[0]) * 100
        recv_y = float(recv_data_split[1]) * 100
        recv_z = float(recv_data_split[2]) * 100
        # 无人机位置坐标信息
        x.set('     x:     ' + "%.2f" % recv_y + '    cm')
        y.set('     y:     ' + "%.2f" % recv_x + '    cm')
        z.set('     z:     ' + "%.2f" % recv_z + '    cm')
        # 累计巡逻航程
        # w处理拐弯
        # 走完拐弯矫正
        w = int(recv_data_split[3])
        # 向前飞
        if w == 0 or w == 4 or w == 8:
            send_w_num[w] += 1
            if send_w_num[w] == 1:
                if w == 4:
                    total_distance[-1] = 14.4 * 100
                elif w == 8:
                    total_distance[-1] = 24.0 * 100
                total_distance.append(total_distance[-1])
                total_distance[-1] = total_distance[-2] + recv_x
                distance_dm.set('    ' + "%.2f" % total_distance[-1] + '  cm')
            else:
                total_distance[-1] = total_distance[-2] + recv_x
                distance_dm.set('    ' + "%.2f" % total_distance[-1] + '  cm')
        # 向右飞
        elif w == 1:
            send_w_num[w] += 1
            if send_w_num[w] == 1:
                if w == 1:
                    total_distance[-1] = 4 * 100
                total_distance.append(total_distance[-1])
                total_distance[-1] = total_distance[-2] + recv_y
                distance_dm.set('    ' + "%.2f" % total_distance[-1] + '  cm')
            else:
                total_distance[-1] = total_distance[-2] + recv_y
                distance_dm.set('    ' + "%.2f" % total_distance[-1] + '  cm')
        # 向左飞
        elif w == 3 or w == 5 or w == 7 or w == 9 or w == 11:
            # 拐弯点y坐标【改】
            g_y = None
            if w == 3:
                g_y = 480.0
            elif w == 5:
                g_y = 400.0
            elif w == 7:
                g_y = 320.0
            elif w == 9:
                g_y = 240.0
            elif w == 11:
                g_y = 160.0
            send_w_num[w] += 1
            if send_w_num[w] == 1:
                if w == 3:
                    total_distance[-1] = 12.8 * 100
                elif w == 5:
                    total_distance[-1] = 17.6 * 100
                elif w == 7:
                    total_distance[-1] = 22.4 * 100
                elif w == 9:
                    total_distance[-1] = 27.2 * 100
                elif w == 11:
                    total_distance[-1] = 32.0 * 100
                total_distance.append(total_distance[-1])
                total_distance[-1] = total_distance[-2] + g_y - recv_y
                distance_dm.set('    ' + "%.2f" % total_distance[-1] + '  cm')
            else:
                total_distance[-1] = total_distance[-2] + g_y - recv_y
                distance_dm.set('    ' + "%.2f" % total_distance[-1] + '  cm')
        # 向后飞
        elif w == 2 or w == 6 or w == 10:
            # 拐弯点x坐标【改】
            g_x = 360.0
            send_w_num[w] += 1
            if send_w_num[w] == 1:
                if w == 2:
                    total_distance[-1] = 8.8 * 100
                elif w == 6:
                    total_distance[-1] = 19.2 * 100
                elif w == 10:
                    total_distance[-1] = 28.8 * 100
                total_distance.append(total_distance[-1])
                total_distance[-1] = total_distance[-2] + g_x - recv_x
                distance_dm.set('    ' + "%.2f" % total_distance[-1] + '  cm')
            else:
                total_distance[-1] = total_distance[-2] + g_x - recv_x
                distance_dm.set('    ' + "%.2f" % total_distance[-1] + '  cm')
        # 停止
        elif w == 12:
            pass
        time.sleep(1)


# 航程轨迹绘制
def draw_cs():
    # 设置位置
    t.screensize(1200, 1200)
    t.title('无人机巡逻航迹曲线')
    # 设置画笔
    t.speed(10)
    t.pensize(2)
    # 画x轴
    t.penup()
    t.goto(500, 0)
    t.pendown()
    t.goto(0, 0)
    # 画x轴的箭头
    t.penup()
    t.goto(495, 5)
    t.pendown()
    t.goto(500, 0)
    t.goto(495, -5)
    # 画x轴的点
    for i in range(0, 500, 80):
        # 画点
        t.penup()
        t.goto(i, 10)
        t.pendown()
        t.goto(i, 0)
        # 画字
        t.penup()
        if i == 0:  # 对0的处理
            t.goto(i - 10, -25)
            t.write(i, align='center')
        else:
            t.goto(i, -25)
            t.write(i, align='center')
        t.pendown()
    # 画x轴的X
    t.penup()
    t.goto(490, -30)
    t.pendown()
    t.write('x/cm', font=("Arial", 16))
    # 画y轴
    t.penup()
    t.goto(0, 420)
    t.pendown()
    t.goto(0, 0)
    # 画y轴的箭头
    t.penup()
    t.goto(-5, 415)
    t.pendown()
    t.goto(0, 420)
    t.goto(5, 415)
    # 画y轴的点
    for i in range(0, 420, 80):
        # 画点
        t.penup()
        t.goto(10, i)
        t.pendown()
        t.goto(0, i)
        # 画字
        t.penup()
        if i == 0:  # 对0的处理
            pass
        else:
            t.goto(-25, i - 5)
            t.write(i, align='center')
        t.pendown()
    # 画y轴的y
    t.penup()
    t.goto(-30, 410)
    t.pendown()
    t.write('y/cm', font=("Arial", 16))
    # 恢复初始位置
    t.penup()
    t.goto(0, 0)
    while True:
        # 设置颜色
        t.pencolor('red')
        if recv_x is not None and recv_y is not None:
            t.pendown()
            t.goto(recv_y, recv_x)
            t.penup()
        else:
            t.goto(0, 0)
            time.sleep(1)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("消防车无人机显示")
    # 显示消防车IP地址
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    car_ip = tk.Label(root, text='消防车ip：' + s.getsockname()[0])
    car_ip.pack()
    # 无人机ip地址
    flight_ip = tk.Label(root, text='无人机ip：' + flight_ip_address + ':' + str(flight_ip_port))
    flight_ip.pack()
    # 变量
    connect_status = tk.StringVar()
    x = tk.StringVar()
    y = tk.StringVar()
    z = tk.StringVar()
    distance_dm = tk.StringVar()
    # 初始化
    connect_status.set('    连接状态:    未连接')
    x.set('     x:     ' + str(0) + '    cm')
    y.set('     y:     ' + str(0) + '    cm')
    z.set('     z:     ' + str(0) + '    cm')
    distance_dm.set('    ' + str(0) + '  cm')
    # 启动连接按钮
    tk.Button(
        root,
        text='启动连接',
        command=connect_flight
    ).pack()
    connect_status_display = tk.Entry(root, textvariable=connect_status)
    connect_status_display.pack()
    pose = tk.Label(root, text="无人机位置坐标信息")
    pose.pack()
    pose_x = tk.Entry(root, textvariable=x)
    pose_x.pack()
    pose_y = tk.Entry(root, textvariable=y)
    pose_y.pack()
    pose_z = tk.Entry(root, textvariable=z)
    pose_z.pack()
    pose_distance = tk.Label(root, text="累计巡逻航程")
    pose_distance.pack()
    pose_distance_dm = tk.Entry(root, textvariable=distance_dm)
    pose_distance_dm.pack()
    # 开启多线程
    # 显示巡逻航迹曲线
    draw_thread = Thread(target=draw_cs)
    draw_thread.setDaemon(True)
    draw_thread.start()
    # 接收数据
    receive_data_thread = Thread(target=receive_data)
    receive_data_thread.setDaemon(True)
    receive_data_thread.start()
    root.mainloop()
