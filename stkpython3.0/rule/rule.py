"""
根据模式给出对应执行策略，一般返回由命令字典组成的数组, 一个命令字典对应一个实体应进行的操作，仅决策不执行
命令字典格式如下，非...的即默认值
_ = {
    'object_type': ...,        # str, satellite/aircraft
    'index': ...,              # int, 卫星/WRJ列表中的号
    'pattern': ...,            # str, 卫星/WRJ的行为模式
    'level': ...,              # int, 指令优先级
    'location': ...,           # tuple, 地理坐标
    'start_time': ...,         # datetime, 事件开始时间
    'end_time': ...,           # datetime, 事件结束时间
    'duration': ...,           # int, 单位秒, 事件持续时间
    'params': ...              # str/dict, 其他信息
    }
"""

import util
import simulation


# 默认模式设定
def assign_default_pattern():
    pass


# 引导卫星 单目标渐进确认 任务分配规则
def assign_satellite_single_validation(manager, target, current_time, location=(50, 50), level=0):
    """

    :param manager: 临时：EventManager
    :param target: 临时：目标实体
    :param current_time: 事件发生时间
    :param location: FUTURE: 目标位置, 根据位置计算对应卫星
    :return:
    """

    # 规则给定值
    n = 2
    # 计算高精度探测模式下 距离给定时间最早能探测到目标的的n个卫星
    satellite_available = simulation.get_nearest_n_satellite_sim(manager, target, n, current_time)
    # 该时间周期 & 目标位置 无 可执行高精度探测的卫星 FUTURE
    if len(satellite_available) == 0:
        print('该目标无可用高精度探测卫星')
        return []
    # 可执行高精度探测卫星的数量不足   FUTURE
    elif len(satellite_available) < n:
        pass
    # 有足够数量的高精度探测卫星
    # 返回星或机的动作参数
    else:
        ret = [{'object_type': 'satellite',
                'index': i['index'],
                'pattern': 'high_precision',
                'level': level,
                'location': location,
                'start_time': i['start_time'],
                'end_time': i['end_time'],
                'duration': i['duration'],
                'params': ''}
               for i in satellite_available]
        return ret


# 引导卫星 多目标渐进确认 任务分配规则
def assign_satellite_multi_validation():
    pass


# 引导卫星 渐进确认失败 任务分配规则
def validation_failure():
    pass


# 引导WRJ 单目标渐进确认 任务分配规则 @lzk
# FUTURE 考虑 WRJ 不足时的分配和时间
def assign_aircraft_single_reconnoitre(manager, target, time, level=0):
    """
    :param manager: 临时，EventManager
    :param target: 临时，目标实体
    :param time:事件发生时间
    :param level: 优先级
    :return:
    """

    # 规则给定值
    ret = []
    n = 2
    # 计算空闲的无人机数量
    aircraft_available = simulation.get_nearest_n_aircraft_sim(manager, target, n, time)
    # 该时间周期 & 目标位置 无 可执行高精度探测的卫星 FUTURE
    if len(aircraft_available) == 0:
        print('无可用无人机')
        return []
    # 可执行高精度探测卫星的数量不足   FUTURE
    elif len(aircraft_available) < n:
        print('无人机数量不足')
        pass
    # 有足够数量的高精度探测卫星
    # 返回星或机的动作参数
    else:
        ret = [{'object_type': 'aircraft',
                'index': i['index'],
                'pattern': 'moving',
                'level': level,
                'location': target.get_current_location(),
                'start_time': i['start_time'],
                'end_time': i['end_time'],
                'duration': i['duration'],
                'params': ''}
               for i in aircraft_available]

    return ret


# 引导WRJ 多目标渐进确认 任务分配规则
def assign_aircraft_multi_validation():
    pass


# WRJ侦察任务完成 任务分配规则
def reconnoitre_complete(manager, task_index, aircraft_index):
    # index_list = []
    # for i, _aircraft in enumerate(manager.aircraft_list):
    #     if _aircraft.task_index == task_index:
    #         index_list.append(i)
    ret = [{'object_type': 'aircraft',
            'index': aircraft_index,
            'pattern': 'moving',
            'level': 0,
            'location': (),
            'start_time': None,
            'end_time': None,
            'duration': None,
            'params': ''}]

    return ret


# WRJ侦察任务失败 任务分配规则 未超时
def reconnoitre_failure_reassign():
    pass


# WRJ侦察任务失败 任务分配规则 超时
def reconnoitre_failure_timeout():
    pass
