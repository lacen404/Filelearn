# app.py
#  pip install fastapi uvicorn
#  pip install python-multipart
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
import traceback
from llm_analyzer import analyze_content
from document_parser import read_document, read_image

app = FastAPI(title="LLM Analyzer API")

@app.post(
    "/analyze",
    summary="上传题目与文件进行智能分析",
    description=(
        """callbacks=
        "该接口用于将题目内容和对应文件（docx、pdf、jpg/png、py、java）上传给系统，"
        "由后端大模型解析文件内容并生成逻辑分析与评价结果。\n\n"
        "**输入参数：**\n"
        "- `question`：题目内容，字符串类型。\n"
        "- `file`：上传文件，可为 docx/pdf/jpg/png/py/java 格式。\n\n"
        "**返回值：**\n"
        "- JSON 格式结果，包含逻辑分析、正确性评价、总体评分与改进建议。"\n\n
        "**题目举例：**\n"
        "一个猜数字的游戏 游戏特点：🎯 核心功能：4种难度级别：从简单到地狱模式 
        智能提示系统：高低提示 + 距离提示 + 趋势提示
        计分系统：基于剩余机会和难度计算得分
        游戏统计：记录最佳成绩和总得分
        🎮 游戏体验：
        美观的界面：使用表情符号和格式化输出
        错误处理：防止无效输入导致的崩溃
        进度显示：实时显示剩余机会和猜测历史
        暂停继续：游戏间有适当的暂停
        📊 额外功能：
        游戏统计：查看历史成绩
        详细说明：完整的游戏规则说明
        最佳记录：追踪最佳表现"""
    )
)

async def analyze_api(
    question: str = Form(..., description="题目内容"),
    file: UploadFile = None
):
    try:
        if not file:
            raise HTTPException(status_code=400, detail="必须上传一个文件。")

        file_content = await file.read()
        filename = file.filename.lower()

        # 根据文件类型选择解析函数
        if filename.endswith((".jpg", ".jpeg", ".png")):
            text_content = read_image(file_content)
        elif filename.endswith((".docx", ".pdf")):
            text_content = read_document(file_content, filename.split(".")[-1])
        elif filename.endswith((".py", ".java")):
            text_content = file_content.decode("utf-8", errors="ignore")
        else:
            raise HTTPException(status_code=400, detail="不支持的文件类型。")

        content = f"题目：{question}\n\n文件内容：\n{text_content}"
        result = analyze_content(content)

        if not result:
            raise HTTPException(status_code=500, detail="LLM 分析失败，未返回结果。")

        if hasattr(result, "content"):
            try:
                import json
                json_result = json.loads(result.content)
                return JSONResponse(content=json_result)
            except Exception:
                return JSONResponse(content={"raw_output": result.content})
        else:
            return JSONResponse(content={"result": str(result)})

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器错误: {e}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)