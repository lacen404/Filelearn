# llm_analyzer.py

# pip install dotenv
# pip install -U langchain langchain-core langchain-openai langchain-community
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
from dotenv import load_dotenv
import os
import traceback
import json
import time

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from document_parser import read_document
import sys

def debug_env_variables():
    """调试环境变量设置"""
    logger.debug("=" * 50)
    logger.debug("环境变量调试信息")
    logger.debug("=" * 50)
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL")
    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    logger.debug(f"DEEPSEEK_API_KEY: {'***' + api_key[-4:] if api_key and len(api_key) > 4 else '未设置或过短'}")
    logger.debug(f"DEEPSEEK_BASE_URL: {base_url}")
    logger.debug(f"DEEPSEEK_MODEL: {model_name}")
    logger.debug(f"DEBUG模式: {os.getenv('DEBUG', 'False')}")
    
    # 检查必要的环境变量
    if not api_key:
        logger.error("❌ DEEPSEEK_API_KEY 环境变量未设置！")
    if not base_url:
        logger.warning("⚠️  DEEPSEEK_BASE_URL 环境变量未设置，将使用默认值")
    
    logger.debug("=" * 50)

def build_analysis_chain():
    """构建分析链，包含详细的调试信息"""
    start_time = time.time()
    logger.debug("开始构建分析链...")
    
    api_key = os.getenv("DEEPSEEK_API_KEY","sk-fb1aad5eb1234dc3baeeae64a4bf426c")
    base_url = os.getenv("DEEPSEEK_BASE_URL")
    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    logger.debug(f"LLM配置参数:")
    logger.debug(f"  - model: {model_name}")
    logger.debug(f"  - base_url: {base_url}")
    logger.debug(f"  - api_key: {'已设置' if api_key else '未设置'}")

    # 定义提示词模板
    prompt_template = """
你是一位评审专家，请阅读以下内容并从逻辑和正确性进行分析。不要胡说，要严谨认真。
输出 JSON 格式的结论，包含以下字段：
- "logical_analysis": 逻辑分析
- "correctness_evaluation": 正确性评价
- "overall_score": 总体评分(1-10分)
- "suggestions": 改进建议

内容如下：
{content}

请只返回JSON格式的结果，不要有其他文字。
"""
    
    try:
        prompt = PromptTemplate.from_template(prompt_template)
        logger.debug("✅ 提示词模板创建成功")
        logger.debug(f"提示词模板预览: {prompt_template[:100]}...")
    except Exception as e:
        logger.error(f"❌ 提示词模板创建失败: {e}")
        raise

    try:
        llm = ChatOpenAI(
            # api_key=api_key,
            # base_url=base_url,
            # model=model_name,
            # temperature=0.3,
            # timeout=60,  # 增加超时时间
            # max_retries=2  # 增加重试次数
            api_key="sk-248cb36807834c44a1b2b2104861a6e1",
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
            temperature=0.3,
            timeout=60,
            max_retries=2
        )
        logger.debug("✅ LLM客户端创建成功")
        logger.debug(f"LLM参数: temperature=0.3, timeout=60, max_retries=2")
    except Exception as e:
        logger.error(f"❌ LLM客户端创建失败: {e}")
        raise

    # 构建处理链
    try:
        chain = prompt | llm
        build_time = time.time() - start_time
        logger.debug(f"✅ 分析链构建完成，耗时: {build_time:.2f}秒")
        return chain
    except Exception as e:
        logger.error(f"❌ 分析链构建失败: {e}")
        raise

def analyze_content(content: str):
    """分析内容，包含详细的调试信息"""
    start_time = time.time()
    logger.debug("开始分析内容...")
    
    # 内容预处理调试
    logger.debug(f"输入内容统计:")
    logger.debug(f"  - 字符数: {len(content)}")
    logger.debug(f"  - 行数: {content.count(chr(10)) + 1}")
    logger.debug(f"  - 内容预览: {content[:200]}...")
    
    if not content or len(content.strip()) == 0:
        logger.warning("⚠️  输入内容为空，跳过分析")
        return None
    
    try:
        # 构建分析链
        chain_build_start = time.time()
        chain = build_analysis_chain()
        chain_build_time = time.time() - chain_build_start
        logger.debug(f"分析链构建耗时: {chain_build_time:.2f}秒")
        
        # 执行分析
        logger.debug("开始调用LLM API...")
        invoke_start = time.time()

        print("内容长度:", len(content))

        
        result = chain.invoke({"content": content})
        
        invoke_time = time.time() - invoke_start
        logger.debug(f"LLM API调用耗时: {invoke_time:.2f}秒")
        
        if not result:
            logger.warning("⚠️  LLM返回结果为空")
            return None
        
        # 结果调试信息
        logger.debug("✅ LLM分析成功完成")
        logger.debug(f"返回结果类型: {type(result)}")
        
        # 尝试解析结果内容
        try:
            if hasattr(result, 'content'):
                content_str = result.content
                logger.debug(f"结果content属性长度: {len(content_str)}")
                
                # 尝试解析JSON
                try:
                    if content_str.strip().startswith('{'):
                        parsed_json = json.loads(content_str)
                        logger.debug("✅ 结果成功解析为JSON格式")
                        logger.debug(f"JSON键: {list(parsed_json.keys())}")
                    else:
                        logger.warning("⚠️  结果不是JSON格式，返回原始内容")
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️  结果不是有效的JSON格式: {e}")
            else:
                logger.debug(f"结果属性: {dir(result)}")
        except Exception as e:
            logger.debug(f"结果解析调试失败: {e}")
        
        total_time = time.time() - start_time
        logger.debug(f"分析总耗时: {total_time:.2f}秒")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 分析执行出错: {e}")
        logger.debug(f"错误详情: {traceback.format_exc()}")
        return None

