# GPU 安装和启动指南

## 🎮 GPU 模式启动

如果你有 NVIDIA GPU，可以显著加速推理速度（约 5-10x）。

## 📋 前置要求

1. **NVIDIA GPU** (计算能力 >= 3.5)
   - 推荐: RTX 3060 或更高
   - 最低 VRAM: 4GB (推荐 6GB+)

2. **NVIDIA 驱动** (版本 >= 450.80.02)
   ```bash
   nvidia-smi  # 检查驱动版本
   ```

3. **CUDA Toolkit** (版本 11.8 或 12.1)
   ```bash
   nvcc --version  # 检查 CUDA 版本
   ```

## 🚀 快速启动（GPU 模式）

### 方法 1: 使用 GPU 启动脚本（推荐）

```bash
# 1. 确保已安装 GPU 版本的 PyTorch
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# 2. 启动全部服务
./start_gpu.sh

# 或者分别启动
./start_gpu.sh backend   # 只启动后端（GPU）
./start_gpu.sh frontend  # 只启动前端

# 停止服务
./start_gpu.sh stop
```

### 方法 2: 手动启动

```bash
# 设置 GPU 环境变量
export CUDA_VISIBLE_DEVICES=0  # 使用第一个 GPU
export USE_GPU=1

# 启动后端
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 启动前端（新终端）
python gradio_app.py
```

## 🔧 GPU 安装步骤

### Step 1: 安装 CUDA 版本的 PyTorch

根据你的 CUDA 版本选择：

**CUDA 12.1:**
```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

**CUDA 11.8:**
```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**验证安装:**
```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

应该输出:
```
CUDA available: True
GPU: NVIDIA GeForce RTX 3080  # 你的 GPU 名称
```

### Step 2: 测试 GPU 推理

```bash
cd /storage/home/hcoda1/9/eliu354/r-agarg35-0/projects/GAIC-Detector-Web-GUI
python test_system.py
```

看到 `Device: cuda:0` 表示成功使用 GPU。

## 🎯 多 GPU 配置

如果有多个 GPU，可以指定使用哪些：

```bash
# 使用第一个 GPU
export CUDA_VISIBLE_DEVICES=0

# 使用第二个 GPU
export CUDA_VISIBLE_DEVICES=1

# 使用多个 GPU（模型会自动选择第一个）
export CUDA_VISIBLE_DEVICES=0,1,2,3
```

## 📊 性能对比

| 模式 | 图片推理 | 视频推理（16帧） |
|------|---------|-----------------|
| CPU  | ~2-3秒  | ~30-50秒        |
| GPU  | ~0.3秒  | ~5-8秒          |

## 🐛 常见问题

### 问题 1: CUDA out of memory

**症状:** `RuntimeError: CUDA out of memory`

**解决:**
```bash
# 方法 1: 使用更小的 batch size（修改 app/config.py）
MAX_BATCH_SIZE = 1

# 方法 2: 强制使用 CPU
export CUDA_VISIBLE_DEVICES=""
```

### 问题 2: PyTorch 找不到 CUDA

**症状:** `torch.cuda.is_available()` 返回 `False`

**解决:**
1. 检查驱动: `nvidia-smi`
2. 检查 CUDA: `nvcc --version`
3. 重新安装 GPU 版本的 PyTorch:
   ```bash
   pip uninstall torch torchvision
   pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   ```

### 问题 3: 版本不匹配

**症状:** `The NVIDIA driver on your system is too old`

**解决:**
升级 NVIDIA 驱动:
- Ubuntu: `sudo apt update && sudo apt install nvidia-driver-535`
- 其他: 访问 https://www.nvidia.com/download/index.aspx

### 问题 4: 多 GPU 时使用哪个

**解决:**
```bash
# 查看所有 GPU
nvidia-smi

# 选择最空闲的 GPU
export CUDA_VISIBLE_DEVICES=1  # 使用第二个 GPU
```

## 🔍 GPU 监控

### 实时监控 GPU 使用率

```bash
# 方法 1: nvidia-smi 持续监控
watch -n 1 nvidia-smi

# 方法 2: 详细信息
nvidia-smi dmon -s pucvmet

# 方法 3: Python 脚本
python -c "import torch; [print(f'GPU {i}: {torch.cuda.memory_allocated(i)/1024**3:.2f}GB / {torch.cuda.get_device_properties(i).total_memory/1024**3:.2f}GB') for i in range(torch.cuda.device_count())]"
```

## 📈 优化建议

### 1. 预加载模型（减少冷启动时间）

修改 `app/aide_model.py`:
```python
# 在模块加载时就初始化模型
_model_instance = None

def get_model():
    global _model_instance
    if _model_instance is None:
        _model_instance = AIDeInference()
    return _model_instance
```

### 2. 批处理视频帧

修改 `app/video_utils.py`:
```python
# 使用 batch 推理而不是逐帧
frames_tensor = torch.stack([preprocess(frame) for frame in frames])
with torch.no_grad():
    outputs = model(frames_tensor)  # 批量推理
```

### 3. 使用混合精度（FP16）

```bash
export USE_FP16=1  # 在 config.py 中实现
```

## 🎓 Georgia Tech PACE 集群

如果在 PACE 上运行：

```bash
# 1. 请求 GPU 节点
salloc --nodes=1 --ntasks=1 --gres=gpu:V100:1 --time=4:00:00

# 2. 加载模块
module load cuda/12.1
module load anaconda3

# 3. 激活环境
conda activate gaic-detector

# 4. 启动服务
./start_gpu.sh
```

## 📚 参考资源

- PyTorch GPU 安装: https://pytorch.org/get-started/locally/
- CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
- NVIDIA 驱动: https://www.nvidia.com/download/index.aspx
- PACE 集群文档: https://docs.pace.gatech.edu/

## ✅ 验证清单

在启动前确认：

- [ ] `nvidia-smi` 能正常运行
- [ ] `torch.cuda.is_available()` 返回 `True`
- [ ] `test_system.py` 显示 `Device: cuda:0`
- [ ] GPU 显存足够（至少 4GB 可用）
- [ ] PyTorch 版本 >= 2.1.0
- [ ] CUDA 版本匹配 PyTorch

---

**推荐配置:**
- GPU: RTX 3060+ (6GB VRAM)
- CUDA: 12.1
- PyTorch: 2.1.0+cu121
- Driver: 535+

**预期性能:**
- 图片: ~0.3秒/张
- 视频: ~5-8秒（16帧）
- 内存: ~2-3GB VRAM
