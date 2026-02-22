from fastapi import FastAPI, File, UploadFile
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
import torch
import shutil
import os

# 初始化 FastAPI
app = FastAPI()

# 加载模型和处理器
model_id = "Qwen/Qwen3-ASR-1.7B"
processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="cuda"
).eval()

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    # 保存上传的视频文件
    upload_path = f"/data/shared/Qwen3-ASR/{file.filename}"
    with open(upload_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 使用模型进行转写
    audio_input = processor(upload_path, return_tensors="pt", sampling_rate=16000).input_values
    with torch.no_grad():
        logits = model(audio_input).logits
        predicted_ids = torch.argmax(logits, dim=-1)

    # 解码并返回转写结果
    transcription = processor.decode(predicted_ids[0])
    
    return {"filename": file.filename, "transcription": transcription}
