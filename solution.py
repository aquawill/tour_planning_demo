# This code parses date/times, so please
#
#     pip install python-dateutil
#
# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = solution_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import Any, Optional, List, TypeVar, Type, cast, Callable
from datetime import datetime
from enum import Enum
from uuid import UUID
import dateutil.parser


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


@dataclass
class Times:
    driving: int
    serving: int
    waiting: int
    times_break: int

    @staticmethod
    def from_dict(obj: Any) -> 'Times':
        assert isinstance(obj, dict)
        driving = from_int(obj.get("driving"))
        serving = from_int(obj.get("serving"))
        waiting = from_int(obj.get("waiting"))
        times_break = from_int(obj.get("break"))
        return Times(driving, serving, waiting, times_break)

    def to_dict(self) -> dict:
        result: dict = {}
        result["driving"] = from_int(self.driving)
        result["serving"] = from_int(self.serving)
        result["waiting"] = from_int(self.waiting)
        result["break"] = from_int(self.times_break)
        return result


@dataclass
class Statistic:
    cost: float
    distance: int
    duration: int
    times: Times

    @staticmethod
    def from_dict(obj: Any) -> 'Statistic':
        assert isinstance(obj, dict)
        cost = from_float(obj.get("cost"))
        distance = from_int(obj.get("distance"))
        duration = from_int(obj.get("duration"))
        times = Times.from_dict(obj.get("times"))
        return Statistic(cost, distance, duration, times)

    def to_dict(self) -> dict:
        result: dict = {}
        result["cost"] = to_float(self.cost)
        result["distance"] = from_int(self.distance)
        result["duration"] = from_int(self.duration)
        result["times"] = to_class(Times, self.times)
        return result


@dataclass
class Location:
    lat: float
    lng: float

    @staticmethod
    def from_dict(obj: Any) -> 'Location':
        assert isinstance(obj, dict)
        lat = from_float(obj.get("lat"))
        lng = from_float(obj.get("lng"))
        return Location(lat, lng)

    def to_dict(self) -> dict:
        result: dict = {}
        result["lat"] = to_float(self.lat)
        result["lng"] = to_float(self.lng)
        return result


@dataclass
class ActivityTime:
    start: datetime
    end: datetime

    @staticmethod
    def from_dict(obj: Any) -> 'ActivityTime':
        assert isinstance(obj, dict)
        start = from_datetime(obj.get("start"))
        end = from_datetime(obj.get("end"))
        return ActivityTime(start, end)

    def to_dict(self) -> dict:
        result: dict = {}
        result["start"] = self.start.isoformat()
        result["end"] = self.end.isoformat()
        return result


class TypeEnum(Enum):
    ARRIVAL = "arrival"
    BREAK = "break"
    DELIVERY = "delivery"
    DEPARTURE = "departure"


@dataclass
class Activity:
    job_id: str
    type: TypeEnum
    location: Optional[Location] = None
    time: Optional[ActivityTime] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Activity':
        assert isinstance(obj, dict)
        job_id = from_str(obj.get("jobId"))
        type = TypeEnum(obj.get("type"))
        location = from_union([Location.from_dict, from_none], obj.get("location"))
        time = from_union([ActivityTime.from_dict, from_none], obj.get("time"))
        return Activity(job_id, type, location, time)

    def to_dict(self) -> dict:
        result: dict = {}
        result["jobId"] = from_str(self.job_id)
        result["type"] = to_enum(TypeEnum, self.type)
        result["location"] = from_union([lambda x: to_class(Location, x), from_none], self.location)
        result["time"] = from_union([lambda x: to_class(ActivityTime, x), from_none], self.time)
        return result


@dataclass
class StopTime:
    arrival: datetime
    departure: datetime

    @staticmethod
    def from_dict(obj: Any) -> 'StopTime':
        assert isinstance(obj, dict)
        arrival = from_datetime(obj.get("arrival"))
        departure = from_datetime(obj.get("departure"))
        return StopTime(arrival, departure)

    def to_dict(self) -> dict:
        result: dict = {}
        result["arrival"] = self.arrival.isoformat()
        result["departure"] = self.departure.isoformat()
        return result


