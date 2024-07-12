"""
维护事件列表所涉及的方法/借助STK上帝视角实现的一些功能。
方法名含"_sim"尾缀的在后续应被逐步替换掉，所以可以写的稍微随意一些（划掉）
"""
import math
import random
from datetime import datetime
import util
import heapq

time_format = '%d %b %Y %H:%M:%S.%f'


# 时间转换 str -> datetime
def str_to_datetime(_time, _format=time_format):
    return datetime.strptime(_time, _format)


# 计算每段 观测窗口 时长(秒)
def calc_access_duration(start_time, end_time):
    time1 = str_to_datetime(start_time)
    time2 = str_to_datetime(end_time)

    duration = time2 - time1
    seconds = int(duration.total_seconds())
    return seconds


# 事件列表排序
def sort_event_list(event_list):
    return sorted(event_list, key=lambda x: (x['start_time'], x['level']))


# 整理事件
def get_event_list(event_type, observers, pattern, targets):
    event_list = []
    event_matrix = []

    access_raw = util.get_access_period(observers, pattern, targets)

    for i, tar_acc_list in enumerate(access_raw):
        _sub = []
        for j, obs_acc_list in enumerate(tar_acc_list):
            __sub = []
            for k, raw_event in enumerate(obs_acc_list):
                _event = {
                    'event_index': -1,
                    'event_type': event_type,
                    'start_time': str_to_datetime(raw_event[0]),
                    'end_time': str_to_datetime(raw_event[1]),
                    'duration': calc_access_duration(raw_event[0], raw_event[1]),
                    'observer_index': j,
                    'target_index': i,
                    'task_index': -1,
                    'level': 0,
                    'params': ''
                }
                __sub.append(_event)
                event_list.append(_event)
            _sub.append(__sub)
        event_matrix.append(_sub)

    # event_list_sorted = sort_event_list(event_list)
    # return event_list_sorted, event_matrix
    return event_list, event_matrix


# 根据事件列表筛选 前n近的卫星
def get_nearest_n_satellite_sim(_manager, target, n, current_time):
    # 无所谓层级乱用参数什么的了, 只是模拟
    _heap = _manager.shpa_list.copy()
    ret = []
    while len(ret) < n and len(_heap) > 0:
        _event = heapq.heappop(_heap).value
        if _event['end_time'] > current_time:
            if _manager.satellite_list[_event['observer_index']].pattern == 'large_scale':
                ret.append({'index': _event['observer_index'],
                            'start_time': _event['start_time'],
                            'end_time': _event['start_time'],
                            'duration': int((_event['end_time'] - _event['start_time']).total_seconds())
                            })
    return ret



def get_nearest_n_aircraft_sim(_manager, target, n, current_time):
    ret = []
    free_aircraft_list = []
    # # 遍历无人机列表，获取所有空闲的无人机列表
    # for _aircraft in _manager.aircraft_list:
    #     if _aircraft.task_index == -1:
    #         free_aircraft_list.append(_aircraft)
    # # 如果空闲的无人机小于等于n，输出仅有的空闲无人机列表
    # if len(free_aircraft_list) <= n:
    #     for _aircraft in free_aircraft_list:
    #         ret.append({'index': _aircraft.index,
    #                     'start_time': current_time,
    #                     'end_time': current_time,
    #                     'duration': 0
    #                     })
    # # 否则获取通过计算target和无人机的位置，获取距离最近的n个无人机
    # else:
    #     distance_list = []
    #     for _aircraft in free_aircraft_list:
    #         # 计算无人机和目标的距离
    #         distance = calc_distance(_aircraft.get_current_location(current_time), target.location)
    #         # 将无人机序号和距离添加进数组中,并排序
    #         distance_list.append({'index': _aircraft.index, 'distance': distance})
    #     distance_list.sort(key=lambda x: x['distance'])
    #     i = 0
    #     while i < n:
    #         ret.append({'index': distance_list[i]['index'],
    #                     'start_time': current_time,
    #                     'end_time': current_time,
    #                     'duration': 0
    #                     })
    #         i += 1
    for i, _aircraft in enumerate(_manager.aircraft_list):
        if _aircraft.continuous_count <= _aircraft.max_continuous_count:
            free_aircraft_list.append((i, _aircraft.continuous_count))

    free_aircraft_list.sort(key=lambda x: x[1])
    free_aircraft_list = free_aircraft_list[:min(len(free_aircraft_list), n)]

    for i in free_aircraft_list:
        _time = max(current_time, _manager.aircraft_list[i[0]].get_latest_waypoint()['time'])
        ret.append({'index': i[0],
                    'start_time': _time,
                    'end_time': _time,
                    'duration': 0
                    })
    return ret


def calc_distance(location_a, location_b):
    # 计算两点之间的距离
    return ((location_a[0] - location_b[0]) ** 2 + (location_a[1] - location_b[1]) ** 2) ** 0.5


# 根据起点和终点坐标 生成 中间路径点和终点的数组
def generate_waypoints_sim(start, destination, num=3):
    ret = []
    # for i in range(num):
    #     offset = random.randint(5, 10)
    #     ret.append({
    #         'latitude': start[0] + (destination[0] - start[0] + offset) * num / 3,
    #         'longitude': start[1] + (destination[1] - start[1] + offset) * num / 3,
    #         'altitude': 100,
    #         'speed': offset
    #     })
    ret.append({
        'latitude': destination[0],
        'longitude': destination[1],
        'altitude': 100,
        'speed': 3
    })
    return ret
# 新建函数区域点生成函数
def generate_areapoints_sim(start, destination, radius_nm,num_points=10):
    ret = []
    radius_deg = radius_nm / 60.0
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        lat_offset = radius_deg * math.cos(angle)
        lon_offset = radius_deg * math.sin(angle) / math.cos(math.radians(destination[0]))
        waypoint_lat =destination[0] + lat_offset
        waypoint_lon = destination[1] + lon_offset
        ret.append({
            'latitude': waypoint_lat,
            'longitude': waypoint_lon,
            'altitude': 100,
            'speed': 3
        })
    return ret

# 参数中心点，半径，
# 往里塞的点就是巡航目标点
# 返回ret.append({
#         'latitude': destination[0],
#         'longitude': destination[1],
#         'altitude': 100,
#         'speed': 3
#     })
#     return ret