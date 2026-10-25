"""Sverige: verifierad engångshämtning, diskindex och lokal visning/ruttgraf."""
import hashlib
import json
import math
import os
import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import parse_qs, urlsplit
import networkx as nx

SOURCE='https://download.geofabrik.de/europe/sweden-latest.osm.pbf'

@contextmanager
def database(path):
    db=sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True)
    try:yield db
    finally:db.close()

def download_sweden(directory, progress=lambda text:None):
    import requests
    folder=Path(directory);folder.mkdir(parents=True,exist_ok=True)
    if shutil.disk_usage(folder).free<8*1024**3:
        raise ValueError('Minst 8 GB ledigt diskutrymme behövs för hämtning och bearbetning. Det slutliga utrymmesbehovet beror på aktuell datamängd.')
    target=folder/'sweden.osm.pbf';partial=folder/'sweden.osm.pbf.part'
    with requests.get(SOURCE+'.md5',timeout=60) as response:
        response.raise_for_status();expected=response.text.split()[0].lower()
    if len(expected)!=32 or any(c not in '0123456789abcdef' for c in expected):raise ValueError('Geofabrik skickade ingen giltig kontrollsumma.')
    def digest(path):
        h=hashlib.md5()
        with open(path,'rb') as f:
            for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
        return h.hexdigest()
    if target.exists() and digest(target)==expected:
        progress('Sverigefilen finns redan och kontrollsumman stämmer.');return target
    try:
        with requests.get(SOURCE,stream=True,timeout=(30,120)) as response:
            response.raise_for_status();total=int(response.headers.get('Content-Length',0));received=0;last=-1
            if total and shutil.disk_usage(folder).free<total*5:raise ValueError('För lite ledigt utrymme för kartfil och index. Frigör utrymme och försök igen.')
            with partial.open('wb') as f:
                for block in response.iter_content(1024*1024):
                    f.write(block);received+=len(block)
                    mb=received//(10*1024*1024)
                    if mb!=last:
                        progress(f'Hämtar Sverige: {received/1024**2:.0f} MB'+(f' av {total/1024**2:.0f} MB' if total else ''));last=mb
        progress('Verifierar Geofabriks kontrollsumma …')
        if digest(partial)!=expected:raise ValueError('Kontrollsumman stämmer inte. Filen används inte; tidigare karta behålls. Källan kan ha uppdaterats under hämtningen.')
        os.replace(partial,target)
    finally:
        partial.unlink(missing_ok=True)
    return target

