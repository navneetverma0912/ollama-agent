from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings

_embeddings = OllamaEmbeddings(model=settings.embedding_model, base_url=settings.ollama_base_url)
_vectorstore = Chroma(persist_directory=settings.chroma_dir, embedding_function=_embeddings)
_retriever = _vectorstore.as_retriever(search_kwargs={"k": 3})

def search_policy(question: str):
    return _retriever.invoke(question)

def answer_from_context(question: str, context: str) -> str:
    llm = ChatOllama(model=settings.llm_model, base_url=settings.ollama_base_url, temperature=0)
    response = llm.invoke([
        SystemMessage(content=("Answer employee questions using ONLY the supplied company-policy context. "
                              "If the context does not contain the answer, say the information was not found. "
                              "Do not invent policy.")),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion:\n{question}"),
    ])
    return response.content
