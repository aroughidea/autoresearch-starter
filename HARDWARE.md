# Hardware paths

You do not need a specific machine to do this project — you need to pick the right path for the machine you have. There are four.

| Path | You have | Cost | Overnight autonomy? |
|---|---|---|---|
| [1. Windows + NVIDIA](#1-windows--nvidia-locally--the-primary-path) | A gaming/workstation PC | Free | Yes |
| [2. macOS](#2-macos--use-a-sibling-fork) | A Mac | Free | Yes (different repo) |
| [3. No GPU](#3-no-gpu-at-all--the-colab-path) | Any laptop + browser | Free | No (1–3 h sessions) |
| [4. Rented GPU pod](#4-overnight-autonomy-without-local-hardware--rent-a-pod) | Any laptop + ~$5–10 | ~$0.20–0.60/hr | Yes |

---

## 1. Windows + NVIDIA locally — the primary path

This kit as-is. Everything in [README.md](README.md) assumes this path.

**Requirements:**

- Windows 10/11 with an NVIDIA GPU meeting the VRAM floor:

  | GPU architecture | Series | VRAM floor |
  |---|---|---|
  | Turing | RTX 20xx | 8 GB+ |
  | Ampere / Ada / Blackwell | RTX 30xx / 40xx / 50xx | 10 GB+ |

- Laptop and mobile-workstation GPUs are supported when they meet the floor (thermals may reduce throughput — scores, not correctness).
- A recent NVIDIA driver, git, uv, ~10 GB free disk.

**Cost:** free (electricity aside).

**What changes:** nothing — follow the README quickstart. The training script detects your GPU, applies a matching profile, and autotunes batch size on first run.

---

## 2. macOS — use a sibling fork

**This kit does NOT run on Macs.** The code requires CUDA, which Apple hardware does not have — no workaround, no flag, it will not start.

The good news: the upstream author maintains a "notable forks" list, and two Mac forks are on it:

- [miolini/autoresearch-macos](https://github.com/miolini/autoresearch-macos)
- [trevin-creator/autoresearch-mlx](https://github.com/trevin-creator/autoresearch-mlx) (Apple MLX framework)

**Requirements:** an Apple Silicon Mac; follow the chosen fork's own README.

**Cost:** free.

**What changes:** the training internals differ (Metal/MLX instead of CUDA), but the concept is identical — a `program.md` research program, a 5-minute budget, `train.py` as the file experiments edit, keep-or-revert via git. Everything this README teaches about *running the loop* transfers directly; only the setup commands come from the fork's README. Your scores won't be comparable to anyone on this kit, but scores never compare across hardware anyway.

---

## 3. No GPU at all — the Colab path

The `cloud/` folder contains a Colab notebook that runs this same repo on a free cloud GPU.

**Requirements:** a Google account and a browser. That's the whole list.

**Cost:** free — Colab's free tier provides an NVIDIA T4 (16 GB), comfortably above the VRAM floor.

**What changes:**

- Open the notebook in `cloud/` via Colab, point it at **your copy** of this template (created with "Use this template"), and run the cells — they clone your repo, install dependencies, and run the same `prepare.py` / `train.py` loop.
- **Sessions are 1–3 hours**, not overnight: the free tier disconnects idle or long-running sessions, and the runtime's disk vanishes when it ends. Plan sessions like lab slots — run 5–15 experiments, then stop.
- **Push results before the session ends.** Commit `results.tsv` and `train.py` changes back to your GitHub repo every few experiments (the notebook shows how). Anything unpushed when the runtime dies is gone.
- A T4 is slower than most desktop RTX cards, so expect higher `val_bpb` per 5-minute run. Comparisons within your own Colab history remain fair.

---

## 4. Overnight autonomy without local hardware — rent a pod

Want the real unattended-overnight experience with no local GPU? Rent a Linux GPU pod by the hour: [RunPod](https://www.runpod.io/), [Lambda](https://lambda.ai/), [Vast.ai](https://vast.ai/), and similar.

**Requirements:** an account with a GPU provider, a payment method, and basic SSH comfort (open a terminal on a remote machine, run commands, disconnect).

**Cost:** roughly **$0.20–0.60/hour** for a modest single GPU (RTX 3080/4090-class or an A-series card) — an 8–12 hour overnight run lands around **$5–10**. Set a spending cap in the provider's dashboard, and **stop the pod when you're done** — the meter runs while the pod exists, not while it's busy.

**What changes:**

- The pod runs Linux, so use bash equivalents of the PowerShell commands: uv installs with `curl -LsSf https://astral.sh/uv/install.sh | sh`, and logging becomes `2>&1 | tee agent.log`. The training code itself is plain PyTorch and runs on a Linux CUDA box unchanged.
- The workflow is a round trip through GitHub, and this is the punchline of the whole design — **the repo IS the lab state**. `train.py` at HEAD is your best configuration, `results.tsv` is the complete scorecard, the commit log is the experiment history. There is no database, no separate state, nothing to back up. So "moving your lab to the cloud" is just:

  1. On the pod: `git clone` **your copy** of the repo, `uv sync`, `uv run prepare.py`, `uv run train.py --smoke-test`.
  2. Launch the agent loop exactly as in the README (the unattended commands work verbatim, minus `Tee-Object`).
  3. In the morning: `git push` from the pod, **stop the pod**, `git pull` on your laptop. Your entire night of research — every kept change, every logged experiment — is now local, as if the machine had been under your desk.

- Scores from the pod's GPU are not comparable to scores from any other GPU. If you switch hardware mid-project, keep comparing only within contiguous same-hardware stretches of `results.tsv` — or start a fresh log and treat it as a new campaign.
