import random
import util
from comtypes.gen import STKObjects

class Satellite:
    def __init__(self, scenario, is_created=False, name='', params=None, obj=None):
        """
        :param scenario: 该卫星所属场景
        :param is_created: 该卫星是否已被创建, 用于区分新增/读取卫星
        :param name: 卫星名称, 若传入obj则可不传此项
        :param params: 该卫星的详细参数字典
        :param obj: STK 实体, 传入此项则无需传入上两
        """

        self.name = name                    # 名称
        self.type = STKObjects.eSatellite   # 所属种类
        self.scenario = scenario            # 所属场景
        self.obj = None                     # STK 对象
        self.iag_sat = None                 # STKObjects.IAgSatellite
        self.iag_obj = None                 # STKObjects.IAgObject

        self.sensor_list = []               # 拥有的传感器列表
        # 传感器列表中元素如下
        _ = {
            'name': ...,                    # 传感器名称
            'obj': ...,                     # STK 对象
            'iag_sen': ...,                 # STKObjects.IAgSensor
            'iag_obj': ...                  # STKObjects.IAgObject
        }
        self.pattern_list = ['large_scale', 'high_precision']
        self.pattern = 'large_scale'        # 默认行为模式

        if not is_created:
            self.create_satellite(params)
        else:
            self.load_from_obj(obj)

    # 新建卫星 UNTEST
    def create_satellite(self, params):

        def create_with_tle():
            # 设置卫星预报模型为SGP4模型
            self.iag_sat.SetPropagatorType(4)
            # 由IAgVePropagator跳转至IAgVePropagatorSGP4
            pro_sgp4_iag = self.iag_sat.Propagator.QueryInterface(STKObjects.IAgVePropagatorSGP4)
            # 读取tle文件中对应编号的卫星轨
            pro_sgp4_iag.CommonTasks.AddSegsFromFile(params['id'], params['path'])
            # 传递参数
            pro_sgp4_iag.Propagate()

        def create_with_params():
            # eOrbitStateClassical
            keplerian = self.obj.Propagator.InitialState.Representation.ConvertTo(1)
            # eSizeShapeAltitude
            keplerian.SizeShapeType = 0
            # eLocationTrueAnomaly
            keplerian.LocationType = 5
            # eAscNodeLAN
            keplerian.Orientation.AscNodeType = 0

            keplerian.SizeShape.PerigeeAltitude = params['PerigeeAltitude']
            keplerian.SizeShape.ApogeeAltitude = params['ApogeeAltitude']
            keplerian.Orientation.Inclination = params['Inclination']
            keplerian.Orientation.ArgOfPerigee = params['ArgOfPerigee']
            keplerian.Orientation.AscNode.Value = params['AscNode']
            keplerian.Location.Value = params['TrueAnomaly']

            self.obj.Propagator.InitialState.Representation.Assign(keplerian)
            self.obj.Propagator.Propagate()

        # 创建特定名称的卫星对象
        self.obj = self.scenario.sce.Children.New(self.type, self.name)
        # 从IAgSTKObject接口跳转至IAgSatellite
        self.iag_sat = self.obj.QueryInterface(STKObjects.IAgSatellite)
        self.iag_obj = self.obj.QueryInterface(STKObjects.IAgStkObject)

        # 根据 tle 载入卫星
        if 'id' in params:
            create_with_tle()
        # 根据自定义参数载入卫星
        else:
            create_with_params()

    # 从已有对象载入 卫星 和 传感器
    def load_from_obj(self, obj):
        if obj is not None:
            self.name = obj.InstanceName
            self.obj = obj
            self.iag_sat = obj.QueryInterface(STKObjects.IAgSatellite)
            self.iag_obj = obj.QueryInterface(STKObjects.IAgStkObject)
            # 载入所拥有的传感器
            sensor_list = self.obj.Children.GetElements(STKObjects.eSensor)
            for item in sensor_list:
                self.sensor_list.append({
                    'name': item.InstanceName,
                    'obj': item,
                    'iag_sen': item.QueryInterface(STKObjects.IAgSensor),
                    'iag_obj': item.QueryInterface(STKObjects.IAgStkObject)
                })
        else:
            print('satellite::创建失败, 传入为None')


    def set_pattern(self, pattern):
        if pattern not in self.pattern_list:
            print(f'satellite::行为模式\'{pattern}\'不存在')
            return
        self.pattern = pattern
        # 进行一些传感器参数的变化并同步至STK(只是切换的话好像不用)

    # 设置已有传感器的参数
    def set_sensor(self, sensor_index, params):
        pass

    # 添加传感器并设置参数 UNTEST
    def add_sensor(self, params=None):
        if params is not None:
            # FUTURE
            pass
        else:
            # 默认传感器就是 45° 的观测角约束
            sensor_name = 'sensor{}'.format(len(self.sensor_list))
            sensor = self.obj.Children.New(STKObjects.eSensor, sensor_name)
            # 设置传感器参数
            # sensor.CommonTasks.SetPatternRectangular(20, 25)
            # sensor.CommonTasks.SetPointingFixedAzEl(90, 60, 1)  # eAzElAboutBoresightRotate
            # sensor.SetLocationType(0)  # eSnFixed
            # sensor.LocationData.AssignCartesian(-.0004, -.0004, .004)
            self.sensor_list.append({
                'name': sensor_name,
                'obj': sensor,
                'iag_sen': sensor.QueryInterface(STKObjects.IAgSensor),
                'iag_obj': sensor.QueryInterface(STKObjects.IAgStkObject)
            })

    # 获取某行为模式下传感器
    def get_sensor(self, pattern):
        if pattern not in self.pattern_list:
            print('satellite::get_sensor: 非法的行为模式')
            return None

        if pattern == 'large_scale':
            # FUTURE 待定,未来修改, 不确定单模式下是否有多个传感器在工作
            return self.iag_obj
        elif pattern == 'high_precision':
            # FUTURE 待定,未来修改, 不确定单模式下是否有多个传感器在工作
            if len(self.sensor_list) != 0:
                return self.sensor_list[0]['iag_obj']
            else:
                return None

    # 删除指定传感器
    def delete_sensor(self, sensor_index):
        # FUTURE
        pass

