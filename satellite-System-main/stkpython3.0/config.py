"""
储存常量和全局参数。创建的比较早，初始化用的实体参数列表现在来看大概是烂掉的，如果用得到建议重写
"""


# WRJ 列表

aircraft_list = [{'name': '', },
                 ]
# 目标 列表
facility_list = [{'name': '', 'latitude': 0, 'longitude': 0, 'altitude': 0},
                 {'name': '', 'latitude': 0, 'longitude': 0, 'altitude': 0},
                 {'name': '', 'latitude': 0, 'longitude': 0, 'altitude': 0},
                 ]
# 卫星 列表





satellite_list = [{'name': '', 'id': 111, 'path': ''},
                 ]

# STK 项目文件夹
stk_project_dir = 'C:/Users/David205x/Documents/STK Project/'
scenario_name = 'Scenario_learn'
scenario_path = f'{scenario_name}/{scenario_name}.sc'
scenario_path_absolute = stk_project_dir + scenario_path

# 本项目绝对路径
project_dir = 'C:/Users/David205x/Documents/PyCharm Project/pythonProject/'
# 卫星tle文件相对路径
tle_path = 'asset/yaogan.txt'
# 卫星tle文件绝对路径
tle_path_absolute = project_dir + tle_path