@dataclass
class Stop:
    location: Location
    time: StopTime
    load: List[int]
    activities: List[Activity]

    @staticmethod
    def from_dict(obj: Any) -> 'Stop':
        assert isinstance(obj, dict)
        location = Location.from_dict(obj.get("location"))
        time = StopTime.from_dict(obj.get("time"))
        load = from_list(from_int, obj.get("load"))
        activities = from_list(Activity.from_dict, obj.get("activities"))
        return Stop(location, time, load, activities)

    def to_dict(self) -> dict:
        result: dict = {}
        result["location"] = to_class(Location, self.location)
        result["time"] = to_class(StopTime, self.time)
        result["load"] = from_list(from_int, self.load)
        result["activities"] = from_list(lambda x: to_class(Activity, x), self.activities)
        return result


class TypeID(Enum):
    ISUZU = "isuzu"
    MITSUBISHI = "mitsubishi"


@dataclass
class Tour:
    vehicle_id: str
    type_id: TypeID
    stops: List[Stop]
    statistic: Statistic

    @staticmethod
    def from_dict(obj: Any) -> 'Tour':
        assert isinstance(obj, dict)
        vehicle_id = from_str(obj.get("vehicleId"))
        type_id = TypeID(obj.get("typeId"))
        stops = from_list(Stop.from_dict, obj.get("stops"))
        statistic = Statistic.from_dict(obj.get("statistic"))
        return Tour(vehicle_id, type_id, stops, statistic)

    def to_dict(self) -> dict:
        result: dict = {}
        result["vehicleId"] = from_str(self.vehicle_id)
        result["typeId"] = to_enum(TypeID, self.type_id)
        result["stops"] = from_list(lambda x: to_class(Stop, x), self.stops)
        result["statistic"] = to_class(Statistic, self.statistic)
        return result


class Description(Enum):
    CANNOT_BE_ASSIGNED_DUE_TO_MAX_DISTANCE_CONSTRAINT_OF_VEHICLE = "cannot be assigned due to max distance constraint of vehicle"
    CANNOT_BE_ASSIGNED_DUE_TO_SHIFT_TIME_CONSTRAINT_OF_VEHICLE = "cannot be assigned due to shift time constraint of vehicle"


@dataclass
class Reason:
    code: int
    description: Description

    @staticmethod
    def from_dict(obj: Any) -> 'Reason':
        assert isinstance(obj, dict)
        code = from_int(obj.get("code"))
        description = Description(obj.get("description"))
        return Reason(code, description)

    def to_dict(self) -> dict:
        result: dict = {}
        result["code"] = from_int(self.code)
        result["description"] = to_enum(Description, self.description)
        return result


@dataclass
class Unassigned:
    job_id: str
    reasons: List[Reason]

    @staticmethod
    def from_dict(obj: Any) -> 'Unassigned':
        assert isinstance(obj, dict)
        job_id = from_str(obj.get("jobId"))
        reasons = from_list(Reason.from_dict, obj.get("reasons"))
        return Unassigned(job_id, reasons)

    def to_dict(self) -> dict:
        result: dict = {}
        result["jobId"] = from_str(self.job_id)
        result["reasons"] = from_list(lambda x: to_class(Reason, x), self.reasons)
        return result


@dataclass
class Solution:
    statistic: Statistic
    problem_id: UUID
    tours: List[Tour]
    unassigned: List[Unassigned]

    @staticmethod
    def from_dict(obj: Any) -> 'Solution':
        assert isinstance(obj, dict)
        statistic = Statistic.from_dict(obj.get("statistic"))
        problem_id = UUID(obj.get("problemId"))
        tours = from_list(Tour.from_dict, obj.get("tours"))
        unassigned = from_list(Unassigned.from_dict, obj.get("unassigned"))
        return Solution(statistic, problem_id, tours, unassigned)

    def to_dict(self) -> dict:
        result: dict = {}
        result["statistic"] = to_class(Statistic, self.statistic)
        result["problemId"] = str(self.problem_id)
        result["tours"] = from_list(lambda x: to_class(Tour, x), self.tours)
        result["unassigned"] = from_list(lambda x: to_class(Unassigned, x), self.unassigned)
        return result


def solution_from_dict(s: Any) -> Solution:
    return Solution.from_dict(s)


def solution_to_dict(x: Solution) -> Any:
    return to_class(Solution, x)
