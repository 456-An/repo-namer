import sys
import json
import csv
from datetime import datetime
from pathlib import Path
from rename import rename_recursive
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QListWidget, QListWidgetItem, QComboBox, QTextEdit, QMessageBox, QCheckBox, QStatusBar,
    QDialog, QFrame, QGroupBox, QSplitter, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QMimeData, QSize
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont, QPalette, QColor

class RulesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Naming Rules")
        self.resize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Instructions
        instructions = QLabel("Edit the JSON rules below. These rules define how special characters and patterns are converted during renaming.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; padding: 10px; background: #f5f5f5; border-radius: 5px;")
        layout.addWidget(instructions)
        
        # Text editor
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Consolas", 11))
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background: #2b2b2b;
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.text_edit)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        self.save_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #da190b;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

class DragDropWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.parent_window = parent

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("background: #e3f2fd; border: 2px dashed #2196F3; border-radius: 8px;")

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("")
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                path = urls[0].toLocalFile()
                if Path(path).is_dir():
                    self.parent_window.folder_entry.setText(path)
                    self.parent_window.preview_changes()
                else:
                    QMessageBox.warning(self, "Warning", "Please drop a folder, not a file!")

class RepoNamerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Repo Namer - GUI")
        self.resize(1000, 800)
        self.setAcceptDrops(True)
        
        # Apply modern style
        self.setStyleSheet("""
            QMainWindow {
                background: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                outline: none;
            }
            QPushButton:hover {
                background: #1976D2;
            }
            QPushButton:pressed {
                background: #0D47A1;
            }
            QPushButton:focus {
                outline: none;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
                background: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #2196F3;
            }
            QListWidget {
                border: 2px solid #ddd;
                border-radius: 4px;
                background: white;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background: #e3f2fd;
                color: #1976D2;
                border-left: 4px solid #2196F3;
            }
            QListWidget::item:hover {
                background: #f5f5f5;
            }
        """)
        
        self.current_lang = 'en'
        self.languages = {
            'en': {
                'title': 'Repo Namer - GUI',
                'folder_label': 'Folder to rename:',
                'browse': 'Browse',
                'drag_hint': '💡 Tip: Drag and drop folders anywhere in the window!',
                'options': 'Options',
                'style_label': 'Naming style:',
                'ignore_label': 'Ignore directories:',
                'preview': 'Preview Changes',
                'apply': 'Apply Changes',
                'clear': 'Clear',
                'output': 'Preview Results',
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
                'please_review': 'Please click "Preview Changes" to see the changes with new rules.',
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
                'drag_hint': '💡 提示：可以拖曳資料夾到視窗的任何地方！',
                'options': '選項',
                'style_label': '命名風格:',
                'ignore_label': '忽略資料夾:',
                'preview': '預覽變更',
                'apply': '套用變更',
                'clear': '清除',
                'output': '預覽結果',
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
                'please_review': '請點擊「預覽變更」來查看新規則的效果。',
                'select_folder': '選擇資料夾',
                'save_file': '儲存報告',
                'csv_files': 'CSV 檔案 (*.csv)',
                'json_files': 'JSON 檔案 (*.json)',
                'txt_files': '文字檔案 (*.txt)',
                'all_files': '所有檔案 (*.*)'
            }
        }
        self.folder_path = ''
        self.changes = []
        self.style_var = 'kebab'
        self.ignore_var = '.git,node_modules,.venv'
        self.report_format = 'txt'
        self.init_ui()

    def t(self, key):
        return self.languages[self.current_lang].get(key, key)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                path = urls[0].toLocalFile()
                if Path(path).is_dir():
                    self.folder_entry.setText(path)
                    self.preview_changes()
                else:
                    QMessageBox.warning(self, "Warning", "Please drop a folder, not a file!")

    def init_ui(self):
        font_title = QFont('Segoe UI', 14, QFont.Bold)
        font_label = QFont('Segoe UI', 12)
        font_entry = QFont('Segoe UI', 11)
        font_btn = QFont('Segoe UI', 11, QFont.Bold)
        font_list = QFont('Consolas', 10)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Header with Language selection
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        self.lang_label = QLabel(self.t('language'))
        self.lang_label.setFont(font_label)
        header_layout.addWidget(self.lang_label)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['English', '中文'])
        self.lang_combo.setCurrentIndex(0)
        self.lang_combo.currentIndexChanged.connect(self.update_language)
        self.lang_combo.setFont(font_entry)
        header_layout.addWidget(self.lang_combo)
        main_layout.addLayout(header_layout)

        # Folder selection group
        folder_group = QGroupBox("Folder Selection")
        folder_group.setFont(font_title)
        folder_layout = QVBoxLayout()
        folder_group.setLayout(folder_layout)
        
        # Folder input row
        folder_input_layout = QHBoxLayout()
        self.folder_label = QLabel(self.t('folder_label'))
        self.folder_label.setFont(font_label)
        folder_input_layout.addWidget(self.folder_label)
        
        self.folder_entry = QLineEdit()
        self.folder_entry.setFont(font_entry)
        self.folder_entry.setPlaceholderText("Enter folder path or drag and drop a folder here...")
        folder_input_layout.addWidget(self.folder_entry)
        
        self.browse_btn = QPushButton(self.t('browse'))
        self.browse_btn.setFont(font_btn)
        self.browse_btn.clicked.connect(self.browse_folder)
        folder_input_layout.addWidget(self.browse_btn)
        folder_layout.addLayout(folder_input_layout)
        
        # Drag hint
        self.drag_hint = QLabel(self.t('drag_hint'))
        self.drag_hint.setFont(QFont('Segoe UI', 10))
        self.drag_hint.setStyleSheet('color: #666; font-style: italic;')
        folder_layout.addWidget(self.drag_hint)
        main_layout.addWidget(folder_group)

        # Options group
        options_group = QGroupBox("Options")
        options_group.setFont(font_title)
        options_layout = QVBoxLayout()
        options_group.setLayout(options_layout)
        
        # First row: Style
        options_row1 = QHBoxLayout()
        self.style_label = QLabel(self.t('style_label'))
        self.style_label.setFont(font_label)
        options_row1.addWidget(self.style_label)
        
        self.style_combo = QComboBox()
        self.style_combo.addItems(['kebab', 'snake', 'lower-camel', 'upper-camel'])
        self.style_combo.setCurrentText(self.style_var)
        self.style_combo.setFont(font_entry)
        options_row1.addWidget(self.style_combo)
        
        options_row1.addStretch()
        options_layout.addLayout(options_row1)
        
        # Second row: Ignore directories
        options_row2 = QHBoxLayout()
        self.ignore_label = QLabel(self.t('ignore_label'))
        self.ignore_label.setFont(font_label)
        options_row2.addWidget(self.ignore_label)
        
        self.ignore_entry = QLineEdit(self.ignore_var)
        self.ignore_entry.setFont(font_entry)
        self.ignore_entry.setPlaceholderText(".git,node_modules,.venv")
        options_row2.addWidget(self.ignore_entry)
        options_layout.addLayout(options_row2)
        main_layout.addWidget(options_group)

        # Action buttons group
        actions_group = QGroupBox("Actions")
        actions_group.setFont(font_title)
        actions_layout = QVBoxLayout()
        actions_group.setLayout(actions_layout)
        
        # Main action buttons
        main_actions = QHBoxLayout()
        self.preview_btn = QPushButton(self.t('preview'))
        self.preview_btn.setFont(font_btn)
        self.preview_btn.clicked.connect(self.preview_changes)
        main_actions.addWidget(self.preview_btn)
        
        self.apply_btn = QPushButton(self.t('apply'))
        self.apply_btn.setFont(font_btn)
        self.apply_btn.clicked.connect(self.apply_changes)
        main_actions.addWidget(self.apply_btn)
        
        self.edit_rules_btn = QPushButton(self.t('edit_rules'))
        self.edit_rules_btn.setFont(font_btn)
        self.edit_rules_btn.clicked.connect(self.edit_rules)
        main_actions.addWidget(self.edit_rules_btn)
        
        main_actions.addStretch()
        
        # Report options
        self.report_label = QLabel(self.t('report_format'))
        self.report_label.setFont(font_label)
        main_actions.addWidget(self.report_label)
        
        self.report_combo = QComboBox()
        self.report_combo.addItems(['txt', 'csv', 'json'])
        self.report_combo.setCurrentText('txt')
        self.report_combo.setFont(font_entry)
        main_actions.addWidget(self.report_combo)
        
        self.save_report_btn = QPushButton(self.t('save_report'))
        self.save_report_btn.setFont(font_btn)
        self.save_report_btn.clicked.connect(self.save_report)
        main_actions.addWidget(self.save_report_btn)
        actions_layout.addLayout(main_actions)
        main_layout.addWidget(actions_group)

        # Results group
        results_group = QGroupBox(self.t('output'))
        results_group.setFont(font_title)
        results_layout = QVBoxLayout()
        results_group.setLayout(results_layout)
        
        # Results header with control buttons
        results_header = QHBoxLayout()
        
        # List widget
        self.changes_list = QListWidget()
        self.changes_list.setFont(font_list)
        self.changes_list.setSelectionMode(QListWidget.MultiSelection)
        self.changes_list.setMinimumHeight(300)
        results_layout.addWidget(self.changes_list)
        
        # Control buttons for the list
        list_controls = QHBoxLayout()
        self.clear_btn = QPushButton(self.t('clear'))
        self.clear_btn.setFont(font_btn)
        self.clear_btn.clicked.connect(self.clear_changes)
        list_controls.addWidget(self.clear_btn)
        
        self.select_all_btn = QPushButton(self.t('select_all'))
        self.select_all_btn.setFont(font_btn)
        self.select_all_btn.clicked.connect(self.select_all)
        list_controls.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton(self.t('deselect_all'))
        self.deselect_all_btn.setFont(font_btn)
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        list_controls.addWidget(self.deselect_all_btn)
        
        list_controls.addStretch()
        results_layout.addLayout(list_controls)
        main_layout.addWidget(results_group)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: #e3f2fd;
                color: #1976D2;
                padding: 5px;
                border-top: 1px solid #ddd;
            }
        """)
        self.setStatusBar(self.status_bar)

    def update_language(self):
        lang = self.lang_combo.currentText()
        self.current_lang = 'en' if lang == 'English' else 'zh'
        self.setWindowTitle(self.t('title'))
        self.folder_label.setText(self.t('folder_label'))
        self.browse_btn.setText(self.t('browse'))
        self.drag_hint.setText(self.t('drag_hint'))
        self.style_label.setText(self.t('style_label'))
        self.ignore_label.setText(self.t('ignore_label'))
        self.lang_label.setText(self.t('language'))
        self.preview_btn.setText(self.t('preview'))
        self.apply_btn.setText(self.t('apply'))
        self.clear_btn.setText(self.t('clear'))
        self.edit_rules_btn.setText(self.t('edit_rules'))
        self.select_all_btn.setText(self.t('select_all'))
        self.deselect_all_btn.setText(self.t('deselect_all'))
        self.report_label.setText(self.t('report_format'))
        self.save_report_btn.setText(self.t('save_report'))
        self.status_bar.showMessage('')

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.t('select_folder'))
        if folder:
            self.folder_entry.setText(folder)
            self.preview_changes()

    def preview_changes(self):
        folder = self.folder_entry.text().strip()
        if not folder:
            QMessageBox.critical(self, "Error", self.t('error_no_folder'))
            return
        folder_path = Path(folder)
        if not folder_path.exists():
            QMessageBox.critical(self, "Error", self.t('error_folder_not_exist').format(folder))
            return
        try:
            self.style_var = self.style_combo.currentText()
            self.ignore_var = self.ignore_entry.text().strip()
            ignore_dirs = None
            if self.ignore_var:
                ignore_dirs = set(self.ignore_var.split(','))
            self.changes = rename_recursive(folder_path, apply=False, ignore_dirs=ignore_dirs, style=self.style_var)
            self.changes_list.clear()
            if not self.changes:
                self.status_bar.showMessage(self.t('no_changes'))
            else:
                for old, new in self.changes:
                    item = QListWidgetItem(f"{old} → {new}")
                    self.changes_list.addItem(item)
                self.status_bar.showMessage(self.t('found_items').format(len(self.changes)) + ' ' + self.t('preview_warning'))
        except Exception as e:
            QMessageBox.critical(self, "Error", self.t('error_occurred').format(str(e)))

    def apply_changes(self):
        if not self.changes:
            QMessageBox.warning(self, "Warning", self.t('warning_no_changes'))
            return
        selected = self.changes_list.selectedIndexes()
        if not selected:
            items_to_apply = self.changes
        else:
            items_to_apply = [self.changes[i.row()] for i in selected]
        reply = QMessageBox.question(self, "Confirm", self.t('confirm_apply').format(len(items_to_apply)),
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        try:
            folder = self.folder_entry.text().strip()
            folder_path = Path(folder)
            self.style_var = self.style_combo.currentText()
            self.ignore_var = self.ignore_entry.text().strip()
            ignore_dirs = None
            if self.ignore_var:
                ignore_dirs = set(self.ignore_var.split(','))
            changes = rename_recursive(folder_path, apply=True, ignore_dirs=ignore_dirs, style=self.style_var)
            self.status_bar.showMessage(self.t('changes_applied') + ' ' + self.t('renamed_items').format(len(changes)))
            self.changes_list.clear()
            self.changes = []
        except Exception as e:
            QMessageBox.critical(self, "Error", self.t('error_occurred').format(str(e)))

    def clear_changes(self):
        self.changes_list.clear()
        self.changes = []
        self.status_bar.showMessage('')

    def select_all(self):
        self.changes_list.selectAll()

    def deselect_all(self):
        self.changes_list.clearSelection()

    def save_report(self):
        if not self.changes:
            QMessageBox.warning(self, "Warning", self.t('warning_no_changes'))
            return
        report_format = self.report_combo.currentText()
        if report_format == 'csv':
            ext, filter_str = '.csv', self.t('csv_files')
        elif report_format == 'json':
            ext, filter_str = '.json', self.t('json_files')
        else:
            ext, filter_str = '.txt', self.t('txt_files')
        filename, _ = QFileDialog.getSaveFileName(self, self.t('save_file'), f'report{ext}', f'{filter_str};;{self.t("all_files")}')
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
                        'folder': self.folder_entry.text().strip(),
                        'style': self.style_var,
                        'ignore_dirs': self.ignore_var,
                        'changes': [
                            {'old': str(old), 'new': str(new)}
                            for old, new in self.changes
                        ]
                    }
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(report_data, f, indent=2, ensure_ascii=False)
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"Repo Namer Report\n")
                        f.write(f"Generated: {datetime.now()}\n")
                        f.write(f"Folder: {self.folder_entry.text().strip()}\n")
                        f.write(f"Style: {self.style_var}\n")
                        f.write(f"Ignore: {self.ignore_var}\n\n")
                        f.write(f"Changes ({len(self.changes)} items):\n")
                        for old, new in self.changes:
                            f.write(f"  {old} → {new}\n")
                QMessageBox.information(self, "Info", f"Report saved to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving report: {str(e)}")

    def edit_rules(self):
        try:
            with open('rules.json', 'r', encoding='utf-8') as f:
                current_rules = json.load(f)
            
            dialog = RulesDialog(self)
            dialog.text_edit.setText(json.dumps(current_rules, indent=2, ensure_ascii=False))
            
            if dialog.exec() == QDialog.Accepted:
                try:
                    new_rules = json.loads(dialog.text_edit.toPlainText())
                    with open('rules.json', 'w', encoding='utf-8') as f:
                        json.dump(new_rules, f, indent=2, ensure_ascii=False)
                    
                    # Reload rules in cleaner module
                    from cleaner import reload_rules
                    reload_rules()
                    
                    QMessageBox.information(self, "Info", self.t('rules_updated') + "\n\n" + self.t('please_review'))
                except Exception as e:
                    QMessageBox.critical(self, "Error", f'Error saving rules: {str(e)}')
        except Exception as e:
            QMessageBox.critical(self, "Error", f'Error loading rules: {str(e)}')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RepoNamerWindow()
    window.show()
    sys.exit(app.exec()) 