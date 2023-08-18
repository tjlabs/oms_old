from dataclasses import field, dataclass
from datetime import timedelta
from datetime import datetime
from collections import defaultdict

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
class CoordinatesWithIsindoor:
    x: int = 0
    y: int = 0
    is_indoor: bool = False
    mobile_time: datetime = datetime.now()

@dataclass
class OneUserPositionErrTable:
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
    avg_stabilization_time: float = 0.0
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
class OneuserWholeTestSets:
    test_sets: list[TestSet] = field(default_factory=list)
    user_id: str = ""

@dataclass
class LocationTrackingTime:
    calc_date: datetime = datetime.now()
    avg_loc_track_time: float = 0.0
    quantile_50th: list = field(default_factory=list)
    quantile_90th: list = field(default_factory=list)
    quantile_95th: list = field(default_factory=list)
    min_avg_ltt: list = field(default_factory=list)
    