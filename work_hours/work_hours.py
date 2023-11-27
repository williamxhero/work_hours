from datetime import datetime, timedelta, time

class TC:
	''' Time Calculator '''

	@staticmethod
	def diff_sec(dt2:time, dt1:time):
		''' dt2 - dt1 in seconds '''
		return dt2.hour * 3600 + dt2.minute * 60 - dt1.hour * 3600 - dt1.minute * 60
	
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
		return (dt2.hour == dt1.hour) and (dt2.minute == dt1.minute)
	
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

	def __init__(self, *work_time_frames):
		self.time_frames = []
		self.set(*work_time_frames)

	def set(self, *work_time_frames):
		if len(work_time_frames) == 0: return

		lst_t2 = time(0)
		for tft in work_time_frames:
			t1, t2 = tft[0], tft[1]
			t1 = time(t1.hour, t1.minute)
			t2 = time(t2.hour, t2.minute)
			if TC.less_equal(t1, lst_t2) or TC.less_equal(t2, t1):
				raise Exception('invalid work time frames: %s' % str(tft))
			lst_t2 = t1
			self.time_frames.append((t1, t2))
		
		self.first = self.time_frames[0][0]
		self.last = self.time_frames[-1][1]


class WorkHours:
	def __init__(self, rest_hours:WorkTimeFrames=None):
		''' Given a time range, calculate the work hours within it. 
		MINIMAL supported time resolution is MINUTES.
		Default work time frames: 9:00 ~ 12:00,  13:00 ~ 18:00

		9:00, 12:00, ... are lines, they called EDGE, could be work or rest.
		Depends on the context:
			from 9:00 to 12:00, both 9:00 and 12:00 is work hours.
			from 12:00 to 13:00, both 12:00 and 13:00 is rest hours.
			from 13:00 to 18:00, both 13:00 and 18:00 is work hours.
		
		Time during work hours frame range called SOLID. they are always work hours.
		(, 8:59] is always rest hour. [9:01, ) is always work hour.

		wh = WorkHours( WorkTimeFrames (
					( time(9, 0), time(12, 0) ), 
					( time(13, 0), time(18, 0) ), )
		'''
		from work_hours.exception_cn import exceptions
		self.xs = exceptions

		if rest_hours is not None:
			self.wtf = rest_hours
		else:
			self.wtf = WorkTimeFrames()
			self.wtf.set( (time(9, 0), time(12, 0)), (time(13, 0), time(18, 0)) )
	
	def is_workday(self, dt:datetime)->bool:
		''' to check if the given date is a workday. 
		means from 00:00 ~ 24:59, is any hours are work hours, the day is a workday.
		'''
		dt_str = dt.strftime('%Y%m%d')
		if dt_str in self.xs:
			return self.xs[dt_str]
		week = dt.weekday()
		return week <= 4
	
	def is_workhours(self, dt:datetime, start:bool=True)->bool:
		''' to check if the given datetime is in work hours:minutes. 
		if is "start", on left edge is work, on right edge is rest.
		if is "end" (not "start"), on left edge is rest, on right edge is work.
		'''
		if not self.is_workday(dt):
			return False
		
		tm = dt.time()
		for tf_f, tf_t in self.wtf.time_frames:
			if start:
				if TC.less_equal(tf_f, tm) and TC.less_than(tm, tf_t): return True
			else:
				if TC.less_than(tf_f, tm) and TC.less_equal(tm, tf_t): return True
		
		return False
	
	def add_workdays(self, dt:datetime, workdays:int)->datetime:
		''' get the datetime of n workdays to future(+) or to past(-) the given date.
		The working hours in the starting day will be included. So, if `dt` is the begining of workday,
		the add 1 day, the result will be the end of this day, not the next day begining.
		'''
		if workdays == 0: return dt
		_1_day = timedelta(days=1)
		to_future = workdays > 0 # move to_future
		workdays = abs(workdays)

		if not self.is_workhours(dt, to_future):
			dt = self._move_to_workhours(dt, to_future)

		the_day = dt
		while workdays > 0:
			while True:
				the_day = (the_day + _1_day) if to_future else (the_day - _1_day)
				if self.is_workday(the_day): 
					workdays -= 1
					break

		dt_from, dt_to = self._trim_datetimes(dt, the_day)
		return dt_to if to_future else dt_from

	def calc(self, dt1:datetime, dt2:datetime)->float:
		''' 
		returns the work hours between `dt1` and `dt2`. order of `dt1` and `dt2` does not matter. 
		returns:
			the work hours between `dt1` and `dt2`. positive number or 0.
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
				hours += self._calc_inday_hours(dt_cur.time(), end_tim)

			# next day begins from first.
			dt_cur = self._day_wh_begin(dt_cur)
			dt_cur += timedelta(days=1)

		return hours
	
	
	def _move_to_workhours(self, dt:datetime, to_future:bool=True):
		''' move the given datetime to the nearest work hour (to the edge). 
		No move if already in the work hours (solid).
		move `to_future` means move to the begining of the next work hour range. 
		If `dt` on the right edge, also moved.
		move "to past" (not `to_future`) means move to the end of the last work hour range.
		if `dt` on the left edge, also moved.
		'''
		if self.is_workhours(dt, to_future): return dt

		_1_day = timedelta(days=1)

		# not in workday, move to next/last workday
		day_mvd = False
		while not self.is_workday(dt):
			day_mvd = True
			if to_future:
				dt += _1_day
			else:
				dt -= _1_day

		# if moved, hours set to starts/ends.
		if day_mvd:
			if to_future:
				dt = self._day_wh_begin(dt)
			else:
				dt = self._day_wh_end(dt)
			return dt
		
		# in workday, but not in workhours. move to the nearest edge:
		tm = dt.time()
		if to_future and TC.less_equal(self.wtf.last, tm):
			tmr = self._day_wh_begin(dt + _1_day)
			dt = self._move_to_workhours(tmr, True) # next workday begins
			return dt
		
		if (not to_future) and TC.less_equal(tm, self.wtf.first):
			yst = self._day_wh_end(dt - _1_day)
			dt = self._move_to_workhours(yst, False) # last workday ends
			return dt

		if to_future:
			for tf_f, _ in self.wtf.time_frames:
				if TC.less_than(tm, tf_f):
					dt = datetime(dt.year, dt.month, dt.day, tf_f.hour, tf_f.minute)
					return dt
		else:
			for _, tf_t in self.wtf.time_frames[::-1]:
				if TC.less_than(tf_t, tm):
					dt = datetime(dt.year, dt.month, dt.day, tf_t.hour, tf_t.minute)
					return dt

		return dt
	
	def _trim_datetimes(self, dt1:datetime, dt2:datetime):
		''' trim the datetimes to the nearest work hours. 
		if between `dt1` and `dt2`, there has no workdays, 
		then return two nearest future workhours (same values).
		'''
		if dt1 == dt2: return dt1, dt2
		if dt1 > dt2:
			dt1, dt2 = dt2, dt1

		if not self.is_workhours(dt1, True):
			dt1 = self._move_to_workhours(dt1, True)

		if not self.is_workhours(dt2, False):
			dt2 = self._move_to_workhours(dt2, False)

		if dt1 > dt2: return dt1, dt1
		return dt1, dt2
	
	def _calc_inday_hours(self, tm_fm:time, tm_to:time) -> float:
		if TC.less_equal(tm_to, tm_fm): return 0
		total_secs = 0
		for tf_f, tf_t in self.wtf.time_frames:
			if TC.less_equal(tf_t, tm_fm): continue
			if TC.less_equal(tm_to, tf_f): break
			tf2 = TC.later(tf_f, tm_fm)
			tt2 = TC.earlier(tf_t, tm_to)
			total_secs += TC.diff_sec(tt2, tf2)
		return total_secs / 3600

	def _day_wh_begin(self, dt:datetime):
		''' set time to begining of the day.'''
		return datetime(dt.year, dt.month, dt.day, self.wtf.first.hour, self.wtf.first.minute, 0)
	
	def _day_wh_end(self, dt:datetime):
		''' set time to end of the day. '''
		return datetime(dt.year, dt.month, dt.day, self.wtf.last.hour, self.wtf.last.minute, 0)
	
	

			
				