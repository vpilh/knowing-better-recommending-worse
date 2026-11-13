# Handoff: set up the run machine (WSL + vLLM on the RTX 5090)

For Valentin, on the run machine, and for Claude Code if you open it there. Written 9 Nov 2026.

**Goal:** before the sprint starts (Fri 13 Nov, 13:00 CET), the RTX 5090 serves a small 4-bit model from
WSL through vLLM and returns logprobs. Nothing more.
**Not now:** no project code (item generator, prompts, analysis). That starts Friday.
Context: [PLAN.md](PLAN.md) (the project), [DESIGN.md](DESIGN.md) (models, readout, stack).

**Note for Claude Code:** walk the user through the steps one at a time. Run each check, compare it with the
expected result, and do not move on while a check fails. Record versions in the log at the end of
this file.

Machine: Windows 11, RTX 5090 32 GB plus Intel iGPU, Core Ultra 9 285K, 64 GB RAM, about 0.95 TB free. At the
start nothing is installed (no driver check yet, no WSL distribution, no Python environment).

---

## Step 1. NVIDIA driver (Windows)

1. Install the current NVIDIA driver for the RTX 5090 (GeForce Game Ready or Studio, from nvidia.com or the
   NVIDIA app). Reboot.
2. Check, in PowerShell:
   ```powershell
   nvidia-smi
   ```
   **Expected:** the table lists "NVIDIA GeForce RTX 5090" with about 32 GB, and the header shows
   "CUDA Version: 12.8" or higher. Blackwell (sm_120) needs CUDA 12.8 or newer.

Do **not** install an NVIDIA driver inside WSL later. WSL uses the Windows driver.

## Step 2. WSL and Ubuntu

In PowerShell (as administrator):
```powershell
wsl --update
wsl --install -d Ubuntu-24.04
wsl --set-default-version 2
```
Create the Linux user when prompted. Check:
```powershell
wsl -l -v      # Ubuntu-24.04, VERSION 2
wsl --version  # note the WSL version
```

Optional: if C: is short of space, move the distribution to a larger drive
(`wsl --manage Ubuntu-24.04 --move D:\WSL\Ubuntu`). Models need about 150 GB.

## Step 3. Give WSL enough memory

Create `C:\Users\<you>\.wslconfig`:
```ini
[wsl2]
memory=48GB
swap=16GB
```
Then run `wsl --shutdown` and reopen Ubuntu. Check inside Ubuntu with `free -g`: the total should be about 47.

## Step 4. GPU inside WSL

In Ubuntu:
```bash
nvidia-smi
```
**Expected:** the same RTX 5090 and CUDA version as in Step 1. If the command is missing: update the
Windows driver, run `wsl --update`, then `wsl --shutdown`. Do not install a Linux driver.

Base tools:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential git curl
```

## Step 5. Python environment (uv, inside WSL)

Keep everything on the Linux filesystem (`~/...`), not under `/mnt/c` or `/mnt/d`: model loading
from Windows drives is much slower.
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
mkdir -p ~/epistemics && cd ~/epistemics
uv venv --python 3.12
source .venv/bin/activate
uv pip install vllm
```
vLLM pulls a matching PyTorch with its own CUDA runtime, so no separate CUDA toolkit is needed.
Check:
```bash
python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0))"
python -c "import vllm; print(vllm.__version__)"
```
**Expected:** "NVIDIA GeForce RTX 5090" and capability `(12, 0)`, with no error.

## Step 6. Hugging Face access

```bash
uv pip install -U huggingface_hub
hf auth login          # paste a read token from huggingface.co/settings/tokens
```
Some models are gated: open their Hugging Face pages and accept the licence. Gemma models always are;
check the others when you pick the checkpoints.

## Step 7. Smoke test: serve a small model and read logprobs

This is an environment check, not project code. Terminal 1:
```bash
cd ~/epistemics && source .venv/bin/activate
vllm serve Qwen/Qwen3-4B-AWQ --max-model-len 4096 --gpu-memory-utilization 0.85
```
If that repository name does not exist, use any small 4-bit (AWQ) instruct model.

