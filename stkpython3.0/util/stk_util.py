"""
    与STK通信连接所抽象出的方法, 部分针对性任务写于对应类内
"""
import comtypes.client
import entity

# 连接 STK 实例
def connect_STK_instance(app_visible=1, user_control=1):
    # 返回根对象
    uiApplication = comtypes.client.GetActiveObject('STK12.Application')
    uiApplication.Visible = app_visible
    uiApplication.UserControl = user_control
    return uiApplication.Personality2

# 释放 STK 实例
def close_STK_instance():
    pass

# 获取指定时间 access 计算结果, 参数列表为空则表示计算整个场景范围的
def get_access_period(observers, pattern, targets, start_time=None, end_time=None):

    def custom_period(_access):
        _access.AccessTimePeriod = 2  # eUserSpecAccessTime
        accessTimePeriod = _access.AccessTimePeriodData

        accessTimePeriod.AccessInterval.State = 2  # eCrdnSmartIntervalStateStartStop

        accessStartEpoch = accessTimePeriod.AccessInterval.GetStartEpoch()
        accessStartEpoch.SetImplicitTime(start_time)
        accessTimePeriod.AccessInterval.SetStartEpoch(accessStartEpoch)

        accessStopEpoch = accessTimePeriod.AccessInterval.GetStopEpoch()
        accessStopEpoch.SetImplicitTime(end_time)
        accessTimePeriod.AccessInterval.SetStopEpoch(accessStopEpoch)

    def get_access(obs, tar):
        access = obs.GetAccessToObject(tar)
        if start_time and end_time:
            custom_period(access)
        access.ComputeAccess()
        _result = access.ComputedAccessIntervalTimes.ToArray(0, -1)
        return _result

    ret = []
    # 观测者和目标列表
    if type(observers) == list and type(targets) == list:
        for target in targets:
            sub = []
            for observer in observers:
                sensor = observer.get_sensor(pattern)
                try:
                    result = get_access(sensor, target.iag_obj)
                except:
                    result = []
                sub.append(result)
            ret.append(sub)
    # 单个观测者和目标
    else:
        sensor = observers.get_sensor(pattern)
        if sensor is not None:
            ret = get_access(sensor, targets.iag_obj)
        else:
            ret = []
    return ret

# 设置场景当前时间
def set_current_time():
    pass

# 获取场景当前时间
def get_current_time():
    pass
