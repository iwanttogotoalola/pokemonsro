import gradio as gr
import pandas as pd
import numpy as np
from PIL import Image
import os, glob

# === Настройки проекта ===
CSV_PATH = "pokemon.csv"
IMAGES_DIR = "images"

# --- Проверяем наличие файлов ---
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError("Файл pokemon.csv не найден. Помести его рядом с app.py.")
if not os.path.exists(IMAGES_DIR):
    raise FileNotFoundError("Папка 'images' не найдена. Помести туда изображения покемонов.")

# --- Загружаем CSV ---
df = pd.read_csv(CSV_PATH)

# --- Сопоставляем имена с изображениями (.png) ---
image_files = glob.glob(os.path.join(IMAGES_DIR, "*.png"))
file_map = {os.path.splitext(os.path.basename(f))[0].lower(): f for f in image_files}

names, types, paths = [], [], []
for _, row in df.iterrows():
    name = str(row["Name"]).strip()
    key = name.lower()
    if key in file_map:
        names.append(name)
        types.append(row["Type1"])
        paths.append(file_map[key])

# --- Исправление прозрачности ---
def fix_transparency(img_array, bg_color=(540, 540, 540)):
    """Убираем прозрачность, добавляем светлый фон."""
    if img_array.shape[-1] == 4:
        alpha = img_array[:, :, 3:] / 255.0
        rgb = img_array[:, :, :3]
        bg = np.ones_like(rgb) * np.array(bg_color)
        img_array = rgb * alpha + bg * (1 - alpha)
    return img_array.astype(np.uint8)

# --- Функция показа покемона ---
def show_pokemon(name):
    name = name.lower().strip()
    for i, n in enumerate(names):
        if n.lower() == name:
            path = paths[i]
            img = np.array(Image.open(path).convert("RGBA"))
            img = fix_transparency(img)
            img = Image.fromarray(img)
            poke_type = types[i]
            return img, f"🧩 Имя: {names[i]}\n🔹 Тип: {poke_type}"
    return None, f"❌ Покемон '{name}' не найден."

# --- Список покемонов для выпадающего меню ---
pokemon_list = sorted(list(dict.fromkeys(names)))

# === Интерфейс Gradio ===
demo = gr.Interface(
    fn=show_pokemon,
    inputs=gr.Dropdown(choices=pokemon_list, label="Выбери покемона"),
    outputs=[
        gr.Image(label="Изображение покемона"),
        gr.Textbox(label="Информация", lines=2)
    ],
    title="🎮 Pokemon Classifier",
    description=(
        "Интерактивный покедекс, созданный в Google Colab и развёрнутый на Render. "
        "Выбери покемона из списка, чтобы увидеть его изображение и тип."
    ),
    allow_flagging="never",
    theme="soft",
)

# === Запуск (для Render) ===
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
