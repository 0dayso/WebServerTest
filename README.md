这是一个WebServer测试工程，可以抓取XXX网站，完成资料填写，信息提交。car.py实现的是核心的HTTP流程。car_process.py会生成car.py中方法的进程，并进行控制，包含配置数据更新，进程重启停止等等功能。 listen_task.py支持server到各个进程之间数据通信。这三个文件相当于了loadrunner的VUG模块，另外包含了部分Controller功能

本工程的控制中心，在listen_server.py中实现各个客户端的监控，客户端启动之后会登录到server，server提供了token功能（token函数），客户端在某些HTTP流程需要申请token，实际上起到一个控制单位时间最大并发数的功能。客户端listen_task中启动了token进程，在客户端也可以控制部分HTTP最大并发数。

控制界面在ui.py中实现。
