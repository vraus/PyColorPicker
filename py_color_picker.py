import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
from colorthief import ColorThief

class ColorPickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Picker App")
        self.root.geometry("800x500")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.pipette_active = False
        self.color_preview = None
        self.zoom_preview = None

        # Frame for the image
        self.image_frame = ctk.CTkFrame(root, width=400, height=400)
        self.image_frame.pack(side=ctk.LEFT, padx=10, pady=10)

        # Button to load image
        self.load_button = ctk.CTkButton(root, text="Load Image", command=self.load_image)
        self.load_button.pack()

        # Canvas to display image
        self.canvas = ctk.CTkCanvas(self.image_frame, width=400, height=400)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.get_color_from_image)
        self.canvas.bind("<Motion>", self.update_color_preview)

        # Frame for color picker and palette (enlarged)
        self.color_frame = ctk.CTkFrame(root, width=300, height=400)
        self.color_frame.pack(side=ctk.RIGHT, padx=10, pady=10)

        # Frame to show selected color and value
        self.selected_color_box = ctk.CTkFrame(self.color_frame, width=100, height=50)
        self.selected_color_box.pack(pady=10)

        self.selected_color_display = ctk.CTkLabel(self.selected_color_box, text="", width=15)
        self.selected_color_display.pack(side=ctk.LEFT, padx=(5, 0))

        self.selected_color_label = ctk.CTkLabel(self.selected_color_box, text="", width=15)
        self.selected_color_label.pack(side=ctk.LEFT, padx=(5, 0))

        # Button to pick color
        self.pick_color_button = ctk.CTkButton(self.color_frame, text="Pick Color from Image", command=self.activate_pipette)
        self.pick_color_button.pack(pady=10)

        # Frame to display color palette
        self.palette_frame = ctk.CTkFrame(self.color_frame)
        self.palette_frame.pack(pady=10)

        self.image_path = None
        self.image = None

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image_path = file_path
            self.image = Image.open(file_path).convert("RGB")
            self.image.thumbnail((400, 400))
            self.imgtk = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=ctk.NW, image=self.imgtk)
            self.show_palette()

    def activate_pipette(self):
        if self.image:
            self.pipette_active = True

    def update_color_preview(self, event):
        if self.pipette_active and self.image:
            x, y = event.x, event.y
            if 0 <= x < self.image.width and 0 <= y < self.image.height:
                rgb_color = self.image.getpixel((x, y))
                hex_color = '#%02x%02x%02x' % rgb_color[:3]

                if self.color_preview is None:
                    self.color_preview = self.canvas.create_oval(
                        x + 15, y - 15, x + 45, y + 15,
                        outline='black', fill=hex_color, width=2
                    )
                else:
                    self.canvas.coords(self.color_preview, x + 15, y - 15, x + 45, y + 15)
                    self.canvas.itemconfig(self.color_preview, fill=hex_color)

                if self.zoom_preview is None:
                    self.zoom_preview = ctk.CTkCanvas(self.canvas, width=50, height=50, bg="white")
                    self.zoom_preview.place(x=x+20, y=y+20)
                else:
                    self.zoom_preview.place(x=x+20, y=y+20)

                zoom_image = self.get_zoomed_image(x, y)
                self.zoom_preview_image = ImageTk.PhotoImage(zoom_image)
                self.zoom_preview.create_image(25, 25, image=self.zoom_preview_image)

    def get_zoomed_image(self, x, y, zoom_factor=3):
        box_size = 10
        box = (x - box_size, y - box_size, x + box_size, y + box_size)
        region = self.image.crop(box)
        zoom_image = region.resize((50 * zoom_factor, 50 * zoom_factor), Image.NEAREST)
        
        # Draw crosshair on the zoomed image
        draw = ImageDraw.Draw(zoom_image)
        crosshair_color = "black"
        center = (25 * zoom_factor, 25 * zoom_factor)  # Center of the zoomed image
        
        # Draw vertical line
        draw.line((center[0], 0, center[0], 50 * zoom_factor), fill=crosshair_color, width=1)
        
        # Draw horizontal line
        draw.line((0, center[1], 50 * zoom_factor, center[1]), fill=crosshair_color, width=1)
        
        return zoom_image

    def get_color_from_image(self, event):
        if self.pipette_active:
            x, y = event.x, event.y
            if self.image:
                rgb_color = self.image.getpixel((x, y))
                hex_color = '#%02x%02x%02x' % rgb_color[:3]
                self.selected_color_label.configure(text=hex_color)  # Update with the hex value
                self.selected_color_display.configure(fg_color=hex_color, text="  ")  # Display color
                self.root.clipboard_clear()
                self.root.clipboard_append(hex_color)
                self.pipette_active = False
                if self.color_preview:
                    self.canvas.delete(self.color_preview)
                    self.color_preview = None
                if self.zoom_preview:
                    self.zoom_preview.destroy()
                    self.zoom_preview = None

    def show_palette(self):
        if self.image_path:
            color_thief = ColorThief(self.image_path)
            palette = color_thief.get_palette(color_count=8)
            for widget in self.palette_frame.winfo_children():
                widget.destroy()
            for color in palette:
                hex_color = '#%02x%02x%02x' % color
                btn = ctk.CTkButton(self.palette_frame, fg_color=hex_color, text='', width=40, height=40, command=lambda c=hex_color: self.select_palette_color(c))
                btn.pack(pady=5)

    def select_palette_color(self, color):
        self.selected_color_label.configure(text=color)  # Update with the hex value
        self.selected_color_display.configure(fg_color=color, text="  ")  # Display color
        self.root.clipboard_clear()
        self.root.clipboard_append(color)

if __name__ == "__main__":
    root = ctk.CTk()
    app = ColorPickerApp(root)
    root.mainloop()
