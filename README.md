# Pulsse AI Engagement Analytics Service

HOI (Human-Object Interaction) Engagement Detection Service using Depth Anything v2 for depth-aware interaction detection.

## Quick Start

```bash
# 1. Create and activate virtual environment
python3 -m venv pulsse
source pulsse/bin/activate  # Linux/macOS

# 2. Install dependencies (choose one)
pip install -r requirements-cpu.txt      # CPU only
pip install -r requirements-gpu-cu121.txt  # GPU with CUDA 12.1

# 3. Configure Kafka in config.yaml
# Edit Kafka.BootstrapServers to point to your Kafka broker

# 4. Run the service
python main.py
```

## Features

- **Depth-Aware HOI Detection**: Uses Depth Anything v2 to understand 3D spatial relationships
- **Multiple Interaction Types**: HOLDING, TOUCHING, USING, NEAR, TALKING, EXAMINING, REACHING
- **YOLO Object Detection**: Detects objects (bottles, phones, chairs, etc.) for interaction analysis
- **Multi-Camera Support**: Process multiple video streams simultaneously
- **Temporal Smoothing**: Filters brief/noisy detections for stable output
- **Kafka Integration**: Real-time event streaming pipeline

## Architecture

```
┌──────────────────┐
│  Kafka Event     │  KafkaPersonDetectionEvent (persons + frame)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Frame Decode    │  base64 → BGR numpy array
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  YOLO Detection  │  Detect objects (bottles, chairs, etc.)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Depth Anything   │  Estimate depth for entire frame
│      v2          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Depth-Aware HOI  │  Compare depth distances + spatial overlap
│   Classifier     │  → TOUCHING, TALKING, HOLDING, NEAR, etc.
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Track Active     │  Track ongoing interactions
│ Interactions     │  Publish when they END
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Publish to Kafka │  video.insights.person.engagement
└──────────────────┘
```

## Prerequisites

- **Python**: 3.10 or higher (recommended: 3.12+)
- **Kafka**: Running Kafka broker (default: `10.10.10.100:9092`)
- **Operating System**: Linux (recommended), macOS, or Windows

### Hardware Requirements

| Mode | RAM | VRAM | Processing Speed |
|------|-----|------|------------------|
| CPU | 8GB+ | - | ~1-2 FPS |
| GPU (CUDA) | 8GB+ | 4GB+ | ~15-30 FPS |

---

## Installation

### Step 1: Clone/Navigate to Project

```bash
cd "/home/makki/Downloads/Pulsse AI Engagement Final Code - v1/Pulsse AI Final Code"
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv pulsse

# Activate virtual environment
# Linux/macOS:
source pulsse/bin/activate

# Windows:
# pulsse\Scripts\activate
```

---

## Option A: CPU Installation (Easier, Slower)

### Step 3A: Install All Dependencies (One Command)

```bash
pip install -r requirements-cpu.txt
```

### Step 4A: Verify Installation

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"
```

Expected output:
```
PyTorch: 2.x.x+cpu
CUDA: False
```

---

## Option B: GPU Installation (NVIDIA CUDA)

### Step 3B: Check CUDA Version

```bash
nvidia-smi
```

Note your CUDA version (e.g., CUDA 11.8, 12.1, 12.4).

### Step 4B: Install Dependencies (One Command)

Choose the command matching your CUDA version:

**CUDA 11.8:**
```bash
pip install -r requirements-gpu-cu118.txt
```

**CUDA 12.1:**
```bash
pip install -r requirements-gpu-cu121.txt
```

**CUDA 12.4 (Latest):**
```bash
pip install -r requirements-gpu-cu124.txt
```

### Step 5B: Verify GPU Installation

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
```

Expected output:
```
PyTorch: 2.x.x+cu121
CUDA Available: True
GPU: NVIDIA GeForce RTX 3080
```

---

## Option C: Manual Installation (If Above Don't Work)

