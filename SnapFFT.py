import numpy as np
import cv2
import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
from matplotlib.lines import Line2D
from PIL import Image, ImageTk, ImageGrab
import io
import win32clipboard
from win32con import CF_DIB

class FFTApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SnapFFT")
        self.root.geometry("1400x800")

        self.img_bgr = None
        self.img_gray = None
        self.processed_rgb = None
        self.fft_image = None
        self.spatial_calibrated = False
        self.spatial_calibration = 1.0
        self.unit_name = "units"
        self.box_drawn = False
        self.setup_widgets()

    def setup_widgets(self):
        # Left control panel
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.load_button = ttk.Button(self.control_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=5)

        self.paste_button = ttk.Button(self.control_frame, text="Paste Image", command=self.paste_image)
        self.paste_button.pack(pady=5)

        self.copy_orig_button = ttk.Button(self.control_frame, text="Copy Original", command=self.copy_original_to_clipboard)
        self.copy_orig_button.pack(pady=5)

        self.copy_fft_button = ttk.Button(self.control_frame, text="Copy FFT", command=self.copy_fft_to_clipboard)
        self.copy_fft_button.pack(pady=5)

        self.draw_line_btn = ttk.Button(self.control_frame, text="Draw Line", command=self.enable_line_mode)
        self.draw_line_btn.pack(pady=5)

        self.reset_zoom_btn = ttk.Button(self.control_frame, text="Reset Zoom", command=self.reset_zoom)
        self.reset_zoom_btn.pack(pady=5)

        ttk.Label(self.control_frame, text="Calibration (units/pixel):").pack()
        self.calibration_factor = tk.DoubleVar(value=1.0)
        self.calibration_entry = ttk.Entry(self.control_frame, textvariable=self.calibration_factor)
        self.calibration_entry.pack()

        ttk.Label(self.control_frame, text="Unit Name:").pack()
        self.unit_name_var = tk.StringVar(value="units")
        self.unit_name_entry = ttk.Entry(self.control_frame, textvariable=self.unit_name_var)
        self.unit_name_entry.pack()

        self.distance_label = ttk.Label(self.control_frame, text="")
        self.distance_label.pack(pady=5)

        self.fft_distance_label = ttk.Label(self.control_frame, text="")
        self.fft_distance_label.pack(pady=5)

        self.fft_calc_label = ttk.Label(self.control_frame, text="")
        self.fft_calc_label.pack(pady=5)

        # Colormap selection
        ttk.Label(self.control_frame, text="Original Image Colormap").pack(pady=5)
        self.orig_cmap_var = tk.StringVar(value='gray')
        orig_cmap_menu = ttk.Combobox(self.control_frame, textvariable=self.orig_cmap_var, state="readonly")
        orig_cmap_menu['values'] = ['gray', 'viridis', 'plasma', 'inferno', 'magma', 'cividis', 'jet', 'hot']
        orig_cmap_menu.pack()
        orig_cmap_menu.bind("<<ComboboxSelected>>", lambda e: self.update_image())

        ttk.Label(self.control_frame, text="FFT Image Colormap").pack(pady=5)
        self.fft_cmap_var = tk.StringVar(value='gray')
        fft_cmap_menu = ttk.Combobox(self.control_frame, textvariable=self.fft_cmap_var, state="readonly")
        fft_cmap_menu['values'] = ['gray', 'viridis', 'plasma', 'inferno', 'magma', 'cividis', 'jet', 'hot']
        fft_cmap_menu.pack()
        fft_cmap_menu.bind("<<ComboboxSelected>>", lambda e: self.update_fft())

        # Image display area
        self.image_frame = ttk.Frame(self.root)
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.orig_slider_frame = ttk.Frame(self.image_frame)
        self.orig_slider_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(self.orig_slider_frame, text="Brightness").grid(row=0, column=0)
        self.brightness_slider = tk.Scale(self.orig_slider_frame, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.update_image)
        self.brightness_slider.grid(row=0, column=1, sticky="ew")

        ttk.Label(self.orig_slider_frame, text="Contrast").grid(row=1, column=0)
        self.contrast_slider = tk.Scale(self.orig_slider_frame, from_=0.5, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, command=self.update_image)
        self.contrast_slider.set(1.0)
        self.contrast_slider.grid(row=1, column=1, sticky="ew")

        ttk.Label(self.orig_slider_frame, text="Gamma").grid(row=2, column=0)
        self.gamma_slider = tk.Scale(self.orig_slider_frame, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, command=self.update_image)
        self.gamma_slider.set(1.0)
        self.gamma_slider.grid(row=2, column=1, sticky="ew")

        self.fft_slider_frame = ttk.Frame(self.image_frame)
        self.fft_slider_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(self.fft_slider_frame, text="FFT Brightness").grid(row=0, column=0)
        self.fft_brightness_slider = tk.Scale(self.fft_slider_frame, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.update_fft)
        self.fft_brightness_slider.grid(row=0, column=1, sticky="ew")

        ttk.Label(self.fft_slider_frame, text="FFT Contrast").grid(row=1, column=0)
        self.fft_contrast_slider = tk.Scale(self.fft_slider_frame, from_=0.5, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, command=self.update_fft)
        self.fft_contrast_slider.set(1.0)
        self.fft_contrast_slider.grid(row=1, column=1, sticky="ew")

        ttk.Label(self.fft_slider_frame, text="FFT Gamma").grid(row=2, column=0)
        self.fft_gamma_slider = tk.Scale(self.fft_slider_frame, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, command=self.update_fft)
        self.fft_gamma_slider.set(1.0)
        self.fft_gamma_slider.grid(row=2, column=1, sticky="ew")

        self.figure = Figure(figsize=(10, 5))
        self.ax_original = self.figure.add_subplot(121)
        self.ax_fft = self.figure.add_subplot(122)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.image_frame)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.toggle_selector = None
        self.line_artist = None
        self.cid_click = None
        self.drawing_line = False
        self.start_point = None

        self.canvas.mpl_connect("scroll_event", self.on_scroll)

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg *.bmp *.tif *.tiff")])
        if file_path:
            self.display_image(file_path)

    def on_drop(self, event):
        file_path = event.data.strip("{}")
        self.display_image(file_path)

    def paste_image(self):
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                self.img_bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                self.display_image_array()
        except Exception as e:
            print("Failed to paste image:", e)

    def display_image(self, path):
        self.img_bgr = cv2.imread(path)
        self.display_image_array()

    def display_image_array(self):
        if self.img_bgr is None:
            return
        self.img_rgb = cv2.cvtColor(self.img_bgr, cv2.COLOR_BGR2RGB)
        self.img_gray = cv2.cvtColor(self.img_bgr, cv2.COLOR_BGR2GRAY)
        self.reset_zoom()
        self.update_image()

        if self.toggle_selector:
            self.toggle_selector.disconnect_events()

        self.toggle_selector = RectangleSelector(
            self.ax_original, self.on_select,
            drawtype='box', useblit=True,
            button=[1], minspanx=5, minspany=5,
            spancoords='pixels', interactive=True
        )

        self.canvas.draw()

    def update_image(self, *_):
        if self.img_rgb is None:
            return
        brightness = self.brightness_slider.get()
        contrast = self.contrast_slider.get()
        gamma = self.gamma_slider.get()

        img = self.img_rgb.astype(np.float32)
        img = img * contrast + brightness
        img = np.clip(img / 255.0, 0, 1) ** (1 / gamma)
        img = np.clip(img * 255, 0, 255).astype(np.uint8)

        self.processed_rgb = img
        self.ax_original.clear()
        self.ax_original.imshow(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY), cmap=self.orig_cmap_var.get())
        self.ax_original.set_title("Original Image")
        self.canvas.draw()

    def on_select(self, eclick, erelease):
        if self.img_gray is None:
            return
        self.x1, self.y1 = int(eclick.xdata), int(eclick.ydata)
        self.x2, self.y2 = int(erelease.xdata), int(erelease.ydata)
        roi = self.img_gray[min(self.y1, self.y2):max(self.y1, self.y2), min(self.x1, self.x2):max(self.x1, self.x2)]
        #print(self.x2 - self.x1)
        if roi.size == 0:
            return
        magnitude_spectrum = np.abs(np.fft.fftshift(np.fft.fft2(roi - roi.mean()))) ** 0.25
        self.fft_image = magnitude_spectrum
        self.update_fft()
        self.box_drawn = True

    def update_fft(self, *_):
        if self.fft_image is None:
            return
        brightness = self.fft_brightness_slider.get()
        contrast = self.fft_contrast_slider.get()
        gamma = self.fft_gamma_slider.get()

        img = self.fft_image.copy().astype(np.float32)
        img = img * contrast + brightness
        img = np.clip(img / 255.0, 0, 1) ** (1 / gamma)
        img = np.clip(img * 255, 0, 255)
        self.ax_fft.clear()
        self.ax_fft.imshow(img, cmap=self.fft_cmap_var.get())
        self.ax_fft.set_title("FFT Output")
        self.canvas.draw()

    def enable_line_mode(self):
        self.drawing_line = True
        self.start_point = None
        self.cid_click = self.canvas.mpl_connect("button_press_event", self.on_line_draw)

    def on_line_draw(self, event):
        if not self.drawing_line or event.inaxes not in [self.ax_original, self.ax_fft]:
            return
        if self.start_point is None:
            self.start_point = (event.xdata, event.ydata)
            if self.line_artist:
                self.line_artist.remove()
                self.canvas.draw()
        else:
            x0, y0 = self.start_point
            x1, y1 = event.xdata, event.ydata
            self.line_artist = Line2D([x0, x1], [y0, y1], color="cyan", linewidth=2)
            event.inaxes.add_line(self.line_artist)
            self.canvas.draw()

            pixel_dist = np.hypot(x1 - x0, y1 - y0)
            cal = self.calibration_factor.get()
            self.unit_name = self.unit_name_var.get()
            real_dist = pixel_dist * cal
            #print("the box distance is", self.x2 - self.x1)
            if self.box_drawn == True:
                reciprocal_dist = pixel_dist/((self.x2 - self.x1) * cal)
                text_fft = f" The reciprocal distance is {pixel_dist:.2f} px | {reciprocal_dist:.2f} 1/{self.unit_name}"
            
            
            text = f" The real distance is {pixel_dist:.2f} px | {real_dist:.2f} {self.unit_name}"
            

            if event.inaxes == self.ax_original:
                self.distance_label.config(text=text)
                self.spatial_calibration = cal
                self.spatial_calibrated = True
            else:
                self.fft_distance_label.config(text=text_fft)
                if self.spatial_calibrated and real_dist != 0:
                    val = 20 / reciprocal_dist
                    self.fft_calc_label.config(text=f"20/{reciprocal_dist:.2f} = {val:.2f} Ang")
            self.drawing_line = False
            self.start_point = None
            self.canvas.mpl_disconnect(self.cid_click)

    def on_scroll(self, event):
        base_scale = 1.2
        ax = event.inaxes
        if ax is None:
            return
        scale_factor = base_scale if event.step > 0 else 1 / base_scale
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        xdata, ydata = event.xdata, event.ydata
        new_xlim = [xdata - (xdata - xlim[0]) / scale_factor,
                    xdata + (xlim[1] - xdata) / scale_factor]
        new_ylim = [ydata - (ydata - ylim[0]) / scale_factor,
                    ydata + (ylim[1] - ydata) / scale_factor]
        ax.set_xlim(new_xlim)
        ax.set_ylim(new_ylim)
        self.canvas.draw()

    def reset_zoom(self):
        self.update_image()
        if self.fft_image is not None:
            self.update_fft()

    def copy_image_to_clipboard(self, pil_img):
        output = io.BytesIO()
        pil_img.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(CF_DIB, data)
        win32clipboard.CloseClipboard()

    def copy_original_to_clipboard(self):
        if self.processed_rgb is not None:
            img = cv2.cvtColor(self.processed_rgb, cv2.COLOR_RGB2BGR)
            self.copy_image_to_clipboard(Image.fromarray(img))

    def copy_fft_to_clipboard(self):
        if self.fft_image is not None:
            fft_display = self.ax_fft.images[0].make_image(self.canvas.get_renderer())[0]
            img = Image.fromarray(np.asarray(fft_display))
            self.copy_image_to_clipboard(img)

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FFTApp(root)
    root.mainloop()
