# 🍎 Food AI — Classification & Calorie Estimation

A production-ready Food Image Classification and Calorie Estimation system powered by **Deep Learning**. The backend handles ALL intelligence using PyTorch + MobileNetV2 on GPU, while the frontend is a pure UI layer.

---

## ⚙️ Architecture

```
User → React UI → POST /predict → FastAPI + PyTorch (GPU) → JSON Response → UI Display
```

| Layer     | Technology                        | Responsibility           |
|-----------|-----------------------------------|--------------------------|
| Frontend  | React + Vite                      | UI rendering ONLY        |
| Backend   | FastAPI + PyTorch + MobileNetV2   | ALL inference + logic    |
| GPU       | NVIDIA CUDA                       | Accelerated inference    |
| Model     | MobileNetV2 (Transfer Learning)   | 101-class Food-101       |

---

## 📁 Project Structure

```
├── backend/
│   ├── main.py              ← FastAPI server (POST /predict)
│   ├── utils.py             ← Model builder + preprocessing
│   ├── calorie_map.json     ← 101 food → calorie mapping
│   ├── train.py             ← (Optional) Fine-tune on Food-101
│   ├── model.pth            ← Trained weights (after training)
│   └── requirements.txt     ← Python dependencies
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx           ← UI component (API-connected)
│       └── index.css         ← Premium dark theme
│
└── README.md
```

---

## 🚀 Setup & Run

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for frontend)
- **NVIDIA GPU** with CUDA support
- **PyTorch** with CUDA (already installed: `torch 2.6.0+cu124`)

### 1️⃣ Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# (Optional) Train the model on Food-101 for accurate predictions
python train.py

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will:
- ✅ Verify CUDA GPU availability (fails if no GPU)
- ✅ Load MobileNetV2 model onto GPU
- ✅ Warm up with a dummy inference
- ✅ Start listening on `http://localhost:8000`

### 2️⃣ Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs on `http://localhost:5173`

---

## 🧪 Usage Flow

1. Open `http://localhost:5173` in your browser
2. Upload a food image (JPEG, PNG, WebP)
3. Click **"Analyze Image"**
4. The backend:
   - Preprocesses the image (resize, normalize, tensor)
   - Runs MobileNetV2 inference on GPU
   - Applies softmax for classification
   - Looks up calories from `calorie_map.json`
5. Results displayed: **Food Name**, **Confidence %**, **Calories**

---

## 📡 API Reference

### `POST /predict`

**Request:** Multipart form with image file

```bash
curl -X POST -F "file=@pizza.jpg" http://localhost:8000/predict
```

**Response:**

```json
{
  "food": "Pizza",
  "confidence": 0.9234,
  "calories": 266,
  "class_id": "pizza",
  "inference_time_ms": 12.3
}
```

### `GET /health`

```json
{
  "status": "healthy",
  "gpu": "NVIDIA GeForce RTX 4060 Laptop GPU",
  "model_loaded": true
}
```

---

## 🧠 Model Details

- **Architecture:** MobileNetV2 with custom classifier head
- **Backbone:** Pretrained on ImageNet (1000 classes)
- **Classifier:** `1280 → Dropout → 512 → ReLU → Dropout → 101`
- **Training:** Two-phase (frozen backbone → full fine-tune)
- **Classes:** 101 Food-101 categories
- **Inference:** GPU-only, ~10-15ms per image on RTX 4060

---

## 🔧 Training (Optional but Recommended)

For accurate food predictions, fine-tune the model:

```bash
cd backend
python train.py
```

This will:
- Auto-download the Food-101 dataset (~5 GB)
- Phase 1: Train classifier head (5 epochs, backbone frozen)
- Phase 2: Full fine-tuning (10 epochs)
- Save best model as `model.pth`

Training takes ~2-3 hours on RTX 4060.