### Step 3C: Install PyTorch Manually

Visit https://pytorch.org/get-started/locally/ and select your configuration.

Example for CUDA 12.1:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Step 4C: Install Base Dependencies

```bash
pip install -r requirements-base.txt
```

---

## Configuration

### Edit `config.yaml`

```yaml
# Kafka Configuration
Kafka:
  BootstrapServers: "10.10.10.100:9092"  # Change to your Kafka broker
  Consumer:
    GroupId: "engagement-analytics-group"
    SessionTimeoutMs: 30000
    HeartbeatIntervalMs: 9000
    MaxPollIntervalMs: 300000
  Topics:
    Input: "video.insights.person"
    Output: "video.insights.person.engagement"

# Model Configuration
Model:
  Path: "yolo11n.pt"  # Use yolo11n.pt (nano) for CPU, yolo11l.pt (large) for GPU
  Conf: 0.3

# HOI Detection Configuration
HOI:
  Enabled: true
  DepthModel:
    Variant: "small"    # Options: "small", "base", "large"
    Device: "auto"      # Options: "auto", "cuda", "cpu"
    MaxDepth: 20.0
  InteractionThresholds:
    DepthProximity: 0.15
    NearThreshold: 0.3
    MinConfidence: 0.5
    SpatialOverlap: 0.1
    TalkingDistanceRatio: 2.0
  Temporal:
    SmoothingFrames: 3
    InactivityTimeout: 1.0
```

### Model Selection Guide

| Scenario | YOLO Model | Depth Model | Device |
|----------|------------|-------------|--------|
| CPU (slow) | `yolo11n.pt` | `small` | `cpu` |
| GPU (fast) | `yolo11l.pt` | `base` or `large` | `cuda` |
| Balanced | `yolo11s.pt` | `small` | `auto` |

---

## Running the Service

### Activate Virtual Environment

```bash
source pulsse/bin/activate  # Linux/macOS
# or
# pulsse\Scripts\activate   # Windows
```

### Start the Service

```bash
python main.py
```

### Expected Output

```
============================================================
HOI Engagement Analytics Service
============================================================
Input topic: video.insights.person
Output topic: video.insights.person.engagement
Architecture: Direct Async Pipeline (no multiprocessing)
Event loop: uvloop (high-performance)
HOI Detection: Enabled
Depth Model: small
Depth Device: auto
============================================================
Ensuring Kafka topics exist...
✓ Kafka topics verified/created
Loading YOLO model: yolo11n.pt
Loading Depth Anything v2 model (small)...
Depth model loaded on: cpu
Service started. Listening for events...
```

---

## Troubleshooting

### Issue 1: Kafka Connection Failed

**Error:**
```
Failed to connect to Kafka at 10.10.10.100:9092
```

**Solution:**
1. Verify Kafka is running: `telnet 10.10.10.100 9092`
2. Update `config.yaml` with correct Kafka address
3. Check firewall rules

### Issue 2: Kafka Consumer Timeout Errors

**Error:**
```
OffsetCommit failed... UnknownMemberIdError
Heartbeat failed: local member_id was not recognized
```

**Cause:** Processing is too slow on CPU, blocking heartbeats.

**Solutions:**

1. **Use smaller models:**
   ```yaml
   Model:
     Path: "yolo11n.pt"  # nano instead of large
   HOI:
     DepthModel:
       Variant: "small"
   ```

2. **Increase timeouts in `config.yaml`:**
   ```yaml
   Kafka:
     Consumer:
       SessionTimeoutMs: 60000
       HeartbeatIntervalMs: 18000
       MaxPollIntervalMs: 600000
   ```

3. **Use GPU** for 10-50x faster processing

### Issue 3: CUDA Out of Memory

**Error:**
```
CUDA out of memory
```

**Solutions:**
1. Use smaller models (`yolo11n.pt`, depth `small`)
2. Reduce batch size
3. Set `Device: "cpu"` in config.yaml

