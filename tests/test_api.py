from fastapi.testclient import TestClient
from main import app
client=TestClient(app)
def test_health():
    r=client.get('/api/health'); assert r.status_code==200 and r.json()['success']
def test_farm_and_zone():
    f=client.post('/api/farms',json={'name':'Test Farm','rows':2,'columns':2}).json()['farm']
    z=client.post('/api/zones',json={'farm_id':f['id'],'code':'Z1','row':0,'column':0,'crop':'Tomato'}).json()['zone']
    assert z['farm_id']==f['id']
    assert client.get(f"/api/farms/{f['id']}").status_code==200
