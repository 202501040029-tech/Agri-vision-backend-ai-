from pydantic import BaseModel, Field
from typing import Optional
class FarmIn(BaseModel): name:str; owner:Optional[str]=None; rows:int=Field(2,ge=1,le=100); columns:int=Field(2,ge=1,le=100); area_ha:Optional[float]=Field(None,gt=0)
class ZoneIn(BaseModel): farm_id:int; code:str; row:int=Field(0,ge=0); column:int=Field(0,ge=0); crop:str='Unknown'; area_ha:Optional[float]=Field(None,gt=0)
class IrrigationIn(BaseModel): zone_id:int; soil_moisture:Optional[float]=Field(None,ge=0,le=100); simulated:bool=False; rainfall_mm:Optional[float]=Field(None,ge=0); symptoms:list[str]=[]
class SecondOpinionIn(BaseModel): inspection_id:int; farmer_observations:list[str]=[]
class SimulationIn(BaseModel): farm_id:int; unit_treatment_cost:float=Field(0,ge=0); resource_per_ha:float=Field(0,ge=0); water_per_ha_l:Optional[float]=Field(None,ge=0); selected_zone_ids:list[int]=[]; priority_zone_ids:list[int]=[]
class ScoutingIn(BaseModel): farm_id:int; start_zone_id:Optional[int]=None
class ChatIn(BaseModel): session_id:Optional[int]=None; message:str; language:str='en'; farm_id:Optional[int]=None
