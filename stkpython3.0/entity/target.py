import config
from comtypes.gen import STKObjects

class Target:
    def __init__(self, scenario, is_created, name='', params=None, obj=None):

        self.name = name
        self.type = STKObjects.eTarget
        self.scenario = scenario            # 所属场景
        self.obj = None
        self.iag_tar = None
        self.iag_obj = None

        self.level = 0                      # FUTURE 目标优先级
        self.location = (0,0)               # 目标坐标
        # FUTURE 个体的移动轨迹和可见时间待实现

        if not is_created:
            self.create_target(params)
        else:
            self.load_from_obj(obj)
    
    # 新建目标
    def create_target(self, params):
        # 创建特定名称的目标对象
        self.obj = self.scenario.sce.Children.New(self.type, self.name)
        # 从IAgSTKObject接口跳转至IAgSatellite
        self.iag_tar = self.obj.QueryInterface(STKObjects.IAgTarget)
        self.iag_obj = self.obj.QueryInterface(STKObjects.IAgStkObject)

    # 从已有对象载入目标对象
    def load_from_obj(self, obj):
        if obj is not None:
            self.obj = obj
            self.iag_tar = obj.QueryInterface(STKObjects.IAgTarget)
            self.iag_obj = obj.QueryInterface(STKObjects.IAgStkObject)
        else:
            print('target::创建失败, 传入为None')

    def get_current_location(self, time=None):
        raw = self.iag_tar.Position. QueryPlanetodeticArray()
        return raw[0], raw[1]
