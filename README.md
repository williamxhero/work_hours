# Calc Work Hours
计算两个`DateTime`之间，工作时间的长度（小时）。这个工具最初是用来计算任务工时的。给定任务开始时间，任务结束时间，得出任务工时。会刨去中国的法定节假日及周末。因为中国假日每年发布一次，所以这个工具的第二位版本号就是最新支持年份，如：`v0.2023`就是已经更新到2023年节假日及调休。起始年份是2015年。早于2015年的日期，或者晚于版本号日期，只刨去周末。

Calculate the length of work hours between two `DateTime`s. This tool was originally used to calculate task hours. Given the task start time and the task end time, the task hours are calculated. It will exclude China's statutory holidays and weekends. Because China's holidays are released once a year, the second version number of this tool is the latest supported year, such as: `v0.2023` means that it has been updated to 2023 holidays and adjustments. The starting year is 2015. Dates earlier than 2015 or later then the version year will only exclude weekends.


## install
目前只支持 python 3.11 及更高：

Currently only supports python 3.11 and higher:

`pip311 install calc_work_hours`

## usage
```python
from datetime import datetime, time

from work_hours import WorkHours

wh = WorkHours()

#计算某天是否工作日 
# #Calculate whether a day is a working day
ret = wh.is_workday(datetime(2023, 10, 2))  
# 周一，但是 False
# Monday, but False
print(ret) 

ret = wh.is_workday(datetime(2023, 10, 7))
# 周六，但是 True
# Saturday, but True
print(ret) 

#计算两个日期之间的工作时间
#Calculate the working time between two dates
ret = wh.calc(datetime(2023, 9, 22, 1, 1, 1), datetime(2023, 10, 4, 18, 0, 0)) 
# 40 (hours)
print(ret) 

```