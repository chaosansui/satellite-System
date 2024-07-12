import random

import config
import queue
import simulation
from comtypes.gen import STKObjects


class Aircraft:
    def __init__(self, scenario, is_created, name='', params=None, obj=None):
        """
        :param scenario: 该卫星所属场景
        :param is_created: 该卫星是否已被创建, 用于区分新增/读取卫星
        :param name: 卫星名称, 若传入obj则可不传此项
        :param params: 该卫星的详细参数字典
        :param obj: STK 实体, 传入此项则无需传入上两
        """

        self.name = name  # 名称
        self.type = STKObjects.eAircraft  # 所属种类
        self.scenario = scenario  # 所属场景
        self.obj = None  # STK 对象
        self.iag_air = None  # STKObjects.IAgAircraft
        self.iag_obj = None  # STKObjects.IAgObject

        self.sensor_list = []  # 拥有的传感器列表
        # 传感器列表中元素如下
        _ = {
            'name': ...,  # 传感器名称
            'obj': ...,  # STK 对象
            'iag_sen': ...,  # STKObjects.IAgSensor
            'iag_obj': ...  # STKObjects.IAgObject
        }
        self.pattern_list = ['stand_by', 'moving', 'point', 'area']
        self.pattern = 'stand_by'  # 默认行为模式
        # self.start_location = (30, 50)  # 起飞点 (23.81,117.26)(24.88,118.71)(25.76, 119.53)
        self.task_index = -1  # 当前所属任务, 待命则 -1
        self.task_queue = queue.Queue()
        self.continuous_count = 0
        self.max_continuous_count = 2

        airport = [(23.81, 117.26), (24.88, 118.71), (25.76, 119.53)]
        self.start_location = airport[random.randint(0, len(airport) - 1)]
        self.location = airport[int(self.name[-1])%3]

        if not is_created:
            self.create_aircraft(params)
        else:
            self.load_from_obj(obj)

    # 从已有对象载入WRJ对象 UNTEST
    def load_from_obj(self, obj):
        if obj is not None:
            self.obj = obj
            self.iag_air = self.obj.QueryInterface(STKObjects.IAgAircraft)
            self.iag_obj = self.obj.QueryInterface(STKObjects.IAgStkObject)
            # 删除所有已有路径点, 将self.start_location设置为第一个路径点
            self.remove_all_way_points()
            self.add_way_points([{
                'latitude': self.start_location[0],
                'longitude': self.start_location[1],
                'altitude': 100,
                'speed': 1
            }])
        else:
            print('aircraft::创建失败, 传入为None')

    # 设置WRJ行为模式 UNTEST
    def set_pattern(self, pattern):
        if pattern not in self.pattern_list:
            print(f'aircraft::行为模式\'{pattern}\'不存在')
            return
        self.pattern = pattern
        # 进行一些路点、传感器参数的变化并同步至STK
        ...

    # 清除重复时间点
    def remove_repeated_point(self):
        route = self.iag_air.Route
        route = route.QueryInterface(STKObjects.IAgVePropagatorGreatArc)
        if route.Waypoints.Count < 2:
            return
        else:
            i = 2
            while i < route.Waypoints.Count:
                if route.Waypoints.Item(i).Time == route.Waypoints.Item(i - 1).Time:
                    route.Waypoints.RemoveAt(i)
                else:
                    i += 1

    # 使用速度添加路径点
    def add_way_points(self, points):
        self.iag_air.SetRouteType(STKObjects.ePropagatorGreatArc)
        route = self.iag_air.Route
        route = route.QueryInterface(STKObjects.IAgVePropagatorGreatArc)

        # 设置首飞开始时间
        # start_epoch = route.EphemerisInterval.GetStartEpoch()
        # start_epoch.SetExplicitTime('')
        # route.EphemerisInterval.SetStartEpoch(start_epoch)

        self.remove_repeated_point()

        for point in points:
            # 设置路径点添加模式
            if 'time' in point:
                route.Method = STKObjects.AgEVeWayPtCompMethod(STKObjects.eDetermineVelFromTime)
            else:
                route.Method = STKObjects.AgEVeWayPtCompMethod(STKObjects.eDetermineTimeAccFromVel)

            waypoint = route.Waypoints.Add()
            waypoint.Longitude = point['longitude']
            waypoint.Latitude = point['latitude']
            waypoint.Altitude = point['altitude']
            if 'time' in point:
                waypoint.Time = point['time']
            else:
                waypoint.Speed = point['speed']

        route.Propagate()

    # 清空路径点
    def remove_all_way_points(self):
        self.iag_air.SetRouteType(STKObjects.ePropagatorGreatArc)
        route = self.iag_air.Route
        route = route.QueryInterface(STKObjects.IAgVePropagatorGreatArc)
        route.Waypoints.RemoveAll()

    # 设置飞行目标点 并维护任务编号
    def set_destination(self, destination, task_index, current_time):
        # 若不为返程任务 则根据约束添加任务队列
        if task_index != -1:
            self.continuous_count += 1
            self.task_queue.put(task_index)
            # 若处于机场则直接执行任务
            if self.task_index == -1:
                self.task_index = task_index
                # 添加时间点
                self.add_way_points([{
                    'latitude': self.start_location[0],
                    'longitude': self.start_location[1],
                    'altitude': 100,
                    'time': current_time.strftime('%d %b %Y %H:%M:%S.%f')
                }])
        # 返程任务
        else:
            pass

        # 添加路径点
        points = simulation.generate_waypoints_sim(self.start_location, destination)
        self.add_way_points(points)

    # 任务完成的模式处理
    def task_complete(self, current_time=None):
        # 若任务列表为空则设置目标为返航
        if self.task_queue.empty():
            self.task_index = -1
            self.set_destination(self.start_location, -1, current_time)
            self.continuous_count = 0
        # 切换为任务列表的下一个任务编号
        else:
            self.task_index = self.task_queue.get()