def build_database(source, destination, progress=lambda text:None):
    import osmium
    dest=Path(destination);dest.parent.mkdir(parents=True,exist_ok=True)
    temporary=dest.with_suffix('.building.sqlite');index=dest.with_suffix('.node-index')
    temporary.unlink(missing_ok=True);index.unlink(missing_ok=True)
    db=sqlite3.connect(temporary)
    db.executescript('CREATE TABLE ways(id INTEGER PRIMARY KEY,kind TEXT,tags TEXT,nodes TEXT,coords TEXT,minzoom INTEGER); CREATE VIRTUAL TABLE bounds USING rtree(id,west,east,south,north); CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT);')
    class Handler(osmium.SimpleHandler):
        def __init__(self):super().__init__();self.count=0
        def way(self,way):
            tags=dict(way.tags)
            highway=tags.get('highway')
            kind='road' if highway else 'coastline' if tags.get('natural')=='coastline' else 'water' if tags.get('natural')=='water' else 'park' if tags.get('leisure') in ('park','garden','nature_reserve') or tags.get('landuse') in ('forest','grass','recreation_ground') else 'building' if 'building' in tags else None
            if kind is None:return
            if len(way.nodes)<2:return
            if any(not n.location.valid() for n in way.nodes):
                raise ValueError('Kartfilen saknar nodpositioner. Tidigare karta behålls.')
            coords=[[n.lon,n.lat] for n in way.nodes];nodes=[n.ref for n in way.nodes]
            xs=[p[0] for p in coords];ys=[p[1] for p in coords]
            minzoom=4 if highway in ('motorway','trunk') or kind=='coastline' else 7 if highway=='primary' else 8 if highway in ('secondary','tertiary') else 13 if kind=='building' else 11
            db.execute('INSERT INTO ways VALUES (?,?,?,?,?,?)',(way.id,kind,json.dumps(tags),json.dumps(nodes),json.dumps(coords),minzoom))
            db.execute('INSERT INTO bounds VALUES (?,?,?,?,?)',(way.id,min(xs),max(xs),min(ys),max(ys)))
            self.count+=1
            if self.count%10000==0:
                db.commit();progress(f'Förbereder offlinekartan: {self.count:,} kartobjekt …')
    try:
        progress('Bygger lokalt kartindex. Detta görs en gång och kan ta lång tid …')
        handler=Handler()
        def parse():
            try:
                handler.apply_file(str(source),locations=True,idx='sparse_file_array,'+str(index))
            except Exception as error:
                # Frigör native-filhandtag som annars hålls kvar av traceback på Windows.
                message=str(error)
                error.__traceback__=None
                return message
            return None
        error=parse()
        if error is not None:raise ValueError(error)
        if handler.count==0:raise ValueError('Kartfilen innehåller inga användbara kartobjekt.')
        progress('Optimerar kartindexet …')
        db.execute('CREATE INDEX ways_zoom ON ways(minzoom)')
        db.execute('INSERT INTO metadata VALUES (?,?)',('updated',datetime.now(timezone.utc).isoformat()))
        db.execute('INSERT INTO metadata VALUES (?,?)',('source',SOURCE))
        db.commit()
        if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('Kartindexet kunde inte valideras.')
        db.close();os.replace(temporary,dest)
        return str(dest)
    finally:
        db.close();temporary.unlink(missing_ok=True);index.unlink(missing_ok=True)

