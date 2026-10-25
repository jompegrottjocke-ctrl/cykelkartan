import json
import networkx as nx
import pytest
from app.routing import calculate, classify, allowed, minutes, export_route, MODES
from app.storage import Store

@pytest.fixture
def graph():
    g=nx.MultiDiGraph(crs='epsg:4326')
    for i in range(4):g.add_node(i,x=13+i*.001,y=55.6)
    for a,b in [(0,1),(1,2),(0,3),(3,2)]:g.add_edge(a,b,length=100 if b!=3 else 400,highway='cycleway')
    return g

def test_classification_and_bans():
    assert classify({'highway':'cycleway'})=='separat'
    assert classify({'highway':'path','foot':'designated','bicycle':'designated'})=='gemensam'
    assert classify({'cycleway:right':'lane'})=='fält'
    assert not allowed({'bicycle':'no'})
    assert not allowed({'highway':'elevator'})
    assert not allowed({'access':'private'})
    assert allowed({'access':'no','bicycle':'yes'})

def test_route_directed_and_forbidden(graph):
    r=calculate(graph,[[55.6,13],[55.6,13.002]])
    assert r['meters']==200
    assert r['coords'][0]==[55.6,13]
    with pytest.raises(nx.NetworkXNoPath):calculate(graph,[[55.6,13.002],[55.6,13]])
    graph[1][2][0]['bicycle']='no'
    assert calculate(graph,[[55.6,13],[55.6,13.002]])['meters']==500

@pytest.mark.parametrize('mode',MODES)
def test_modes(graph,mode):
    r=calculate(graph,[[55.6,13],[55.6,13.002]],mode)
    assert r['meters']==200

def test_speed():
    assert minutes(10000,20)==30
    with pytest.raises(ValueError):minutes(100,0)

def test_export(graph,tmp_path):
    r=calculate(graph,[[55.6,13],[55.6,13.002]])
    f=tmp_path/'r.geojson';export_route(r,f)
    assert json.loads(f.read_text())['geometry']['coordinates'][0]==[13,55.6]
    f=tmp_path/'r.gpx';export_route(r,f)
    from xml.etree import ElementTree as ET
    assert len(ET.parse(f).findall('.//{*}trkpt'))==3

def test_store(tmp_path):
    s=Store(tmp_path/'db.sqlite');s.set('speed',20);s.save('Test',{'points':[1,2]})
    other=Store(tmp_path/'db.sqlite');assert other.get('speed')==20
    row=other.saved()[0];assert row[1]=='Test';other.delete(row[0]);assert not other.saved()

def test_update_preserves_previous(tmp_path,monkeypatch,graph):
    from app.services import MapData
    import osmnx as ox
    d=MapData(tmp_path);ox.save_graphml(graph,d.path);before=d.path.read_bytes()
    monkeypatch.setattr(ox,'graph_from_place',lambda *a,**kw:nx.MultiDiGraph())
    with pytest.raises(ValueError):d.update()
    assert d.path.read_bytes()==before

def test_bicycle_oneway_exception(graph):
    graph[0][1][0]['oneway:bicycle']='no'
    r=calculate(graph,[[55.6,13.001],[55.6,13]])
    assert r['meters']==100

def test_signal_wait(graph):
    graph.nodes[1]['highway']='traffic_signals'
    r=calculate(graph,[[55.6,13],[55.6,13.002]],mode=MODES[1],wait=True)
    assert r['wait']==.35
