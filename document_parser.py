# document_parser.py
# 文档读取与预处理模块
# 依赖安装：
# pip install langchain langchain-community langchain-text-splitters
# document_parser.py
# 文档读取与预处理模块
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import logging
from typing import List, Optional

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_document(file_path: str) -> List:
    """
    读取文档内容
    
    Args:
        file_path: 文档文件路径
        
    Returns:
        str: 文档内容字符串
        
    Raises:
        ValueError: 不支持的文件类型
        FileNotFoundError: 文件不存在
        Exception: 其他读取错误
    """
    # 调试：检查文件是否存在
    if not os.path.exists(file_path):
        error_msg = f"文件不存在: {file_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    # 获取文件扩展名和文件大小
    ext = os.path.splitext(file_path)[-1].lower()
    file_size = os.path.getsize(file_path)
    
    logger.info(f"开始读取文件: {file_path}")
    logger.info(f"文件类型: {ext}, 文件大小: {file_size} 字节")
    
    try:
        if ext == ".pdf":
            logger.debug("使用 PyPDFLoader 读取 PDF 文件")
            loader = PyPDFLoader(file_path)
        elif ext in [".doc", ".docx"]:
            logger.debug("使用 Docx2txtLoader 读取 Word 文档")
            loader = Docx2txtLoader(file_path)
        elif ext in [".txt", ".py"]:
            logger.debug("使用 TextLoader 读取文本文件")
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            error_msg = f"不支持的文件类型: {ext}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # 加载文档
        logger.debug("开始加载文档内容...")
        docs = loader.load()
        # 文本分块
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
        splits = text_splitter.split_documents(docs)
        logger.info(f"拆分为 {len(splits)} 个子文档")
        return splits
        
    except Exception as e:
        error_msg = f"读取文件时发生错误: {str(e)}"
        logger.error(error_msg)
        raise

def read_document_with_metadata(file_path: str) -> dict:
    """
    读取文档内容并返回详细信息（用于调试）
    
    Args:
        file_path: 文档文件路径
        
    Returns:
        dict: 包含文档内容和元数据的字典
    """
    if not os.path.exists(file_path):
        return {"error": f"文件不存在: {file_path}"}
    
    ext = os.path.splitext(file_path)[-1].lower()
    
    try:
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext in [".doc", ".docx"]:
            loader = Docx2txtLoader(file_path)
        elif ext in [".txt", ".py"]:
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            return {"error": f"不支持的文件类型: {ext}"}
        
        docs = loader.load()
        # 文本分块
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
        splits = text_splitter.split_documents(docs)
        # 收集详细信息
        result = {
            "file_path": file_path,
            "file_type": ext,
            "file_size": os.path.getsize(file_path),
            "total_chunks": len(splits),
            "chunks": [],
            "total_content": "",
            "metadata": {},
            "documents": splits
        }
        contents = []
        for i, doc in enumerate(splits):
            chunk_info = {
                "chunk_id": i,
                "content_length": len(doc.page_content),
                "line_count": doc.page_content.count('\n') + 1,
                "metadata": doc.metadata,
                "content_preview": doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            }
            result["chunks"].append(chunk_info)
            contents.append(doc.page_content)
        result["total_content"] = "\n".join(contents)
        result["total_chars"] = len(result["total_content"])
        result["total_lines"] = result["total_content"].count('\n') + 1
        return result
        
    except Exception as e:
        return {"error": f"读取错误: {str(e)}"}

def test_file_readability(file_paths: List[str]) -> None:
    """
    测试多个文件的可读性
    
    Args:
        file_paths: 文件路径列表
    """
    logger.info("=" * 50)
    logger.info("开始文件可读性测试")
    logger.info("=" * 50)
    
    for file_path in file_paths:
        logger.info(f"\n测试文件: {file_path}")
        try:
            # 使用详细模式获取更多信息
            result = read_document_with_metadata(file_path)
            
            if "error" in result:
                logger.error(f"❌ 读取失败: {result['error']}")
            else:
                logger.info(f"✅ 读取成功")
                logger.info(f"   文件类型: {result['file_type']}")
                logger.info(f"   文件大小: {result['file_size']} 字节")
                logger.info(f"   分块数量: {result['total_chunks']}")
                logger.info(f"   总字符数: {result['total_chars']}")
                logger.info(f"   总行数: {result['total_lines']}")
                
                # 显示每个分块的元数据（对于PDF很重要）
                for chunk in result["chunks"][:2]:  # 只显示前2个分块的信息
                    logger.info(f"   分块 {chunk['chunk_id']+1}: {chunk['content_length']} 字符")
                    if chunk['metadata']:
                        logger.info(f"     元数据: {chunk['metadata']}")
                
        except Exception as e:
            logger.error(f"❌ 测试过程中发生异常: {str(e)}")

def main():
    """
    主函数 - 用于测试文档读取功能
    """
    # 测试文件列表（请根据实际情况修改这些路径）
    test_files = [
        # 请添加实际存在的测试文件路径
        # "sample.pdf",
        # "sample.docx", 
        # "sample.txt",
        "sample.py"
    ]
    
    # 如果没有指定测试文件，创建一些示例文件进行测试
    if not test_files:
        logger.info("未提供测试文件，创建示例文件...")
        
        # 创建示例文本文件
        sample_txt = "sample_test.txt"
        with open(sample_txt, 'w', encoding='utf-8') as f:
            f.write("这是一个测试文本文件\n")
            f.write("第二行内容\n")
            f.write("第三行内容，用于测试文档读取功能。\n")
        
        # 创建示例Python文件
        sample_py = "sample_test.py"
        with open(sample_py, 'w', encoding='utf-8') as f:
            f.write('''# 示例Python文件
def hello_world():
    """这是一个示例函数"""
    print("Hello, World!")
    return True

class TestClass:
    def __init__(self):
        self.name = "Test"
        
if __name__ == "__main__":
    hello_world()
''')
        
        test_files = [sample_txt, sample_py]
    
    # 运行可读性测试
    test_file_readability(test_files)
    
    # 单独测试一个文件的详细内容
    if test_files:
        logger.info("\n" + "=" * 50)
        logger.info("详细内容测试")
        logger.info("=" * 50)
        
        test_file = test_files[0]
        try:
            content = read_document(test_file)
            logger.info(f"文件 '{test_file}' 的内容预览:")
            logger.info("-" * 30)
            # 只显示前200个字符作为预览
            preview = content[:200] + "..." if len(content) > 200 else content
            logger.info(preview)
            logger.info("-" * 30)
            
        except Exception as e:
            logger.error(f"详细内容测试失败: {str(e)}")
    
    # 测试错误情况
    logger.info("\n" + "=" * 50)
    logger.info("错误情况测试")
    logger.info("=" * 50)
    
    # 测试不存在的文件
    try:
        read_document("non_existent_file.pdf")
    except Exception as e:
        logger.info(f"✅ 正确捕获错误 (文件不存在): {type(e).__name__}: {e}")
    
    # 测试不支持的文件类型
    try:
        read_document("test.jpg")
    except Exception as e:
        logger.info(f"✅ 正确捕获错误 (不支持的类型): {type(e).__name__}: {e}")

if __name__ == "__main__":
    main()