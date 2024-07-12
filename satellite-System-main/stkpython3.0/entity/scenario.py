import entity
from comtypes.gen import STKObjects

class Scenario:
    def __init__(self, root, is_created, name='', path=None):
        """
        :param root: 该场景所依附的STK应用实例
        :param is_created: 目标场景是否已被创建, True则读取已有场景文件, False则新建场景
        :param path:
        :param name:
        """

        self.name = name                    # 场景名称
        self.type = STKObjects.eScenario    # 所属种类
        self.root = root
        self.sce = None
        self.interface = None

        if is_created:
            self.load_scenario(path)
        else:
            self.create_scenario(name)

    # 创建新场景
    def create_scenario(self, name):
        print('创建场景中...')
        root_iag = self.root.QueryInterface(STKObjects.IAgStkObject)
        self.sce = root_iag.Children.New(STKObjects.eScenario, name)
        self.interface = self.sce.QueryInterface(STKObjects.IAgScenario)
        self.name = name

    # 加载已有场景
    def load_scenario(self, path):
        # 从文件中加载场景
        if path is not None:
            self.root.load(path)
        # 连接当前stk实例中的场景
        print('加载场景中...')
        self.sce = self.root.CurrentScenario
        self.interface = self.sce.QueryInterface(STKObjects.IAgScenario)
        self.name = self.sce.InstanceName

    # 保存当前场景
    def save_scenario(self, path):
        if self.sce is not None:
            self.root.SaveAs(path)
            print(f'保存场景成功至{path}！')

    # 设置场景时间
    def set_scenario_time(self,
                          start_time='11 Apr 2024 00:00:00.000 ',
                          end_time='11 Apr 2024 01:00:00.000 ',
                          date_format='UTCG'):
        self.root.UnitPreferences.SetCurrentUnit('DateFormat', date_format)
        self.interface.SetTimePeriod(start_time, end_time)
        # self.root.Rewind()
        print('设置仿真时间成功！')

    # 获取场景中单个实体的数据
    def get_entity(self, entity_type, entity_name):
        entity_list = self.sce.Children.GetElements(entity_type)
        entity = entity_list.Item(entity_name)
        return entity

    # 获取场景中某一类型实体列表
    def get_entities(self, entity_type):
        entity_list = self.sce.Children.GetElements(entity_type)
        ret = []
        for item in entity_list:
            name = item.InstanceName
            if entity_type == STKObjects.eAircraft:
                ret.append(entity.Aircraft(self, True, name, obj=item))
            elif entity_type == STKObjects.eSatellite:  # satellite
                ret.append(entity.Satellite(self, True, name, obj=item))
            elif entity_type == STKObjects.eTarget:
                ret.append(entity.Target(self, True, name, obj=item))
        return ret

    # 移除场景中某一实体
    def remove_entity(self, entity):
        self.sce.Children.Unload(entity.type, entity.name)
        pass
