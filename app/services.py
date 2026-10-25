import os
from pathlib import Path
from datetime import datetime, timezone
import osmnx as ox

class MapData:
    def __init__(self, directory):
        self.directory=Path(directory)
        self.directory.mkdir(parents=True,exist_ok=True)
        self.path=self.directory/'malmo.graphml'
        ox.settings.cache_folder=str(self.directory/'http-cache')
        ox.settings.use_cache=True
        ox.settings.http_user_agent='CykelframjandetMalmo/0.1 desktop cycling route planner'
        for tag in ('oneway:bicycle','bicycle:forward','bicycle:backward','cycleway:left','cycleway:right','cycleway:both','bicycle_road','cyclestreet','foot'):
            if tag not in ox.settings.useful_tags_way: ox.settings.useful_tags_way.append(tag)
        ox.settings.requests_timeout=120
        self.graph=None

    def load(self):
        if self.path.exists(): self.graph=ox.load_graphml(self.path)
        return self.graph

    def update(self):
        # Kommungränsen hämtas av OSMnx. Tidigare fungerande graf ersätts först efter validering.
        graph=ox.graph_from_place('Malmö kommun, Skåne, Sweden',network_type='bike',simplify=True)
        if len(graph)<100 or graph.number_of_edges()<100:
            raise ValueError('Datamängden är oväntat liten. Tidigare karta behålls.')
        temp=self.directory/'malmo-new.graphml'
        ox.save_graphml(graph,temp)
        checked=ox.load_graphml(temp)
        os.replace(temp,self.path)
        self.graph=checked
        return datetime.now(timezone.utc).isoformat()

    def features(self):
        from app.routing import classify
        features=[]; seen=set()
        if self.graph is None: return features
        g=self.graph
        for u,v,k,d in g.edges(keys=True,data=True):
            identity=(min(u,v),max(u,v),str(d.get('osmid')),str(d.get('geometry')))
            if identity in seen: continue
            seen.add(identity)
            geometry=d.get('geometry')
            coords=list(geometry.coords) if geometry is not None else [(g.nodes[u]['x'],g.nodes[u]['y']),(g.nodes[v]['x'],g.nodes[v]['y'])]
            features.append({'type':'Feature','properties':{'kind':classify(d)},'geometry':{'type':'LineString','coordinates':coords}})
        return features
