# Hardware paths

You do not need a specific machine to do this project — you need to pick the right path for the machine you have. There are three.

| Path | You have | Cost | Overnight autonomy? |
|---|---|---|---|
| [1. Windows + NVIDIA](#1-windows--nvidia-locally--the-primary-path) | A gaming/workstation PC | Free | Yes |
| [2. macOS](#2-macos--use-a-sibling-fork) | A Mac | Free | Yes (different repo) |
| [3. Rented GPU pod](#3-overnight-autonomy-without-local-hardware--rent-a-pod) | Any laptop + ~$5–10 | ~$0.20–0.60/hr | Yes |

**One thing the table doesn't have to cover: serving.** All three rows are about *training*, which is where the hardware requirements live. Running the finished model is cheap on every path — these models are ~19M parameters, so `chat.py` serves them on a plain CPU with no GPU anywhere in the picture. The existence proof is the live demo, [autoresearch-demo.fly.dev](https://autoresearch-demo.fly.dev/): two trained checkpoints served from a single small shared CPU machine that sleeps when idle (the first visit waits ~12 seconds while it wakes, then it's quick). Its deployment recipe — Dockerfile and `fly.toml` — is public in the worked-example repo's [`deploy/`](https://github.com/aroughidea/autoresearch-win-rtx/tree/master/deploy) folder if you want to host your own result the same way. So choose your path below on GPU access alone; whatever you train will run anywhere afterwards.

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
- A recent NVIDIA driver, git, uv, ~10 GB free disk (`session.py --check` checks it).

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

**What changes:** the training internals differ (Metal/MLX instead of CUDA), and the forks keep Karpathy's original loop: 5-minute runs, and git commits as the record. This kit's record, `lab.py`, `session.py` and 10-minute runs do not carry over, but the ideas do: a `program.md` for the agent, `train.py` as the file experiments edit, keep or undo by the score. The setup commands come from the fork's README. Your scores won't be comparable to anyone on this kit, but scores never compare across hardware anyway.

---

## 3. Overnight autonomy without local hardware — rent a pod

Want the real unattended-overnight experience with no local GPU? Rent a Linux GPU pod by the hour: [RunPod](https://www.runpod.io/), [Lambda](https://lambda.ai/), [Vast.ai](https://vast.ai/), and similar.

**Requirements:** an account with a GPU provider, a payment method, and basic SSH comfort (open a terminal on a remote machine, run commands, disconnect).

**Cost:** roughly **$0.20–0.60/hour** for a modest single GPU (RTX 3080/4090-class or an A-series card) — a 10-hour session lands around **$5–10**. Set a spending cap in the provider's dashboard, and **stop the pod when you're done** — the meter runs while the pod exists, not while it's busy.

**What changes:**

- The pod runs Linux, so use bash equivalents of the PowerShell commands: uv installs with `curl -LsSf https://astral.sh/uv/install.sh | sh`, and logging becomes `2>&1 | tee agent.log`. The training code itself is plain PyTorch and runs on a Linux CUDA box unchanged.
- The session's record lives on the pod, in `sessions/<name>/`, and it is not in git: **copy it off before you stop the pod.** Stopping a pod deletes what is on it. The round trip:

  1. On the pod: `git clone` **your copy** of the repo, `uv sync`, `uv run prepare.py`, `uv run train.py --smoke-test`.
  2. Start the session as in the README (`uv run session.py tinystories own`), with two differences on a pod:
     - **Keep it running after you disconnect:** start it inside `tmux` (`tmux new -s night`, then the command; detach with Ctrl+B then D). Closing an SSH session otherwise ends everything started in it.
     - **Sign the agent in without a browser:** for Claude Code, run `claude setup-token` on your own computer and set the token it prints as `CLAUDE_CODE_OAUTH_TOKEN` on the pod; or use an API key. Treat either like a password.
  3. In the morning, from your laptop, copy the session's folder and the kept models down, then **stop the pod**:
     `scp -r -P <port> <user>@<pod address>:<repo folder>/sessions/<name> sessions/` and the same for `checkpoints/`. Your provider's dashboard shows the address, port and user. The night is then on your laptop, as if the machine had been under your desk: `uv run lab.py use <name>` makes it the active session, and `uv run lab.py history` reads it.

- Scores from the pod's GPU are not comparable to scores from any other GPU. If you switch hardware, start a new session: scores compare only within one machine's sessions.
