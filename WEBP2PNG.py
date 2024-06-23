import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageGrab, UnidentifiedImageError
import win32clipboard
import io
import os
import datetime

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QUICK IMAGE | EGAMI KCIUQ")
        self.root.attributes("-topmost", True)

        # Set fixed window size
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        self.image_format = 'PNG'  # Default format
        self.format_var = tk.StringVar(value='PNG')  # Set 'PNG' as the default
        self.available_formats = ['PNG', 'JPEG', 'BMP']

        # Initialize aspect ratio attribute
        self.aspect_ratio = None
        self.zoom_level = 1.0

        # Menu configuration
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        self.options_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Options", menu=self.options_menu)

        self.format_menu = tk.Menu(self.options_menu, tearoff=0)
        self.options_menu.add_cascade(label="Output Format", menu=self.format_menu)

        for format in self.available_formats:
            self.format_menu.add_radiobutton(label=format, variable=self.format_var, value=format, command=self.update_format)
        
        self.always_on_top_var = tk.BooleanVar(value=True)
        self.options_menu.add_checkbutton(label="Always on Top", variable=self.always_on_top_var, command=self.toggle_always_on_top)

        # Cropping Menu
        self.aspect_ratios = ['1:1', '4:3', '3:4', '16:9', '9:16', 'Free']
        self.aspect_ratio_var = tk.StringVar(value='Free')

        # UI elements
        self.label = tk.Label(root, text="Paste an image here (Ctrl+V):")
        self.label.grid(row=0, column=0, columnspan=7, sticky="ew")

        self.canvas = tk.Canvas(root, bg="white", height=400, width=600)
        self.canvas.grid(row=1, column=0, columnspan=7, sticky="nsew")

        # Zoom slider
        self.zoom_slider = tk.Scale(root, from_=0.5, to=2.0, orient=tk.HORIZONTAL, resolution=0.1, command=self.update_zoom)
        self.zoom_slider.set(1.0)
        self.zoom_slider.grid(row=2, column=0, columnspan=7, sticky="ew")

        # Aspect Ratio Buttons
        self.ratio_buttons = []
        for i, ratio in enumerate(self.aspect_ratios):
            btn = tk.Button(root, text=ratio, command=lambda r=ratio: self.update_aspect_ratio(r), width=5)
            btn.grid(row=3, column=i, sticky="ew")
            self.ratio_buttons.append(btn)

        self.rotate_left_button = tk.Button(root, text="Rotate Left", command=lambda: self.rotate_image(90), width=12)
        self.rotate_left_button.grid(row=4, column=1, sticky="ew")

        self.flip_horizontal_button = tk.Button(root, text="Flip Horizontal", command=self.flip_horizontal, width=12)
        self.flip_horizontal_button.grid(row=4, column=2, sticky="ew")

        self.flip_vertical_button = tk.Button(root, text="Flip Vertical", command=self.flip_vertical, width=12)
        self.flip_vertical_button.grid(row=4, column=3, sticky="ew")

        self.crop_button = tk.Button(root, text="Crop Image", command=self.start_crop, width=12)
        self.crop_button.grid(row=4, column=4, sticky="ew")

        self.copy_button = tk.Button(root, text="Copy", command=self.copy_to_clipboard, width=12)
        self.copy_button.grid(row=4, column=5, sticky="ew")

        self.rotate_right_button = tk.Button(root, text="Rotate Right", command=lambda: self.rotate_image(-90), width=12)
        self.rotate_right_button.grid(row=4, column=6, sticky="ew")

        # Events
        self.root.bind("<Control-v>", self.paste_image)
        self.root.bind("<Control-c>", self.copy_to_clipboard_event)
        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.image = None
        self.converted_image_path = None
        self.display_image_resized = None
        self.rect = None
        self.crop_rectangle = None
        self.start_x = None
        self.start_y = None

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create floating button for quick conversion
        self.create_floating_button()

    def create_floating_button(self):
        self.floating_root = tk.Toplevel(self.root)
        self.floating_root.geometry("70x50")
        self.floating_root.overrideredirect(True)
        self.floating_root.attributes("-topmost", True)

        # Variables to store position
        self.start_x = None
        self.start_y = None

        # Create a button
        self.button = tk.Button(self.floating_root, text="Convert", command=self.quick_convert, bg="lightgrey")
        self.button.pack(expand=True, fill=tk.BOTH)

        # Bind drag events for moving the widget
        self.button.bind("<ButtonPress-3>", self.start_move)
        self.button.bind("<B3-Motion>", self.on_move)

    def start_move(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_move(self, event):
        x = self.floating_root.winfo_x() + event.x - self.start_x
        y = self.floating_root.winfo_y() + event.y - self.start_y
        self.floating_root.geometry(f"+{x}+{y}")

    def quick_convert(self):
        try:
            print("Attempting to grab image from clipboard...")
            clipboard_content = ImageGrab.grabclipboard()
            print(f"Clipboard content type: {type(clipboard_content)}")

            if isinstance(clipboard_content, list):
                print(f"Clipboard contains a list with {len(clipboard_content)} items.")
                for index, item in enumerate(clipboard_content):
                    print(f"Item {index}: type {type(item)}")
                    if isinstance(item, Image.Image):
                        clipboard_content = item
                        break
                    elif isinstance(item, str):
                        if item.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
                            try:
                                clipboard_content = Image.open(item)
                                break
                            except Exception as e:
                                print(f"Failed to open image from path: {item} - {e}")
                else:
                    clipboard_content = None

            if isinstance(clipboard_content, Image.Image):
                print("Image found in clipboard.")
                output = io.BytesIO()
                clipboard_content.save(output, format="PNG")
                png_data = output.getvalue()
                print(f"PNG data length: {len(png_data)} bytes")

                # Display the image in the app (if desired)
                self.image = clipboard_content
                self.process_image()

                # Copy the image as PNG back to the clipboard
                output.seek(0)
                image_data = output.read()

                def send_to_clipboard(clip_type, data):
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(clip_type, data)
                    win32clipboard.CloseClipboard()

                # Prepare the image data for the clipboard
                bmp_data = Image.open(io.BytesIO(image_data)).convert("RGB")
                with io.BytesIO() as bmp_output:
                    bmp_data.save(bmp_output, format="BMP")
                    bmp_data = bmp_output.getvalue()[14:]  # BMP data needs to exclude the BMP header info

                send_to_clipboard(win32clipboard.CF_DIB, bmp_data)

                print("PNG image copied back to clipboard.")
                self.button.config(bg="green")
            else:
                print("No image found in clipboard.")
                self.button.config(bg="red")
        except Exception as e:
            print(f"An error occurred: {e}")
            self.button.config(bg="red")

    def set_output_format(self, format):
        self.image_format = format

    def update_format(self):
        self.set_output_format(self.format_var.get())

    def update_aspect_ratio(self, ratio):
        if ratio == 'Free':
            self.aspect_ratio = None
        else:
            width, height = map(int, ratio.split(':'))
            self.aspect_ratio = width / height
        self.aspect_ratio_var.set(ratio)

    def toggle_always_on_top(self):
        self.root.attributes("-topmost", self.always_on_top_var.get())

    def paste_image(self, event):
        try:
            win32clipboard.OpenClipboard()
            image_data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
            print(f"Image data length from clipboard: {len(image_data)}")
            win32clipboard.CloseClipboard()

            if image_data:
                image = Image.open(io.BytesIO(image_data))
                self.image = image
                self.zoom_level = 1.0  # Reset zoom level when a new image is pasted
                self.zoom_slider.set(1.0)
                self.process_image()
            else:
                raise Exception("No image data in clipboard.")
        except Exception as e:
            print(f"Failed to paste image. Error: {e}")
            messagebox.showerror("Error", f"Failed to paste image. Error: {e}")

    def copy_to_clipboard_event(self, event):
        self.copy_to_clipboard()

    def rotate_image(self, angle):
        if self.image:
            self.image = self.image.rotate(angle, expand=True)
            self.process_image()

    def flip_horizontal(self):
        if self.image:
            self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
            self.process_image()

    def flip_vertical(self):
        if self.image:
            self.image = self.image.transpose(Image.FLIP_TOP_BOTTOM)
            self.process_image()

    def process_image(self):
        if self.image:
            self.display_image(self.image)
            self.save_image()
            self.copy_to_clipboard()

    def display_image(self, image):
        self.canvas.delete("all")
        self.display_image_resized = self.resize_proportionally(image)
        self.tk_image = ImageTk.PhotoImage(self.display_image_resized)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def resize_proportionally(self, image):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_width, image_height = image.size

        if image_width == 0 or image_height == 0:
            return image

        ratio = min(canvas_width / image_width, canvas_height / image_height) * self.zoom_level
        new_width = int(image_width * ratio)
        new_height = int(image_height * ratio)

        return image.resize((new_width, new_height), Image.LANCZOS)

    def update_zoom(self, value):
        self.zoom_level = float(value)
        if self.image:
            self.display_image(self.image)

    def save_image(self):
        if not os.path.exists('./CONVERTED'):
            os.makedirs('./CONVERTED')
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.converted_image_path = f"./CONVERTED/Image-{timestamp}.{self.image_format.lower()}"
        self.image.save(self.converted_image_path, self.image_format)

    def copy_to_clipboard(self):
        if self.image:
            output = io.BytesIO()
            self.image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()

    def start_crop(self):
        if self.crop_rectangle and self.crop_rectangle != [0, 0, 0, 0]:
            self.apply_crop()
        else:
            messagebox.showerror("Error", "No crop area selected. Please draw a crop area first.")

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_mouse_drag(self, event):
        cur_x, cur_y = event.x, event.y
        if self.aspect_ratio:
            try:
                if (cur_x - self.start_x) / (cur_y - self.start_y) > self.aspect_ratio:
                    cur_x = self.start_x + (cur_y - self.start_y) * self.aspect_ratio
                else:
                    cur_y = self.start_y + (cur_x - self.start_x) / self.aspect_ratio
            except ZeroDivisionError:
                pass  # Handle or log the zero division error gracefully

        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        self.crop_rectangle = self.canvas.coords(self.rect)
        if self.crop_rectangle == [0, 0, 0, 0]:
            self.crop_rectangle = None

    def apply_crop(self):
        if self.image and self.crop_rectangle:
            x0, y0, x1, y1 = [int(c) for c in self.crop_rectangle]

            # Convert canvas coordinates to image coordinates
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            image_width, image_height = self.image.size

            canvas_ratio = min(canvas_width / image_width, canvas_height / image_height)
            image_display_width = image_width * canvas_ratio
            image_display_height = image_height * canvas_ratio

            offset_x = (canvas_width - image_display_width) // 2
            offset_y = (canvas_height - image_display_height) // 2

            x0 = int((x0 - offset_x) / canvas_ratio)
            y0 = int((y0 - offset_y) / canvas_ratio)
            x1 = int((x1 - offset_x) / canvas_ratio)
            y1 = int((y1 - offset_y) / canvas_ratio)

            x0 = max(0, x0)
            y0 = max(0, y0)
            x1 = min(image_width, x1)
            y1 = min(image_height, y1)

            crop_box = (x0, y0, x1, y1)
            self.image = self.image.crop(crop_box)
            self.process_image()
            self.crop_rectangle = None

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()
