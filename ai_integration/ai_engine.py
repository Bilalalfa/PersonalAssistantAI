import subprocess
import base64
from PyQt6.QtCore import QThread, pyqtSignal
from langchain_ollama import OllamaLLM

class ChatWorker(QThread):
    response_ready = pyqtSignal(str)
    
    def __init__(self, model, context, images=None):
        super().__init__()
        self.model = model
        self.context = context
        self.images = images
        
    def run(self):
        try:
            llm = OllamaLLM(model=self.model)
            if self.images:
                # Note: OllamaLLM from langchain_ollama supports 'images' in bind or invoke
                # However, raw invoke might need specific formatting for vision
                response = llm.invoke(self.context, images=self.images)
            else:
                response = llm.invoke(self.context)
            self.response_ready.emit(response)
        except Exception as e:
            self.response_ready.emit(f"Error: {str(e)}")

def get_models():
    try:
        result = subprocess.run(["ollama", "list"], stdout=subprocess.PIPE, text=True)
        return [line.split()[0] for line in result.stdout.strip().split("\n")[1:]]
    except:
        return []

def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None
