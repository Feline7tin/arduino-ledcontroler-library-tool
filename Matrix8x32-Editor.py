import tkinter as tk
import re

ROWS = 8
COLS = 32
CELL_SIZE = 20

class LEDMatrixEditor:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE, bg='black')
        self.canvas.pack()
        self.pixels = [[0] * COLS for _ in range(ROWS)]
        self.drawing = False
        self.erasing = False

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.export_button = tk.Button(root, text="Export as C Array", command=self.export)
        self.export_button.pack(pady=(10, 2))

        self.import_text = tk.Text(root, height=8, width=70)
        self.import_text.pack(pady=(5, 2))

        self.import_button = tk.Button(root, text="Import from C Array", command=self.import_from_text)
        self.import_button.pack(pady=(0, 10))

        root.resizable(False, False)

        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        for row in range(ROWS):
            for col in range(COLS):
                x0 = col * CELL_SIZE
                y0 = row * CELL_SIZE
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE
                color = "cyan" if self.pixels[row][col] else "gray20"
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")

    def on_click(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        if 0 <= col < COLS and 0 <= row < ROWS:
            self.drawing = True
            self.erasing = self.pixels[row][col] == 1
            self.pixels[row][col] = 0 if self.erasing else 1
            self.redraw()

    def on_drag(self, event):
        if not self.drawing:
            return
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        if 0 <= col < COLS and 0 <= row < ROWS:
            self.pixels[row][col] = 0 if self.erasing else 1
            self.redraw()

    def on_release(self, event):
        self.drawing = False

    def export(self):
        modules = COLS // 8
        result = "byte image[8][{}] = {{\n".format(modules)
        for row in range(ROWS):
            result += "  {"
            for m in range(modules):
                byte = 0
                for b in range(8):
                    col = m * 8 + (7 - b)
                    if self.pixels[row][col]:
                        byte |= (1 << b)
                result += "B{:08b}".format(byte)
                if m < modules - 1:
                    result += ", "
            result += "},\n"
        result += "};\n"
        self.show_export_window(result)

    def show_export_window(self, text):
        win = tk.Toplevel(self.root)
        win.title("Exported C Code")
        text_widget = tk.Text(win, wrap=tk.NONE, height=15, width=70)
        text_widget.insert(tk.END, text)
        text_widget.pack()
        text_widget.configure(state='disabled')

    def import_from_text(self):
        raw = self.import_text.get("1.0", tk.END)
        bytes_per_row = COLS // 8
        # Extract binary values like B00011000 using regex
        matches = re.findall(r'B([01]{8})', raw)
        if len(matches) != ROWS * bytes_per_row:
            print("Invalid input format or size.")
            return

        new_pixels = [[0] * COLS for _ in range(ROWS)]
        idx = 0
        for row in range(ROWS):
            for m in range(bytes_per_row):
                byte_str = matches[idx]
                for b in range(8):
                    col = m * 8 + b  # reverse bit order
                    new_pixels[row][col] = int(byte_str[b])
                idx += 1
        self.pixels = new_pixels
        self.redraw()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("8x32 LED Matrix Pattern Editor (Import/Export Enabled)")
    app = LEDMatrixEditor(root)
    root.mainloop()
