import axios from "axios"; const api=axios.create({baseURL:"http://127.0.0.1:8000"});
export const sendMessage=async(message,thread_id,employee_id="EMP001")=>(await api.post("/api/chat",{message,thread_id,employee_id})).data;
export const approveRequest=async(thread_id,approved,employee_id="EMP001")=>(await api.post("/api/approval",{thread_id,approved,employee_id})).data;
export const getChats=async(employee_id="EMP001")=>(await api.get("/api/chats",{params:{employee_id}})).data;
export const getChatHistory=async(thread_id,employee_id="EMP001")=>(await api.get(`/api/chats/${thread_id}`,{params:{employee_id}})).data;
export const getEmployee=async(id="EMP001")=>(await api.get(`/api/employee/${id}`)).data;
export const getLeaveBalance=async(id="EMP001")=>(await api.get(`/api/leave-balance/${id}`)).data;