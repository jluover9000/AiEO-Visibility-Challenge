from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
import pickle

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "rag" / "docs"
CHUNKS_PATH = PROJECT_ROOT / "vector_store" / "chunks.pkl"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def load_documents(docs_dir: Path) -> list:
    """Load all .md files from docs_dir as LangChain Document objects."""
    loader = DirectoryLoader(
        str(docs_dir),
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
    )
    documents = loader.load()
    print(f"Loaded {len(documents)} document(s) from {docs_dir}")
    return documents


def split_documents(documents: list) -> list:
    """Split documents into smaller chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunk(s) (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks


def save_chunks(chunks: list, path: Path) -> None:
    """Serialize document chunks to disk for later use by the retriever."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(chunks, f)
    print(f"Chunks saved to {path}")


def main() -> None:
    documents = load_documents(DOCS_DIR)
    chunks = split_documents(documents)
    save_chunks(chunks, CHUNKS_PATH)
    print("Ingestion complete.")


if __name__ == "__main__":
    main()