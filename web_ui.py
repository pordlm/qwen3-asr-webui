import gradio as gr
import torch
import os
import sys

# 尝试导入官方库，如果不存在则尝试自动安装
try:
    from qwen_asr import Qwen3ASRModel
except ImportError:
    print("⚠️ 未检测到 'qwen-asr' 库，正在尝试安装...")
    os.system("pip install -U qwen-asr -i https://pypi.tuna.tsinghua.edu.cn/simple")
    try:
        from qwen_asr import Qwen3ASRModel
    except ImportError:
        print("❌ 无法安装 qwen-asr，请手动运行: pip install qwen-asr")
        sys.exit(1)

print("正在初始化 Qwen3-ASR 模型...")

# 1. 确定模型路径
# 优先检查 Docker 挂载路径下的 'model' 文件夹
LOCAL_MODEL_PATH = "/data/shared/Qwen3-ASR/model"
if os.path.exists(LOCAL_MODEL_PATH):
    print(f"✅ 发现本地模型: {LOCAL_MODEL_PATH}")
    MODEL_ID = LOCAL_MODEL_PATH
else:
    print(f"⚠️ 未找到本地模型 {LOCAL_MODEL_PATH}，将尝试使用 hf-mirror.com 在线加载...")
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
    MODEL_ID = "Qwen/Qwen3-ASR-1.7B"

# 2. 硬件检测
if torch.cuda.is_available():
    device = "cuda:0"
    # 如果显卡支持 bf16 (如 30系/40系)，优先使用以节省显存，否则用 float16
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    print(f"🚀 使用 GPU: {torch.cuda.get_device_name(0)} (dtype={dtype})")
else:
    device = "cpu"
    dtype = torch.float32
    print("🐢 未检测到 GPU，将使用 CPU 运行 (速度较慢)")

# 3. 加载模型 (使用官方 SDK 方式)
try:
    model = Qwen3ASRModel.from_pretrained(
        MODEL_ID,
        dtype=dtype,
        device_map=device,
    )
    print(">>> 模型加载成功！服务准备就绪。")
except Exception as e:
    print(f"\n❌ 模型加载失败: {e}")
    print("如果是 'trust_remote_code' 相关错误，请检查 qwen-asr 包版本是否最新。")
    sys.exit(1)

# 4. 推理函数
def transcribe(audio_path):
    if not audio_path:
        return "请提供音频文件。"
    
    print(f"正在处理音频: {audio_path}")
    try:
        # 调用官方 SDK 的 transcribe 接口
        results = model.transcribe(
            audio=audio_path,
            language=None,  # None = 自动检测语言
        )
        # 结果是一个列表，取第一项
        if results and len(results) > 0:
            return results[0].text
        else:
            return "未识别到有效的语音内容。"
    except Exception as e:
        return f"识别出错: {str(e)}"

# 5. 构建 Gradio 界面
with gr.Blocks(title="Qwen3-ASR WebUI") as demo:
    gr.Markdown("# 🎤 Qwen3-ASR 语音识别 (Local)")
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(sources=["upload", "microphone"], type="filepath", label="请说话或上传音频")
            btn = gr.Button("开始识别", variant="primary")
        
        with gr.Column():
            text_output = gr.Textbox(label="识别结果", lines=6, show_label=True)

    btn.click(fn=transcribe, inputs=audio_input, outputs=text_output)

if __name__ == "__main__":
    print(f"Running on local URL: http://localhost:8000")
    demo.launch(server_name="0.0.0.0", server_port=80)