# 添加函数区域探测，传参：目标点的坐标，半径默认值
    def area_detection(self, destination,radius):
        points = simulation.generate_areapoints_sim(self.start_location, destination, radius)
        self.add_way_points(points)


    # 获取当前飞行任务结束后的时间
    def get_complete_time(self):
        pass

    # 获取路径点
    def get_waypoints(self):
        route = self.iag_air.SetRouteType(STKObjects.ePropagatorGreatArc)
        route = self.iag_air.Route
        route = route.QueryInterface(STKObjects.IAgVePropagatorGreatArc)
        raw = route.Waypoints
        points = raw.ToArray()
        _list = []
        for point in points:
            _list.append({
                'time': simulation.str_to_datetime(point[0]),
                'latitude': point[1],
                'longitude': point[2],
                'altitude': point[3],
                'speed': point[4],
                'accel': point[5]
            })
        return _list

    # 获取最晚路径点
    def get_latest_waypoint(self):
        points = self.get_waypoints()
        return points[-1]

    # 以下为弃用

    # 新建WRJ
    def create_aircraft(self, params):
        # 创建特定名称的WRJ对象
        self.obj = self.scenario.sce.Children.New(self.type, self.name)
        # 从IAgSTKObject接口跳转至IAgSatellite
        self.iag_air = self.obj.QueryInterface(STKObjects.IAgAircraft)
        self.iag_obj = self.obj.QueryInterface(STKObjects.IAgStkObject)

        # 删除所有已有路径点, 将self.start_location设置为第一个路径点
        self.remove_all_way_points()

    # 设置已有传感器的参数
    def set_sensor(self, sensor_index, params):
        pass

    # 添加传感器并设置参数
    def add_sensor(self, params):
        pass

    # 删除指定传感器
    def delete_sensor(self, sensor_index):
        pass

    # 获取无人机当前的位置
    def get_current_location(self, time):
        # 向STK请求某时间刻的位置
        # 返回位置元组
        pass