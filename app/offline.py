"""Läs raster-MBTiles lokalt. Inga nätanrop eller massnedladdningar."""
import json
from contextlib import contextmanager
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import re

class TilePackage:
    def __init__(self, path):
        self.path=Path(path).resolve(strict=True)
        with self.connect() as db:
            self.metadata=dict(db.execute('SELECT name,value FROM metadata'))
            db.execute('SELECT zoom_level,tile_column,tile_row,tile_data FROM tiles LIMIT 1').fetchone()
            row=db.execute('SELECT min(zoom_level),max(zoom_level) FROM tiles').fetchone()
        if self.metadata.get('format','').lower() not in ('png','jpg','jpeg'):
            raise ValueError('Välj raster-MBTiles (PNG/JPEG). Vektor-MBTiles/PBF stöds inte av denna kartvisare.')
        if row[0] is None: raise ValueError('Kartpaketet innehåller inga kartplattor.')
        self.metadata['format']=self.metadata['format'].lower()
        self.minzoom,self.maxzoom=map(int,row)
        if not 0<=self.minzoom<=self.maxzoom<=22: raise ValueError('Ogiltiga zoomnivåer i kartpaketet.')
        self.scheme=self.metadata.get('scheme','tms')
        if self.scheme not in ('tms','xyz'): raise ValueError('Kartpaketets koordinatsystem stöds inte.')
        self.bounds=None
        if self.metadata.get('bounds'):
            import math
            values=list(map(float,self.metadata['bounds'].split(',')))
            if len(values)!=4 or not all(map(math.isfinite,values)):raise ValueError('Ogiltig kartutbredning.')
            west,south,east,north=values
            if not -180<=west<east<=180 or not -90<=south<north<=90:raise ValueError('Ogiltig kartutbredning.')
            self.bounds=[[south,west],[north,east]]

    @contextmanager
    def connect(self):
        db=sqlite3.connect(self.path.as_uri()+'?mode=ro',uri=True)
        try:yield db
        finally:db.close()

    def tile(self,z,x,y):
        if not self.minzoom<=z<=self.maxzoom or not 0<=x<2**z or not 0<=y<2**z:return None
        row_y=2**z-1-y if self.scheme=='tms' else y
        with self.connect() as db:
            row=db.execute('SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?',(z,x,row_y)).fetchone()
        return bytes(row[0]) if row else None

class OfflineServer:
    def __init__(self, path):
        self.package=TilePackage(path)
        package=self.package
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                match=re.fullmatch(r'/tiles/(\d{1,2})/(\d{1,8})/(\d{1,8})',urlsplit(self.path).path)
                if not match:self.send_error(404);return
                try:data=package.tile(*map(int,match.groups()))
                except sqlite3.Error:self.send_error(503);return
                if data is None:self.send_error(404);return
                self.send_response(200)
                self.send_header('Content-Type','image/png' if package.metadata['format']=='png' else 'image/jpeg')
                self.send_header('Content-Length',str(len(data)))
                self.send_header('Access-Control-Allow-Origin','*')
                self.end_headers();self.wfile.write(data)
            def log_message(self,*args):pass
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        self.thread=Thread(target=self.server.serve_forever,daemon=True);self.thread.start()

    def config(self):
        p=self.package
        return dict(url=f'http://127.0.0.1:{self.server.server_port}/tiles/{{z}}/{{x}}/{{y}}',minZoom=p.minzoom,maxZoom=p.maxzoom,bounds=p.bounds,name=p.metadata.get('name',p.path.stem),attribution=p.metadata.get('attribution','© OpenStreetMap-bidragsgivare'))

    def close(self):self.server.shutdown();self.server.server_close();self.thread.join(timeout=2)
