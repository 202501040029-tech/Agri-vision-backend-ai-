def assess(visual, soil_moisture=None, simulated=False, rainfall_mm=None, symptoms=None):
    symptoms=symptoms or []; evidence=[]
    if visual: evidence.append('Image-based colour indicators are heuristic and may reflect disease or nutrient stress, not only water stress.')
    if soil_moisture is not None:
        evidence.append(('Simulated' if simulated else 'Farmer-provided')+f' soil-moisture value: {soil_moisture}%.')
        if soil_moisture < 20: status='Irrigation recommended'
        elif soil_moisture < 35: status='Possible water stress – verify soil moisture'
        else: status='No immediate irrigation indication'
    elif visual and visual.get('yellow_brown_fraction',0) > .25:
        status='Possible water stress – verify soil moisture'; evidence.append('Elevated yellow/brown pixel fraction detected; this is not specific to drought.')
    else:
        status='Insufficient data – further inspection required'; evidence.append('Soil-moisture measurement is unavailable; visual image alone is insufficient.')
    if rainfall_mm is not None: evidence.append(f'Recent rainfall supplied: {rainfall_mm} mm.')
    rec={'Irrigation recommended':'Check soil moisture and crop stage, then irrigate according to local agronomic guidance.','Possible water stress – verify soil moisture':'Possible visual stress only. Verify soil moisture and recent rainfall before watering.','No immediate irrigation indication':'No immediate irrigation indication from supplied data; continue routine monitoring.','Insufficient data – further inspection required':'Collect a soil-moisture reading or inspect the zone before deciding.'}[status]
    return {"status":status,"confidence":None,"evidence":evidence,"recommendation":rec,"soil_moisture":soil_moisture,"measurement_type":"simulated" if simulated and soil_moisture is not None else ("farmer_provided" if soil_moisture is not None else "unavailable")}
