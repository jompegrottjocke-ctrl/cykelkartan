"""Riktad ruttberäkning på verkliga OSM-kanter."""
import json
import math
from xml.etree.ElementTree import Element, SubElement, ElementTree
import networkx as nx

MODES = ['Kortaste rutten', 'Snabbaste rutten', 'Säkrare rutten', 'Trevligaste rutten', 'Maximera cykelbana']

def classify(tags):
    highway = tags.get('highway')
    if tags.get('bicycle_road') == 'yes' or tags.get('cyclestreet') == 'yes':
        return 'cykelgata'
    if highway in ('cycleway', 'path', 'footway') and tags.get('foot') in ('yes', 'designated') and tags.get('bicycle') in ('yes', 'designated'):
        return 'gemensam'
    if highway == 'cycleway':
        return 'separat'
    cycle = [str(tags.get(k, '')) for k in ('cycleway', 'cycleway:left', 'cycleway:right', 'cycleway:both')]
    if any(v in ('track', 'opposite_track') for v in cycle):
        return 'separat'
    if any(v in ('lane', 'opposite_lane', 'shared_lane') for v in cycle):
        return 'fält'
    return 'övrig'

def allowed(tags):
    return tags.get('bicycle') not in ('no', 'private', 'dismount') and not (tags.get('access') in ('no', 'private') and tags.get('bicycle') not in ('yes', 'designated', 'permissive')) and tags.get('highway') not in ('motorway', 'motorway_link', 'steps')

def minutes(meters, speed):
    if not 5 <= speed <= 40:
        raise ValueError('Hastigheten måste vara mellan 5 och 40 km/h.')
    return meters / 1000 / speed * 60

def calculate(graph, points, mode=MODES[0], speed=15, detour=20, wait=False):
    import osmnx as ox
    if len(points) < 2:
        raise ValueError('Välj startpunkt och destination.')
    g = nx.MultiDiGraph(graph)
    g.remove_edges_from([(u,v,k) for u,v,k,d in g.edges(keys=True,data=True) if not allowed(d)])
    # OSM:s uttryckliga cykelundantag till enkelriktning.
    for u,v,k,d in list(g.edges(keys=True,data=True)):
        if d.get('oneway:bicycle') == 'no' and not g.has_edge(v,u):
            reverse=dict(d)
            if reverse.get('geometry') is not None:
                from shapely.geometry import LineString
                reverse['geometry']=LineString(list(reverse['geometry'].coords)[::-1])
            g.add_edge(v,u,**reverse)
    def cost(u,v,d):
        if 'length' in d: return edge_cost(d)
        return min(edge_cost(x) for x in d.values()) + (0.35 if mode == MODES[1] and wait and g.nodes[v].get('highway') == 'traffic_signals' else 0)
    def edge_cost(d):
        length = float(d.get('length', 0))
        kind = classify(d)
        if mode == MODES[1]: return minutes(length, speed)
        if mode in (MODES[2],MODES[4]): return length * {'separat':.45,'gemensam':.6,'cykelgata':.7,'fält':.85,'övrig':1.8}[kind]
        if mode == MODES[3]: return length * (.65 if kind in ('separat','gemensam','cykelgata') else 1.2)
        return length
    nodes=[]
    for lat,lon in points:
        node=ox.distance.nearest_nodes(g,lon,lat)
        n=g.nodes[node]
        distance=math.hypot((float(n['y'])-lat)*111000,(float(n['x'])-lon)*62000)
        if distance>1000: raise ValueError('Punkten ligger för långt från det lokala cykelvägnätet.')
        nodes.append(node)
    route=[]
    for a,b in zip(nodes,nodes[1:]):
        selected=nx.shortest_path(g,a,b,weight=cost)
        if mode == MODES[4]:
            shortest=nx.shortest_path(g,a,b,weight='length')
            def length(path): return sum(min(float(d['length']) for d in g[u][v].values()) for u,v in zip(path,path[1:]))
            if length(selected)>length(shortest)*(1+detour/100): selected=shortest
        route.extend(selected if not route else selected[1:])
    coords=[]; total=0; distribution={}; instructions=[]
    for u,v in zip(route,route[1:]):
        d=min(g[u][v].values(),key=edge_cost)
        length=float(d['length']); total+=length; kind=classify(d)
        distribution[kind]=distribution.get(kind,0)+length
        geometry=d.get('geometry')
        xy=list(geometry.coords) if geometry is not None else [(g.nodes[u]['x'],g.nodes[u]['y']),(g.nodes[v]['x'],g.nodes[v]['y'])]
        if math.hypot(xy[-1][0]-g.nodes[u]['x'],xy[-1][1]-g.nodes[u]['y'])<math.hypot(xy[0][0]-g.nodes[u]['x'],xy[0][1]-g.nodes[u]['y']): xy.reverse()
        segment=[[float(y),float(x)] for x,y in xy]
        coords.extend(segment if not coords else segment[1:])
        name=d.get('name','Cykelbar väg utan angivet namn')
        if isinstance(name,list): name=', '.join(name)
        instructions.append({'text':f'Följ {name} i {length:.0f} m', 'coords':segment})
    if not coords: raise ValueError('Punkterna ligger vid samma väganslutning. Välj punkter längre ifrån varandra.')
    signals=sum(g.nodes[n].get('highway')=='traffic_signals' for n in route)
    return dict(coords=coords,meters=total,minutes=minutes(total,speed),wait=signals*.35 if wait else 0,distribution=distribution,instructions=instructions,points=points,mode=mode)

def export_route(route, path):
    if str(path).lower().endswith('.gpx'):
        root=Element('gpx',version='1.1',creator='Cykelfrämjandet Malmö',xmlns='http://www.topografix.com/GPX/1/1')
        segment=SubElement(SubElement(root,'trk'),'trkseg')
        for lat,lon in route['coords']: SubElement(segment,'trkpt',lat=str(lat),lon=str(lon))
        ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
    else:
        data={'type':'Feature','geometry':{'type':'LineString','coordinates':[[lon,lat] for lat,lon in route['coords']]},'properties':{k:route[k] for k in ('meters','minutes','wait','mode')}}
        with open(path,'w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False)
