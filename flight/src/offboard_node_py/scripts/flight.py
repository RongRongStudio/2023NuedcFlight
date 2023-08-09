#! /usr/bin/python
# coding:utf-8
import time
import rospy
# 位置坐标(x,y,z)
from geometry_msgs.msg import PoseStamped
# 状态[OFFBOARD]
from mavros_msgs.msg import State
# 服务
# CommandBool:连接成功标志
# CommandBoolRequest:请求连接成功标志
# SetMode:设置模式
# SetModeRequest:设置模式连接成功标志
from mavros_msgs.srv import SetMode, SetModeRequest, CommandBoolRequest, CommandBool
import socket
from threading import Thread

pos_dict = {
    # 1.向上，小于停
    0: [1.5, 1.4],
    # 2.向前，小于停
    1: [3.8, 3.79],
    # 3.向右，小于绝对值停
    2: [-4.4, 4.38],
    # 4.向下，大于停
    3: [0, 0.1],
    # 5.向左，大于绝对值停
    4: [-3.6, 3.7],
    # 6.向上，小于停
    5: [2.8, 2.7],
    # 7.向左，大于绝对值停
    6: [-2.8, 2.9],
    # 8.向下，大于停
    7: [0.1, 0.2],
    # 9.向左，大于绝对值停
    8: [-2.0, 2.1],
    # 10.向上，小于停
    9: [2.8, 2.7],
    # 11.向左，大于绝对值停
    10: [-1.2, 1.3],
    # 12.向下，大于停
    11: [0.1, 0.2],
    # 13.向左，大于绝对值停
    12: [-0.4, 0.5],
    # 14.降落，大于停
    13: [0, 0.2]
}
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
# 当前状态
current_state = State()


# 当前状态回调
def state_cb(msg):
    global current_state
    current_state = msg


# 当前位置
current_position = PoseStamped()


# 当前位置回调
def state_pos(msg):
    global current_position
    current_position = msg


# 位置坐标
pose = PoseStamped()


def flight_position():
    while True:
        local_pos_pub.publish(pose)
        rate.sleep()


# 前进状况[上下左右]
w = None
s = None


def send_data():
    try:
        while True:
            # 5.接收数据
            # 接受客户端发送的数据，接收的数据最大字节数是1024
            recv_max = service_cilent_socket.recv(1024)
            # 对二进制数据进行解码
            recv_content = recv_max.decode()
            recv_data = str(recv_content)
            if recv_data == '1':
                # 6.发送数据
                # x,y,z
                # x:前方 y:左方【负】z:上方
                # w弯道处理
                x = current_position.pose.position.x
                y = abs(current_position.pose.position.y)
                z = current_position.pose.position.z
                send_content = "%.2f %.2f %.2f %d" % (x, y, z, w)
                # 准备发送的数据，编码
                send_data = send_content.encode()
                # 7.关闭套接字
                # 发送数据给客户端
                service_cilent_socket.send(send_data)
    except:
        service_cilent_socket.close()
        # 关闭服务端的套接字，终止和客户端提供建立连接请求的服务，相当于10086停止提供服务
        # listen后的若关闭，之前已经连接成功的客户端仍能通信，相当于卡点银行取钱
        # 当客户端套接字调用close后，服务器端的recv会解阻塞，返回的数据长度为0
        tcp_sever_socket.close()


