from dataclasses import field, dataclass
from datetime import timedelta

from numpy import float64
# ** dataclass로 끌고 가는게 왜 진짜로 편리한지 적어두기
# 편리한 이유 1: 여러 세부 속성들을 하나의 큰 속성으로 묶어서 반환 및 입력 받을 수 있어서 전달 인자가 줄어들고
# 안전하다. 
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
    device_info: DiscoveredDevice = DiscoveredDevice()

@dataclass
class OneUserTTFF:
    stabilization_time: timedelta = timedelta()

@dataclass
class TimeToFirstFix:
    sector_id: int = 6
    calc_date: str = ""
    avg_stabilization_time: float = 0.0
    hour_unit_TTFF: list[int] = field(default_factory=list)
    user_count: int = 0

@dataclass
class PositionTrajectory:
    sector_id: int = 0
    calc_date: str = ""
    one_day_stat: OneUserPositionErrTable = OneUserPositionErrTable()
    one_day_data_cnt: float = 0.0

if __name__ == '__main__':
    0