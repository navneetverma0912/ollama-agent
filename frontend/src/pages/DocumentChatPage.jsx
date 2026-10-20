import {useRef,useState} from "react";
import {chatWithDocuments,uploadDocuments} from "../api/chat";

const WORKSPACE_STORAGE_KEY="employee-agent-document-workspace";

export default function DocumentChatPage(){
  const[knowledgeBaseId,setKnowledgeBaseId]=useState(()=>localStorage.getItem(WORKSPACE_STORAGE_KEY));
  const[files,setFiles]=useState([]);
  const[messages,setMessages]=useState([]);
  const[question,setQuestion]=useState("");
  const[busy,setBusy]=useState(false);
  const[error,setError]=useState("");
  const[notice,setNotice]=useState("");
  const fileInput=useRef(null);

  async function uploadSelectedFiles(){
    if(!files.length)return;
    setBusy(true);setError("");setNotice("");
    try{
      const result=await uploadDocuments(files,knowledgeBaseId);
      setKnowledgeBaseId(result.knowledge_base_id);
      localStorage.setItem(WORKSPACE_STORAGE_KEY,result.knowledge_base_id);
      setNotice(`Indexed ${result.files.length} file${result.files.length===1?"":"s"} into ${result.chunks} searchable sections.`);
      setFiles([]);
      if(fileInput.current)fileInput.current.value="";
    }catch(e){
      setError(e.response?.data?.detail||"Could not process the selected files.");
    }finally{setBusy(false)}
  }

  async function sendQuestion(event){
    event.preventDefault();
    const text=question.trim();
    if(!text||!knowledgeBaseId||busy)return;
    setQuestion("");setError("");setNotice("");
    setMessages(current=>[...current,{role:"user",content:text}]);
    setBusy(true);
    try{
      const history=messages.slice(-6).map(({role,content})=>({role,content}));
      const result=await chatWithDocuments(knowledgeBaseId,text,history);
      const sources=result.sources?.length?`\n\nSources: ${result.sources.join(", ")}`:"";
      setMessages(current=>[...current,{role:"assistant",content:`${result.answer}${sources}`}]);
    }catch(e){
      setMessages(current=>[...current,{role:"assistant",content:e.response?.data?.detail||"Could not answer from the uploaded documents."}]);
    }finally{setBusy(false)}
  }

  function startNewWorkspace(){
    localStorage.removeItem(WORKSPACE_STORAGE_KEY);
    setKnowledgeBaseId(null);setFiles([]);setMessages([]);setError("");setNotice("");
    if(fileInput.current)fileInput.current.value="";
  }

  return <section className="documents-page">
    <header><div><h1>Chat with your documents</h1><p>Upload PDFs or text files, then ask questions grounded in their contents.</p></div><label>● Isolated workspace</label></header>
    <div className="documents-layout">
      <section className="panel document-upload">
        <div className="document-section-heading"><div><span className="document-step">1</span><h2>Add your files</h2></div>{knowledgeBaseId&&<button className="text-button" onClick={startNewWorkspace} disabled={busy}>New workspace</button>}</div>
        <p className="muted">Supported formats: PDF and TXT. Up to 10 files, 10 MB each.</p>
        <label className="file-dropzone">
          <span className="upload-icon" aria-hidden="true">↑</span>
          <strong>Select documents to upload</strong>
          <span>Choose one or more PDF or TXT files</span>
          <input ref={fileInput} type="file" accept=".pdf,.txt,application/pdf,text/plain" multiple onChange={event=>setFiles(Array.from(event.target.files||[]))}/>
        </label>
        {!!files.length&&<div className="selected-files" aria-live="polite">{files.map((file,index)=><div key={`${file.name}-${index}`}><span>📄 {file.name}</span><small>{(file.size/1024/1024).toFixed(2)} MB</small></div>)}</div>}
        <button className="primary-button upload-button" onClick={uploadSelectedFiles} disabled={!files.length||busy}>{busy?"Processing…":"Upload and index files"}</button>
        {notice&&<p className="success-message" role="status">{notice}</p>}
        {error&&<p className="error-message" role="alert">{error}</p>}
        {knowledgeBaseId&&<p className="workspace-ready" role="status"><span/> Documents are ready for questions</p>}
      </section>
      <section className="panel document-chat-panel">
        <div className="document-section-heading"><div><span className="document-step">2</span><h2>Ask questions</h2></div></div>
        <div className="document-messages" aria-live="polite">
          {!messages.length&&<div className="document-welcome"><span aria-hidden="true">✦</span><h3>Your document assistant</h3><p>{knowledgeBaseId?"Ask a question about the files in this workspace.":"Upload and index files first to start a grounded conversation."}</p></div>}
          {messages.map((message,index)=><div key={index} className={`document-message ${message.role}`}><b>{message.role==="user"?"You":"AI"}</b><span>{message.content}</span></div>)}
          {busy&&knowledgeBaseId&&<div className="document-message assistant"><b>AI</b><span>Searching your documents…</span></div>}
        </div>
        <form className="document-question-form" onSubmit={sendQuestion}>
          <input value={question} onChange={event=>setQuestion(event.target.value)} placeholder={knowledgeBaseId?"Ask something about your documents…":"Upload files to begin"} maxLength={1000} disabled={!knowledgeBaseId||busy}/>
          <button className="primary-button" type="submit" disabled={!knowledgeBaseId||!question.trim()||busy}>Send</button>
        </form>
      </section>
    </div>
  </section>
}
