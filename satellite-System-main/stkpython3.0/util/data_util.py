"""
涉及数学运算的方法，大多方法应返回计算数值。此处的方法不应被主函数直接调用，请于合适位置对对应功能进行调用封装
"""

import math
import random
# 英制单位转国际单位, feet_to_km：英尺换算为公里，
def feet_to_km(feet_value):
    return 0.3048 / 1000 * feet_value

# 英制单位转国际单位, knots_to_km_per_second：节转换为km/s。
def knots_to_km_per_s(knots_value):
    return 1.852 / 3600 * knots_value


# 红外载荷对 静止陆基sm目标 的探测概率 UNTEST
def infrared_static_prob(F, S, H, Nc, NETD, T, fweather, w):
    """
    :param F: 卫星发射率
    :param S: 接收面积
    :param H: 卫星高度
    :param Nc: 目标数量
    :param NETD: 噪声等效温度差
    :param T: 积分时间
    :param fweather:天气因子
    :return:
    """
    # 首先计算信噪比（SNR）
    n0 = (S / H) * Nc
    SNR = (0.2 * F * n0) ** 0.5 * (T / NETD)
    if SNR > 1:
        # 根据信噪比计算侦察概率。
        p = fweather * (1 - math.exp(-0.15 * ((SNR - 1) ** 2)))
        return p
    else:
        return 0

# 红外载荷对 动态陆基sm目标 的探测概率 UNTEST
def infrared_imaging_move(F, S, H, Nc, NETD, fweather, i, longitude, latitude, A, Gmax, T, w):
    """
    :param F: 卫星发射率
    :param S: 接收面积
    :param H: 卫星高度
    :param Nc: 目标数量
    :param NETD: 噪声等效温度差
    :param fweather:天气因子
    :param T1:
    :param i:卫星轨道的倾角
    :param longitude:探测区域的经度间隔
    :param latitude:纬度间隔
    :param A:探测区域的面积
    :param Gmax:最大观测时间
    :param T:积分时间
    :return:
    """
    Re = 6371.393
    angle_radians = math.radians(i)
    # i为卫星轨道倾角
    if angle_radians > math.atan(longitude / latitude) or angle_radians == math.atan(latitude / longitude):
        a = Re * longitude * w
        b = A * math.sin(angle_radians)
        z = a / b
        g = 1 - math.exp(-z)
    else:
        z = Re * longitude * w / (A * math.cos(angle_radians))
        g = 1 - math.exp(-z)
    n = T / Gmax
    # 根据卫星轨道倾角和探测区域的位置，计算侦察卫星在内在某一区域发现目标的概率
    p0 = 1 - (1 - g) ** n
    p = infrared_static_prob(F, S, H, Nc, NETD, T, fweather, w)
    # 并将其与红外成像卫星的静止侦察概率相乘，得到移动侦测概率。
    pm = p * p0
    return pm

#可见光对静止陆基sm目标的探测概率
def optical_imaging(ji=7.8, yf=1, l=20, H=35800000, B=4, solar_altitude_angle=0.3, target_contrast=1, meteorological_impact=1,
                    satellite_stabilization=0.9511):
    cx = ji / H
    lf = (1 / (yf * cx)) * 0.0000001
    thr = (((B * lf) / l) ** 2)
    ptheory = math.exp(-thr)
    P = ptheory * solar_altitude_angle * target_contrast * meteorological_impact * satellite_stabilization
    return P

#SAR可见光对静止陆基sm目标的探测概率
def sar(s=200, b=1, r=0.01):
    p = math.exp(math.sqrt(s) - b * r) / (1 + math.exp(math.sqrt(s) - b * r))
    return p

# 根据轨道计算 前n近的卫星
def get_nearest_n_satellite():
    pass

# 根据起飞点和目标点设置飞行路径点
def generate_waypoints(start, destination):
    pass