# 🧹 repo-namer

> A Python CLI tool to clean and standardize folder and file names by applying customizable naming rules

---

## 🚀 Features

- 🔡 Convert all folder and file names to lowercase
- ✨ Remove or convert special symbols (e.g., `C++ → cpp`, `C# → csharp`)
- 🔁 Recursively process entire folders
- 🕵️‍♂️ Default is dry-run mode: preview changes only (use `--apply` to actually rename)
- 🛠️ Customizable rules via `rules.json`

---

## 📦 Installation

> Requires only Python 3, no extra packages needed

---

## 📝 CLI Options

| Option           | Description                              | Example                  | Default                |
|------------------|------------------------------------------|--------------------------|------------------------|
| `--apply`        | Actually rename files/folders (otherwise dry-run) | `--apply`                | dry-run (preview only) |
| `--ignore`       | Ignore specific folders (comma-separated) | `--ignore .git,node_modules` | `.git,node_modules,.venv` |
| `--report`       | Output change log to file                 | `--report log.txt`       | None                   |
| `--git`          | Use git mv instead of os.rename (for git repos) | `--git`                  | use os.rename          |
| `--style`        | Naming style (`kebab`, `snake`, `lower-camel`, `upper-camel`) | `--style snake`          | kebab                  |

---

## ⚡ Usage Examples

```bash
# 1. Preview changes (dry-run)
python rename.py test-folder

# 2. Actually rename
python rename.py test-folder --apply

# 3. Ignore specific folders (comma-separated, overrides default)
python rename.py test-folder --ignore .git,node_modules,dist,build

# 4. Output change log to report.txt
python rename.py test-folder --report report.txt

# 5. Combine multiple options
python rename.py test-folder --apply --ignore .git,node_modules,dist --report log.txt

# 6. Use git mv in a git repo
python rename.py test-folder --apply --git

# 7. Choose naming style
python rename.py test-folder --style kebab        # my-folder-name (default)
python rename.py test-folder --style snake        # my_folder_name
python rename.py test-folder --style lower-camel  # myFolderName
python rename.py test-folder --style upper-camel  # MyFolderName
```

---

## 💡 Tips

- If `--ignore` is not specified, `.git`, `node_modules`, `.venv` are ignored by default
- To not ignore any folder, use an empty string:
  ```bash
  python rename.py test-folder --ignore ""
  ```
- If `--report` is specified, all changes (old → new) are written to the file
- If `--git` is specified, `git mv` is used (for git repos)
- If `--style` is specified, you can choose naming style:
  - `kebab`: my-folder-name (default)
  - `snake`: my_folder_name
  - `lower-camel`: myFolderName
  - `upper-camel`: MyFolderName

---

## 📂 Custom Rules

- Edit `rules.json` to customize naming rules
- Example:
  ```json
  {
    "c#": "csharp",
    "c++": "cpp",
    " ": "-",
    "+": "",
    "#": "",
    "&": "and"
  }
  ```

---

## 🧪 Test Folder

- `test-folder/` contains various messy-named folders/files for testing

---

## 🖥️ GUI Version

For users who prefer a graphical interface, you can also use the GUI version:

```bash
python gui.py
```

### GUI Features
- 📁 Browse and select folders visually
- 👀 Preview all changes before applying
- ⚙️ Configure naming style and ignore directories
- ✅ Apply changes with confirmation dialog
- 📝 View detailed output in scrollable text area
- 🎯 Drag and drop folders directly into the GUI
- 🔄 Auto-preview after drag and drop

---

## 📝 License

MIT License

---

# 🧹 repo-namer（中文版）

> 自動清理與統一檔案／資料夾命名的 Python CLI 工具

---

## 🚀 特色功能

- 🔡 將資料夾與檔案名稱轉為小寫
- ✨ 移除或轉換特殊符號（如 `C++ → cpp`, `C# → csharp`）
- 🔁 遞迴處理整個資料夾
- 🕵️‍♂️ 預設為模擬模式，僅預覽將修改的項目（加上 `--apply` 才會實際改名）
- 🛠️ 可自訂規則 via `rules.json`

---

## 📦 安裝方式

> 只需 Python 3，免安裝額外套件

---

## 📝 參數總覽

| 參數             | 說明                                 | 型態/範例                | 預設值                |
|------------------|--------------------------------------|--------------------------|-----------------------|
| `--apply`        | 實際執行命名修改（不加只預覽）       | `--apply`                | 不加則為模擬模式      |
| `--ignore`       | 忽略特定資料夾（逗號分隔）           | `--ignore .git,node_modules` | `.git,node_modules,.venv` |
| `--report`       | 輸出修改報告到檔案                   | `--report log.txt`       | 無                    |
| `--git`          | 用 git mv 取代 os.rename（git 專案用）| `--git`                  | 不加則用 os.rename    |
| `--style`        | 命名格式（kebab、snake、lower-camel、upper-camel） | `--style snake`          | kebab                 |

---

## ⚡ 常見用法

```bash
# 1. 預覽會修改哪些檔案（模擬模式）
python rename.py test-folder

# 2. 實際執行命名修改
python rename.py test-folder --apply

# 3. 自訂要忽略的資料夾（用逗號分隔，會取代預設 .git,node_modules,.venv）
python rename.py test-folder --ignore .git,node_modules,dist,build

# 4. 輸出修改報告到 report.txt
python rename.py test-folder --report report.txt

# 5. 同時指定多個參數
python rename.py test-folder --apply --ignore .git,node_modules,dist --report log.txt

# 6. 在 git 專案中使用 git mv（保持 git 追蹤）
python rename.py test-folder --apply --git

# 7. 選擇不同的命名格式
python rename.py test-folder --style kebab        # my-folder-name（預設）
python rename.py test-folder --style snake        # my_folder_name
python rename.py test-folder --style lower-camel  # myFolderName
python rename.py test-folder --style upper-camel  # MyFolderName
```

---

## 💡 小提醒

- 未指定 `--ignore` 時，預設會忽略 `.git`、`node_modules`、`.venv`
- 不忽略任何資料夾可輸入空字串：
  ```bash
  python rename.py test-folder --ignore ""
  ```
- 指定 `--report` 會將所有將修改的項目（舊 → 新）輸出到指定檔案
- 指定 `--git` 會使用 `git mv`，適合在 git 專案中使用
- 指定 `--style` 可選擇命名格式：
  - `kebab`：my-folder-name（預設）
  - `snake`：my_folder_name
  - `lower-camel`：myFolderName
  - `upper-camel`：MyFolderName

---

## 📂 規則自訂

- 修改 `rules.json` 可自訂命名轉換規則
- 範例：
  ```json
  {
    "c#": "csharp",
    "c++": "cpp",
    " ": "-",
    "+": "",
    "#": "",
    "&": "and"
  }
  ```

---

## 🧪 測試資料夾

- `test-folder/` 內含多種亂命名資料夾與檔案，方便測試

---

## 🖥️ GUI 版本

對於偏好圖形化介面的使用者，也可以使用 GUI 版本：

```bash
python gui.py
```

### GUI 功能
- 📁 視覺化瀏覽與選擇資料夾
- 👀 在套用前預覽所有變更
- ⚙️ 設定命名風格與忽略資料夾
- ✅ 透過確認對話框套用變更
- 📝 在可捲動文字區域查看詳細輸出
- 🎯 直接拖曳資料夾到 GUI 中
- 🔄 拖曳後自動預覽變更

---

## 📝 授權

MIT License
