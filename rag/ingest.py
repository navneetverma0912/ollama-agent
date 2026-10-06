from pathlib import Path
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from config import settings

def load_documents():
    documents = []
    folder = Path(settings.documents_dir)
    folder.mkdir(parents=True, exist_ok=True)
    for path in folder.iterdir():
        if path.suffix.lower() == ".txt":
            documents.extend(TextLoader(str(path), encoding="utf-8").load())
        elif path.suffix.lower() == ".pdf":
            documents.extend(PyPDFLoader(str(path)).load())
    return documents

def main():
    documents = load_documents()
    if not documents:
        raise SystemExit(f"No .txt or .pdf documents found in {settings.documents_dir}")
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    chunks = splitter.split_documents(documents)
    embeddings = OllamaEmbeddings(model=settings.embedding_model, base_url=settings.ollama_base_url)
    Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=settings.chroma_dir)
    print(f"Loaded documents: {len(documents)}")
    print(f"Created chunks: {len(chunks)}")
    print(f"Chroma database: {settings.chroma_dir}")

if __name__ == "__main__":
    main()
