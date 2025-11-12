# document_parser.py
# 文档读取与预处理模块
# 依赖安装：
# pip install langchain langchain-community langchain-text-splitters
# pip install pytesseract opencv-python pillow numpy
# document_parser.py
# 文档读取与预处理模块
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import logging
from typing import List, Optional
import tempfile

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import pytesseract
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

def read_image(file_content: bytes) -> str:
    """
    读取图片内容并提取文字信息（OCR实现）
    
    依赖:
        - pip install pytesseract opencv-python pillow numpy
        - 系统需安装 tesseract-ocr，并确保可在 PATH 中调用
        - 如需中文支持，安装 chi_sim.traineddata 语言包
          (macOS: brew install tesseract tesseract-lang)
    
    Args:
        file_content: 图片文件的二进制内容
        
    Returns:
        str: 识别出的文本内容
    """
    try:
        logger.info("开始读取图片内容并进行OCR识别")
        # 将二进制数据转换为numpy数组
        image_array = np.frombuffer(file_content, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            logger.error("图像解码失败")
            return "[图像解码失败]"

        # 转灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 二值化提升识别效果
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # 转换为PIL Image以便pytesseract识别
        pil_image = Image.fromarray(thresh)
        text = pytesseract.image_to_string(pil_image, lang="chi_sim+eng")

        # 清理多余换行与空白
        clean_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
        if not clean_text:
            clean_text = "[未识别出文字]"

        logger.info("OCR识别完成")
        return clean_text

    except Exception as e:
        logger.error(f"OCR识别时出错: {e}")
        return f"[OCR识别出错: {e}]"

def read_document(file_input, file_type: Optional[str] = None) -> str:
    """
    读取文档内容，支持文件路径和上传的二进制内容。

    Args:
        file_input: 文件路径(str) 或 文件字节流(bytes)
        file_type: 文件类型（扩展名），如 'pdf'、'docx'

    Returns:
        str: 文档内容文本
    """
    try:
        # 如果传入的是路径
        if isinstance(file_input, str):
            file_path = file_input
        else:
            # 如果传入的是字节流，写入临时文件
            suffix = f".{file_type}" if file_type else ""
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_file.write(file_input)
            temp_file.flush()
            file_path = temp_file.name

        ext = os.path.splitext(file_path)[-1].lower()

        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext in [".doc", ".docx"]:
            loader = Docx2txtLoader(file_path)
        elif ext in [".txt", ".py", ".java"]:
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            raise ValueError(f"不支持的文件类型: {ext}")

        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        text = "\n".join([doc.page_content for doc in splits])
        return text

    finally:
        # 若使用了临时文件则删除
        if not isinstance(file_input, str) and os.path.exists(file_path):
            os.remove(file_path)


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