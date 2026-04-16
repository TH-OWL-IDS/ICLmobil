from pydantic import BaseModel
from typing import List, Optional
from TripApiResponse import TripResponse
from PtGeoJson import Properties


class TripResult(BaseModel):
    origin: List[float]
    origin_stop: str
    destination_name: str
    destination: List[float]
    destination_stop: str
    fid: int
    properties: Properties
    trip: Optional[TripResponse] = None

    def to_json(self):
        return self.model_dump_json()
