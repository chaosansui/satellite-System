"""
事件管理类，消息队列。按时间顺序给出每个需要做出决策的事件，一般由卫星access初始化，接收决策产生的事件并进行清理和排序
事件字典格式如下 非...的即默认值
_ = {
    'event_index': -1,        # 事件序号
    'event_type': ...,      # 事件类型, 用于区分操作
    'start_time': ...,      # 事件起始时间
    'end_time': ...,        # 事件终止时间
    'duration': ...,        # 事件持续时间
    'observer_index': ...,    # 观测者编号
    'target_index': ...,      # 目标编号
    'task_index': -1,         # 所属任务编号
    'level': 0,             # 事件优先度 FUTURE
    'params': ''            # 回报参数 FUTURE
    }
"""

import heapq
import datetime
import util
import simulation


def color_print(event):
    red = '\033[91m'
    yellow = '\033[93m'
    green = '\033[92m'
    suffix = '\033[0m'

    print('[E%02d]-[T%02d]-\033[92m[L%d]\033[0m %s %35s  satellite_%02d target_%02d'
          % (event['event_index'],
             event['task_index'],
             event['level'],
             str(event['start_time']).ljust(30, ' '),
             event['event_type'],
             event['observer_index'],
             event['target_index']
             ))
    # if event['event_type'] == 'satellite_discovery':
    #     print(green + '[event]' + str(event) + suffix)
    # elif event['event_type'] == 'satellite_single_validation':
    #     print(yellow + '[event]' + str(event) + suffix)


class Event:
    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        if self.value['start_time'] != other.value['start_time']:
            return self.value['start_time'] < other.value['start_time']
        elif self.value['level'] != other.value['level']:
            return self.value['level'] < other.value['level']
        elif self.value['task_index'] != other.value['task_index']:
            return self.value['task_index'] < other.value['task_index']

    def __str__(self):
        ret = '[E%02d]-[T%02d]-\033[92m[L%d]\033[0m %s %35s  observer_%02d target_%02d\t%s' \
              % (self.value['event_index'],
                 self.value['task_index'],
                 self.value['level'],
                 str(self.value['start_time']).ljust(30, ' '),
                 self.value['event_type'],
                 self.value['observer_index'],
                 self.value['target_index'],
                 self.value['params'])
        return ret

class EventManager:
    def __init__(self, satellite_list, aircraft_list, sm_target_list, events=None):

        self.satellite_list = satellite_list
        self.aircraft_list = aircraft_list
        self.sm_target_list = sm_target_list

        self.todo_list = []         # 事件待办列表, heapq
        self.todo_list = []         # 事件待办列表, heapq
        self.done_list = []         # 事件已完成列表, list

        self.shpa_list = []         # 临时属性, 存放所有卫星在 高精度模式 下与目标的 access

        # 用 count -> cnt 缩写的代码害我不浅
        self.event_count = 0
        self.task_count = 0

        # 使用卫星大规模探测事件初始化事件列表
        if events is None:
            _list, _ = simulation.get_event_list('env_target_under_window_period', satellite_list, 'large_scale', sm_target_list)
            self.add_events(_list)
        # 使用给定事件初始化事件列表
        else:
            self.add_events(events)
        # 载入卫星高精度探测 access
        _list, _ = simulation.get_event_list('', satellite_list, 'high_precision', sm_target_list)
        for event in _list:
            heapq.heappush(self.shpa_list, Event(event))

    # 获取新事件编号
    def get_event_index(self):
        self.event_count += 1
        return self.event_count

    # 获取新任务编号 (外部不应使用)
    def get_task_index(self):
        self.task_count += 1
        return self.task_count

    # 添加单个事件, 事件添加时无需event_index, 被执行时才会分配
    def add_event(self, event, task_index=None):
        # 按照 事件开始时间 和 优先级 进行排序
        heapq.heappush(self.todo_list, (Event(event)))

    # 批量添加事件
    def add_events(self, events):
        for event in events:
            self.add_event(event)

    # 移除单个事件
    def remove_event(self):
        pass

    # 批量移除事件 多个 feature 默认为与条件
    def remove_events(self, feature):
        new_list = []
        heapq.heapify(new_list)

        while len(self.todo_list) != 0:
            event = heapq.heappop(self.todo_list)
            flag = True
            for key, value in feature.items():
                flag = flag and event.value[key] == feature[key]
            if not flag:
                heapq.heappush(new_list, event)

        self.todo_list = new_list

    # 获取接下来的事件 此时才对 event_index 和 task_index 进行赋值
    def get_next_event(self):
        # 从列表取出事件并解压
        event = heapq.heappop(self.todo_list)
        # event = event.value
        # 分配 index
        event.value['event_index'] = self.get_event_index()
        if event.value['task_index'] == -1:
            event.value['task_index'] = self.get_task_index()

        # 放入 done_list
        if event.value['event_type'].startswith('env'):
            event.value['class'] = 'env'
        elif event.value['event_type'].startswith('report'):
            event.value['class'] = 'report'
        elif event.value['event_type'].startswith('rule'):
            event.value['class'] = 'rule'
        else:
            event.value['class'] = 'action'
        self.done_list.append(event)

        print(event)
        # color_print(event)
        return event.value

    # 场景发生变化, 事件列表进行更新
    def update_event(self):
        pass

    # 事件列表是否为空
    def is_event_empty(self):
        return len(self.todo_list) == 0

    # 保存日志
    def save_log(self):
        path = f'simulation/log/todo.csv'
        with open(str(path), 'w+') as f:
            f.write('event_index,event_type,start_time,end_time,duration,observer_index,target_index,task_index,level,param\n')
            for event in self.todo_list:
                for _, value in event.value.items():
                    f.write(str(value))
                    f.write(',')
                f.write('\b\n')

        with open(f'simulation/log/done.csv', 'w+') as f:
            f.write('event_index,event_type,start_time,end_time,duration,observer_index,target_index,task_index,level,param,class\n')
            for event in self.done_list:
                for _, value in event.value.items():
                    f.write(str(value).replace(',', ';'))
                    f.write(',')
                f.write('\n')

    # 绘制 gantt 图
    def draw_gantt(self):
        task_count = 0
        task_list = {}
        for _event in self.done_list:
            if _event.value['task_index'] not in task_list:
                task_list[_event.value['task_index']] = []
            task_list[_event.value['task_index']].append(_event)

        with open('simulation/log/gantt.md', 'w+') as gantt:
            gantt.write('```mermaid\n')
            gantt.write('gantt\n')
            gantt.write('    title gantt_graph\n')
            gantt.write('    dateFormat YYYY-MM-DD hh:mm:ss\n')
            for i, events in task_list.items():
                gantt.write(f'    section task{i}\n')
                for j, event in enumerate(events):
                    if j != len(events) - 1:
                        duration = (events[j+1].value['start_time'] - event.value["start_time"]).seconds
                    else:
                        duration = 20
                    gantt.write('        %s: %s, %is\n' % (
                        event.value["event_type"],
                        event.value["start_time"],
                        duration))
            gantt.write('```\n\n')
