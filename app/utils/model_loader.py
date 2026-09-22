import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")

llm=ChatGroq(model="qwen/qwen3.6-27b")
business_analyst_llm = ChatGroq(model="qwen/qwen3.6-27b")
product_owner_llm = ChatGroq(model="openai/gpt-oss-20b")
system_designer_llm = ChatGroq(model="qwen/qwen3.8-27b")
business_analyst_llm = ChatGroq(model="openai/gpt-oss-20b")
technical_analyst_llm = ChatGroq(model="qwen/qwen3.6-27b")
business_analyst_llm = ChatGroq(model="qwen/qwen3.8-27b")
technical_architect_llm = ChatGroq(model="qwen/qwen3.8-27b")
software_developer1_llm = ChatGroq(model="openai/gpt-oss-20b")
software_developer2_llm = ChatGroq(model="qwen/qwen3.8-27b")
software_lead_llm = ChatGroq(model="openai/gpt-oss-20b")
security_engineer_llm = ChatGroq(model="qwen/qwen3.8-27b")
qa_engineer_llm = ChatGroq(model="openai/gpt-oss-20b")
qa_reviewer_llm = ChatGroq(model="qwen/qwen3.8-27b")
qa_lead_llm = ChatGroq(model="openai/gpt-oss-20b")

