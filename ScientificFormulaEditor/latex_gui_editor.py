from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
import re
import io

def convert_to_latex(equation: str) -> str:
    try:
        # Очистка лишнего
        equation = re.sub(r'\s+', ' ', equation).strip()

        # Спецсимволы
        symbol_map = {
            'Δ': r'\Delta', 'ϕ': r'\phi', '∼': r'\sim',
            '∫': r'\int', '∞': r'\infty', '−': '-', '＋': '+'
        }
        for sym, latex in symbol_map.items():
            equation = equation.replace(sym, latex)

        # Индексы типа phiSCCL → \phi_{\mathrm{SCCL}}
        equation = re.sub(r'(\\phi)\s*([A-Z]{2,})', r'\1_{\mathrm{\2}}', equation)

        # Степени b2 → b^2 и (b2+z2)^3/2 → (b^2 + z^2)^{3/2}
        equation = re.sub(r'([a-zA-Z])(\d)', r'\1^{\2}', equation)
        equation = re.sub(r'\)\s*(\d)/(\d)', r')^{\1/\2}', equation)

        # Интеграл
        equation = re.sub(r'\\int_\{([^\}]+)\}\^\{([^\}]+)\}', r'\\int_{\1}^{\2}', equation)

        # Дроби вида a / b
        equation = re.sub(r'(\S+)\s*/\s*(\S+)', r'\\frac{\1}{\2}', equation)

        # Дифференциалы
        equation = re.sub(r'([a-zA-Z])\s*d([a-zA-Z])', r'\\1 \\, \\mathrm{d}\\2', equation)

        equation = re.sub(r'\bd([a-zA-Z])\b', r'\\mathrm{d}\1', equation)
        equation = re.sub(
            r'([a-zA-Z])\s*d([a-zA-Z])',
            lambda m: f"{m.group(1)} \\, \\mathrm{{d}}{m.group(2)}",
            equation
        )


        # Окончательная чистка
        equation = re.sub(r'\s+', ' ', equation).strip()

        return f"${equation}$"

    except Exception as e:
        return f"Ошибка при преобразовании: {str(e)}"


def render_latex_to_canvas(latex_code, canvas):
    fig = Figure(figsize=(7, 1.5), dpi=100)
    ax = fig.add_subplot(111)
    ax.axis('off')
    ax.text(0.5, 0.5, latex_code, fontsize=18, ha='center', va='center')

    buf = io.BytesIO()
    FigureCanvasAgg(fig).print_png(buf)
    buf.seek(0)

    image = Image.open(buf)
    photo = ImageTk.PhotoImage(image)

    canvas.image = photo
    canvas.delete("all")
    canvas.create_image(0, 0, anchor='nw', image=photo)

def on_convert():
    raw_eq = input_text.get("1.0", tk.END)
    latex_eq = convert_to_latex(raw_eq)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, latex_eq)
    render_latex_to_canvas(latex_eq, preview_canvas)

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(output_text.get("1.0", tk.END))
    messagebox.showinfo("Скопировано", "Формула скопирована в буфер обмена!")

root = tk.Tk()
root.title("Scientific Formula Editor + LaTeX Preview")
root.geometry("800x700")

tk.Label(root, text="Введите формулу:", font=("Arial", 12)).pack(pady=5)
input_text = tk.Text(root, height=8, width=90, wrap=tk.WORD, font=("Courier New", 12))
input_text.pack(padx=10, pady=5)

tk.Button(root, text="Преобразовать в LaTeX", command=on_convert, width=25).pack(pady=10)

tk.Label(root, text="Результат (LaTeX):", font=("Arial", 12)).pack(pady=5)
output_text = tk.Text(root, height=4, width=90, wrap=tk.WORD, font=("Courier New", 12))
output_text.pack(padx=10, pady=5)

tk.Button(root, text="Копировать в буфер", command=copy_to_clipboard, width=25).pack(pady=10)

tk.Label(root, text="Предпросмотр формулы:", font=("Arial", 12)).pack(pady=5)
preview_canvas = tk.Canvas(root, width=700, height=150, bg="white")
preview_canvas.pack(pady=10)

root.mainloop()
