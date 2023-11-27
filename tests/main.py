from datetime import datetime, time
import unittest
from work_hours import WorkHours

def to_dt(s):
	return datetime.strptime(s, '%Y-%m-%d %H:%M')

class TestDemo(unittest.TestCase):

	def test_1_is_workday(self):
		WH = WorkHours()
		self.assertFalse(WH.is_workday(datetime(2023, 9, 30))) # saturday, also holiday
		self.assertFalse(WH.is_workday(datetime(2023, 10, 2))) # monday, but holiday
		self.assertFalse(WH.is_workday(datetime(2023, 10, 14))) # saturday, rest
		self.assertTrue(WH.is_workday(datetime(2023, 10, 7))) # saturday, but work
		self.assertTrue(WH.is_workday(datetime(2023, 10, 13))) # friday, work
		pass

	def test_2_is_workhours(self):
		WH= WorkHours()

		self.assertTrue(WH.is_workhours(to_dt('2023-10-08 10:00'))) # 10点怎么算都是工作时间
		self.assertFalse(WH.is_workhours(to_dt('2023-10-01 14:00'))) # 假日
	
		self.assertTrue(WH.is_workhours(to_dt('2023-10-08 09:00'))) # 9点开始都是工作时间
		self.assertFalse(WH.is_workhours(to_dt('2023-10-08 09:00'), False)) # 到9点都是休息时间

		self.assertTrue(WH.is_workhours(to_dt('2023-10-08 18:00'), False)) # 到18点都是工作时间
		self.assertFalse(WH.is_workhours(to_dt('2023-10-08 18:00'))) # 18点开始都是休息时间

	def test_3_move_to_workhours(self):
		WH=WorkHours()

		# 工作时间
		dt = WH._move_to_workhours(to_dt('2023-10-08 10:00'), True)
		self.assertEqual(dt, to_dt('2023-10-08 10:00'))
		
		# 跨节日 往后
		dt = WH._move_to_workhours(to_dt('2023-09-28 18:10'), True)
		self.assertEqual(dt, to_dt('2023-10-07 09:00'))

		# 节日中 往后
		dt = WH._move_to_workhours(to_dt('2023-10-03 10:10'), True)
		self.assertEqual(dt, to_dt('2023-10-07 09:00'))

		# 工作日结束 往后
		dt = WH._move_to_workhours(to_dt('2023-10-07 18:10'), True)
		self.assertEqual(dt, to_dt('2023-10-08 09:00'))

		# 天边界 往后
		dt = WH._move_to_workhours(to_dt('2023-10-07 18:00'), True)
		self.assertEqual(dt, to_dt('2023-10-08 09:00'))	

		# 当天开始前 往后
		dt = WH._move_to_workhours(to_dt('2023-10-08 08:00'), True)
		self.assertEqual(dt, to_dt('2023-10-08 09:00'))

		# 中间开始前 往后
		dt = WH._move_to_workhours(to_dt('2023-10-08 12:30'), True)
		self.assertEqual(dt, to_dt('2023-10-08 13:00'))

		# 中间边界 往后
		dt = WH._move_to_workhours(to_dt('2023-10-08 12:00'), True)
		self.assertEqual(dt, to_dt('2023-10-08 13:00'))	


		# 工作时间
		dt = WH._move_to_workhours(to_dt('2023-10-08 10:00'), False)
		self.assertEqual(dt, to_dt('2023-10-08 10:00'))
		
		# 过昨日 往前
		dt = WH._move_to_workhours(to_dt('2023-10-08 08:00'), False)
		self.assertEqual(dt, to_dt('2023-10-07 18:00'))

		# 天边界 往前
		dt = WH._move_to_workhours(to_dt('2023-10-08 09:00'), False)
		self.assertEqual(dt, to_dt('2023-10-07 18:00'))	

		# 跨节日  往前
		dt = WH._move_to_workhours(to_dt('2023-10-07 08:00'), False)
		self.assertEqual(dt, to_dt('2023-09-28 18:00'))

		# 节日中  往前
		dt = WH._move_to_workhours(to_dt('2023-10-04 08:00'), False)
		self.assertEqual(dt, to_dt('2023-09-28 18:00'))

		# 当天中  往前
		dt = WH._move_to_workhours(to_dt('2023-10-08 12:30'), False)
		self.assertEqual(dt, to_dt('2023-10-08 12:00'))

		# 中间边界 往前
		dt = WH._move_to_workhours(to_dt('2023-10-08 13:00'), False)
		self.assertEqual(dt, to_dt('2023-10-08 12:00'))	

		# 当天结束 往前
		dt = WH._move_to_workhours(to_dt('2023-10-08 18:10'), False)
		self.assertEqual(dt, to_dt('2023-10-08 18:00'))

	def test_4_trim_datetime(self):
		WH = WorkHours()
		f, t = WH._trim_datetimes(to_dt('2023-10-08 10:00'), to_dt('2023-10-08 10:00'))
		self.assertEqual(f, to_dt('2023-10-08 10:00'))
		self.assertEqual(t, to_dt('2023-10-08 10:00'))

		f, t = WH._trim_datetimes(to_dt('2023-10-07 12:00'), to_dt('2023-10-07 13:00'))
		self.assertEqual(f, to_dt('2023-10-07 13:00'))
		self.assertEqual(t, to_dt('2023-10-07 13:00'))

		f, t = WH._trim_datetimes(to_dt('2023-10-02 10:00'), to_dt('2023-10-03 10:00'))
		self.assertEqual(f, to_dt('2023-10-07 09:00'))
		self.assertEqual(t, to_dt('2023-10-07 09:00'))

		f, t = WH._trim_datetimes(to_dt('2023-10-07 18:00'), to_dt('2023-10-08 09:00'))
		self.assertEqual(f, to_dt('2023-10-08 09:00'))
		self.assertEqual(t, to_dt('2023-10-08 09:00'))

		f, t = WH._trim_datetimes(to_dt('2023-10-08 8:00'), to_dt('2023-10-08 19:00'))
		self.assertEqual(f, to_dt('2023-10-08 09:00'))
		self.assertEqual(t, to_dt('2023-10-08 18:00'))

		f, t = WH._trim_datetimes(to_dt('2023-10-07 18:00'), to_dt('2023-10-09 09:00'))
		self.assertEqual(f, to_dt('2023-10-08 09:00'))
		self.assertEqual(t, to_dt('2023-10-08 18:00'))

		f, t = WH._trim_datetimes(to_dt('2023-10-08 09:00'), to_dt('2023-10-08 17:00'))
		self.assertEqual(f, to_dt('2023-10-08 09:00'))
		self.assertEqual(t, to_dt('2023-10-08 17:00'))

		f, t = WH._trim_datetimes(to_dt('2023-10-08 10:00'), to_dt('2023-10-08 17:00'))
		self.assertEqual(f, to_dt('2023-10-08 10:00'))
		self.assertEqual(t, to_dt('2023-10-08 17:00'))



	def test_5_add_workdays(self):
		WH = WorkHours()

		dt = WH.add_workdays(datetime(2023, 9, 22), 5)
		dt = WH.add_workdays(datetime(2023, 9, 22), -5)

		# 工作时间 -> 工作时间
		dt = WH.add_workdays(to_dt('2023-10-08 10:00'), 0)
		self.assertEqual(dt, to_dt('2023-10-08 10:00'))

		dt = WH.add_workdays(to_dt('2023-10-08 10:00'), 1)
		self.assertEqual(dt, to_dt('2023-10-09 10:00'))

		dt = WH.add_workdays(to_dt('2023-10-08 07:00'), 1)
		self.assertEqual(dt, to_dt('2023-10-08 18:00'))

		dt = WH.add_workdays(to_dt('2023-10-08 18:10'), 1)
		self.assertEqual(dt, to_dt('2023-10-09 18:00'))

		# 节日 -> 节日
		dt = WH.add_workdays(to_dt('2023-10-05 10:00'), -2)
		self.assertEqual(dt, to_dt('2023-09-27 09:00'))

		dt = WH.add_workdays(to_dt('2023-10-03 10:00'), 2)
		self.assertEqual(dt, to_dt('2023-10-08 18:00'))

		# 节日 -> 工作时间
		dt = WH.add_workdays(to_dt('2023-10-01 10:00'), -2)
		self.assertEqual(dt, to_dt('2023-09-27 09:00'))

		dt = WH.add_workdays(to_dt('2023-10-05 10:00'), 2)
		self.assertEqual(dt, to_dt('2023-10-08 18:00'))

		# 工作时间 -> 节日
		dt = WH.add_workdays(to_dt('2023-09-27 10:00'), 2)
		self.assertEqual(dt, to_dt('2023-10-07 10:00'))

		dt = WH.add_workdays(to_dt('2023-10-07 18:00'), -2)
		self.assertEqual(dt, to_dt('2023-09-28 09:00'))
	

	def test_6_calc_inday_hour(self):
		WH = WorkHours()

		# all in rest
		hrs = WH._calc_inday_hours(time(4, 0), time(9, 0))
		self.assertAlmostEqual(hrs, 0)

		hrs = WH._calc_inday_hours(time(19, 0), time(20, 0))
		self.assertAlmostEqual(hrs, 0)
		
		hrs = WH._calc_inday_hours(time(12, 0), time(13, 0))
		self.assertAlmostEqual(hrs, 0)
		
		hrs = WH._calc_inday_hours(time(12, 10), time(12, 50))
		self.assertAlmostEqual(hrs, 0)

		# all in work
		hrs = WH._calc_inday_hours(time(9, 0), time(12, 0))
		self.assertAlmostEqual(hrs, 3)

		hrs = WH._calc_inday_hours(time(10, 0), time(13, 0))
		self.assertAlmostEqual(hrs, 2)

		hrs = WH._calc_inday_hours(time(10, 0), time(14, 0))
		self.assertAlmostEqual(hrs, 3)

		hrs = WH._calc_inday_hours(time(12, 0), time(14, 0))
		self.assertAlmostEqual(hrs, 1)

		hrs = WH._calc_inday_hours(time(12, 10), time(15, 0))
		self.assertAlmostEqual(hrs, 2)

		hrs = WH._calc_inday_hours(time(13, 0), time(15, 0))
		self.assertAlmostEqual(hrs, 2)

		hrs = WH._calc_inday_hours(time(14, 0), time(18, 0))
		self.assertAlmostEqual(hrs, 4)

		# rest to work
		hrs = WH._calc_inday_hours(time(8, 0), time(10, 0))
		self.assertAlmostEqual(hrs, 1)

		hrs = WH._calc_inday_hours(time(8, 0), time(13, 0))
		self.assertAlmostEqual(hrs, 3)

		hrs = WH._calc_inday_hours(time(8, 0), time(16, 0))
		self.assertAlmostEqual(hrs, 6)

		hrs = WH._calc_inday_hours(time(8, 0), time(18, 0))
		self.assertAlmostEqual(hrs, 8)

		# work to rest
		hrs = WH._calc_inday_hours(time(10, 0), time(19, 0))
		self.assertAlmostEqual(hrs, 7)

		hrs = WH._calc_inday_hours(time(12, 0), time(20, 0))
		self.assertAlmostEqual(hrs, 5)

		hrs = WH._calc_inday_hours(time(14, 0), time(20, 0))
		self.assertAlmostEqual(hrs, 4)

		# special times:
		hrs = WH._calc_inday_hours(time(10, 0), time(10, 0))
		self.assertAlmostEqual(hrs, 0)

		hrs = WH._calc_inday_hours(time(15, 0), time(10, 0))
		self.assertAlmostEqual(hrs, 0)

		pass

	def test_7_calc(self):
		WH = WorkHours()
		
		# all holidays
		hrs = WH.calc(to_dt('2023-09-29 01:01'), to_dt('2023-10-06 18:00'))
		self.assertAlmostEqual(hrs, 0)

		hrs = WH.calc(to_dt('2023-10-01 01:01'), to_dt('2023-10-05 18:00'))
		self.assertAlmostEqual(hrs, 0)

		# include_holidays
		hrs = WH.calc(to_dt('2023-09-29 01:01'), to_dt('2023-10-07 18:00'))
		self.assertAlmostEqual(hrs, 8)
		
		hrs = WH.calc(to_dt('2023-09-28 01:01'), to_dt('2023-10-07 18:00'))
		self.assertAlmostEqual(hrs, 16)
		
		hrs = WH.calc(to_dt('2023-09-22 01:01'), to_dt('2023-10-09 18:00'))
		self.assertAlmostEqual(hrs, 8*8)

		# within_1day
		# actually, it's same as _calc_inday_hour. so just test it once.
		hrs = WH.calc(to_dt('2023-10-08 10:00'), to_dt('2023-10-08 12:00'))
		self.assertAlmostEqual(hrs, 2)
		
		# across_holidays
		# work to rest
		hrs = WH.calc(to_dt('2023-09-28 01:01'), to_dt('2023-10-05 18:00'))
		self.assertAlmostEqual(hrs, 8)
		
		# rest to work
		hrs = WH.calc(to_dt('2023-09-30 01:01'), to_dt('2023-10-08 18:00'))
		self.assertAlmostEqual(hrs, 16)

		# more work to rest
		hrs = WH.calc(to_dt('2023-09-22 01:01'), to_dt('2023-10-04 18:00'))
		self.assertAlmostEqual(hrs, 5*8)


if __name__ == "__main__" :
	 unittest.main(verbosity=3)