def test_llm_connection():
    """测试LLM连接和基本功能"""
    logger.info("🧪 开始LLM连接测试...")
    
    try:
        # 使用简单的测试内容
        test_content = "这是一个测试文档。它包含一些基本内容用于验证LLM连接和分析功能。"
        
        chain = build_analysis_chain()
        logger.debug("✅ 连接测试 - 分析链构建成功")
        
        # 测试调用
        test_result = chain.invoke({"content": test_content})
        
        if test_result:
            logger.info("✅ LLM连接测试成功")
            if hasattr(test_result, 'content'):
                logger.debug(f"测试响应预览: {test_result.content[:100]}...")
            return True
        else:
            logger.error("❌ LLM连接测试失败 - 返回结果为空")
            return False
            
    except Exception as e:
        logger.error(f"❌ LLM连接测试失败: {e}")
        return False

def main():
    """主函数，包含增强的调试功能"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LLM 文档分析工具")
    parser.add_argument("file", nargs="?", default="test.docx", help="要分析的文件路径")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--test-connection", action="store_true", help="测试LLM连接")
    parser.add_argument("--show-env", action="store_true", help="显示环境变量信息")
    args = parser.parse_args()

    # 设置日志级别
    if args.debug or os.getenv("DEBUG") == "True":
        logger.setLevel(logging.DEBUG)
        logger.debug("🔧 调试模式已开启")
    
    # 显示环境变量信息
    if args.show_env:
        debug_env_variables()
    
    # 测试连接
    if args.test_connection:
        test_llm_connection()
        return

    file_path = args.file
    logger.info(f"📁 加载文件: {file_path}")

    # 文件存在性检查
    if not os.path.exists(file_path):
        logger.error(f"❌ 文件不存在: {file_path}")
        logger.debug(f"当前工作目录: {os.getcwd()}")
        logger.debug(f"目录列表: {os.listdir('.')}")
        return

    try:
        # 文档解析
        logger.debug("开始文档解析...")
        parse_start = time.time()
        docs = read_document(file_path)
        parse_time = time.time() - parse_start
        logger.debug(f"文档解析耗时: {parse_time:.2f}秒")
        
        if not docs:
            logger.warning("⚠️  文档解析结果为空，请检查文件格式或路径")
            return
        
        # 处理文档内容
        if hasattr(docs, '__iter__') and not isinstance(docs, str):
            content_parts = []
            for i, doc in enumerate(docs):
                if hasattr(doc, 'page_content'):
                    content_parts.append(doc.page_content)
                    logger.debug(f"文档块 {i+1}: {len(doc.page_content)} 字符")
                else:
                    content_parts.append(str(doc))
            content = "\n".join(content_parts)
        else:
            content = str(docs)
        
        logger.info(f"📊 文档内容统计: {len(content)} 字符, {content.count(chr(10)) + 1} 行")
        
        # 内容分析
        if len(content.strip()) == 0:
            logger.warning("⚠️  文档内容为空，跳过分析")
            return
            
        result = analyze_content(content)
        
        # 输出结果
        print("\n" + "=" * 60)
        print("分析结果：")
        print("=" * 60)
        
        if result:
            if hasattr(result, 'content'):
                # 尝试美化输出JSON
                content_str = result.content
                try:
                    # 尝试解析和美化JSON
                    if content_str.strip().startswith('{'):
                        parsed = json.loads(content_str)
                        print(json.dumps(parsed, indent=2, ensure_ascii=False))
                    else:
                        print(content_str)
                except json.JSONDecodeError:
                    print(content_str)
            else:
                print(result)
        else:
            print("❌ 分析失败，无结果返回")
            
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 执行出错: {e}")
        logger.debug(f"错误堆栈:\n{traceback.format_exc()}")

if __name__ == "__main__":
    start_time = time.time()
    logger.info(f"🚀 启动程序，传入参数: {sys.argv[1:]}")
    logger.debug(f"Python版本: {sys.version}")
    logger.debug(f"工作目录: {os.getcwd()}")
    
    main()
    
    total_time = time.time() - start_time
    logger.info(f"🏁 程序执行完成，总耗时: {total_time:.2f}秒")