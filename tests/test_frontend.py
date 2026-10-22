"""Syntax and pure frontend logic in JavaScriptCore; no browser/network used."""
import ctypes
import json
import sys
import unittest
from pathlib import Path

@unittest.skipUnless(sys.platform=='darwin','JavaScriptCore syntax harness requires macOS; use a JS engine on other hosts')
class FrontendLogic(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.js=ctypes.CDLL('/System/Library/Frameworks/JavaScriptCore.framework/JavaScriptCore')
  signatures={
   'JSGlobalContextCreate':(ctypes.c_void_p,[ctypes.c_void_p]),
   'JSStringCreateWithUTF8CString':(ctypes.c_void_p,[ctypes.c_char_p]),
   'JSCheckScriptSyntax':(ctypes.c_bool,[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_void_p)]),
   'JSEvaluateScript':(ctypes.c_void_p,[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_void_p)]),
   'JSValueToStringCopy':(ctypes.c_void_p,[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p]),
   'JSStringGetUTF8CString':(ctypes.c_size_t,[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t]),
   'JSStringRelease':(None,[ctypes.c_void_p]),
   'JSGlobalContextRelease':(None,[ctypes.c_void_p]),
  }
  for name,(ret,args) in signatures.items():
   fn=getattr(cls.js,name);fn.restype=ret;fn.argtypes=args
  cls.public=Path(__file__).resolve().parents[1]/'public'
 def string(self,value,ctx):
  ref=self.js.JSValueToStringCopy(ctx,value,None);buffer=ctypes.create_string_buffer(50000)
  self.js.JSStringGetUTF8CString(ref,buffer,len(buffer));self.js.JSStringRelease(ref)
  return buffer.value.decode()
 def evaluate(self,script):
  ctx=self.js.JSGlobalContextCreate(None);ref=self.js.JSStringCreateWithUTF8CString(script.encode());error=ctypes.c_void_p()
  value=self.js.JSEvaluateScript(ctx,ref,None,None,1,ctypes.byref(error));self.js.JSStringRelease(ref)
  try:
   if error.value: raise AssertionError(self.string(error,ctx))
   return self.string(value,ctx)
  finally:self.js.JSGlobalContextRelease(ctx)
 def test_script_syntax(self):
  for filename in ('planner.js','app.js','sw.js'):
   ctx=self.js.JSGlobalContextCreate(None);ref=self.js.JSStringCreateWithUTF8CString((self.public/filename).read_bytes());err=ctypes.c_void_p()
   self.assertTrue(self.js.JSCheckScriptSyntax(ctx,ref,None,1,ctypes.byref(err)),filename)
   self.js.JSStringRelease(ref);self.js.JSGlobalContextRelease(ctx)
 def test_rendering_and_owned_offline_queue(self):
  source=(self.public/'planner.js').read_text()+'\n'+(self.public/'app.js').read_text().rsplit('(async()=>{',1)[0]
  harness="""
const fakeNode={innerHTML:'',textContent:'',classList:{add(){},remove(){}},querySelector(){return null;}};
const document={querySelector(){return fakeNode;},querySelectorAll(){return [];},addEventListener(){}};
const window={addEventListener(){}};const navigator={};
const setInterval=()=>0;const setTimeout=()=>0;const clearTimeout=()=>{};
const storage=new Map();const localStorage={getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)};
"""
  fixture={'user':{'id':'user-a','name':'<script>alert(1)</script>','email':'test@example.cz','code':'example-code','settings':{'kcal':2350,'protein':170,'carbs':260,'fat':70,'water':2500,'weekly':3,'rest':120,'gamification':True,'share':False}},'workouts':[],'exercises':[],'sets':[],'meals':[],'water':[],'metrics':[]}
  script=harness+source+'\nstate='+json.dumps(fixture)+';community={friends:[],feed:[],challenges:[]};'+"""
const pages=[renderHome(),renderTrain(),renderFood(),renderFriends(),renderProfile()];
localStorage.setItem('forma-queue-user-b',JSON.stringify([{id:'private-other',exercise_id:'e'}]));
const otherInvisible=allSets().length===0;
localStorage.setItem('forma-queue-user-a',JSON.stringify([{id:'own',exercise_id:'e',weight:92,extra:30,reps:8}]));
JSON.stringify({pages:pages.map(p=>p.length>100),escaped:!pages[0].includes('<script>'),otherInvisible,own:allSets().length,total:totalWeight(allSets()[0]),stack:performance({reps:15},{mode:'stack'})});
"""
  result=json.loads(self.evaluate(script))
  self.assertTrue(all(result['pages']));self.assertTrue(result['escaped']);self.assertTrue(result['otherInvisible'])
  self.assertEqual(result['own'],1);self.assertEqual(result['total'],122);self.assertIn('zásobník',result['stack'])

if __name__=='__main__':unittest.main()