class SwedenData:
    def __init__(self,path):
        self.path=Path(path)
        with database(path) as db:
            db.execute('SELECT id,kind,tags,nodes,coords,minzoom FROM ways LIMIT 1').fetchone()
            self.metadata=dict(db.execute('SELECT key,value FROM metadata'))
    def rows(self,bbox,limit,zoom=22,roads_only=False):
        west,south,east,north=bbox
        with database(self.path) as db:
            if zoom<10:
                return db.execute('SELECT w.id,w.kind,w.tags,w.nodes,w.coords FROM ways w INDEXED BY ways_zoom CROSS JOIN bounds b ON b.id=w.id WHERE w.minzoom<=? AND b.west<=? AND b.east>=? AND b.south<=? AND b.north>=? LIMIT ?', (zoom,east,west,north,south,limit)).fetchall()
            return db.execute('SELECT w.id,w.kind,w.tags,w.nodes,w.coords FROM bounds b JOIN ways w ON w.id=b.id WHERE b.west<=? AND b.east>=? AND b.south<=? AND b.north>=? AND w.minzoom<=? AND (?=0 OR w.kind=?) LIMIT ?', (east,west,north,south,zoom,int(roads_only),'road',limit)).fetchall()
    def features(self,bbox,zoom):
        rows=self.rows(bbox,15001,zoom);features=[]
        for identifier,kind,tags,_,coords in rows[:15000]:
            tags=json.loads(tags);coords=json.loads(coords)
            if zoom<13 and kind=='building':continue
            if zoom<9 and (kind!='road' or tags.get('highway') not in ('motorway','trunk','primary','secondary')):continue
            if zoom<12 and kind=='road' and tags.get('highway') in ('service','footway','path','steps'):continue
            from app.routing import classify
            polygon=kind!='road' and coords[0]==coords[-1] and len(coords)>=4
            if zoom<13 and len(coords)>2:
                from shapely.geometry import LineString,Polygon
                shape=Polygon(coords) if polygon else LineString(coords)
                simple=shape.simplify(360/(256*2**zoom),preserve_topology=True)
                coords=list(simple.exterior.coords) if polygon else list(simple.coords)
            features.append({'type':'Feature','properties':{'kind':kind,'road':classify(tags),'highway':tags.get('highway',''),'name':tags.get('name','')},'geometry':{'type':'Polygon' if polygon else 'LineString','coordinates':[coords] if polygon else coords}})
        return {'type':'FeatureCollection','features':features,'truncated':len(rows)>15000}
    def graph(self,points,padding=.15):
        from app.routing import allowed
        lats=[p[0] for p in points];lons=[p[1] for p in points]
        bbox=[min(lons)-padding,min(lats)-padding,max(lons)+padding,max(lats)+padding]
        rows=self.rows(bbox,250001,roads_only=True)
        if len(rows)>250000:raise ValueError('Ruttområdet är för stort för denna version. Välj kortare etapper.')
        g=nx.MultiDiGraph(crs='epsg:4326')
        for _,kind,tags,nodes,coords in rows:
            if kind!='road':continue
            tags=json.loads(tags)
            if not allowed(tags):continue
            highway=tags.get('highway')
            if highway in ('construction','proposed','platform','motorway_link','trunk','trunk_link') and tags.get('bicycle') not in ('yes','designated'):continue
            if highway in ('footway','pedestrian') and tags.get('bicycle') not in ('yes','designated','permissive'):continue
            nodes=json.loads(nodes);coords=json.loads(coords)
            one=tags.get('oneway:bicycle',tags.get('oneway','yes' if tags.get('junction')=='roundabout' else 'no'))
            reverse_only=one=='-1';both=one not in ('yes','1','true','-1')
            for (u,a),(v,b) in zip(zip(nodes,coords),zip(nodes[1:],coords[1:])):
                g.add_node(u,x=a[0],y=a[1]);g.add_node(v,x=b[0],y=b[1])
                lat1,lat2=map(math.radians,(a[1],b[1]));dlon=math.radians(b[0]-a[0]);dlat=lat2-lat1
                length=6371000*2*math.asin(min(1,math.sqrt(math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2)))
                attrs={**tags,'length':length}
                if not reverse_only and tags.get('bicycle:forward')!='no':g.add_edge(u,v,**attrs)
                if (both or reverse_only) and tags.get('bicycle:backward')!='no':g.add_edge(v,u,**attrs)
        if not len(g):raise ValueError('Inga cykelbara vägar i detta område i offlinepaketet.')
        return g

class SwedenServer:
    def __init__(self,path):
        self.data=SwedenData(path);data=self.data
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed=urlsplit(self.path)
                if parsed.path!='/features':self.send_error(404);return
                try:
                    params=parse_qs(parsed.query);bbox=list(map(float,params['bbox'][0].split(',')));zoom=int(params['zoom'][0])
                    if len(bbox)!=4 or not all(map(math.isfinite,bbox)) or not -180<=bbox[0]<bbox[2]<=180 or not -90<=bbox[1]<bbox[3]<=90 or not 0<=zoom<=22:raise ValueError()
                    payload=json.dumps(data.features(bbox,zoom)).encode()
                except (KeyError,ValueError):self.send_error(400);return
                except sqlite3.Error:self.send_error(503);return
                self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.send_header('Access-Control-Allow-Origin','*');self.end_headers();self.wfile.write(payload)
            def log_message(self,*args):pass
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);self.thread=Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def config(self):return {'kind':'sweden','url':f'http://127.0.0.1:{self.server.server_port}/features','minZoom':4,'maxZoom':19,'bounds':[[55,10],[69.5,24.5]],'attribution':'© OpenStreetMap-bidragsgivare · Geofabrik · ODbL'}
    def close(self):self.server.shutdown();self.server.server_close();self.thread.join(timeout=2)
