def progression(inspections):
    return [{"inspection_id":i.id,"date":i.created_at.isoformat() if i.created_at else None,"disease":i.disease.disease if i.disease else None,"severity":i.disease.severity if i.disease else None,"irrigation_status":i.irrigation.status if i.irrigation else None} for i in inspections]
