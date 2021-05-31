# /usr/bin/env python
# -*- coding:utf-8 -*-

"""
1.解析 crontab 配置文件中的五个数间参数(分 时 日 月 周)，获取他们对应的取值范围
2.将时间戳与crontab配置中一行时间参数对比，判断该时间戳是否在配置设定的时间范围内
"""

# $Id $

import re, time, sys
from Core.FDateTime.FDateTime import FDateTime


def get_struct_time(time_stamp_int):
    """
    按整型时间戳获取格式化时间 分 时 日 月 周
    Args:
        time_stamp_int 为传入的值为时间戳(整形)，如：1332888820
        经过localtime转换后变成
        time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    Return:
        list____返回 分 时 日 月 周
    """

    st_time = time.localtime(time_stamp_int)
    return [st_time.tm_min, st_time.tm_hour, st_time.tm_mday, st_time.tm_mon, st_time.tm_wday]


def get_strptime(time_str, str_format):
    """从字符串获取 整型时间戳
    Args:
        time_str 字符串类型的时间戳 如 '31/Jul/2013:17:46:01'
        str_format 指定 time_str 的格式 如 '%d/%b/%Y:%H:%M:%S'
    Return:
        返回10位整型(int)时间戳，如 1375146861
    """
    return int(time.mktime(time.strptime(time_str, str_format)))


def get_str_time(time_stamp, str_format='%Y%m%d%H%M'):
    """
    获取时间戳,
    Args:
        time_stamp 10位整型(int)时间戳，如 1375146861
        str_format 指定返回格式，值类型为 字符串 str
    Rturn:
        返回格式 默认为 年月日时分，如2013年7月9日1时3分 :201207090103
    """
    return time.strftime("%s" % str_format, time.localtime(time_stamp))


def match_cont(patten, cont):
    """
    正则匹配(精确符合的匹配)
    Args:
        patten 正则表达式
        cont____ 匹配内容
    Return:
        True or False
    """
    res = re.match(patten, cont)
    if res:
        return True
    else:
        return False


def handle_num(val, ranges=(0, 100), res=list()):
    """处理纯数字"""
    val = int(val)
    if val >= ranges[0] and val <= ranges[1]:
        res.append(val)
    return res


def handle_nlist(val, ranges=(0, 100), res=list()):
    """处理数字列表 如 1,2,3,6"""
    val_list = val.split(',')
    for tmp_val in val_list:
        tmp_val = int(tmp_val)
        if tmp_val >= ranges[0] and tmp_val <= ranges[1]:
            res.append(tmp_val)
    return res


def handle_star(val, ranges=(0, 100), res=list()):
    """处理星号"""
    if val == '*':
        tmp_val = ranges[0]
        while tmp_val <= ranges[1]:
            res.append(tmp_val)
            tmp_val = tmp_val + 1
    return res


def handle_starnum(val, ranges=(0, 100), res=list()):
    """星号/数字 组合 如 */3"""
    tmp = val.split('/')
    val_step = int(tmp[1])
    if val_step < 1:
        return res
    val_tmp = int(tmp[1])
    while val_tmp <= ranges[1]:
        res.append(val_tmp)
        val_tmp = val_tmp + val_step
    return res


def handle_range(val, ranges=(0, 100), res=list()):
    """处理区间 如 8-20"""
    tmp = val.split('-')
    range1 = int(tmp[0])
    range2 = int(tmp[1])
    tmp_val = range1
    if range1 < 0:
        return res
    while tmp_val <= range2 and tmp_val <= ranges[1]:
        res.append(tmp_val)
        tmp_val = tmp_val + 1
    return res


def handle_rangedv(val, ranges=(0, 100), res=list()):
    """处理区间/步长 组合 如 8-20/3 """
    tmp = val.split('/')
    range2 = tmp[0].split('-')
    val_start = int(range2[0])
    val_end = int(range2[1])
    val_step = int(tmp[1])
    if (val_step < 1) or (val_start < 0):
        return res
    val_tmp = val_start
    while val_tmp <= val_end and val_tmp <= ranges[1]:
        res.append(val_tmp)
        val_tmp = val_tmp + val_step
    return res


def parse_conf(conf, ranges=(0, 100), res=list()):
    """解析crontab 五个时间参数中的任意一个"""
    # 去除空格，再拆分
    conf = conf.strip(' ').strip(' ')
    conf_list = conf.split(',')
    other_conf = []
    number_conf = []
    for conf_val in conf_list:
        if match_cont(PATTEN['number'], conf_val):
            # 记录拆分后的纯数字参数
            number_conf.append(conf_val)
        else:
            # 记录拆分后纯数字以外的参数，如通配符 * , 区间 0-8, 及 0－8/3 之类
            other_conf.append(conf_val)
    if other_conf:
        # 处理纯数字外各种参数
        for conf_val in other_conf:
            for key, ptn in PATTEN.items():
                if match_cont(ptn, conf_val):
                    res = PATTEN_HANDLER[key](val=conf_val, ranges=ranges, res=res)
    if number_conf:
        if len(number_conf) > 1 or other_conf:
            # 纯数字多于1，或纯数字与其它参数共存，则数字作为时间列表
            res = handle_nlist(val=','.join(number_conf), ranges=ranges, res=res)
        else:
            # 只有一个纯数字存在，则数字为时间 间隔
            res = handle_num(val=number_conf[0], ranges=ranges, res=res)
    return res


