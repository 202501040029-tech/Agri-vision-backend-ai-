from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import get_db
from models import *
from schemas import *
from config import settings
from services.disease_detection import predict
from services.image_analysis import analyze_image
from services.second_opinion import assess
from services.irrigation_engine import assess as irrigation_assess
from services.risk_engine import score_zones
from services.route_optimizer import optimize
from services.simulation_engine import compare
from services.progression_engine import progression
from services.gemini_service import reply

router=APIRouter(prefix='/api')
def farm_or_404(db,id):
    x=db.get(Farm,id)
    if not x: raise HTTPException(404,'Farm not found')
    return x
def zone_or_404(db,id):
    x=db.get(Zone,id)
    if not x: raise HTTPException(404,'Zone not found')
    return x
@router.get('/health')
def health(): return {"success":True,"status":"healthy","service":"AgriVision AI"}
@router.post('/farms')
def create_farm(data:FarmIn,db:Session=Depends(get_db)):
    x=Farm(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return {"success":True,"farm":farm_dict(x)}
def farm_dict(x): return {"id":x.id,"name":x.name,"owner":x.owner,"rows":x.rows,"columns":x.columns,"area_ha":x.area_ha,"created_at":x.created_at.isoformat()}
@router.get('/farms')
def farms(db:Session=Depends(get_db)): return {"success":True,"farms":[farm_dict(x) for x in db.scalars(select(Farm)).all()]}
@router.get('/farms/{farm_id}')
def get_farm(farm_id:int,db:Session=Depends(get_db)):
    x=farm_or_404(db,farm_id); return {"success":True,"farm":farm_dict(x),"zones":[zone_dict(z) for z in x.zones]}
@router.put('/farms/{farm_id}')
def update_farm(farm_id:int,data:FarmIn,db:Session=Depends(get_db)):
    x=farm_or_404(db,farm_id)
    for k,v in data.model_dump().items(): setattr(x,k,v)
    db.commit(); db.refresh(x); return {"success":True,"farm":farm_dict(x)}
def zone_dict(z): return {"id":z.id,"farm_id":z.farm_id,"code":z.code,"row":z.row,"column":z.column,"crop":z.crop,"area_ha":z.area_ha}
@router.post('/zones')
def create_zone(data:ZoneIn,db:Session=Depends(get_db)):
    farm_or_404(db,data.farm_id); x=Zone(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return {"success":True,"zone":zone_dict(x)}
@router.get('/zones')
def zones(farm_id:int|None=None,db:Session=Depends(get_db)):
    q=select(Zone)
    if farm_id is not None:q=q.where(Zone.farm_id==farm_id)
    return {"success":True,"zones":[zone_dict(z) for z in db.scalars(q).all()]}
@router.get('/zones/{zone_id}')
def get_zone(zone_id:int,db:Session=Depends(get_db)):
    z=zone_or_404(db,zone_id); return {"success":True,"zone":zone_dict(z)}
@router.put('/zones/{zone_id}')
def update_zone(zone_id:int,data:ZoneIn,db:Session=Depends(get_db)):
    z=zone_or_404(db,zone_id); farm_or_404(db,data.farm_id)
    for k,v in data.model_dump().items():setattr(z,k,v)
    db.commit(); db.refresh(z); return {"success":True,"zone":zone_dict(z)}
@router.post('/analysis/analyze')
async def analyze(zone_id:int=Form(...), symptoms:str=Form(''), notes:str=Form(''), image:UploadFile=File(...), db:Session=Depends(get_db)):
    z=zone_or_404(db,zone_id)
    if image.content_type not in ('image/jpeg','image/png','image/webp'): raise HTTPException(415,'Only JPEG, PNG and WEBP images are accepted')
    data=await image.read()
    if not data or len(data)>settings.max_upload_mb*1024*1024: raise HTTPException(413,f'Image must be non-empty and <= {settings.max_upload_mb} MB')
    ext={'image/jpeg':'.jpg','image/png':'.png','image/webp':'.webp'}[image.content_type]; path=Path(settings.upload_dir)/(uuid4().hex+ext); path.write_bytes(data)
    try: visual=analyze_image(str(path))
    except ValueError as e: path.unlink(missing_ok=True); raise HTTPException(400,str(e))
    pred=predict(str(path)); ins=Inspection(zone_id=z.id,image_path=str(path),symptoms=symptoms,notes=notes); db.add(ins); db.flush()
    dp=DiseasePrediction(inspection_id=ins.id,**pred,details={"visual_analysis":visual}); db.add(dp)
    opinion=assess(pred,[s.strip() for s in symptoms.split(',') if s.strip()],[]); so=SecondOpinion(inspection_id=ins.id,**opinion); db.add(so)
    irrigation=irrigation_assess(visual); ia=IrrigationAssessment(inspection_id=ins.id,status=irrigation['status'],confidence=None,evidence=irrigation['evidence'],recommendation=irrigation['recommendation']); db.add(ia); db.commit()
    return {"success":True,"inspection_id":ins.id,"zone_id":z.id,"crop":z.crop,"disease":pred['disease'],"confidence":pred['confidence'],"model_status":pred['model_status'],"severity":pred['severity'],"visual_analysis":visual,"second_opinion":opinion,"irrigation":irrigation}
@router.get('/analysis/{inspection_id}')
def get_analysis(inspection_id:int,db:Session=Depends(get_db)):
    i=db.get(Inspection,inspection_id)
    if not i:raise HTTPException(404,'Inspection not found')
    return inspection_dict(i)
def inspection_dict(i):return {"inspection_id":i.id,"zone_id":i.zone_id,"image_path":i.image_path,"symptoms":i.symptoms,"created_at":i.created_at.isoformat(),"disease":i.disease.disease if i.disease else None,"confidence":i.disease.confidence if i.disease else None,"second_opinion":i.second_opinion.status if i.second_opinion else None,"irrigation":i.irrigation.status if i.irrigation else None}
@router.get('/analysis/history/{zone_id}')
def analysis_history(zone_id:int,db:Session=Depends(get_db)):
    zone_or_404(db,zone_id); items=db.scalars(select(Inspection).where(Inspection.zone_id==zone_id).order_by(Inspection.created_at)).all(); return {"success":True,"history":[inspection_dict(i) for i in items]}
@router.post('/doctor/second-opinion')
def second_opinion(data:SecondOpinionIn,db:Session=Depends(get_db)):
    i=db.get(Inspection,data.inspection_id)
    if not i:raise HTTPException(404,'Inspection not found')
    p={"confidence":i.disease.confidence if i.disease else None,"disease":i.disease.disease if i.disease else None}; result=assess(p,(i.symptoms or '').split(','),data.farmer_observations)
    so=db.scalar(select(SecondOpinion).where(SecondOpinion.inspection_id==i.id).order_by(SecondOpinion.created_at.desc()))
    if so:
        so.status=result['status']; so.explanation=result['explanation']; so.next_action=result['next_action']
    else:
        db.add(SecondOpinion(inspection_id=i.id,**result))
    db.commit(); return {"success":True,**result,"scientific_confirmation":False}
@router.get('/doctor/{inspection_id}')
def doctor_get(inspection_id:int,db:Session=Depends(get_db)):
    i=db.get(Inspection,inspection_id)
    if not i:raise HTTPException(404,'Inspection not found')
    return {"success":True,"second_opinion":i.second_opinion.status if i.second_opinion else None,"explanation":i.second_opinion.explanation if i.second_opinion else None}
@router.post('/irrigation/analyze')
def irrigation(data:IrrigationIn,db:Session=Depends(get_db)):
    z=zone_or_404(db,data.zone_id); result=irrigation_assess(None,data.soil_moisture,data.simulated,data.rainfall_mm,data.symptoms)
    ins=Inspection(zone_id=z.id,notes='Irrigation-only assessment'); db.add(ins); db.flush(); db.add(IrrigationAssessment(inspection_id=ins.id,status=result['status'],confidence=None,soil_moisture=data.soil_moisture,is_simulated=data.simulated,evidence=result['evidence'],recommendation=result['recommendation'])); db.commit()
    return {"success":True,"inspection_id":ins.id,"zone_id":z.id,**result}
@router.get('/irrigation/zone/{zone_id}')
def irrigation_zone(zone_id:int,db:Session=Depends(get_db)):
    zone_or_404(db,zone_id); ins=db.scalars(select(Inspection).where(Inspection.zone_id==zone_id).order_by(Inspection.created_at.desc())).all(); return {"success":True,"zone_id":zone_id,"assessments":[{"inspection_id":i.id,"status":i.irrigation.status,"evidence":i.irrigation.evidence,"recommendation":i.irrigation.recommendation} for i in ins if i.irrigation]}
@router.get('/irrigation/farm/{farm_id}')
def irrigation_farm(farm_id:int,db:Session=Depends(get_db)):
    f=farm_or_404(db,farm_id); result=[]
    for z in f.zones:
        latest=next((i.irrigation for i in sorted(z.inspections,key=lambda a:a.created_at,reverse=True) if i.irrigation),None)
        status=latest.status if latest else 'Insufficient data – further inspection required'; color='blue' if status=='Irrigation recommended' else ('yellow' if status.startswith('Possible') else ('green' if status.startswith('No immediate') else 'grey'))
        result.append({"zone_id":z.id,"zone_code":z.code,"status":status,"color":color})
    return {"success":True,"zones":result}
@router.get('/risk/farm/{farm_id}')
def risk_farm(farm_id:int,db:Session=Depends(get_db)):
    f=farm_or_404(db,farm_id); return {"success":True,"risk":score_zones(f.zones),"interpretation":"Inspection-priority heuristic, not a validated disease-spread probability."}
@router.get('/risk/zone/{zone_id}')
def risk_zone(zone_id:int,db:Session=Depends(get_db)):
    z=zone_or_404(db,zone_id); return {"success":True,"risk":next(x for x in score_zones(z.farm.zones) if x['zone_id']==z.id)}
@router.get('/risk/map/{farm_id}')
def risk_map(farm_id:int,db:Session=Depends(get_db)):
    f=farm_or_404(db,farm_id); return {"success":True,"map":[{**x,"row":next(z.row for z in f.zones if z.id==x['zone_id']),"column":next(z.column for z in f.zones if z.id==x['zone_id'])} for x in score_zones(f.zones)]}
@router.get('/progression/{zone_id}')
def zone_progression(zone_id:int,db:Session=Depends(get_db)):
    z=zone_or_404(db,zone_id); return {"success":True,"zone_id":zone_id,"timeline":progression(sorted(z.inspections,key=lambda i:i.created_at))}
@router.get('/progression/farm/{farm_id}')
def farm_progression(farm_id:int,db:Session=Depends(get_db)):
    f=farm_or_404(db,farm_id); return {"success":True,"zones":[{"zone_id":z.id,"zone_code":z.code,"timeline":progression(sorted(z.inspections,key=lambda i:i.created_at))} for z in f.zones]}
@router.post('/simulation/compare')
def simulation(data:SimulationIn,db:Session=Depends(get_db)):
    f=farm_or_404(db,data.farm_id); res=compare(f,f.zones,data.selected_zone_ids,data.priority_zone_ids,data.unit_treatment_cost,data.resource_per_ha,data.water_per_ha_l); db.add(SimulationResult(farm_id=f.id,assumptions=data.model_dump(),results=res)); db.commit(); return {"success":True,**res}
@router.post('/scouting/optimize')
def scouting(data:ScoutingIn,db:Session=Depends(get_db)):
    f=farm_or_404(db,data.farm_id); risk=score_zones(f.zones); priorities={x['zone_id']:x['score'] for x in risk}; return {"success":True,**optimize(f.zones,data.start_zone_id,priorities)}
@router.post('/assistant/chat')
def chat(data:ChatIn,db:Session=Depends(get_db)):
    sess=db.get(ChatSession,data.session_id) if data.session_id else None
    if data.session_id and not sess:raise HTTPException(404,'Chat session not found')
    if not sess:sess=ChatSession(language=data.language); db.add(sess); db.flush()
    db.add(ChatMessage(session_id=sess.id,role='user',content=data.message)); context={}
    if data.farm_id:
        f=farm_or_404(db,data.farm_id); context={"farm":f.name,"zones":[{"code":z.code,"crop":z.crop,"latest_inspection":inspection_dict(z.inspections[-1]) if z.inspections else None} for z in f.zones]}
    ans=reply(data.message,data.language,context); db.add(ChatMessage(session_id=sess.id,role='assistant',content=ans['response'])); db.commit(); return {"success":True,"session_id":sess.id,**ans}
@router.get('/assistant/history/{session_id}')
def chat_history(session_id:int,db:Session=Depends(get_db)):
    s=db.get(ChatSession,session_id)
    if not s:raise HTTPException(404,'Chat session not found')
    return {"success":True,"messages":[{"role":m.role,"content":m.content,"created_at":m.created_at.isoformat()} for m in db.scalars(select(ChatMessage).where(ChatMessage.session_id==session_id).order_by(ChatMessage.created_at)).all()]}
@router.get('/analytics/farm/{farm_id}')
def analytics(farm_id:int,db:Session=Depends(get_db)):
    f=farm_or_404(db,farm_id); inspections=[i for z in f.zones for i in z.inspections]; return {"success":True,"farm_id":f.id,"zone_count":len(f.zones),"inspection_count":len(inspections),"model_configured":any(i.disease and i.disease.confidence is not None for i in inspections),"irrigation_status_counts":{s:sum(1 for i in inspections if i.irrigation and i.irrigation.status==s) for s in ['Irrigation recommended','Possible water stress – verify soil moisture','No immediate irrigation indication','Insufficient data – further inspection required']}}
@router.get('/reports/farm/{farm_id}')
def report(farm_id:int,db:Session=Depends(get_db)):
    f=farm_or_404(db,farm_id); return {"success":True,"farm":farm_dict(f),"zones":[{"zone":zone_dict(z),"history":progression(sorted(z.inspections,key=lambda i:i.created_at))} for z in f.zones],"generated_at":now().isoformat()}
