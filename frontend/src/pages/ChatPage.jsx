import {useEffect,useState} from "react";
import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";
import ApprovalCard from "../components/ApprovalCard";
import {sendMessage,approveRequest,getChats,getChatHistory} from "../api/chat";

const EMPLOYEE_ID="EMP001";

export default function ChatPage(){
  const[messages,setMessages]=useState([]),[tid,setTid]=useState(null),[approval,setApproval]=useState(null),[loading,setLoading]=useState(false),[chats,setChats]=useState([]),[historyError,setHistoryError]=useState("");
  async function refreshChats(){
    try{setChats(await getChats(EMPLOYEE_ID));setHistoryError("")}
    catch{setHistoryError("Could not load saved chats.")}
  }
  useEffect(()=>{refreshChats()},[]);

  function startNewChat(){setTid(null);setMessages([]);setApproval(null)}

  async function openChat(threadId){
    setLoading(true);
    try{
      const data=await getChatHistory(threadId,EMPLOYEE_ID);
      setTid(threadId);
      setMessages(data.messages.map(message=>({role:message.role,content:message.message})));
      setApproval(null);
    }catch(e){setHistoryError(e.response?.data?.detail||"Could not open this chat.")}
    finally{setLoading(false)}
  }

  async function send(text){
    setMessages(x=>[...x,{role:"user",content:text}]);setLoading(true);
    try{
      const d=await sendMessage(text,tid,EMPLOYEE_ID);
      setTid(d.thread_id);
      setMessages(x=>[...x,{role:"assistant",content:d.answer}]);
      if(d.status==="approval_required")setApproval(d.approval);
      await refreshChats();
    }catch(e){setMessages(x=>[...x,{role:"assistant",content:e.response?.data?.detail||"Backend connection failed."}]);await refreshChats()}
    finally{setLoading(false)}
  }

  async function decide(ok){
    setLoading(true);
    try{
      const d=await approveRequest(tid,ok,EMPLOYEE_ID);
      setApproval(null);
      setMessages(x=>[...x,{role:"assistant",content:d.answer||"Request completed."}]);
      await refreshChats();
    }catch(e){setMessages(x=>[...x,{role:"assistant",content:e.response?.data?.detail||"Approval failed."}])}
    finally{setLoading(false)}
  }

  return <section><header><div><h1>Employee Service Assistant</h1><p>Ask questions and complete employee service requests.</p></div><label>● Online</label></header><div className="chat-layout"><div className="card"><ChatWindow messages={messages} loading={loading}/>{approval&&<ApprovalCard approval={approval} onDecision={decide} loading={loading}/>}<ChatInput onSend={send} disabled={loading}/></div><aside className="chat-sidebar"><button className="new-chat" onClick={startNewChat} disabled={loading}>＋ New chat</button><h2>Saved chats</h2>{historyError&&<p className="history-error">{historyError}</p>}{!chats.length&&!historyError&&<p className="history-empty">Your chats will appear here.</p>}<div className="chat-list">{chats.map(chat=><button key={chat.thread_id} className={"chat-list-item "+(tid===chat.thread_id?"selected":"")} onClick={()=>openChat(chat.thread_id)} disabled={loading} title={chat.title}>{chat.title}</button>)}</div></aside></div></section>
}