Terminal 2, once the server reports it is ready:
```bash
curl -s localhost:8000/v1/chat/completions -H "Content-Type: application/json" -d '{
  "model": "Qwen/Qwen3-4B-AWQ",
  "messages": [{"role": "user", "content": "Is 7 larger than 5? Start your answer with A (yes) or B (no)."}],
  "max_tokens": 1, "logprobs": true, "top_logprobs": 5, "temperature": 0
}' | python -m json.tool
```
**Expected:** `choices[0].logprobs.content[0].top_logprobs` lists 5 tokens with logprobs, "A" near
the top. That is the readout the project uses.

## Step 8. Fallback, only if vLLM fails on sm_120

Plain transformers in a second environment:
```bash
cd ~ && mkdir -p epistemics-hf && cd epistemics-hf
uv venv --python 3.12 && source .venv/bin/activate
uv pip install torch --index-url https://download.pytorch.org/whl/cu128
uv pip install transformers accelerate
python -c "import torch; print(torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0))"
```
Note which path works in the log below.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `nvidia-smi` missing in WSL | Update the Windows driver; `wsl --update`; `wsl --shutdown` |
| "no kernel image is available" / sm_120 not supported | PyTorch or vLLM too old: `uv pip install -U vllm` in a fresh venv |
| `libcudart.so.12` import error | Mixed CUDA builds: delete `.venv`, reinstall only vLLM |
| CUDA out of memory at start | Lower `--gpu-memory-utilization` (0.8) or `--max-model-len` (2048) |
| `fatal error: Python.h: No such file or directory` (Triton) | `sudo apt install -y python3.12-dev` |
| `Could not find nvcc and default cuda_home='/usr/local/cuda'` (FlashInfer) | Install the toolkit only (no driver): NVIDIA `cuda-keyring` for `wsl-ubuntu`, then `sudo apt install cuda-toolkit-13-0` (matches torch cu130); `CUDA_HOME=/usr/local/cuda` and its `bin` on `PATH` (set in `~/.bashrc`). Quick workaround: `export VLLM_USE_FLASHINFER_SAMPLER=0` |
| First token is `<think>` (Qwen3 and other reasoning models) | Add `"chat_template_kwargs": {"enable_thinking": false}` to the request |
| Very slow model load | Model files under `/mnt/...`: move them to `~` (the Hugging Face cache defaults to `~/.cache/huggingface`) |

## Log (fill in)

| Item | Value |
|---|---|
| Windows NVIDIA driver / CUDA version (Step 1) | 610.60 / CUDA 13.3 (checked 9 Nov) |
| WSL version (Step 2) | WSL 3.0.3.0, kernel 6.18.54.1-1, Ubuntu-24.04 on WSL 2 (distribution on C:) |
| Python / torch / CUDA / capability (Step 5) | Python 3.12.3 / torch 2.14.0+cu130 / CUDA 13.0 / (12, 0) |
| vLLM version (Step 5) | 0.33.0 (uv 0.13.7) |
| Smoke test passed, model used (Step 7) | Yes, 9 Nov. Qwen/Qwen3-4B-AWQ: P("A") ≈ 1.0, "B" at logprob −29.8. About 28 GB VRAM at 0.85 utilisation |
| Path that works: vLLM or transformers fallback | vLLM (fallback not needed) |
| Problems and fixes | (1) WSL 2 needed the VM Platform feature: `wsl --install --no-distribution` plus a reboot. (2) Triton: `Python.h` missing → `sudo apt install python3.12-dev`. (3) FlashInfer sampler JIT needs `nvcc` → first worked around with `export VLLM_USE_FLASHINFER_SAMPLER=0`, then fixed by installing `cuda-toolkit-13-0` from NVIDIA's wsl-ubuntu repository (toolkit only, no driver). (4) Qwen3 answers `<think>` first → send `"chat_template_kwargs": {"enable_thinking": false}` in the request. Step 6: logged in to Hugging Face as `tinopi` |

When this is done: copy the log back into [DESIGN.md](DESIGN.md) under "Serving stack".
