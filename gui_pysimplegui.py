import PySimpleGUI as sg
import json
import os
from pathlib import Path
from rename import rename_recursive
import csv
from datetime import datetime

class ModernRepoNamerGUI:
    def __init__(self):
        # Set theme
        sg.theme('LightBlue2')
        
        # Language settings
        self.current_lang = 'en'
        self.languages = {
            'en': {
                'title': 'Repo Namer - GUI',
                'folder_label': 'Folder to rename:',
                'browse': 'Browse',
                'drag_hint': '💡 Tip: Drag and drop folders here!',
                'options': 'Options',
                'style_label': 'Naming style:',
                'ignore_label': 'Ignore directories:',
                'preview': 'Preview Changes',
                'apply': 'Apply Changes',
                'clear': 'Clear',
                'output': 'Output',
                'select_all': 'Select All',
                'deselect_all': 'Deselect All',
                'report_format': 'Report Format:',
                'save_report': 'Save Report',
                'edit_rules': 'Edit Rules',
                'language': 'Language:',
                'no_changes': '✅ No files or folders need to be renamed.',
                'found_items': '📝 Found {} items to rename:',
                'preview_warning': '⚠️ This is a preview. Click "Apply Changes" to actually rename.',
                'confirm_apply': 'Are you sure you want to rename {} items?\n\nThis action cannot be undone!',
                'changes_applied': '✅ All changes have been applied!',
                'renamed_items': 'Renamed {} items:',
                'error_no_folder': 'Please select a folder first!',
                'error_folder_not_exist': 'Folder does not exist: {}',
                'warning_no_changes': 'No changes to apply. Please preview changes first!',
                'error_occurred': 'An error occurred: {}',
                'rules_updated': 'Rules updated successfully!',
                'select_folder': 'Select Folder',
                'save_file': 'Save Report',
                'csv_files': 'CSV files (*.csv)',
                'json_files': 'JSON files (*.json)',
                'txt_files': 'Text files (*.txt)',
                'all_files': 'All files (*.*)'
            },
            'zh': {
                'title': 'Repo Namer - GUI',
                'folder_label': '要重命名的資料夾:',
                'browse': '瀏覽',
                'drag_hint': '💡 提示：可以拖曳資料夾到這裡！',
                'options': '選項',
                'style_label': '命名風格:',
                'ignore_label': '忽略資料夾:',
                'preview': '預覽變更',
                'apply': '套用變更',
                'clear': '清除',
                'output': '輸出',
                'select_all': '全選',
                'deselect_all': '取消全選',
                'report_format': '報告格式:',
                'save_report': '儲存報告',
                'edit_rules': '編輯規則',
                'language': '語言:',
                'no_changes': '✅ 沒有需要重命名的檔案或資料夾。',
                'found_items': '📝 找到 {} 個項目需要重命名:',
                'preview_warning': '⚠️ 這是預覽。點擊「套用變更」才會實際重命名。',
                'confirm_apply': '確定要重命名 {} 個項目嗎？\n\n此操作無法復原！',
                'changes_applied': '✅ 所有變更已套用！',
                'renamed_items': '已重命名 {} 個項目:',
                'error_no_folder': '請先選擇資料夾！',
                'error_folder_not_exist': '資料夾不存在: {}',
                'warning_no_changes': '沒有變更可套用。請先預覽變更！',
                'error_occurred': '發生錯誤: {}',
                'rules_updated': '規則更新成功！',
                'select_folder': '選擇資料夾',
                'save_file': '儲存報告',
                'csv_files': 'CSV 檔案 (*.csv)',
                'json_files': 'JSON 檔案 (*.json)',
                'txt_files': '文字檔案 (*.txt)',
                'all_files': '所有檔案 (*.*)'
            }
        }
        
        # Variables
        self.folder_path = ''
        self.changes = []
        self.selected_items = set()
        self.style_var = 'kebab'
        self.ignore_var = '.git,node_modules,.venv'
        self.report_format = 'txt'
        
        self.setup_layout()
    
    def t(self, key):
        """Get translated text"""
        return self.languages[self.current_lang].get(key, key)
    
    def setup_layout(self):
        # Main layout
        layout = [
            # Title
            [sg.Text(self.t('title'), font=('Arial', 16, 'bold'), justification='center', expand_x=True)],
            
            # Folder selection
            [sg.Text(self.t('folder_label'), size=(15, 1)), 
             sg.Input(key='-FOLDER-', size=(50, 1), enable_events=True),
             sg.Button(self.t('browse'), key='-BROWSE-')],
            
            # Drag hint
            [sg.Text(self.t('drag_hint'), font=('Arial', 9), text_color='gray')],
            
            # Options frame
            [sg.Frame(self.t('options'), [
                [sg.Text(self.t('style_label'), size=(15, 1)),
                 sg.Combo(['kebab', 'snake', 'lower-camel', 'upper-camel'], 
                         default_value=self.style_var, key='-STYLE-', size=(20, 1))],
                [sg.Text(self.t('ignore_label'), size=(15, 1)),
                 sg.Input(default_text=self.ignore_var, key='-IGNORE-', size=(50, 1))],
                [sg.Text(self.t('language'), size=(15, 1)),
                 sg.Combo(['English', '中文'], default_value='English', key='-LANG-', 
                         enable_events=True, size=(20, 1))]
            ])],
            
            # Action buttons
            [sg.Button(self.t('preview'), key='-PREVIEW-', size=(12, 1)),
             sg.Button(self.t('apply'), key='-APPLY-', size=(12, 1)),
             sg.Button(self.t('clear'), key='-CLEAR-', size=(12, 1)),
             sg.Button(self.t('edit_rules'), key='-RULES-', size=(12, 1))],
            
            # Selection buttons
            [sg.Button(self.t('select_all'), key='-SELECT_ALL-', size=(12, 1)),
             sg.Button(self.t('deselect_all'), key='-DESELECT_ALL-', size=(12, 1))],
            
            # Report options
            [sg.Text(self.t('report_format'), size=(15, 1)),
             sg.Combo(['txt', 'csv', 'json'], default_value='txt', key='-REPORT_FORMAT-', size=(10, 1)),
             sg.Button(self.t('save_report'), key='-SAVE_REPORT-', size=(12, 1))],
            
            # Changes list
            [sg.Text(self.t('output'), font=('Arial', 12, 'bold'))],
            [sg.Listbox(values=[], key='-CHANGES-', size=(80, 15), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                       enable_events=True)],
            
            # Status bar
            [sg.Text('', key='-STATUS-', size=(80, 1))]
        ]
        
        self.window = sg.Window(self.t('title'), layout, resizable=True, finalize=True)
        
        # Enable drag and drop
        self.window['-FOLDER-'].bind('<Drop>', '_DROP')
    
    def update_language(self):
        """Update GUI language"""
        if self.window['-LANG-'].get() == 'English':
            self.current_lang = 'en'
        else:
            self.current_lang = 'zh'
        
        # Update window title
        self.window.set_title(self.t('title'))
    
    def browse_folder(self):
        """Browse for folder"""
        folder = sg.popup_get_folder(self.t('select_folder'))
        if folder:
            self.window['-FOLDER-'].update(folder)
            self.folder_path = folder
    
    def preview_changes(self):
        """Preview changes"""
        folder = self.window['-FOLDER-'].get()
        if not folder:
            sg.popup_error(self.t('error_no_folder'))
            return
        
        folder_path = Path(folder)
        if not folder_path.exists():
            sg.popup_error(self.t('error_folder_not_exist').format(folder))
            return
        
        try:
            # Get options
            self.style_var = self.window['-STYLE-'].get()
            self.ignore_var = self.window['-IGNORE-'].get()
            
            # Parse ignore directories
            ignore_dirs = None
            if self.ignore_var.strip():
                ignore_dirs = set(self.ignore_var.split(','))
            
            # Get changes
            self.changes = rename_recursive(folder_path, apply=False, 
                                          ignore_dirs=ignore_dirs, 
                                          style=self.style_var)
            
            # Update changes list
            changes_list = []
            for old, new in self.changes:
                changes_list.append(f"{old} → {new}")
            
            self.window['-CHANGES-'].update(values=changes_list)
            
            # Update status
            if not self.changes:
                self.window['-STATUS-'].update(self.t('no_changes'))
            else:
                self.window['-STATUS-'].update(
                    self.t('found_items').format(len(self.changes)) + 
                    ' ' + self.t('preview_warning')
                )
                
        except Exception as e:
            sg.popup_error(self.t('error_occurred').format(str(e)))
    
    def apply_changes(self):
        """Apply changes"""
        if not self.changes:
            sg.popup_error(self.t('warning_no_changes'))
            return
        
        # Get selected items
        selected_indices = self.window['-CHANGES-'].get_indexes()
        if not selected_indices:
            # If nothing selected, apply all
            items_to_apply = self.changes
        else:
            # Apply only selected items
            items_to_apply = [self.changes[i] for i in selected_indices]
        
        # Confirm
        result = sg.popup_yes_no(
            self.t('confirm_apply').format(len(items_to_apply))
        )
        if result != 'Yes':
            return
        
        try:
            folder = self.window['-FOLDER-'].get()
            folder_path = Path(folder)
            
            # Parse ignore directories
            ignore_dirs = None
            if self.ignore_var.strip():
                ignore_dirs = set(self.ignore_var.split(','))
            
            # Apply changes (we'll need to modify rename_recursive to accept specific items)
            # For now, apply all changes
            changes = rename_recursive(folder_path, apply=True, 
                                    ignore_dirs=ignore_dirs, 
                                    style=self.style_var)
            
            # Update status
            self.window['-STATUS-'].update(
                self.t('changes_applied') + ' ' + 
                self.t('renamed_items').format(len(changes))
            )
            
            # Clear changes
            self.changes = []
            self.window['-CHANGES-'].update(values=[])
            
        except Exception as e:
            sg.popup_error(self.t('error_occurred').format(str(e)))
    
    def save_report(self):
        """Save report to file"""
        if not self.changes:
            sg.popup_error(self.t('warning_no_changes'))
            return
        
        report_format = self.window['-REPORT_FORMAT-'].get()
        
        # Get file extension
        if report_format == 'csv':
            file_types = (self.t('csv_files'), '*.csv')
        elif report_format == 'json':
            file_types = (self.t('json_files'), '*.json')
        else:
            file_types = (self.t('txt_files'), '*.txt')
        
        filename = sg.popup_get_file(
            self.t('save_file'),
            save_as=True,
            file_types=(file_types, (self.t('all_files'), '*.*'))
        )
        
        if filename:
            try:
                if report_format == 'csv':
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Old Path', 'New Path'])
                        for old, new in self.changes:
                            writer.writerow([str(old), str(new)])
                
                elif report_format == 'json':
                    report_data = {
                        'timestamp': datetime.now().isoformat(),
                        'folder': self.window['-FOLDER-'].get(),
                        'style': self.style_var,
                        'ignore_dirs': self.ignore_var,
                        'changes': [
                            {'old': str(old), 'new': str(new)} 
                            for old, new in self.changes
                        ]
                    }
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(report_data, f, indent=2, ensure_ascii=False)
                
                else:  # txt
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"Repo Namer Report\n")
                        f.write(f"Generated: {datetime.now()}\n")
                        f.write(f"Folder: {self.window['-FOLDER-'].get()}\n")
                        f.write(f"Style: {self.style_var}\n")
                        f.write(f"Ignore: {self.ignore_var}\n\n")
                        f.write(f"Changes ({len(self.changes)} items):\n")
                        for old, new in self.changes:
                            f.write(f"  {old} → {new}\n")
                
                sg.popup_ok(f"Report saved to {filename}")
                
            except Exception as e:
                sg.popup_error(f"Error saving report: {str(e)}")
    
    def edit_rules(self):
        """Edit rules.json"""
        try:
            with open('rules.json', 'r', encoding='utf-8') as f:
                current_rules = json.load(f)
            
            # Create rules editing window
            rules_layout = [
                [sg.Text('Edit Naming Rules (JSON format):')],
                [sg.Multiline(default_text=json.dumps(current_rules, indent=2), 
                             key='-RULES_TEXT-', size=(60, 15))],
                [sg.Button('Save'), sg.Button('Cancel')]
            ]
            
            rules_window = sg.Window('Edit Rules', rules_layout, modal=True)
            
            while True:
                event, values = rules_window.read()
                
                if event == sg.WIN_CLOSED or event == 'Cancel':
                    break
                elif event == 'Save':
                    try:
                        new_rules = json.loads(values['-RULES_TEXT-'])
                        with open('rules.json', 'w', encoding='utf-8') as f:
                            json.dump(new_rules, f, indent=2, ensure_ascii=False)
                        sg.popup_ok(self.t('rules_updated'))
                        break
                    except json.JSONDecodeError:
                        sg.popup_error('Invalid JSON format!')
                    except Exception as e:
                        sg.popup_error(f'Error saving rules: {str(e)}')
            
            rules_window.close()
            
        except Exception as e:
            sg.popup_error(f'Error loading rules: {str(e)}')
    
    def run(self):
        """Main event loop"""
        while True:
            event, values = self.window.read()
            
            if event == sg.WIN_CLOSED:
                break
            elif event == '-BROWSE-':
                self.browse_folder()
            elif event == '-PREVIEW-':
                self.preview_changes()
            elif event == '-APPLY-':
                self.apply_changes()
            elif event == '-CLEAR-':
                self.window['-CHANGES-'].update(values=[])
                self.window['-STATUS-'].update('')
                self.changes = []
            elif event == '-SELECT_ALL-':
                self.window['-CHANGES-'].set_value([i for i in range(len(self.changes))])
            elif event == '-DESELECT_ALL-':
                self.window['-CHANGES-'].set_value([])
            elif event == '-SAVE_REPORT-':
                self.save_report()
            elif event == '-RULES-':
                self.edit_rules()
            elif event == '-LANG-':
                self.update_language()
            elif event == '-FOLDER-_DROP':
                # Handle drag and drop
                if values['-FOLDER-']:
                    path = Path(values['-FOLDER-'])
                    if path.is_dir():
                        self.window['-FOLDER-'].update(str(path))
                        self.folder_path = str(path)
                        # Auto-preview
                        self.preview_changes()
                    else:
                        sg.popup_error('Please drop a folder, not a file!')
        
        self.window.close()

def main():
    app = ModernRepoNamerGUI()
    app.run()

if __name__ == "__main__":
    main() 