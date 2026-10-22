import http.cookiejar
import http.client
import io
import importlib.util
import json
import os
import sqlite3
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
import uuid
from pathlib import Path

spec=importlib.util.spec_from_file_location('forma_server',Path(__file__).resolve().parents[1]/'server.py')
server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)

class InProcessSocket:
 """Exercise the actual HTTP handler without opening a network port."""
 def __init__(self,request): self.input=io.BytesIO(request);self.output=io.BytesIO()
 def makefile(self,*args,**kwargs): return self.input
 def sendall(self,data): self.output.write(data)

class Client:
 def __init__(self): self.cookie=''
 def open(self,request):
  if isinstance(request,str): request=urllib.request.Request(request)
  parsed=urllib.parse.urlsplit(request.full_url)
  target=parsed.path+('?' + parsed.query if parsed.query else '')
  body=request.data or b''
  headers={**dict(request.header_items()),'Host':'127.0.0.1:8765','Connection':'close'}
  if body: headers['Content-Length']=str(len(body))
  if self.cookie: headers['Cookie']=self.cookie
  raw=(request.get_method()+' '+target+' HTTP/1.1\r\n'+''.join(k+': '+v+'\r\n' for k,v in headers.items())+'\r\n').encode()+body
  sock=InProcessSocket(raw);server.Handler(sock,('127.0.0.1',54321),None)
  response=http.client.HTTPResponse(InProcessSocket(sock.output.getvalue()));response.begin()
  if response.getheader('Set-Cookie'): self.cookie=response.getheader('Set-Cookie').split(';')[0]
  if response.status>=400: raise urllib.error.HTTPError(request.full_url,response.status,'',response.headers,io.BytesIO(response.read()))
  response.status=response.status
  return response

