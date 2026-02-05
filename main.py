import fitz # From PyMuPDF (https://github.com/pymupdf/PyMuPDF)
import os
import sys
import threading
from tkinter import Tk, filedialog, messagebox, Label, Button, Frame, StringVar, Toplevel
from tkinter.ttk import Progressbar, Style, Combobox

background_color = "#0F172A"
frame_color = "#1E293B"
accent_color = "#06B6D4"
button_color = "#0EA5E9"
text_color = "#F1F5F9"
empty_color = "#334155"
hover_color = "#0284C7"
progress_bg_color = "#FFFFFF"
progress_text_color = "#1E293B"
progress_bar_color = "#0EA5E9"
progress_trough_color = "#E2E8F0"

window_title = "Triceratops PDF to Image"
window_width = 650
window_height = 700
window_resizable = False

selected_theme = "vista"

class PDFConverter:
    def __init__(self, root):
        self.root = root
        self.root.title(window_title)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)

        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.resizable(False, False)
        
        # Set icon
        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, 'assets', 'app.ico')
            else:
                icon_path = './assets/app.ico'

            self.root.iconbitmap(icon_path)
    
        except:
            pass
        
        self.root.configure(bg=background_color)

        # Vars
        self.pdf_path = StringVar(value="No input selected")
        self.output_dir = StringVar(value="No output selected")
        self.quality_var = StringVar(value="High (300 DPI)")
        
        style = Style()
        style.theme_use(selected_theme)
        
        # Configure Combobox style to match theme
        style.configure("Custom.TCombobox",
                       fieldbackground=empty_color,
                       background=button_color,
                       foreground=text_color,
                       arrowcolor=text_color,
                       bordercolor=empty_color,
                       lightcolor=empty_color,
                       darkcolor=empty_color,
                       selectbackground=button_color,
                       selectforeground=text_color)
        style.map("Custom.TCombobox",
                 fieldbackground=[("readonly", empty_color)],
                 selectbackground=[("readonly", empty_color)],
                 selectforeground=[("readonly", text_color)],
                 foreground=[("readonly", text_color)])
        
        header = Frame(self.root, bg=frame_color, height=120)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        title = Label(header, text="PDF to Image", font=("Segoe UI", 24, "bold"), bg=frame_color, fg=text_color)
        title.pack(pady=(20, 5))
        
        subtitle = Label(header, text="Made by @TriceratopsGang", font=("Segoe UI", 12), bg=frame_color, fg=text_color)
        subtitle.pack()
        
        content = Frame(self.root, bg=frame_color)
        content.pack(fill="both", expand=True, padx=20, pady=(20, 20))
        
        # PDF Selection
        pdf_frame = Frame(content, bg=frame_color)
        pdf_frame.pack(fill="x", padx=10, pady=(10, 10))
        
        Label(pdf_frame, text="PDF File:", font=("Segoe UI", 12, "bold"), bg=frame_color, fg=text_color).pack(anchor="w", pady=(0, 8))
        
        # Display box
        pdf_display_frame = Frame(pdf_frame, bg=empty_color, relief="flat", bd=0)
        pdf_display_frame.pack(fill="x", pady=(0, 12))
        
        pdf_display = Label(pdf_display_frame, textvariable=self.pdf_path, font=("Segoe UI", 12), bg=background_color, fg=text_color, anchor="w", padx=16, pady=12)
        pdf_display.pack(fill="x")
        
        pdf_btn = Button(pdf_frame, text="Select PDF File", 
                        command=self.select_pdf,
                        font=("Segoe UI", 11, "bold"),
                        bg=button_color, fg=text_color,
                        activebackground=accent_color,
                        activeforeground=text_color,
                        relief="flat", pady=12,
                        cursor="hand2", bd=0)
        pdf_btn.pack(fill="x")

        # Output Folder
        output_frame = Frame(content, bg=frame_color)
        output_frame.pack(fill="x", padx=10, pady=(10, 10))
        
        Label(output_frame, text="Output Folder:", font=("Segoe UI", 12, "bold"), bg=frame_color, fg=text_color).pack(anchor="w", pady=(0, 8))
        
        # Display box
        output_display_frame = Frame(output_frame, bg=empty_color, relief="flat", bd=0)
        output_display_frame.pack(fill="x", pady=(0, 12))
        
        output_display = Label(output_display_frame, textvariable=self.output_dir, font=("Segoe UI", 12), bg=background_color, fg=text_color, anchor="w", padx=16, pady=12)
        output_display.pack(fill="x")
        
        output_btn = Button(output_frame, text="Select Output Folder", 
                           command=self.select_output,
                           font=("Segoe UI", 11, "bold"),
                           bg=button_color, fg=text_color,
                           activebackground=accent_color,
                           activeforeground=text_color,
                           relief="flat", pady=12,
                           cursor="hand2", bd=0)
        output_btn.pack(fill="x")

        # Quality Selection
        quality_frame = Frame(content, bg=frame_color)
        quality_frame.pack(fill="x", padx=10, pady=(10, 10))
        
        Label(quality_frame, text="Image Quality:", font=("Segoe UI", 12, "bold"), bg=frame_color, fg=text_color).pack(anchor="w", pady=(0, 8))
        
        quality_combo = Combobox(quality_frame, textvariable=self.quality_var, 
                                values=["Screen (72 DPI)", "Standard (150 DPI)", "High (300 DPI)", "Print Quality (600 DPI)", "Maximum (1200 DPI)"],
                                state="readonly", font=("Segoe UI", 11), height=10, style="Custom.TCombobox")
        quality_combo.pack(fill="x", pady=(0, 12))
        
        quality_info = Label(quality_frame, text="Higher quality = larger files & slower conversion", 
                           font=("Segoe UI", 9, "italic"), bg=frame_color, fg=text_color)
        quality_info.pack(anchor="w")

        # Convert Button
        self.convert_btn = Button(content, text="Convert to Image/s", 
                                 command=self.start_conversion,
                                 font=("Segoe UI", 12, "bold"),
                                 bg=button_color, fg=text_color,
                                 activebackground=accent_color,
                                 activeforeground=text_color,
                                 relief="flat", pady=16,
                                 cursor="hand2", bd=0,
                                 state="disabled")
        self.convert_btn.pack(fill="x", pady=(20, 0))
    
    def select_pdf(self):
        file_path = filedialog.askopenfilename(title="Select PDF file", filetypes=[("PDF files", "*.pdf")])

        if file_path:
            self.pdf_path.set(file_path)
            self.check_ready()
    
    def select_output(self):
        folder_path = filedialog.askdirectory(title="Select output folder")

        if folder_path:
            self.output_dir.set(folder_path)
            self.check_ready()
    
    def check_ready(self):
        if (self.pdf_path.get() != "No input selected" and 
            self.output_dir.get() != "No output selected"):
            self.convert_btn.config(state="normal", bg=button_color, fg=text_color)
        else:
            self.convert_btn.config(state="disabled", bg=empty_color, fg=text_color)

    def start_conversion(self):

        # Disable button during conversion
        self.convert_btn.config(state="disabled", bg=empty_color, fg="#94A3B8")

        # Create progress window using Toplevel
        self.progress_win = Toplevel(self.root)
        self.progress_win.title("Converting...")
        self.progress_win.geometry("450x180")
        self.progress_win.resizable(False, False)
        self.progress_win.configure(bg=progress_bg_color)
        
        # Center window
        self.progress_win.update_idletasks()

        x = (self.progress_win.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.progress_win.winfo_screenheight() // 2) - (180 // 2)

        self.progress_win.geometry(f"450x180+{x}+{y}")

        Label(self.progress_win, text="Converting PDF to Image/s", font=("Segoe UI", 14, "bold"), bg=progress_bg_color, fg=progress_text_color).pack(pady=(25, 5))

        self.progress_label = Label(self.progress_win, text="Initializing...", font=("Segoe UI", 10), bg=progress_bg_color, fg="#64748B")
        self.progress_label.pack(pady=(0, 15))
        
        style = Style()
        style.configure("Custom.Horizontal.TProgressbar", 
                       troughcolor=progress_trough_color,
                       background=progress_bar_color,
                       bordercolor=progress_trough_color,
                       lightcolor=progress_bar_color,
                       darkcolor=progress_bar_color,
                       thickness=25)
        
        self.progress_bar = Progressbar(self.progress_win, 
                                       orient="horizontal", 
                                       length=380, 
                                       mode="determinate",
                                       style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(pady=(0, 25))

        # Start thread
        threading.Thread(target=self.convert_pdf, daemon=True).start()

    def convert_pdf(self):
        try:
            quality_map = {
                "Screen (72 DPI)": 72,
                "Standard (150 DPI)": 150,
                "High (300 DPI)": 300,
                "Print Quality (600 DPI)": 600,
                "Maximum (1200 DPI)": 1200
            }
            dpi = quality_map[self.quality_var.get()]
            
            doc = fitz.open(self.pdf_path.get())
            total_pages = len(doc)

            self.progress_bar["maximum"] = total_pages
    
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=dpi)
                image_path = os.path.join(self.output_dir.get(), f'page_{page_num + 1}.png')
                pix.save(image_path)
                
                self.progress_bar["value"] = page_num + 1
                self.progress_label.config(text=f"Processing page {page_num + 1} of {total_pages}")
                self.progress_win.update_idletasks()
            
            doc.close()

            self.progress_win.destroy()

            messagebox.showinfo("Success", f"Successfully converted {total_pages} pages at {dpi} DPI!\n\nSaved to:\n{self.output_dir.get()}")
            
            # Re-enable button
            self.convert_btn.config(state="normal", bg=button_color, fg=text_color)
            
        except Exception as e:
            self.progress_win.destroy()

            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

            self.convert_btn.config(state="normal", bg=button_color, fg=text_color)

# Run
if __name__ == "__main__":
    root = Tk()

    app = PDFConverter(root)
    app.check_ready()

    root.mainloop()