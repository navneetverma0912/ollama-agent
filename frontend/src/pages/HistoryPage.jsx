import {useEffect,useState} from "react";
import {getChats,getChatHistory} from "../api/chat";

const EMPLOYEE_ID="EMP001";

export default function HistoryPage(){
  const[chats,setChats]=useState([]),[selected,setSelected]=useState(null),[messages,setMessages]=useState([]),[error,setError]=useState("");

  useEffect(()=>{
    getChats(EMPLOYEE_ID).then(setChats).catch(()=>setError("Could not load saved chats."));
  },[]);

  async function openChat(threadId){
    try{
      const data=await getChatHistory(threadId,EMPLOYEE_ID);
      setSelected(data.chat);
      setMessages(data.messages);
      setError("");
    }catch(e){setError(e.response?.data?.detail||"Could not load this conversation.")}
  }

  return <section><h1>Conversation History</h1><p>Your saved conversations are stored in the database.</p>{error&&<p className="history-error">{error}</p>}<div className="history-layout"><div className="panel history-sessions"><h2>Saved chats</h2>{!chats.length&&!error&&<p className="history-empty">No saved conversations yet.</p>}{chats.map(chat=><button key={chat.thread_id} className={"chat-list-item "+(selected?.thread_id===chat.thread_id?"selected":"")} onClick={()=>openChat(chat.thread_id)}>{chat.title}</button>)}</div><div className="panel history-messages"><h2>{selected?.title||"Select a conversation"}</h2>{messages.map((message,index)=><div key={`${message.created_at}-${index}`} className={"msg "+message.role}><b>{message.role==="user"?"You":"AI"}</b><span>{message.message}</span></div>)}</div></div></section>
}
