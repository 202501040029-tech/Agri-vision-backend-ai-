from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

def now(): return datetime.now(timezone.utc)
class Farm(Base):
    __tablename__='farms'
    id: Mapped[int]=mapped_column(primary_key=True); name: Mapped[str]=mapped_column(String(120)); owner: Mapped[str|None]=mapped_column(String(120),nullable=True)
    rows: Mapped[int]=mapped_column(Integer,default=2); columns: Mapped[int]=mapped_column(Integer,default=2); area_ha: Mapped[float|None]=mapped_column(Float,nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    zones=relationship('Zone',back_populates='farm',cascade='all, delete-orphan')
class Zone(Base):
    __tablename__='zones'
    id: Mapped[int]=mapped_column(primary_key=True); farm_id: Mapped[int]=mapped_column(ForeignKey('farms.id')); code: Mapped[str]=mapped_column(String(40))
    row: Mapped[int]=mapped_column(Integer,default=0); column: Mapped[int]=mapped_column(Integer,default=0); crop: Mapped[str]=mapped_column(String(80),default='Unknown')
    area_ha: Mapped[float|None]=mapped_column(Float,nullable=True); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    farm=relationship('Farm',back_populates='zones'); inspections=relationship('Inspection',back_populates='zone',cascade='all, delete-orphan')
class Inspection(Base):
    __tablename__='inspections'
    id: Mapped[int]=mapped_column(primary_key=True); zone_id: Mapped[int]=mapped_column(ForeignKey('zones.id')); image_path: Mapped[str|None]=mapped_column(String(500),nullable=True)
    symptoms: Mapped[str|None]=mapped_column(Text,nullable=True); notes: Mapped[str|None]=mapped_column(Text,nullable=True); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    zone=relationship('Zone',back_populates='inspections'); disease=relationship('DiseasePrediction',uselist=False,cascade='all, delete-orphan'); second_opinion=relationship('SecondOpinion',uselist=False,cascade='all, delete-orphan'); irrigation=relationship('IrrigationAssessment',uselist=False,cascade='all, delete-orphan')
class DiseasePrediction(Base):
    __tablename__='disease_predictions'
    id: Mapped[int]=mapped_column(primary_key=True); inspection_id: Mapped[int]=mapped_column(ForeignKey('inspections.id')); disease: Mapped[str]=mapped_column(String(120),default='Model unavailable')
    confidence: Mapped[float|None]=mapped_column(Float,nullable=True); severity: Mapped[str|None]=mapped_column(String(40),nullable=True); model_status: Mapped[str]=mapped_column(String(80),default='not_configured'); details: Mapped[dict]=mapped_column(JSON,default=dict)
class SecondOpinion(Base):
    __tablename__='second_opinions'
    id: Mapped[int]=mapped_column(primary_key=True); inspection_id: Mapped[int]=mapped_column(ForeignKey('inspections.id')); status: Mapped[str]=mapped_column(String(80)); explanation: Mapped[str]=mapped_column(Text); next_action: Mapped[str]=mapped_column(Text); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class IrrigationAssessment(Base):
    __tablename__='irrigation_assessments'
    id: Mapped[int]=mapped_column(primary_key=True); inspection_id: Mapped[int]=mapped_column(ForeignKey('inspections.id')); status: Mapped[str]=mapped_column(String(100)); confidence: Mapped[float|None]=mapped_column(Float,nullable=True)
    soil_moisture: Mapped[float|None]=mapped_column(Float,nullable=True); is_simulated: Mapped[bool]=mapped_column(Boolean,default=False); evidence: Mapped[list]=mapped_column(JSON,default=list); recommendation: Mapped[str]=mapped_column(Text)
class Intervention(Base):
    __tablename__='interventions'
    id: Mapped[int]=mapped_column(primary_key=True); farm_id: Mapped[int]=mapped_column(ForeignKey('farms.id')); zone_id: Mapped[int|None]=mapped_column(ForeignKey('zones.id'),nullable=True); action: Mapped[str]=mapped_column(String(200)); notes: Mapped[str|None]=mapped_column(Text,nullable=True); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class SimulationResult(Base):
    __tablename__='simulation_results'
    id: Mapped[int]=mapped_column(primary_key=True); farm_id: Mapped[int]=mapped_column(ForeignKey('farms.id')); assumptions: Mapped[dict]=mapped_column(JSON); results: Mapped[dict]=mapped_column(JSON); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class ChatSession(Base):
    __tablename__='chat_sessions'
    id: Mapped[int]=mapped_column(primary_key=True); language: Mapped[str]=mapped_column(String(20),default='en'); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class ChatMessage(Base):
    __tablename__='chat_messages'
    id: Mapped[int]=mapped_column(primary_key=True); session_id: Mapped[int]=mapped_column(ForeignKey('chat_sessions.id')); role: Mapped[str]=mapped_column(String(20)); content: Mapped[str]=mapped_column(Text); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class FarmerFeedback(Base):
    __tablename__='farmer_feedback'
    id: Mapped[int]=mapped_column(primary_key=True); inspection_id: Mapped[int|None]=mapped_column(ForeignKey('inspections.id'),nullable=True); rating: Mapped[int]=mapped_column(Integer); comment: Mapped[str|None]=mapped_column(Text,nullable=True); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
