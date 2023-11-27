# Calc Work Hours
计算两个`DateTime`之间，工作时间的长度（小时）。这个工具最初是用来计算任务工时的。给定任务开始时间，任务结束时间，得出任务工时。会刨去中国的法定节假日及周末。因为中国假日每年发布一次，所以这个工具的第二位版本号就是最新支持年份，如：`v0.2023`就是已经更新到2023年节假日及调休。起始年份是2015年。早于2015年的日期，或者晚于版本号日期，只刨去周末。

Calculate the length of work hours between two `DateTime`s. This tool was originally used to calculate task hours. Given the task start time and the task end time, the task hours are calculated. It will exclude China's statutory holidays and weekends. Because China's holidays are released once a year, the second version number of this tool is the latest supported year, such as: `v0.2023` means that it has been updated to 2023 holidays and adjustments. The starting year is 2015. Dates earlier than 2015 or later then the version year will only exclude weekends.


## Install
目前只支持 python 3.11 及更高：

Currently only supports python 3.11 and higher:

`pip311 install calc_work_hours`

## Usage
```python
from work_hours import WorkHours
wh = WorkHours()
```

### 计算两个`datetime`之间的工作时间长度(小时)  
### Calculate the working time duration (hours) between two `datetime`s

``` python
from datetime import datetime

ret = wh.calc(datetime(2023, 9, 22, 1, 1, 1), datetime(2023, 10, 4, 18, 0, 0)) 
print(ret) 
# 40.0 (hours)
```

### 计算`datetime`是否工作日 
### Calculate whether a `datetime` is a working day

``` python
ret = wh.is_workday(datetime(2023, 10, 2))  
print(ret) 
# 周一，但是 False
# Monday, but False

ret = wh.is_workday(datetime(2023, 10, 7))
print(ret) 
# 周六，但是 True
# Saturday, but True
```
### 计算某个`datetime`是否为工作时间，需要动态的考虑边界。比如9:00，如果（某段时间）从9点开始，那9点是工作时间，如果是（某段时间）到9点结束，那么就不是工作时间。
### Calculate whether a `datetime` is working time, you need to dynamically consider the boundary. For example, 9:00, if (a period of time) starts at 9 o'clock, then 9 o'clock is working time, if (a period of time) ends at 9 o'clock, then 9 is not working time.

``` python
is_work = wh.is_workhours(datetime(2023, 9, 22, 9, 0, 0), )
print(is_work)
# True. The time frame starting from 9:00 ~ 

is_work = wh.is_workhours(datetime(2023, 9, 22, 9, 0, 0), False)
print(is_work)
# False. The time frame ending at 9:00 ~ 
```
### 计算`datetime`的下/上n个工作日的时间
### Calculate n working days after/before a certain `datetime`

``` python
dt = wh.add_workdays(datetime(2023, 9, 22), 5)
print(dt)
# 2023-09-28 18:00
```
09-22|09-23|09-24|09-25|09-26|09-27|09-28
-|-|-|-|-|-|-
 fri | sat | sun | mon | tue | wed | thu
 1   |  .. |  .. |  2  |  3  |  4  | 5

``` python
dt = wh.add_workdays(datetime(2023, 9, 22), -5)
print(dt)
# 2023-09-15 09:00
```

