import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import sys
import os
from rename import rename_recursive
import tkinterdnd2 as tkdnd

class RepoNamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Repo Namer - GUI")
        self.root.geometry("800x600")
        
        # Variables
        self.folder_path = tk.StringVar()
        self.style_var = tk.StringVar(value="kebab")
        self.ignore_var = tk.StringVar(value=".git,node_modules,.venv")
        self.changes = []
        
        self.setup_ui()
        self.setup_drag_drop()
    
    def setup_drag_drop(self):
        # Enable drag and drop
        self.root.drop_target_register(tkdnd.DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)
        
        # Make the folder entry a drop target too
        self.folder_entry.drop_target_register(tkdnd.DND_FILES)
        self.folder_entry.dnd_bind('<<Drop>>', self.on_drop)
    
    def on_drop(self, event):
        # Get the dropped file/folder path
        files = event.data
        
        # Handle different OS formats
        if files.startswith('{'):
            # Windows format: {file1} {file2}
            files = files.strip('{}').split('} {')
        else:
            # Unix format: file1 file2
            files = files.split()
        
        if files:
            # Take the first dropped item
            dropped_path = files[0]
            
            # Convert to Path object
            path = Path(dropped_path)
            
            # Check if it's a directory
            if path.is_dir():
                self.folder_path.set(str(path))
                # Auto-preview after drop
                self.preview_changes()
            else:
                messagebox.showwarning("Warning", "Please drop a folder, not a file!")
    
    def setup_ui(self):
        # Configure font sizes
        title_font = ('Arial', 12, 'bold')
        label_font = ('Arial', 10)
        button_font = ('Arial', 10)
        entry_font = ('Arial', 10)
        output_font = ('Consolas', 10)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Folder selection
        folder_label = ttk.Label(main_frame, text="Folder to rename:", font=label_font)
        folder_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.folder_entry = ttk.Entry(main_frame, textvariable=self.folder_path, width=50, font=entry_font)
        self.folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        browse_button = ttk.Button(main_frame, text="Browse", command=self.browse_folder)
        browse_button.grid(row=0, column=2, padx=5)
        
        # Drop hint
        drop_hint = ttk.Label(main_frame, text="💡 Tip: You can also drag and drop a folder here!", 
                             font=('Arial', 9), foreground='gray')
        drop_hint.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(1, weight=1)
        
        # Naming style
        style_label = ttk.Label(options_frame, text="Naming style:", font=label_font)
        style_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        style_combo = ttk.Combobox(options_frame, textvariable=self.style_var, 
                                  values=["kebab", "snake", "lower-camel", "upper-camel"], 
                                  state="readonly", width=15, font=entry_font)
        style_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Ignore directories
        ignore_label = ttk.Label(options_frame, text="Ignore directories:", font=label_font)
        ignore_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        ignore_entry = ttk.Entry(options_frame, textvariable=self.ignore_var, width=50, font=entry_font)
        ignore_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        preview_button = ttk.Button(button_frame, text="Preview Changes", command=self.preview_changes)
        preview_button.pack(side=tk.LEFT, padx=5)
        
        apply_button = ttk.Button(button_frame, text="Apply Changes", command=self.apply_changes)
        apply_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_output)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Output area
        output_label = ttk.Label(main_frame, text="Output:", font=label_font)
        output_label.grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        
        self.output_text = scrolledtext.ScrolledText(main_frame, height=20, width=80, font=output_font)
        self.output_text.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure main frame weights
        main_frame.rowconfigure(5, weight=1)
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
    
    def preview_changes(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder first!")
            return
        
        folder_path = Path(folder)
        if not folder_path.exists():
            messagebox.showerror("Error", f"Folder does not exist: {folder}")
            return
        
        try:
            # Parse ignore directories
            ignore_dirs = None
            if self.ignore_var.get().strip():
                ignore_dirs = set(self.ignore_var.get().split(','))
            # If no ignore directories specified, use default (None will use default in rename_recursive)
            
            # Get changes
            self.changes = rename_recursive(folder_path, apply=False, 
                                          ignore_dirs=ignore_dirs, 
                                          style=self.style_var.get())
            
            # Display results
            self.output_text.delete(1.0, tk.END)
            if not self.changes:
                self.output_text.insert(tk.END, "✅ No files or folders need to be renamed.\n")
            else:
                self.output_text.insert(tk.END, f"📝 Found {len(self.changes)} items to rename:\n\n")
                for old, new in self.changes:
                    self.output_text.insert(tk.END, f"  {old} → {new}\n")
                self.output_text.insert(tk.END, f"\n⚠️ This is a preview. Click 'Apply Changes' to actually rename.\n")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def apply_changes(self):
        if not self.changes:
            messagebox.showwarning("Warning", "No changes to apply. Please preview changes first!")
            return
        
        # Confirm before applying
        result = messagebox.askyesno("Confirm", 
                                   f"Are you sure you want to rename {len(self.changes)} items?\n\n"
                                   "This action cannot be undone!")
        if not result:
            return
        
        try:
            folder = self.folder_path.get()
            folder_path = Path(folder)
            
            # Parse ignore directories
            ignore_dirs = None
            if self.ignore_var.get().strip():
                ignore_dirs = set(self.ignore_var.get().split(','))
            # If no ignore directories specified, use default (None will use default in rename_recursive)
            
            # Apply changes
            changes = rename_recursive(folder_path, apply=True, 
                                    ignore_dirs=ignore_dirs, 
                                    style=self.style_var.get())
            
            # Display results
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "✅ All changes have been applied!\n\n")
            self.output_text.insert(tk.END, f"Renamed {len(changes)} items:\n\n")
            for old, new in changes:
                self.output_text.insert(tk.END, f"  {old} → {new}\n")
            
            # Clear changes list
            self.changes = []
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        self.changes = []

def main():
    root = tkdnd.TkinterDnD.Tk()
    app = RepoNamerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 