def parse_crontab_time(conf_string):
    """
    解析crontab时间配置参数
    Args:
        conf_string  配置内容(共五个值：分 时 日 月 周)
                     取值范围 分钟:0-59 小时:1-23 日期:1-31 月份:1-12 星期:0-6(0表示周日)
    Return:
    crontab_range    list格式，分 时 日 月 周 五个传入参数分别对应的取值范围
    """
    time_limit = ((0, 59), (1, 23), (1, 31), (1, 12), (0, 6))
    crontab_range = []
    clist = []
    conf_length = 5
    tmp_list = conf_string.split(' ')
    for val in tmp_list:
        if len(clist) == conf_length:
            break
        if val:
            clist.append(val)

    if len(clist) != conf_length:
        return -1, 'config error whith [%s]' % conf_string
    cindex = 0
    for conf in clist:
        res_conf = []
        res_conf = parse_conf(conf, ranges=time_limit[cindex], res=res_conf)
        if not res_conf:
            return -1, 'config error whith [%s]' % conf_string
        crontab_range.append(res_conf)
        cindex = cindex + 1
    return 0, crontab_range


def time_match_crontab(crontab_time, time_struct):
    """
    将时间戳与crontab配置中一行时间参数对比，判断该时间戳是否在配置设定的时间范围内
    Args:
        crontab_time____crontab配置中的五个时间（分 时 日 月 周)参数对应时间取值范围
        time_struct____ 某个整型时间戳，如：1375027200 对应的 分 时 日 月 周
    Return:
    tuple 状态码, 状态描述
    """
    cindex = 0
    for val in time_struct:
        if val not in crontab_time[cindex]:
            return 0, False
        cindex = cindex + 1
    return 0, True


def close_to_cron(crontab_time, time_struct):
    """coron的指定范围(crontab_time)中 最接近 指定时间 time_struct 的值"""
    close_time = time_struct
    cindex = 0
    for val_struct in time_struct:
        offset_min = val_struct
        val_close = val_struct
        for val_cron in crontab_time[cindex]:
            offset_tmp = val_struct - val_cron
            if offset_tmp > 0 and offset_tmp < offset_min:
                val_close = val_struct
                offset_min = offset_tmp
        close_time[cindex] = val_close
        cindex = cindex + 1
    return close_time


def cron_time_list(
        cron_time,
        year_num=int(get_str_time(time.time(), "%Y")),
        limit_start=get_str_time(time.time(), "%Y%m%d%H%M"),
        limit_end=get_str_time(time.time() + 86400, "%Y%m%d%H%M")
):
    # print "\nfrom ", limit_start , ' to ' ,limit_end
    """
    获取crontab时间配置参数取值范围内的所有时间点 的 时间戳
    Args:
        cron_time 符合crontab配置指定的所有时间点
        year_num____指定在哪一年内 获取
        limit_start 开始时间
    Rturn:
        List  所有时间点组成的列表(年月日时分 组成的时间，如2013年7月29日18时56分：201307291856)
    """
    # 按小时 和 分钟组装
    hour_minute = []
    for minute in cron_time[0]:
        minute = str(minute)
        if len(minute) < 2:
            minute = '0%s' % minute
        for hour in cron_time[1]:
            hour = str(hour)
            if len(hour) < 2:
                hour = '0%s' % hour
            hour_minute.append('%s%s' % (hour, minute))
    # 按天 和 小时组装
    day_hm = []
    for day in cron_time[2]:
        day = str(day)
        if len(day) < 2:
            day = '0%s' % day
        for hour_mnt in hour_minute:
            day_hm.append('%s%s' % (day, hour_mnt))
    # 按月 和 天组装
    month_dhm = []
    # 只有30天的月份
    month_short = ['02', '04', '06', '09', '11']
    for month in cron_time[3]:
        month = str(month)
        if len(month) < 2:
            month = '0%s' % month
        for day_hm_s in day_hm:
            if month == '02':
                if (((not year_num % 4) and (year_num % 100)) or (not year_num % 400)):
                    # 闰年2月份有29天
                    if int(day_hm_s[:2]) > 29:
                        continue
                else:
                    # 其它2月份有28天
                    if int(day_hm_s[:2]) > 28:
                        continue
            if month in month_short:
                if int(day_hm_s[:2]) > 30:
                    continue
            month_dhm.append('%s%s' % (month, day_hm_s))
    # 按年 和 月组装
    len_start = len(limit_start)
    len_end = len(limit_end)
    month_dhm_limit = []
    for month_dhm_s in month_dhm:
        time_ymdhm = '%s%s' % (str(year_num), month_dhm_s)
        # 开始时间\结束时间以外的排除
        if (int(time_ymdhm[:len_start]) < int(limit_start)) or \
                (int(time_ymdhm[:len_end]) > int(limit_end)):
            continue
        month_dhm_limit.append(time_ymdhm)
    if len(cron_time[4]) < 7:
        # 按不在每周指定时间的排除
        month_dhm_week = []
        for time_minute in month_dhm_limit:
            str_time = time.strptime(time_minute, '%Y%m%d%H%M%S')
            if str_time.tm_wday in cron_time[4]:
                month_dhm_week.append(time_minute)
        return month_dhm_week
    return month_dhm_limit


