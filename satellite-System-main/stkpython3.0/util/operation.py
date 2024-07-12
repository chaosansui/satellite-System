"""
可供主函数直接调用的方法，将具体操作逻辑包装后提供给主函数使用，有利于主函数的可读性
"""

import random

import entity
import config

# 从 config 中加载实体 UNTEST
def load_from_config(scenario, entity_type):

    ret = []

    if entity_type == 'aircraft':
        for item in config.aircraft_list:
            ret.append(entity.Aircraft(scenario, False, params=item))
    elif entity_type == 'satellite':
        for item in config.satellite_list:
            ret.append(entity.Satellite(scenario, item))
    elif entity_type == 'target':
        for item in config.facility_list:
            ret.append(entity.Target(scenario, item))
    else:
        raise NotImplementedError()

    return ret

# 随机生成数个实体
def load_from_random(scenario, entity_type, num):

    ret = []
    if entity_type == 'aircraft':
        for i in range(num):

            ret.append(entity.Aircraft(scenario, rf'aircraft{i}', params=''))
    # UNTEST
    elif entity_type == 'satellite':
        for i in range(num):
            params = {
                'PerigeeAltitude': random.randint(200, 800),  # 随机近地点高度，单位为千米
                'ApogeeAltitude': random.randint(200, 800),  # 随机远地点高度，单位为千米
                'Inclination': random.randint(0, 180),  # 随机轨道倾角，单位为度
                'ArgOfPerigee': random.randint(0, 360),  # 随机近地点幅角，单位为度
                'AscNode': random.randint(0, 360),  # 随机升交点赤经，单位为度
                'TrueAnomaly': random.randint(0, 360),  # 随机真近点角，单位为度
            }
            ret.append(entity.Satellite(scenario, False, rf'satellite_{i}', params=params))

    elif entity_type == 'target':
        for i in range(num):
            ret.append(entity.Target(scenario, {'name': rf'target{i}'}))
    else:
        raise NotImplementedError()

    return ret

# 从tle文件中加载卫星实体
def load_satellite_from_tle(scenario, tle_path):
    # 返回字典格式的必须信息并且调用对应载入方法
    ret = []
    with open(tle_path, 'r') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 3):
            name = lines[i].split(' ')[0].replace('\n', '').strip()
            # 读取根数中第三行卫星编号
            norad = lines[i + 2].split(' ')[1]
            ret.append(entity.Satellite(scenario, False, name, {'id': norad, 'path': tle_path}))
    return ret

