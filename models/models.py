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
class OneUserTTFF:
    stabilization_time: timedelta = timedelta()

@dataclass
class TimeToFirstFix:
    sector_id: int = 6
    calc_date: datetime = datetime.now()
    avg_stabilization_time: float = 0.0
    hour_unit_TTFF: list[int] = field(default_factory=list)
    user_count: int = 0

@dataclass
class PositionTrajectory:
    sector_id: int = 0
    calc_date: datetime = datetime.now()
    one_day_stat: OneUserPositionErrTable = OneUserPositionErrTable()
    one_day_data_cnt: float = 0.0

@dataclass
class DailyPED:
    daily_ped_datas: tuple = field(default_factory=tuple)