from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
# from langchain.chat_models import init_chat_model
# sk-248cb36807834c44a1b2b2104861a6e1

prompt_template = """
请阅读以下内容并简单回复：
{content}
"""

prompt = PromptTemplate.from_template(prompt_template)

llm = ChatOpenAI(
    api_key="sk-248cb36807834c44a1b2b2104861a6e1",
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    temperature=0.3,
    timeout=60,
    max_retries=2
)

# model = init_chat_model(
#     "claude-sonnet-4-5-20250929",
#     # Kwargs passed to the model:
#     temperature=0.7,
#     timeout=30,
#     max_tokens=1000,
# )

# chain = prompt | llm

print("分析链构建完成，开始分析内容...")

result = (prompt | llm).invoke({"content": "你是谁？"})

print(result.content)