from datetime import datetime, time
import unittest
from work_hours import WorkHours

def to_dt(s):
	return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

class TestDemo(unittest.TestCase):
	
	def test_a_calc_inday_hour(self):
		WH = WorkHours()

		# all in rest
		hrs = WH._calc_inday_hour(time(4, 0), time(9, 0))
		self.assertAlmostEqual(hrs, 0)

		hrs = WH._calc_inday_hour(time(19, 0), time(20, 0))
		self.assertAlmostEqual(hrs, 0)
		
		hrs = WH._calc_inday_hour(time(12, 0), time(13, 0))
		self.assertAlmostEqual(hrs, 0)
		
		hrs = WH._calc_inday_hour(time(12, 10), time(12, 50))
		self.assertAlmostEqual(hrs, 0)

		# all in work
		hrs = WH._calc_inday_hour(time(9, 0), time(12, 0))
		self.assertAlmostEqual(hrs, 3)

		hrs = WH._calc_inday_hour(time(10, 0), time(13, 0))
		self.assertAlmostEqual(hrs, 2)

		hrs = WH._calc_inday_hour(time(10, 0), time(14, 0))
		self.assertAlmostEqual(hrs, 3)

		hrs = WH._calc_inday_hour(time(12, 0), time(14, 0))
		self.assertAlmostEqual(hrs, 1)

		hrs = WH._calc_inday_hour(time(12, 10), time(15, 0))
		self.assertAlmostEqual(hrs, 2)

		hrs = WH._calc_inday_hour(time(13, 0), time(15, 0))
		self.assertAlmostEqual(hrs, 2)

		hrs = WH._calc_inday_hour(time(14, 0), time(18, 0))
		self.assertAlmostEqual(hrs, 4)

		# rest to work
		hrs = WH._calc_inday_hour(time(8, 0), time(10, 0))
		self.assertAlmostEqual(hrs, 1)

		hrs = WH._calc_inday_hour(time(8, 0), time(13, 0))
		self.assertAlmostEqual(hrs, 3)

		hrs = WH._calc_inday_hour(time(8, 0), time(16, 0))
		self.assertAlmostEqual(hrs, 6)

		hrs = WH._calc_inday_hour(time(8, 0), time(18, 0))
		self.assertAlmostEqual(hrs, 8)

		# work to rest
		hrs = WH._calc_inday_hour(time(10, 0), time(19, 0))
		self.assertAlmostEqual(hrs, 7)

		hrs = WH._calc_inday_hour(time(12, 0), time(20, 0))
		self.assertAlmostEqual(hrs, 5)

		hrs = WH._calc_inday_hour(time(14, 0), time(20, 0))
		self.assertAlmostEqual(hrs, 4)

		# special times:
		hrs = WH._calc_inday_hour(time(10, 0), time(10, 0))
		self.assertAlmostEqual(hrs, 0)

		hrs = WH._calc_inday_hour(time(15, 0), time(10, 0))
		self.assertAlmostEqual(hrs, 0)

		pass

	def test_b_workday(self):
		WH = WorkHours()
		self.assertFalse(WH.is_workday(datetime(2023, 9, 30))) # saturday, also holiday
		self.assertFalse(WH.is_workday(datetime(2023, 10, 2))) # monday, but holiday
		self.assertFalse(WH.is_workday(datetime(2023, 10, 14))) # saturday, rest
		self.assertTrue(WH.is_workday(datetime(2023, 10, 7))) # saturday, but work
		self.assertTrue(WH.is_workday(datetime(2023, 10, 13))) # friday, work
		pass

	def test_c_calc_within_holiday(self):
		WH = WorkHours()
		
		# all holidays
		hrs = WH.calc(to_dt('2023-09-29 01:01:01'), to_dt('2023-10-06 18:00:00'))
		self.assertAlmostEqual(hrs, 0)

		hrs = WH.calc(to_dt('2023-10-01 01:01:01'), to_dt('2023-10-05 18:00:00'))
		self.assertAlmostEqual(hrs, 0)

		pass

	def test_c_calc_include_holidays(self):
		WH = WorkHours()
		
		hrs = WH.calc(to_dt('2023-09-29 01:01:01'), to_dt('2023-10-07 18:00:00'))
		self.assertAlmostEqual(hrs, 8)
		
		hrs = WH.calc(to_dt('2023-09-28 01:01:01'), to_dt('2023-10-07 18:00:00'))
		self.assertAlmostEqual(hrs, 16)
		
		hrs = WH.calc(to_dt('2023-09-22 01:01:01'), to_dt('2023-10-09 18:00:00'))
		self.assertAlmostEqual(hrs, 8*8)

		pass

	def test_c_calc_within_1day(self):
		WH = WorkHours()
		# actually, it's same as _calc_inday_hour. so just test it once.
		hrs = WH.calc(to_dt('2023-10-08 10:00:00'), to_dt('2023-10-08 12:00:00'))
		self.assertAlmostEqual(hrs, 2)
		pass 


	def test_c_calc_across_holidays(self):
		WH = WorkHours()
		
		# work to rest
		hrs = WH.calc(to_dt('2023-09-28 01:01:01'), to_dt('2023-10-05 18:00:00'))
		self.assertAlmostEqual(hrs, 8)
		
		# rest to work
		hrs = WH.calc(to_dt('2023-09-30 01:01:01'), to_dt('2023-10-08 18:00:00'))
		self.assertAlmostEqual(hrs, 16)

		# more work to rest
		hrs = WH.calc(to_dt('2023-09-22 01:01:01'), to_dt('2023-10-04 18:00:00'))
		self.assertAlmostEqual(hrs, 5*8)

		pass

if __name__ == "__main__" :
	 unittest.main(verbosity = 2 )