class FormaIntegration(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();server.DATA=Path(cls.temp.name);server.initialize()
  cls.origin='http://127.0.0.1:8765'
 @classmethod
 def tearDownClass(cls): cls.temp.cleanup()
 def client(self): return Client()
 def req(self,client,path,data=None,headers=None):
  req=urllib.request.Request(self.origin+'/api/'+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json',**(headers or {})})
  try:
   with client.open(req) as res: return res.status,json.load(res)
  except urllib.error.HTTPError as e: return e.code,json.load(e)
 def account(self,name):
  c=self.client();status,_=self.req(c,'register',{'email':str(uuid.uuid4())+'@example.cz','password':'correct-horse-battery','name':name});self.assertEqual(status,200);return c
 def test_complete_workflow_and_privacy(self):
  a,b=self.account('Karel'),self.account('Kamarád')
  self.assertEqual(self.req(self.client(),'state')[0],401)
  self.assertEqual(self.req(a,'template',{})[0],200)
  sa=self.req(a,'state')[1];self.assertEqual(len(sa['exercises']),20);self.assertEqual(len(sa['sets']),0)
  self.assertEqual(len(self.req(b,'state')[1]['exercises']),0)
  e=sa['exercises'][0];wid=str(uuid.uuid4())
  self.assertEqual(self.req(a,'workout',{'id':wid,'name':'Upper'})[0],200)
  payload={'id':str(uuid.uuid4()),'exercise_id':e['id'],'workout_id':wid,'weight':105,'extra':0,'reps':8}
  self.assertEqual(self.req(a,'set',payload)[0],200)
  self.assertEqual(self.req(a,'set',payload)[0],200)
  self.assertEqual(len(self.req(a,'state')[1]['sets']),1)
  stolen={**payload,'id':str(uuid.uuid4())}
  self.assertEqual(self.req(b,'set',stolen)[0],409)
  self.assertEqual(self.req(a,'settings',{'share':True})[0],200)
  self.assertEqual(self.req(a,'workout/finish',{'id':wid,'shared':True})[0],200)
  self.assertEqual(self.req(a,'set',payload)[0],200) # replay after finishing is safe
  self.assertEqual(self.req(a,'set',{**payload,'id':str(uuid.uuid4())})[0],409)
  self.assertEqual(self.req(b,'community')[1]['feed'],[])
  self.assertEqual(self.req(b,'friend',{'code':sa['user']['code']})[0],200)
  community=self.req(b,'community')[1];self.assertEqual(len(community['feed']),1)
  self.assertNotIn('email',community['friends'][0]);self.assertEqual(community['feed'][0]['sets'][0]['weight'],105)
  self.assertEqual(self.req(b,'comment',{'workout_id':wid,'text':'Dobrá práce!'})[0],200)
  self.assertEqual(self.req(b,'reaction',{'workout_id':wid})[0],200)
  self.assertEqual(self.req(b,'community')[1]['feed'][0]['likes'],1)
  self.assertEqual(self.req(a,'settings',{'share':False})[0],200)
  self.assertEqual(self.req(b,'community')[1]['feed'],[])
  self.assertEqual(self.req(b,'comment',{'workout_id':wid,'text':'Hidden'})[0],404)
  self.assertEqual(self.req(a,'challenge',{'title':'Tři tréninky spolu','target':3,'started':int(time.time())-3600,'ends':int(time.time())+86400})[0],200)
  challenge=self.req(b,'community')[1]['challenges'][0]
  self.assertEqual(challenge['members'][0]['count'],1) # aggregate opt-in; no private set details
  self.assertEqual(self.req(b,'challenge/join',{'id':challenge['id']})[0],200)
  self.assertEqual(len(self.req(a,'community')[1]['challenges'][0]['members']),2)
  self.assertEqual(self.req(b,'challenge/leave',{'id':challenge['id']})[0],200)
  self.assertEqual(len(self.req(a,'community')[1]['challenges'][0]['members']),1)
  meal={'id':str(uuid.uuid4()),'day':'2026-10-21','name':'Kuřecí a rýže','kcal':650,'protein':45,'carbs':70,'fat':20,'favorite':True}
  self.assertEqual(self.req(a,'meal',meal)[0],200)
  self.assertEqual(self.req(a,'meal',meal)[0],200)
  self.assertEqual(len(self.req(a,'state')[1]['meals']),1)
  self.assertEqual(self.req(b,'state')[1]['meals'],[])
  self.assertEqual(self.req(a,'water',{'day':'2026-10-21','ml':500})[0],200)
  self.assertEqual(self.req(a,'metric',{'day':'2026-10-21','weight':108,'waist':100})[0],200)
  export=self.req(a,'export')[1];self.assertEqual(export['water'][0]['ml'],500);self.assertEqual(len(export['metrics']),1)
  self.assertNotIn('password',export['user'])
  self.assertEqual(self.req(a,'account/delete',{'confirm':'SMAZAT'})[0],200)
  self.assertEqual(self.req(a,'state')[0],401)
  self.assertEqual(self.req(b,'community')[1]['friends'],[])
 def test_validation_and_csrf(self):
  a=self.account('Bezpečný účet')
  self.assertEqual(self.req(a,'settings',{'kcal':float('nan')})[0],400)
  self.assertEqual(self.req(a,'water',{'day':'not-a-date','ml':250})[0],400)
  self.assertEqual(self.req(a,'settings',{'share':True},{'Origin':'https://evil.example'})[0],403)
  os.environ['FORMA_PUBLIC_URL']='https://forma.example'
  try:
   self.assertEqual(self.req(a,'settings',{'share':True},{'Origin':'http://127.0.0.1:8765'})[0],403)
   self.assertEqual(self.req(a,'settings',{'share':True},{'Origin':'https://forma.example'})[0],200)
  finally: os.environ.pop('FORMA_PUBLIC_URL',None)
  self.assertEqual(self.req(a,'exercise',{'name':"Bench '); DROP TABLE users;--",'plan':'Test'})[0],200)
  self.assertEqual(self.req(a,'state')[0],200)
  self.assertEqual(self.req(a,'analyze',{'photo_id':str(uuid.uuid4())})[0],503)
 def test_workout_priority_and_exercise_order_are_owned_and_persisted(self):
  a,b=self.account('Plánovač'),self.account('Cizí plán')
  self.assertEqual(self.req(a,'template',{})[0],200)
  self.assertEqual(self.req(b,'template',{})[0],200)
  own=self.req(a,'state')[1]['exercises']
  foreign=self.req(b,'state')[1]['exercises'][0]
  upper=[e['id'] for e in own if e['plan']=='Upper'][:3]
  wid=str(uuid.uuid4())
  status,workout=self.req(a,'workout',{'id':wid,'name':'Upper','priority':'back','exercise_order':upper})
  self.assertEqual(status,200)
  self.assertEqual(workout['priority'],'back')
  self.assertEqual(workout['exercise_order'],upper)
  saved=next(w for w in self.req(a,'state')[1]['workouts'] if w['id']==wid)
  self.assertEqual(saved['priority'],'back')
  self.assertEqual(saved['exercise_order'],upper)
  self.assertEqual(self.req(a,'workout',{'id':str(uuid.uuid4()),'name':'Upper','priority':'unknown','exercise_order':upper})[0],400)
  self.assertEqual(self.req(a,'workout',{'id':str(uuid.uuid4()),'name':'Upper','priority':'chest','exercise_order':[foreign['id']]})[0],404)
  lower=next(e['id'] for e in own if e['plan']=='Lower')
  self.assertEqual(self.req(a,'workout',{'id':str(uuid.uuid4()),'name':'Upper','priority':'chest','exercise_order':[lower]})[0],400)
  self.assertEqual(self.req(a,'workout',{'id':str(uuid.uuid4()),'name':'Upper','priority':'chest','exercise_order':[upper[0],upper[0]]})[0],400)
 def test_private_photos(self):
  a,b=self.account('Foto'),self.account('Cizí')
  boundary='forma-boundary';image=b'\xff\xd8\xff'+b'fake-test-jpeg'
  body=('--'+boundary+'\r\nContent-Disposition: form-data; name="file"; filename="test.jpg"\r\nContent-Type: image/jpeg\r\n\r\n').encode()+image+('\r\n--'+boundary+'--\r\n').encode()
  req=urllib.request.Request(self.origin+'/api/photo',body,{'Content-Type':'multipart/form-data; boundary='+boundary})
  with a.open(req) as response: photo=json.load(response)['id']
  with a.open(self.origin+'/api/photo/'+photo) as response: self.assertEqual(response.read(),image)
  self.assertEqual(self.req(b,'photo/'+photo)[0],404)
  self.assertEqual(self.req(b,'meal',{'day':'2026-10-21','name':'Cizí fotka','kcal':1,'photo_id':photo})[0],404)

class SchemaMigration(unittest.TestCase):
 def test_initialize_adds_planner_columns_to_v1_database(self):
  original=server.DATA
  with tempfile.TemporaryDirectory() as folder:
   server.DATA=Path(folder)
   with sqlite3.connect(str(server.DATA/'forma.sqlite3')) as con:
    con.execute('CREATE TABLE workouts(id TEXT PRIMARY KEY,user_id TEXT NOT NULL,name TEXT NOT NULL,started INTEGER NOT NULL,ended INTEGER,shared INTEGER NOT NULL DEFAULT 0)')
   server.initialize()
   with server.db() as con:
    columns={row['name'] for row in con.execute('PRAGMA table_info(workouts)')}
   self.assertIn('priority',columns)
   self.assertIn('exercise_order',columns)
  server.DATA=original

if __name__=='__main__': unittest.main()
