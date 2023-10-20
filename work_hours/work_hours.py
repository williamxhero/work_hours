from datetime import datetime, timedelta, time

class TC:
	''' Time Calculator '''

	@staticmethod
	def diff_sec(dt2:time, dt1:time):
		''' dt2 - dt1 in seconds '''
		return dt2.hour * 3600 + dt2.minute * 60 + dt2.second - dt1.hour * 3600 - dt1.minute * 60 - dt1.second
	
	@staticmethod
	def less_than(dt1:time, dt2:time):
		''' dt1 < dt2 '''
		return TC.diff_sec(dt2, dt1) > 0

	@staticmethod
	def less_equal(dt1:time, dt2:time):
		''' dt1 <= dt2 '''
		return TC.diff_sec(dt2, dt1) >= 0
	
	@staticmethod
	def equal(dt1:time, dt2:time):
		''' dt1 == dt2 '''
		return (dt2.hour == dt1.hour) and (dt2.minute == dt1.minute) and (dt2.second == dt1.second)
	
	@staticmethod
	def later(dt1:time, dt2:time):
		''' the later one '''
		if TC.less_than(dt1, dt2): return dt2
		return dt1
	
	@staticmethod
	def earlier(dt1:time, dt2:time):
		''' the earlier one '''
		if TC.less_than(dt1, dt2): return dt1
		return dt2


class WorkTimeFrames:
	''' work time frames during a day. '''

	def __init__(self):
		self.time_frames = []

	def set(self, *work_time_frames):
		for t1, t2 in work_time_frames:
			self.time_frames.append((t1, t2))
		
		self.first = self.time_frames[0][0]
		self.last = self.time_frames[-1][1]


class WorkHours:
	''' given a time range, calculate the work hours within it. '''

	def __init__(self, rest_hours:WorkTimeFrames=None):
		''' 
		default work time frames: 9:00 ~ 12:00  13:00 ~ 18:00
		'''
		from work_hours.exception_cn import exceptions
		self.xs = exceptions

		if rest_hours is not None:
			self.wtf = rest_hours
		else:
			self.wtf = WorkTimeFrames()
			self.wtf.set( (time(9, 0), time(12, 0)), (time(13, 0), time(18, 0)) )

	def is_workday(self, dt:datetime)->bool:
		''' to check if the given date is a workday. '''

		dt_str = dt.strftime('%Y%m%d')
		if dt_str in self.xs:
			return self.xs[dt_str]
		week = dt.weekday()
		return week <= 4

	def calc(self, dt1:datetime, dt2:datetime)->float:
		''' 
		returns the work hours between dt1 and dt2. order of dt1 and dt2 does not matter. 

		returns:
			the work hours between dt1 and dt2. positive number or 0.
		'''
		if dt1 == dt2: return 0
		dt_beg = dt1 if dt1 < dt2 else dt2
		dt_end = dt2 if dt1 < dt2 else dt1
		dt_cur = dt_beg
		hours = 0
		dt_end_date = dt_end.date()

		while dt_cur < dt_end:
			if self.is_workday(dt_cur):
				# last day ends at last.
				end_tim = dt_end.time() if dt_cur.date() == dt_end_date else self.wtf.last
				hours += self._calc_inday_hour(dt_cur.time(), end_tim)

			# next day begins from first.
			dt_cur = self._day_begin(dt_cur)
			dt_cur += timedelta(days=1)

		return hours
	

	def _calc_inday_hour(self, tm_fm:time, tm_to:time) -> float:
		if TC.less_equal(tm_to, tm_fm): return 0
		total_secs = 0
		for tf_f, tf_t in self.wtf.time_frames:
			if TC.less_equal(tf_t, tm_fm): continue
			if TC.less_equal(tm_to, tf_f): break
			tf2 = TC.later(tf_f, tm_fm)
			tt2 = TC.earlier(tf_t, tm_to)
			total_secs += TC.diff_sec(tt2, tf2)
		return total_secs / 3600

	def _day_begin(self, dt:datetime):
		return datetime(dt.year, dt.month, dt.day, self.wtf.first.hour, self.wtf.first.minute, 0)
	