### Issue 4: No Events Published

**Symptom:** `Published=0, HOI_Engagements=0`

**Explanation:** Events are only published when interactions **END**. If interactions are ongoing, they show as `Active=X` but won't publish until:
1. The interaction stops being detected for > 1 second
2. It was detected for at least 3 frames

### Issue 5: Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'ultralytics'
```

**Solution:**
```bash
pip install ultralytics
```

### Issue 6: uvloop Not Available (Windows)

**Warning:**
```
uvloop not available
```

**Note:** This is expected on Windows. The service will use the standard asyncio event loop (slightly slower but functional).

---

## Project Structure

```
Pulsse AI Final Code/
├── main.py                          # Entry point
├── config.yaml                      # Configuration file
├── requirements.txt                 # Default requirements (CPU)
├── requirements-base.txt            # Base dependencies (no PyTorch)
├── requirements-cpu.txt             # CPU installation
├── requirements-gpu-cu118.txt       # GPU CUDA 11.8
├── requirements-gpu-cu121.txt       # GPU CUDA 12.1
├── requirements-gpu-cu124.txt       # GPU CUDA 12.4
├── README.md                        # This file
│
├── analytics_service/               # Main service code
│   ├── __init__.py
│   ├── base_analytics_service.py    # Base class for analytics
│   ├── depth/                       # Depth estimation module
│   │   ├── __init__.py
│   │   └── depth_estimator.py       # Depth Anything v2 wrapper
│   ├── enagagment_analytics_service/
│   │   ├── __init__.py
│   │   └── engagement_analytics.py  # Main engagement detection
│   └── hoi/                         # HOI detection module
│       ├── __init__.py
│       ├── hoi_detector.py          # HOI orchestrator
│       └── interaction_classifier.py # Depth-aware classifier
│
├── core/                            # Core models and config
│   ├── __init__.py
│   ├── configurations.py            # Config loader
│   ├── constants.py                 # Constants and mappings
│   ├── enums.py                     # Enums (InteractionType, etc.)
│   └── data_contracts/              # Pydantic models
│       ├── __init__.py
│       ├── common_models.py
│       ├── hoi_models.py            # HOI-specific models
│       ├── internal_models.py
│       └── kafka_models.py          # Kafka event models
│
├── services/                        # Kafka services
│   ├── __init__.py
│   ├── kafka_admin.py               # Topic management
│   ├── kafka_consumer.py            # Event consumer
│   └── kafka_producer.py            # Event producer
│
├── utils/                           # Utilities
│   ├── __init__.py
│   ├── helpers.py                   # Helper functions
│   └── logger.py                    # Logging setup
│
└── yolo11n.pt                       # YOLO model file
```

---

## Interaction Types

| Type | Description | Detection Criteria |
|------|-------------|-------------------|
| `HOLDING` | Person holding an object | Depth < 0.15, overlap > 0.3, hand region |
| `TOUCHING` | Physical contact | Depth < 0.15, overlap > 0.3 |
| `USING` | Using an object | Depth < 0.15, overlap > 0.1 |
| `NEAR` | Close proximity | Depth < 0.3, some overlap |
| `TALKING` | Two people conversing | Depth < 0.3, faces aligned, similar height |
| `EXAMINING` | Looking at object | Person facing object, face region aligned |
| `REACHING` | Reaching toward object | Arm extended toward object |

---

## Performance Optimization Tips

### For CPU:

1. Use `yolo11n.pt` (nano model)
2. Use depth model variant `small`
3. Increase Kafka timeouts
4. Process fewer frames (skip every other frame)

### For GPU:

1. Use `yolo11l.pt` (large model) for better accuracy
2. Use depth model variant `base` or `large`
3. Ensure CUDA is properly installed
4. Monitor GPU memory with `nvidia-smi`

---

## License

Proprietary - Pulsse AI

## Support

For issues or questions, contact the Pulsse AI development team.
