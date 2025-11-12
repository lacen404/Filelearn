# Filelearn
## 对上传的文件进行理解，文件主要是上传的综合题作业答案
1. 目前只做了.py文件的上传理解
2. 后续还要完成jpg\png、txt、pdf格式的文档理解
3. 大模型的回答目前使用的是非流式回答，后续还要做流式的回答
4. 还需要封装成API接口

## 使用步骤：
1. 安装依赖库
   pip install -U langchain langchain-core langchain-openai langchain-community langchain-text-splitters dotenv
3. 在根目录/Filelearn下运行
   python llm_analyzer.py sample.py
