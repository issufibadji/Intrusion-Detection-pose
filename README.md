# Intrusion-Detection-pose

Projeto para detecção de intrusões utilizando reconhecimento de pose.

## Como executar o projeto

### 1. Clonar e entrar no diretório

```bash
git clone <url-do-repositório>
cd Intrusion-Detection-pose
```

### 2. Configurar o ambiente

Crie um ambiente virtual (opcional) e instale as dependências:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\\Scripts\\activate  # Windows

pip install -r requirements.txt
pip install opencv-python cvzone pillow numpy filterpy matplotlib scikit-image lap
```

O projeto utiliza bibliotecas como OpenCV, Ultralytics/YOLO, Tkinter e Pillow, todas importadas no script principal.

### 3. Executar a aplicação

```bash
python intrusion_detection.py
```

