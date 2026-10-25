import base64
import json
import sqlite3
from urllib.request import urlopen
from urllib.error import HTTPError
import pytest
from app.offline import TilePackage,OfflineServer
from app.national import build_database,SwedenData,SwedenServer
from app.routing import calculate

PNG=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')
@pytest.fixture
def tiles(tmp_path):
    path=tmp_path/'map.mbtiles'
    with sqlite3.connect(path) as db:
        db.executescript('CREATE TABLE metadata(name TEXT,value TEXT); CREATE TABLE tiles(zoom_level INTEGER,tile_column INTEGER,tile_row INTEGER,tile_data BLOB);')
        db.executemany('INSERT INTO metadata VALUES (?,?)',[('format','png'),('bounds','10,55,25,70')])
        db.execute('INSERT INTO tiles VALUES (1,1,0,?)',(PNG,))
    return path

def test_raster_tiles_tms_and_http(tiles):
    p=TilePackage(tiles);assert p.tile(1,1,1)==PNG;assert p.tile(1,1,0) is None
    server=OfflineServer(tiles)
    try:
        url=server.config()['url'].format(z=1,x=1,y=1)
        with urlopen(url) as response:assert response.read()==PNG
        with pytest.raises(HTTPError):urlopen(url.replace('/1/1/1','/1/1/0'))
    finally:server.close()

def test_vector_mbtiles_rejected(tiles):
    with sqlite3.connect(tiles) as db:db.execute("UPDATE metadata SET value='pbf' WHERE name='format'")
    with pytest.raises(ValueError,match='Vektor'):TilePackage(tiles)

@pytest.fixture
def national(tmp_path):
    # Syntetisk OSM-fixtur, inte verkliga Sverigedata.
    source=tmp_path/'fixture.osm';dest=tmp_path/'sweden.sqlite'
    source.write_text('''<?xml version="1.0"?><osm version="0.6">
    <node id="1" lat="59.330" lon="18.060"/><node id="2" lat="59.330" lon="18.061"/><node id="3" lat="59.331" lon="18.061"/>
    <way id="10"><nd ref="1"/><nd ref="2"/><tag k="highway" v="residential"/><tag k="oneway" v="yes"/><tag k="oneway:bicycle" v="no"/><tag k="name" v="Testvägen"/></way>
    <way id="11"><nd ref="2"/><nd ref="3"/><tag k="highway" v="cycleway"/></way></osm>''',encoding='utf-8')
    build_database(source,dest)
    return dest

def test_pbf_pipeline_map_and_routing_without_network(national):
    d=SwedenData(national);bbox=[18,59,19,60]
    data=d.features(bbox,14);assert len(data['features'])==2
    graph=d.graph([[59.330,18.060],[59.331,18.061]])
    r=calculate(graph,[[59.330,18.060],[59.331,18.061]])
    assert 150<r['meters']<200
    assert calculate(graph,[[59.330,18.061],[59.330,18.060]])['meters']>0
    server=SwedenServer(national)
    try:
        with urlopen(server.config()['url']+'?bbox=18,59,19,60&zoom=14') as response:
            assert len(json.load(response)['features'])==2
    finally:server.close()

def test_failed_import_retains_previous(national,tmp_path):
    old=national.read_bytes();broken=tmp_path/'broken.osm';broken.write_text('not an OSM file')
    with pytest.raises(Exception):build_database(broken,national)
    assert national.read_bytes()==old
    assert not national.with_suffix('.building.sqlite').exists()

def test_regions_cached_separately(tmp_path):
    from app.services import MapData
    d=MapData(tmp_path);d.select_region('Stockholms kommun');stockholm=d.path
    d.select_region('Malmö kommun');assert d.path!=stockholm
    d.select_region('Stockholms kommun');assert d.path==stockholm

def test_bad_checksum_keeps_previous_download(tmp_path,monkeypatch):
    import requests
    import app.national as mod
    from types import SimpleNamespace
    old=tmp_path/'sweden.osm.pbf';old.write_bytes(b'old verified data')
    class Response:
        text='0'*32+' file';headers={}
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def raise_for_status(self):pass
        def iter_content(self,*args):yield b'bad download'
    monkeypatch.setattr(requests,'get',lambda *args,**kwargs:Response())
    monkeypatch.setattr(mod.shutil,'disk_usage',lambda path:SimpleNamespace(free=10**11))
    with pytest.raises(ValueError,match='Kontrollsumman'):mod.download_sweden(tmp_path)
    assert old.read_bytes()==b'old verified data'
    assert not (tmp_path/'sweden.osm.pbf.part').exists()

def test_directional_bicycle_ban(national):
    import networkx as nx
    with sqlite3.connect(national) as db:
        tags=json.loads(db.execute('SELECT tags FROM ways WHERE id=10').fetchone()[0]);tags['bicycle:backward']='no'
        db.execute('UPDATE ways SET tags=? WHERE id=10',(json.dumps(tags),))
    graph=SwedenData(national).graph([[59.330,18.060],[59.330,18.061]])
    with pytest.raises(nx.NetworkXNoPath):calculate(graph,[[59.330,18.061],[59.330,18.060]])

def test_cancel_import_keeps_previous(national,tmp_path):
    before=national.read_bytes()
    def cancel(message):raise ValueError('Avbruten')
    with pytest.raises(ValueError,match='Avbruten'):build_database(tmp_path/'unused.osm',national,cancel)
    assert national.read_bytes()==before
