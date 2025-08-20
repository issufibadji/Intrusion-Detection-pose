# Intrusion-Detection-pose
Intrusion Detection pose

Como executar o projeto
Clonar e entrar no diretório

git clone <url-do-repositório>
cd Intrusion-Detection-pose
Configurar o ambiente

Crie um ambiente virtual (opcional) e instale as dependências:

python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt
pip install opencv-python cvzone pillow numpy filterpy matplotlib scikit-image lap
O projeto utiliza bibliotecas como OpenCV, Ultralyics/YOLO, Tkinter e Pillow, todas importadas no script principal

Executar a aplicação

python intrusion_detection.py