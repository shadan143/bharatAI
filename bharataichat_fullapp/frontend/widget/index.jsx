import React, {useState} from 'react';
import {createRoot} from 'react-dom/client';

function App(){
  const [conv, setConv] = useState(null);
  const [text, setText] = useState('');
  const [msgs, setMsgs] = useState([]);
  async function send(){
    if(!text) return;
    const res = await fetch('http://localhost:8000/v1/messages',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({conversation_id:conv,text,lang:'hi'})});
    const j = await res.json();
    setConv(j.conversation_id);
    setMsgs(m=>[...m,{from:'user',text},{from:'bot',text:j.reply.text}]);
    setText('');
  }
  async function startStream(){
    if(!text) return;
    const url = new URL('http://localhost:8000/stream');
    url.searchParams.set('q', text);
    url.searchParams.set('lang', 'hi');
    const es = new EventSource(url);
    setMsgs(m=>[...m,{from:'user',text}]);
    setText('');
    es.onmessage = (ev)=>{
      try{ const data = JSON.parse(ev.data); const delta = data.delta; setMsgs(m=>[...m,{from:'bot',text: delta}]); }catch(e){}
    };
    es.onerror = (e)=>{ es.close(); }
  }

  return (<div style={{fontFamily:'Arial',width:360}}>
    <h3>BharatAI Chat (Full App Demo)</h3>
    <div style={{height:260,overflowY:'auto',border:'1px solid #ddd',padding:8}}>
      {msgs.map((m,i)=><div key={i} style={{textAlign:m.from==='user'?'right':'left'}}><b>{m.from}</b>: {m.text}</div>)}
    </div>
    <div style={{display:'flex',gap:8,marginTop:8}}>
      <input style={{flex:1,padding:8}} value={text} onChange={e=>setText(e.target.value)} placeholder="Type in Hindi or English"/>
      <button onClick={send}>Send</button><button onClick={startStream}>Stream</button>
    </div>
  </div>);
}

createRoot(document.getElementById('root')).render(<App/>);
