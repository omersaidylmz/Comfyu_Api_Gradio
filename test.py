import json
import os
import time
import random
import gradio as gr
import numpy as np
import requests
from PIL import Image

URL = "http://127.0.0.1:8188/prompt"
OUTPUT_DIR = r"C:\Users\omers\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\ComfyUI\output"

def get_latest_image(folder):
    try:
        files = os.listdir(folder)
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not image_files:
            return None
        
        # Son değiştirilen dosyaya göre sırala
        image_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)))
        latest_image_path = os.path.join(folder, image_files[-1])
        
        # PIL Image objesi olarak aç ve döndür
        return Image.open(latest_image_path)
    except Exception as e:
        print(f"Error in get_latest_image: {str(e)}")
        return None

def start_queue(prompt_workflow):
    try:
        p = {"prompt": prompt_workflow}
        data = json.dumps(p).encode('utf-8')
        response = requests.post(URL, data=data)
        response.raise_for_status()  # HTTP hatalarını kontrol et
    except Exception as e:
        print(f"Error in start_queue: {str(e)}")
        raise

def wait_for_image(previous_image_time):
    timeout = 60  # 60 saniye timeout
    start_time = time.time()
    
    while True:
        if time.time() - start_time > timeout:
            raise TimeoutError("Image generation timed out")
            
        files = os.listdir(OUTPUT_DIR)
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if image_files:
            latest_file = max(image_files, key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)))
            latest_time = os.path.getmtime(os.path.join(OUTPUT_DIR, latest_file))
            
            if latest_time > previous_image_time:
                return os.path.join(OUTPUT_DIR, latest_file)
                
        time.sleep(1)

def generate_image(prompt_text):   
    try:
        # JSON workflow dosyasını yükle
        with open("text_apii.json", "r", encoding='utf-8') as file_json:
            prompt = json.load(file_json)
            prompt["10"]["inputs"]["input_text"] = prompt_text

        # Mevcut son görsel zamanını al
        current_files = os.listdir(OUTPUT_DIR)
        current_time = time.time()
        if current_files:
            latest_file = max(current_files, key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)))
            current_time = os.path.getmtime(os.path.join(OUTPUT_DIR, latest_file))

        # İşlemi başlat
        start_queue(prompt)
        
        # Yeni görseli bekle
        new_image_path = wait_for_image(current_time)
        
        # Görseli PIL Image olarak aç
        generated_image = Image.open(new_image_path)
        
        return generated_image

    except Exception as e:
        print(f"Error in generate_image: {str(e)}")
        # Hata durumunda varsayılan bir görsel döndürebilirsiniz
        return None

# Gradio arayüzü
demo = gr.Interface(
    fn=generate_image,
    inputs=[
        gr.Textbox(label="Promptu Giriniz...", placeholder="Görsel Açıklamanızı Buraya Yazınız...")
    ],
    outputs=[
        gr.Image(type="pil", label="Üretilen Görüntü")
    ],
    title="AI Görüntü Üretici",
    description="Görüntü oluşturmak için bir metin açıklaması girin",
    examples=[
        ["dağların üzerinde güzel bir gün batımı"],
        ["iplikle oynayan sevimli bir kedi"],
    ]
)

# Uygulamayı başlat
if __name__ == "__main__":
    demo.launch(share=True, debug=True)