if __name__ == "__main__":
    rospy.init_node("offb_node_py")
    # 1.创建服务端端套接字对象
    tcp_sever_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 当客户端和服务端建立连接后，服务端程序退出端口号不会立即释放，或改端口号
    # 设置端口号复用，让程序退出端口号立即释放
    tcp_sever_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    # 2.绑定端口号
    tcp_sever_socket.bind(('', 9093))
    # 3.设置监听
    # 不需要让客户端进行等待建立连接
    # listen后的这个套接字只负责接受客户端连接请求，不能收发消息，收发消息使用返回的这个新套接字来完成
    tcp_sever_socket.listen(128)
    # 4.等待接受客户端的连接请求
    # 等待客户端建立连接的请求，只有客户端和服务端建立连接成功代码才会解阻塞，代码才能继续往下执行
    # 客服人员，返回的新套接字，相当于转接
    # 返回新套接字
    service_cilent_socket, ip_port = tcp_sever_socket.accept()
    # 状态节点[订阅] 回调:当前状态
    state_sub = rospy.Subscriber("mavros/state", State, state_cb)
    # 位置坐标[发布]
    local_pos_pub = rospy.Publisher("mavros/setpoint_position/local", PoseStamped, queue_size=10)
    # 位置坐标[订阅]
    local_pos_sub = rospy.Subscriber("/mavros/local_position/pose", PoseStamped, state_pos)
    # 等待设置模式服务
    rospy.wait_for_service("/mavros/set_mode")
    # 创建设置服务对象
    set_mode_client = rospy.ServiceProxy("mavros/set_mode", SetMode)
    # 等待arming解锁服务[True:解锁,False:上锁]
    rospy.wait_for_service("/mavros/cmd/arming")
    # 创建解锁服务对象
    arming_client = rospy.ServiceProxy("mavros/cmd/arming", CommandBool)
    # 话题通信速率大于2hz
    rate = rospy.Rate(20)
    # 等待飞机连接
    while not rospy.is_shutdown() and not current_state.connected:
        rospy.loginfo('Connected Success')
        rate.sleep()
    w = 0
    # 位置坐标[垂直起飞高度]
    pose.pose.position.x = 0
    pose.pose.position.y = 0
    pose.pose.position.z = pos_dict[0][0]
    # 在起飞之前发布设定值
    for i in range(20):
        if rospy.is_shutdown():
            break
        local_pos_pub.publish(pose)
        rate.sleep()
    # 单独写切换
    # 切换+上锁
    offb_set_mode = SetModeRequest()
    offb_set_mode.custom_mode = 'OFFBOARD'
    # 解锁
    arm_cmd = CommandBoolRequest()
    arm_cmd.value = True
    while True:
        if set_mode_client.call(offb_set_mode).mode_sent is True:
            rospy.loginfo("OFFBOARD enabled")
            if arming_client.call(arm_cmd).success is True:
                rospy.loginfo("Vehicle armed")
                break
        rate.sleep()
    # 开启多线程
    # 发送航程线程
    send_data_thread = Thread(target=send_data)
    send_data_thread.setDaemon(True)
    send_data_thread.start()
    # 目标位置发送线程
    flight_thread = Thread(target=flight_position)
    flight_thread.setDaemon(True)
    flight_thread.start()
    # 一、起飞
    # 飞到z1.5
    while True:
        rospy.loginfo(current_position.pose.position.z)
        if current_position.pose.position.z > pos_dict[0][1]:
            break
        rate.sleep()
    rospy.loginfo('z to 1.5')
    # 二、向前走
    # 飞到x=4【坐标系y=4】 向前飞
    pose.pose.position.x = pos_dict[1][0]
    while True:
        if current_position.pose.position.x > pos_dict[1][1]:
            w = 1
            break
        rate.sleep()
    rospy.loginfo('x to 4')
    # 三、向右走
    # 飞到y=4.8【坐标系x=4.8】 向右飞
    pose.pose.position.y = pos_dict[2][0]
    while True:
        rospy.loginfo(current_position.pose.position.y)
        if abs(current_position.pose.position.y) > pos_dict[2][1]:
            w = 2
            break
        rate.sleep()
    rospy.loginfo('y to 4.8')
    # 四、向后飞
    # 飞到x=0【坐标系y=0】向后飞
    pose.pose.position.x = pos_dict[3][0]
    while True:
        rospy.loginfo(current_position.pose.position.x)
        if abs(current_position.pose.position.x) < pos_dict[3][1]:
            w = 3
            break
        rate.sleep()
    rospy.loginfo('x to 0')
    # 五、向左飞
    # 飞到y=-3.6【坐标系x=3.6】向左飞
    pose.pose.position.y = pos_dict[4][0]
    while True:
        rospy.loginfo(current_position.pose.position.y)
        if abs(current_position.pose.position.y) < pos_dict[4][1]:
            w = 4
            break
        rate.sleep()
    rospy.loginfo('y to -3.6')
    # 六、向前飞
    # 飞到x=2.8【坐标系y=2.8】向前飞
    pose.pose.position.x = pos_dict[5][0]
    while True:
        rospy.loginfo(current_position.pose.position.x)
        if abs(current_position.pose.position.x) > pos_dict[5][1]:
            w = 5
            break
        rate.sleep()
    rospy.loginfo('x to 2.8')
    # 七、向左飞
    # 飞到y=-2.8【坐标系x=2.8】向左飞
    pose.pose.position.y = pos_dict[6][0]
    while True:
        rospy.loginfo(current_position.pose.position.y)
        if abs(current_position.pose.position.y) < pos_dict[6][1]:
            w = 6
            break
        rate.sleep()
    rospy.loginfo('y to -2.8')
    # 八、向后飞
    # 飞到x=0【坐标系y=0】向后飞
    pose.pose.position.x = pos_dict[7][0]
    while True:
        rospy.loginfo(current_position.pose.position.x)
        if abs(current_position.pose.position.x) < pos_dict[7][1]:
            w = 7
            break
        rate.sleep()
    rospy.loginfo('x to 0')
    # 九、向左飞
    # 飞到y=-2.0【坐标系x=2.0】向左飞
    pose.pose.position.y = pos_dict[8][0]
    while True:
        rospy.loginfo(current_position.pose.position.y)
        if abs(current_position.pose.position.y) < pos_dict[8][1]:
            w = 8
            break
        rate.sleep()
    rospy.loginfo('y to -2.0')
    # 十、向前飞
    # 飞到x=2.8【坐标系y=2.8】向前飞
    pose.pose.position.x = pos_dict[9][0]
    while True:
        rospy.loginfo(current_position.pose.position.x)
        if abs(current_position.pose.position.x) > pos_dict[9][1]:
            w = 9
            break
        rate.sleep()
    rospy.loginfo('x to 2.8')
    # 十一、向左飞
    # 飞到y=-1.2【坐标系x=1.2】向左飞
    pose.pose.position.y = pos_dict[10][0]
    while True:
        rospy.loginfo(current_position.pose.position.y)
        if abs(current_position.pose.position.y) < pos_dict[10][1]:
            w = 10
            break
        rate.sleep()
    rospy.loginfo('y to -1.2')
    # 十二、向后飞
    # 飞到x=0【坐标系y=0】向后飞
    pose.pose.position.x = pos_dict[11][0]
    while True:
        rospy.loginfo(current_position.pose.position.x)
        if abs(current_position.pose.position.x) < pos_dict[11][1]:
            w = 11
            break
        rate.sleep()
    rospy.loginfo('x to 0')
    # 十三、向左飞
    # 飞到y=-0.4【坐标系x=0.4】向左飞
    pose.pose.position.y = pos_dict[12][0]
    while True:
        rospy.loginfo(current_position.pose.position.y)
        if abs(current_position.pose.position.y) < pos_dict[12][1]:
            w = 12
            break
        rate.sleep()
    rospy.loginfo('y to -04')
    # 十四、降落
    pose.pose.position.z = pos_dict[13][0]
    while True:
        rospy.loginfo(current_position.pose.position.z)
        if current_position.pose.position.z < pos_dict[13][1]:
            rospy.loginfo('z to 0.1')
            break
        rate.sleep()
    rospy.spin()
