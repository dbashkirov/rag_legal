import llama_index
from llama_index.core import (
    VectorStoreIndex,
    Settings,
    PromptTemplate,
    get_response_synthesizer,
)

# from llama_index.core.evaluation import ResponseEvaluator
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import logging
import openai
from src.constants import qa_prompt_tmpl_str, refine_prompt_tmpl_str, context_tmpl_str
from src.utils import messages_to_prompt, completion_to_prompt

logger = logging.getLogger(__name__)

embed_model = HuggingFaceEmbedding("intfloat/multilingual-e5-base", device="cuda")

llm = OpenAI(
    model="gpt-4o",
)


class Prompt(BaseModel):
    text: str


Settings.llm = llm
Settings.embed_model = embed_model


qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)
refine_prompt_tmpl = PromptTemplate(refine_prompt_tmpl_str)

db_law = chromadb.PersistentClient(path="chroma_db_law_test")
chroma_collection = db_law.get_or_create_collection("quickstart")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
law_index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)

law_chat_engine = law_index.as_chat_engine(
    chat_mode="context", context_template=context_tmpl_str, similarity_top_k=5
)

app = FastAPI()


@app.get("/health")
async def health():
    await {"status": "OK"}


@app.post("/saiga_law")
async def saiga_law(prompt: Prompt):
    print(prompt.text)
    logger.info("Starting generation")
    response = law_chat_engine.stream_chat(prompt.text)
    return StreamingResponse(response.response_gen)


@app.get("/source_law")
async def source(prompt: Prompt):
    logger.info("Starting retrieving")
    response = law_chat_engine.stream_chat(prompt.text)
    return [
        {"filename": node.metadata["file_name"], "text": node.text, "score": node.score}
        for node in response.source_nodes
    ]
