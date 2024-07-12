import datetime
import random

import config
import entity
import rule
import simulation
import time
import util
from comtypes.gen import STKObjects

from entity import target

aircraft_list = []
satellite_list = []
sm_target_list = []

# command 格式示例
_ = {
    'object_type': ...,  # str, satellite/aircraft
    'index': ...,  # int, 卫星/WRJ列表中的号
    'pattern': ...,  # str, 卫星/WRJ的行为模式
    'level': ...,  # int, 指令优先级
    'location': ...,  # tuple, 地理坐标
    'start_time': ...,  # datetime, 事件开始时间
    'end_time': ...,  # datetime, 事件结束时间
    'duration': ...,  # int, 单位秒, 事件持续时间
    'params': ...  # str/dict, 其他信息
}
# event 示例 非...的即默认值
_ = {
    'event_index': -1,  # 事件序号
    'event_type': ...,  # 事件类型, 用于区分操作
    'start_time': ...,  # 事件起始时间
    'end_time': ...,  # 事件终止时间
    'duration': ...,  # 事件持续时间
    'observer_index': ...,  # 观测者编号
    'target_index': ...,  # 目标编号
    'task_index': -1,  # 所属任务编号
    'level': 0,  # 事件优先度 FUTURE
    'params': ''  # 回报参数 FUTURE
}


def execute_command(_command):
    if _command['object_type'] == 'satellite':
        pass
    elif _command['object_type'] == 'aircraft':
        pass


def main_1():
    # global aircraft_list, satellite_list, sm_target_list, satellite_event_list, satellite_event_matrix
    # 连接STK应用实例
    # root = util.connect_STK_instance()
    # 通过读取 载入场景及个元素
    # scenario = entity.Scenario(root, True, path=config.scenario_path_absolute)
    # 载入当前打开的场景
    # scenario = entity.Scenario(root, True)
    # aircraft_list = scenario.get_entities(STKObjects.eAircraft)
    # satellite_list = scenario.get_entities(STKObjects.eSatellite)
    # sm_target_list = scenario.get_entities(STKObjects.eTarget)

    # satellite_event_list, satellite_event_matrix = util.get_event_list('', satellite_list, 'large_scale', sm_target_list)
    pass

    print()


def main_2():
    # 连接STK应用实例
    # root = util.connect_STK_instance()
    # 通过创建 新建场景以及各元素
    # scenario = util.create_scenario(root, 'scenario_test')
    # scenario.set_scenario_time(start_time='14 Apr 2024 00:00:00.000',
    #                            end_time='14 Apr 2024 12:00:00.000')
    # aircraft_list = util.load_from_config(scenario, 'aircraft')
    # satellite_list = util.load_satellite_from_tle(scenario, config.tle_path_absolute)
    # sm_target_list = util.load_from_random(scenario, 'target', 3)
    #
    # scenario.save_scenario(config.scenario_path_absolute)
    pass


