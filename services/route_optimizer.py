import networkx as nx

def optimize(zones, start_zone_id=None, priorities=None):
    if not zones: return {"ordered_zones":[],"estimated_grid_distance":0}
    graph=nx.Graph()
    for z in zones: graph.add_node(z.id, row=z.row, col=z.column)
    for a in zones:
        for b in zones:
            if a.id<b.id: graph.add_edge(a.id,b.id,weight=max(1,abs(a.row-b.row)+abs(a.column-b.column)))
    remaining=set(graph.nodes); current=start_zone_id if start_zone_id in remaining else zones[0].id; order=[]; dist=0; priorities=priorities or {}
    while remaining:
        if current not in remaining: current=min(remaining,key=lambda n:nx.shortest_path_length(graph,current,n,weight='weight'))
        candidates=sorted(remaining,key=lambda n:(nx.shortest_path_length(graph,current,n,weight='weight')-min(3,priorities.get(n,0)/30), n))
        nxt=candidates[0]; d=nx.shortest_path_length(graph,current,nxt,weight='weight'); dist+=d
        order.append({"zone_id":nxt,"priority_score":priorities.get(nxt,0),"reason":"Higher inspection priority" if priorities.get(nxt,0)>=50 else "Nearest remaining zone"})
        remaining.remove(nxt); current=nxt
    return {"ordered_zones":order,"estimated_grid_distance":dist,"distance_unit":"grid steps; not GPS distance"}