# crontab时间参数各种写法 的 正则匹配
PATTEN = {
    # 纯数字
    'number': '^[0-9]+$',
    # 数字列表,如 1,2,3,6
    'num_list': '^[0-9]+([,][0-9]+)+$',
    # 星号 *
    'star': '^\*$',
    # 星号/数字 组合，如 */3
    'star_num': '^\*\/[0-9]+$',
    # 区间 如 8-20
    'range': '^[0-9]+[\-][0-9]+$',
    # 区间/步长 组合 如 8-20/3
    'range_div': '^[0-9]+[\-][0-9]+[\/][0-9]+$'
    # 区间/步长 列表 组合，如 8-20/3,21,22,34
    # 'range_div_list':'^([0-9]+[\-][0-9]+[\/][0-9]+)([,][0-9]+)+$'
}
# 各正则对应的处理方法
PATTEN_HANDLER = {
    'number': handle_num,
    'num_list': handle_nlist,
    'star': handle_star,
    'star_num': handle_starnum,
    'range': handle_range,
    'range_div': handle_rangedv
}


def isdo(strs, tips=None):
    """
    判断是否匹配成功！
    """
    try:
        tips = tips == None and "文件名称格式错误：job_月-周-天-时-分_文件名.txt" or tips
        timer = strs.replace('@', "*").replace('%', '/').split('_')[1]
        month, week, day, hour, mins = timer.split('-')
        conf_string = mins + " " + hour + " " + day + " " + month + " " + week
        res, desc = parse_crontab_time(conf_string)
        if res == 0:
            cron_time = desc
        else:
            return False

        now = FDateTime.now()
        now = FDateTime.datetostring(now, "%Y%m%d%H%M00")

        time_stamp = FDateTime.strtotime(now, "%Y%m%d%H%M00")

        # time_stamp = int(time.time())
        # 解析 时间戳对应的 分 时 日 月 周
        time_struct = get_struct_time(time_stamp)
        match_res = time_match_crontab(cron_time, time_struct)
        return match_res[1]
    except:
        print
        tips
        return False


def main():
    """测试用实例"""
    # crontab配置中一行时间参数
    # conf_string = '*/10 * * * * (cd /opt/pythonpm/devpapps; /usr/local/bin/python2.5 data_test.py>>output_error.txt)'
    conf_string = '*/10 * * * *'
    # 时间戳
    time_stamp = int(time.time())

    # 解析crontab时间配置参数 分 时 日 月 周 各个取值范围
    res, desc = parse_crontab_time(conf_string)

    if res == 0:
        cron_time = desc
    else:
        print
        desc
        sys, exit(-1)

    print
    "\nconfig:", conf_string
    print
    "\nparse result(range for crontab):"

    print
    " minute:", cron_time[0]
    print
    " hour: ", cron_time[1]
    print
    " day: ", cron_time[2]
    print
    " month: ", cron_time[3]
    print
    " week day:", cron_time[4]

    # 解析 时间戳对应的 分 时 日 月 周
    time_struct = get_struct_time(time_stamp)
    print
    "\nstruct time(minute hour day month week) for %d :" % \
    time_stamp, time_struct

    # 将时间戳与crontab配置中一行时间参数对比，判断该时间戳是否在配置设定的时间范围内
    match_res = time_match_crontab(cron_time, time_struct)
    print
    "\nmatching result:", match_res

    # crontab配置设定范围中最近接近时指定间戳的一组时间
    most_close = close_to_cron(cron_time, time_struct)
    print
    "\nin range of crontab time which is most colse to struct ", most_close

    time_list = cron_time_list(cron_time)
    print
    "\n\n %d times need to tart-up:\n" % len(time_list)
    print
    time_list[:10], '...'


if __name__ == '__main__':
    # 请看 使用实例
    strs = 'job_@-@-@-@-@_test02.txt.sh'
    print
    isdo(strs)

    # main()0")