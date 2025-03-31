import os
import sys
import shutil
import subprocess
import signal
from PIL import Image

# Carpetas
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"

# Configuraciones
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}
MAX_WIDTH = 500
MAX_HEIGHT = 500

def ensure_folders():
    """Crea las carpetas input/ y output/ si no existen."""
    os.makedirs(INPUT_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def resize_image(image_path):
    """Redimensiona una imagen manteniendo su aspecto."""
    try:
        with Image.open(image_path) as img:
            img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)
            img.save(image_path, quality=85, optimize=True)
            print(f"📐 Imagen redimensionada: {image_path}")
    except Exception as e:
        print(f"❌ Error al redimensionar {image_path}: {e}")

def convert_image_to_webp(image_path, output_path):
    """Convierte una imagen a formato WebP."""
    try:
        img = Image.open(image_path)
        img.save(output_path, "WEBP", quality=80)
        print(f"✅ Imagen convertida: {output_path}")
        os.remove(image_path)
        print(f"🗑️ Imagen original eliminada: {image_path}")
    except Exception as e:
        print(f"❌ Error al convertir {image_path} a WebP: {e}")

def convert_video_to_webm(video_path, output_path):
    """Convierte un video a formato WebM usando FFmpeg."""
    try:
        command = [
            "ffmpeg", "-i", video_path,
            "-c:v", "libvpx-vp9", "-b:v", "1M",
            "-c:a", "libopus", output_path, "-y"
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Video convertido: {output_path}")
    except Exception as e:
        print(f"❌ Error al convertir {video_path} a WebM: {e}")

def process_files():
    """Procesa los archivos de la carpeta input."""
    files = os.listdir(INPUT_FOLDER)

    if not files:
        print("📂 La carpeta 'input/' está vacía. Agrega archivos para procesar.")
        return

    for filename in files:
        file_path = os.path.join(INPUT_FOLDER, filename)
        ext = os.path.splitext(filename)[1].lower()

        if os.path.isfile(file_path):
            base_name = os.path.splitext(filename)[0]
            output_file = os.path.join(OUTPUT_FOLDER, base_name)

            if ext in IMAGE_EXTENSIONS:
                resize_image(file_path)
                convert_image_to_webp(file_path, output_file + ".webp")
            elif ext in VIDEO_EXTENSIONS:
                convert_video_to_webm(file_path, output_file + ".webm")

def rename_webp_files():
    """Renombra archivos .webp en la carpeta output."""
    files = sorted(os.listdir(OUTPUT_FOLDER))
    index = 1

    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext != ".webp":
            continue

        new_name = f"{index:02d}.webp"
        old_path = os.path.join(OUTPUT_FOLDER, file)
        new_path = os.path.join(OUTPUT_FOLDER, new_name)
        os.rename(old_path, new_path)
        print(f"🔤 Renombrado: {file} → {new_name}")
        index += 1

    print("✅ ¡Renombrado completo!")

def signal_handler(sig, frame):
    print("\n🚨 Proceso detenido por el usuario.")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    ensure_folders()

    try:
        process_files()
        rename_webp_files()
        print("🎉 Proceso completo. Revisa la carpeta 'output/'.")
    except KeyboardInterrupt:
        print("\n🚨 Proceso detenido por el usuario.")