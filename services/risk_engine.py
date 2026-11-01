def score_zones(zones):
    # Transparent inspection-priority score, not disease-transmission probability.
    bypos={(z.row,z.column):z for z in zones}; out=[]
    for z in zones:
        own=z.inspections[-1] if z.inspections else None
        score=20 if own else 0; reasons=[]
        if own: score+=20; reasons.append('Zone has inspection history')
        for (r,c),n in bypos.items():
            if abs(r-z.row)<=1 and abs(c-z.column)<=1 and n.id!=z.id and n.inspections:
                score+=15; reasons.append(f'Adjacent zone {n.code} has inspection history')
        score=min(score,100); level='High' if score>=60 else ('Medium' if score>=30 else 'Low')
        out.append({"zone_id":z.id,"zone_code":z.code,"score":score,"status":level,"reasons":reasons or ['No nearby inspection signals recorded']})
    return out
