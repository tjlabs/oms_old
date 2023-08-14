from dataclasses import field, dataclass
from datetime import timedelta
from datetime import datetime

@dataclass
class OneDayInfo:
    start_time: str = ""
    end_time: str = ""
    sector_id: int = 0

@dataclass
class DiscoveredDevice:
    user_id: str = ""
    device_model: str = ""

@dataclass
class Coordinates:
    x: int = 0
    y: int = 0

@dataclass
class OneUserPositionErrTable:
    threshold_10: float = 0.0
    threshold_30: float = 0.0
    threshold_50: float = 0.0
    user_data_cnt: float = 0.0
    user_dist_diff: list[float] = field(default_factory=list)

@dataclass
class SampleOneUserPositionErrTable:
    sector_id: int = 6
    calc_date: datetime = datetime.now()
    user_id: str = ""
    threshold_10: float = 0.0
    threshold_30: float = 0.0
    threshold_50: float = 0.0
    user_data_cnt: float = 0.0
    user_dist_diff: list[float] = field(default_factory=list)

@dataclass
class OneUserTTFF:
    stabilization_time: timedelta = timedelta()

@dataclass
class TimeToFirstFix:
    sector_id: int = 6
    calc_date: datetime = datetime.now()
    avg_stabilization_time: list[float] = field(default_factory=list)
    hour_unit_ttff: list[float] = field(default_factory=list)
    user_count: int = 0

@dataclass
class PositionTrajectory:
    sector_id: int = 0
    calc_date: datetime = datetime.now()
    one_day_stat: OneUserPositionErrTable = field(default_factory=OneUserPositionErrTable)
    one_day_data_cnt: float = 0.0

@dataclass
class DailyPED:
    daily_ped_datas: tuple = field(default_factory=tuple)

@dataclass
class TestSet:
    start_time: datetime = datetime.now()
    end_time: datetime = datetime.now()

@dataclass
class SampleTimeToFirstFix:
    sector_id: int = 6
    user_id: str = ""
    calc_date: datetime = datetime.now()
    avg_stabilization_time: list[float] = field(default_factory=list)
    hour_unit_ttff: list[float] = field(default_factory=list)
    user_count: int = 0

@dataclass
class OneuserWholeTestSets:
    test_sets: list[TestSet] = field(default_factory=list)
    user_id: str = ""