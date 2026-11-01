def compare(farm, zones, selected, priority, cost, resource, water):
    area=sum((z.area_ha or 0) for z in zones); byid={z.id:z for z in zones}
    def calc(ids):
        a=sum((byid[i].area_ha or 0) for i in set(ids) if i in byid)
        return {"selected_area_ha":a,"estimated_resource_units":a*resource,"estimated_treatment_cost":a*cost,"estimated_water_l":a*water if water is not None else None}
    return {"total_farm_area_ha":area,"estimates_only":True,"scenarios":{"A_uniform":calc(list(byid)),"B_targeted":calc(selected),"C_priority_inspection":calc(priority)},"note":"Estimates depend entirely on user-supplied area and cost/resource assumptions; not measured savings."}