if __name__ == '__main__':


    st = time.time()
    # 连接STK应用实例
    root = util.connect_STK_instance()
    print('\033[92m# [%3ds] STK client connected successfully \033[0m' % (time.time() - st))
    # 载入当前打开的场景
    scenario = entity.Scenario(root, True)
    print('\033[92m# [%3ds] Current scenario loaded successfully\033[0m' % (time.time() - st))
    # 加载场景中相关物体
    aircraft_list = scenario.get_entities(STKObjects.eAircraft)
    satellite_list = scenario.get_entities(STKObjects.eSatellite)
    sm_target_list = scenario.get_entities(STKObjects.eTarget)
    print('\033[92m# [%3ds] Entities loaded successfully from the current scenario\033[0m' % (time.time() - st))

    manager = simulation.EventManager(satellite_list, aircraft_list, sm_target_list)
    print('\033[92m# [%3ds] Event manager initialization completed\033[0m' % (time.time() - st))
    # 事件列表按序处理
    while not manager.is_event_empty():
        # 取出将处理的事件
        event = manager.get_next_event()

        # (环境触发) 某目标处于某卫星可视窗口内
        if event['event_type'] == 'env_target_under_window_period':
            # 生成 0-1 随机数
            rand = float(random.randint(1, 100)) / 100
            # 根据概率确定事件分支
            # flag = rand < util.infrared_imaging_move()
            flag = rand < 1

            # 若目标被发现, 添加report且进行satellite_single_validation的安排
            if flag:
                # 按照概率模拟发现时间, 即下一个事件的事件
                event_time = event['start_time'] + datetime.timedelta(seconds=rand * event['duration'])
                # 添加侦测发现通知
                manager.add_event({
                    'event_index': -1,
                    'event_type': 'report_satellite_discovery',
                    'start_time': event_time,
                    'end_time': None,
                    'duration': None,
                    'observer_index': event['observer_index'],
                    'target_index': event['target_index'],
                    'task_index': event['task_index'],
                    'level': event['level'],
                    'params': event['params']
                })
                # 获取决策指令
                command = rule.assign_satellite_single_validation(manager, sm_target_list[event['target_index']],
                                                                  event_time)
                # 记录决策指令
                manager.add_event({
                    'event_index': -1,
                    'event_type': 'rule_assign_satellite_validation',
                    'start_time': event_time + datetime.timedelta(seconds=20),
                    'end_time': None,
                    'duration': None,
                    'observer_index': -1,
                    'target_index': event['target_index'],
                    'task_index': event['task_index'],
                    'level': event['level'],
                    'params': str([i['index'] for i in command])
                })
                # 根据决策添加下一步事件
                for cmd in command:
                    manager.add_event({
                        'event_index': -1,
                        'event_type': 'satellite_single_validation',
                        'start_time': event_time + datetime.timedelta(seconds=30),
                        'end_time': cmd['end_time'],
                        'duration': cmd['duration'],
                        'observer_index': cmd['index'],
                        'target_index': event['target_index'],
                        'task_index': event['task_index'],
                        'level': cmd['level'],
                        'params': cmd['params']
                    })
                manager.remove_events({
                    'event_type': 'env_target_under_window_period',
                    'target_index': event['target_index']})

            # 没有发现目标, 添加report
            else:
                manager.add_event({
                    'event_index': -1,
                    'event_type': 'report_satellite_discovery_miss',
                    'start_time': event['end_time'],
                    'end_time': None,
                    'duration': None,
                    'observer_index': event['observer_index'],
                    'target_index': event['target_index'],
                    'task_index': event['task_index'],
                    'level': 0,
                    'params': ''
                })

        # (主动触发) 卫星引导卫星对某坐标进行高精度探测
        elif event['event_type'] == 'satellite_single_validation':
            # 生成 0-1 随机数
            rand = float(random.randint(1, 100)) / 100
            # 根据概率确定事件分支
            # flag = rand < util. ...()
            flag = rand < 1

            # 若目标坐标被高精度确认, 添加report且进行aircraft航点安排
            if flag:
                # 按照概率模拟发现时间, 即下一个事件的事件
                event_time = event['start_time'] + datetime.timedelta(minutes=rand * 100)
                # 添加侦测发现通知
                manager.add_event({
                    'event_index': -1,
                    'event_type': 'report_satellite_validation',
                    'start_time': event_time,
                    'end_time': None,
                    'duration': None,
                    'observer_index': event['observer_index'],
                    'target_index': event['target_index'],
                    'task_index': event['task_index'],
                    'level': event['level'],
                    'params': event['params']
                })

            # 未确认目标 添加报告
            else:
                manager.add_event({
                    'event_index': -1,
                    'event_type': 'report_satellite_validation_miss',
                    'start_time': event['end_time'],
                    'end_time': None,
                    'duration': None,
                    'observer_index': event['observer_index'],
                    'target_index': event['target_index'],
                    'task_index': event['task_index'],
                    'level': 0,
                    'params': ''
                })

        # 卫星高精度探测到结果 指导 WRJ 下一步
        elif event['event_type'] == 'report_satellite_validation':
            # 获取决策指令
            event_time = event['start_time'] + datetime.timedelta(seconds=100)
            command = rule.assign_aircraft_single_reconnoitre(manager, sm_target_list[event['target_index']],
                                                              event_time)
            # 记录决策指令
            manager.add_event({
                'event_index': -1,
                'event_type': 'rule_assign_aircraft_reconnoitre',
                'start_time': event_time,
                'end_time': None,
                'duration': None,
                'observer_index': -1,
                'target_index': event['target_index'],
                'task_index': event['task_index'],
                'level': event['level'],
                'params': str([i['index'] for i in command])
            })

            for cmd in command:
                # 根据 cmd 指派对应 WRJ 起飞到达指定地点
                manager.aircraft_list[cmd['index']].set_destination(cmd['location'], event['task_index'], event_time)
                # 根据 cmd 得知 WRJ 规划路线后 根据事件 添加 WRJ 到达事件
                manager.add_event({
                    'event_index': -1,
                    'event_type': 'aircraft_arrival',
                    'start_time': manager.aircraft_list[cmd['index']].get_latest_waypoint()['time'],
                    'end_time': cmd['end_time'],
                    'duration': cmd['duration'],
                    'observer_index': cmd['index'],
                    'target_index': event['target_index'],
                    'task_index': event['task_index'],
                    'level': cmd['level'],
                    'params': cmd['params']
                })

        # 卫星渐进确认失败
        # elif event['event_type'] == 'satellite_validation_failure':

        # # (主动触发) WRJ 到达指定坐标
        elif event['event_type'] == 'aircraft_arrival':
            # 生成 0-1 随机数
            rand = float(random.randint(1, 100)) / 100
            # 根据概率确定事件分支
            # flag = rand < util. ...()
            flag = rand < 0.1
            # 确认成功
            if flag:
                # 按照概率模拟发现时间, 即下一个事件的事件
                event_time = event['start_time'] + datetime.timedelta(minutes=rand * 100)
                command = rule.reconnoitre_complete(manager, event['task_index'], event['observer_index'])
                for cmd in command:
                    manager.add_event({
                        'event_index': -1,
                        ####
                        'event_type': 'aircraft_reconnoitre_complete',
                        'start_time': event_time,
                        'end_time': event['end_time'],
                        'duration': event['duration'],
                        'observer_index': cmd['index'],
                        'target_index': event['target_index'],
                        'task_index': event['task_index'],
                        'level': event['level'],
                        'params': cmd['params']
                    })
                    manager.aircraft_list[cmd['index']].task_complete(event_time)
                # manager.remove_events({
                #     'event_type': 'satellite_discovery',
                #     'target_index': event['target_index']})
            else:
                manager.add_event({
                    'event_index': -1,
                    'event_type': 'reconnoitre_failure_reassign',
                    'start_time': event['end_time'],
                    'end_time': None,
                    'duration': None,
                    'observer_index': event['observer_index'],
                    'target_index': event['target_index'],
                    'task_index': event['task_index'],
                    'level': 0,
                    'params': {'reconnoitre_count': 1}
                })
            pass

        # elif event['event_type'] == 'aircraft_single_reconnoitre':
        #     pass
        # 飞机发现目标
        elif event['event_type'] == 'aircraft_reconnoitre_complete':
            # 确认成功
            event_time = event['start_time'] + datetime.timedelta(seconds=10)
            manager.add_event({
                'event_index': -1,
                'event_type': 'report_mission_over',
                'start_time': event_time,
                'end_time': event['end_time'],
                'duration': event['duration'],
                'observer_index': event['observer_index'],
                'target_index': event['target_index'],
                'task_index': event['task_index'],
                'level': event['level'],
                'params': 'information'
            })
            pass
        # 无人机探测失败
        elif event['event_type'] == 'reconnoitre_failure_reassign':
            # 生成 0-1 随机数
            # 调用概率计算函数
            rand = float(random.randint(1, 100)) / 100
            # 根据概率确定事件分支
            # flag = rand < util. ...()
            command = rule.assign_aircraft_single_reconnoitre(manager, sm_target_list[event['target_index']],
                                                              event_time)
            for cmd in command:
                manager.aircraft_list[event['observer_index']].area_detection(cmd['location'], radius=2)
            flag = rand < 1
            event_time = event['start_time'] + datetime.timedelta(seconds=rand * 100)
            # event_time = aircraft_list[event['observe_index']].get_complete_time()
            # 确认成功
            if flag:
                command = rule.reconnoitre_complete(manager, event['task_index'], event['observer_index'])
                for cmd in command:
                    manager.add_event({
                        'event_index': -1,
                        'event_type': 'aircraft_reconnoitre_complete',
                        'start_time': event_time,
                        'end_time': event['end_time'],
                        'duration': event['duration'],
                        'observer_index': cmd['index'],
                        'target_index': event['target_index'],
                        'task_index': event['task_index'],
                        'level': event['level'],
                        'params': cmd['params']
                    })
                    manager.aircraft_list[cmd['index']].task_complete(event_time)
                # manager.remove_events({
                #     'event_type': 'satellite_discovery',
                #     'target_index': event['target_index']})
            elif event['params']['reconnoitre_count'] < 2:
                manager.add_event({
                    'event_index': -1,
                    'event_type': 'reconnoitre_failure_reassign',
                    'start_time': event_time,
                    'end_time': None,
                    'duration': None,
                    'observer_index': event['observer_index'],
                    'target_index': event['target_index'],
                    'task_index': event['task_index'],
                    'level': 0,
                    'params': {'reconnoitre_count': event['params']['reconnoitre_count'] + 1}
                })
            else:
                manager.add_event({
                    'event_index': -1,
                    'event_type': 'reconnoitre_failure_timeout',
                    'start_time': event_time,
                    'end_time': None,
                    'duration': None,
                    'observer_index': event['observer_index'],
                    'target_index': event['target_index'],
                    'task_index': event['task_index'],
                    'level': 0,
                    'params': {'reconnoitre_count': event['params']['reconnoitre_count'] + 1}
                })
            # command = rule.reconnoitre_failure_reassign(manager, sm_target_list[event['target_index']],
            #                                             event_time)
            # for cmd in command:
            #     manager.add_event({
            #         'event_index': -1,
            #         'event_type': 'aircraft_reconnoitre_complete',
            #         'start_time': cmd['start_time'],
            #         'end_time': cmd['end_time'],
            #         'duration': cmd['duration'],
            #         'observer_index': cmd['index'],
            #         'target_index': event['target_index'],
            #         'task_index': event['task_index'],
            #         'level': cmd['level'],
            #         'params': cmd['params']
            #     })

        elif event['event_type'] == 'reconnoitre_failure_timeout':
            command = rule.reconnoitre_failure_timeout(manager, sm_target_list[event['target_index']],
                                                       event_time)
            for cmd in command:
                manager.add_event({
                    'event_index': -1,
                    'event_type': 'report_mission_over',
                    'start_time': cmd['start_time'],
                    'end_time': cmd['end_time'],
                    'duration': cmd['duration'],
                    'observer_index': cmd['index'],
                    'target_index': event['target_index'],
                    'task_index': event['task_index'],
                    'level': cmd['level'],
                    'params': ''
                })

        elif event['event_type'] == 'report_mission_over':
            manager.aircraft_list[event['observer_index']].task_complete()
        else:
            pass

    print('\033[92m# [%3ds] Simulation completed\033[0m' % (time.time() - st))
    manager.save_log()
    print('\033[92m# [%3ds] Log saved\033[0m' % (time.time() - st))
    # manager.draw_gantt()
