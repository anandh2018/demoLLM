from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from src.config import LLM_MODEL, LLM_TEMPERATURE, EMBEDDING_MODEL

load_dotenv()

llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
