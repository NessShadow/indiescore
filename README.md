
# 📖 IndieScore — README

## Overview

**IndieScore** is an automated exam scoring system that processes multiple-choice answer sheets. It supports both:

* **Web app** (Streamlit) for browser-based usage.
* **Desktop app** (Tauri) for offline use on Windows, macOS, and Linux.
* **CLI mode** for advanced users.

---

## ✨ Features

* Upload and manage answer keys
* Upload scanned answer sheets (PDF/PNG/JPG)
* Automatic calibration and scoring
* Export results to CSV/Excel
* Works online (Web) or offline (Desktop)

---

## 📦 Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-org/indiescore.git
cd indiescore
```

### 2. Python Setup (Backend)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

# Install dependencies
pip install -r requirements.txt
```

### 3. Web Interface (Streamlit)

```bash
cd ui
pip install -r requirements.txt   # if UI has extra deps
streamlit run app.py
```

Then open the link shown in the terminal (usually `http://localhost:8501`).

### 4. Desktop Interface (Tauri)

> Requires **Node.js** and **Rust** installed.

```bash
cd ui
npm install
npm run tauri dev
```

This launches the desktop app locally. To build an installer:

```bash
npm run tauri build
```

### 5. CLI Mode (Hybrid Scorer)

```bash
python main_hybrid.py --config config/example.yaml --input ./read_ans --output ./results
```

---

## 🚀 Usage

### Step 1 — Prepare Answer Key

* Place your answer key (YAML/JSON) inside the `config/` folder.
* Or use the **Answer Key Manager** in the UI to create one.

### Step 2 — Upload Answer Sheets

* Scan all sheets at **300 DPI**.
* Place them in the `read_ans/` folder.
* Supported formats: **PDF, JPG, PNG**.

### Step 3 — Run Scoring

* **Web/Desktop:** Use the **Upload Sheets** button → click **Start Scoring**.
* **CLI:** Run `main_hybrid.py` with the proper config.

### Step 4 — View Results

* Scores appear in the **Results Panel**.
* Export results via the UI or check the `results/` folder (CSV/Excel).

---

## 🛠 Troubleshooting

| Problem             | Solution                                              |
| ------------------- | ----------------------------------------------------- |
| App doesn’t start   | Check Python/Node.js versions, reinstall dependencies |
| Sheets not detected | Ensure they are in `read_ans/` and correctly scanned  |
| Wrong scores        | Verify correct answer key is selected                 |
| Export fails        | Make sure you have write permissions in `results/`    |

---

## 📂 Project Structure

```
indiescore-main/
├── main_hybrid.py         # CLI entry point
├── hybrid_scorer.py       # Scoring logic
├── answer_key_manager.py  # Answer key handler
├── score_sheets.py        # Core scoring pipeline
├── calibrate_positions.py # Sheet alignment
├── ui/                    # Web + Desktop frontends
├── config/                # Config files (keys, formats)
├── read_ans/              # Input sheets
├── results/               # Output scores
└── manuals/               # Docs
```

---

## 📜 License

See [LICENSE](LICENSE).
