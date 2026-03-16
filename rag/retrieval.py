from pathlib import Path
from langchain_community.retrievers import BM25Retriever
import pickle

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHUNKS_PATH = PROJECT_ROOT / "vector_store" / "chunks.pkl"
TOP_K = 3


def load_retriever() -> BM25Retriever:
    """Load serialized chunks and build a BM25 retriever."""
    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)
    return BM25Retriever.from_documents(chunks, k=TOP_K)


def retrieve_context(question: str) -> str:
    """
    Retrieve the most relevant document chunks for a given user question.

    Performs a BM25 keyword search against the document chunks and joins
    the matching chunks into a single context string ready to be injected
    into an LLM prompt.

    Parameters
    ----------
    question : str
        The user's natural-language question.

    Returns
    -------
    str
        Concatenated text from the top-K most relevant document chunks,
        separated by blank lines. Returns an empty string if nothing is found.
    """
    retriever = load_retriever()
    docs = retriever.invoke(question)
    return "\n\n".join(doc.page_content for doc in docs)