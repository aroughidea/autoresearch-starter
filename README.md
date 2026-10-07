# autoresearch-starter

Train your own small language model tonight — on the gaming PC you already own, or a rented GPU — and let an AI agent be the researcher. You choose the dataset and the tokenizer; the agent changes the training code, trains for exactly 5 minutes, checks the score, keeps or reverts, and repeats, unattended, while you sleep. In the morning you have models you trained, a record of what each one wrote as it learned, a scoreboard of every experiment, and a git history that *is* your lab notebook. The point is to see how design decisions — the data, the tokens, the recipe the agent evolves — change what a model writes.

**See it first — nothing to install.** The thing you are about to build is already running here: **[autoresearch-demo.fly.dev](https://autoresearch-demo.fly.dev/)**. It serves two models from one real research session — the starting baseline and the best configuration that session found — side by side, so you can hand both the same prompt and read the difference. It is the same browser UI (`chat.py`) this kit ships with, alongside that session's 16-experiment progress chart and a browser for the tokenizer's vocabulary. Free, public, no login. Note what these are: text-completion models, not chat assistants — type the start of a story and they continue it. And notice that the two read almost alike: that session's whole gain was smaller than the difference between two runs of the same code, which is why the agent judges by a score. And one honest caveat: the demo lives on a small machine that sleeps when nobody is visiting, so the *first* page load waits about 12 seconds while it wakes (you get the page, not an error); after that pages come back in a fraction of a second.

**This is a template repository.** On GitHub, click the green **"Use this template"** button → **"Create a new repository"** to get your own copy under your account. Do **not** fork it and do not clone this repo directly — your experiment history is going to live in git commits, and those belong in *your* repo, not this one.

> Based on [karpathy/autoresearch](https://github.com/karpathy/autoresearch), via the Windows/consumer-GPU port [jsegov/autoresearch-win-rtx](https://github.com/jsegov/autoresearch-win-rtx). No NVIDIA GPU? No Windows? See [HARDWARE.md](HARDWARE.md): your own NVIDIA GPU, a Mac (through a sibling fork), or a GPU rented by the hour.

## What you get

- **`train.py`** — the model, optimizer, and training loop. **The one file experiments edit.** Everything in it is fair game: architecture, hyperparameters, batch sizes.
- **`prepare.py`** — data download, tokenizer, dataloader, evaluation, and the fixed rules (5-minute time budget, eval method). **Off-limits during experiments** — it's the referee, and you don't let experiments edit the referee.
- **`program.md`** — the research program: the instructions an agent reads and executes. Works out of the box; rewriting it is the endgame (see [Swap out parts](#swap-out-parts--make-it-yours)).
- **`results.tsv`** — your scoreboard. Starts empty; gains one row per experiment: score, VRAM, keep/discard, description.
- **`capture.py`** and **`runs/`** — every experiment saves what your model wrote at 0, 10, 30, 60 and 120 seconds and at the end, as a small JSON file in `runs/`. A browser explorer for these files is planned; until then, open one to watch a model go from noise to stories. **Off-limits during experiments**, like `prepare.py`.
- **`chat.py`** — a local browser page that runs two of your trained models side by side on the same prompt, with the score chart.
- **`analysis.ipynb`** — a notebook that charts `results.tsv`: score over time, keeps vs discards, top improvements.

## Quickstart (Windows + NVIDIA)

**Requirements:**

- An NVIDIA GPU meeting the VRAM floor: **Turing (RTX 20-series) with 8 GB+**, or **Ampere / Ada / Blackwell (RTX 30/40/50-series) with 10 GB+**. Laptop GPUs count if they meet the floor.
- [git](https://git-scm.com/download/win)
- [uv](https://docs.astral.sh/uv/) — install with:
  `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- Python 3.10+ (uv will fetch one automatically — but read the [Smart App Control note](#troubleshooting-the-real-failure-modes) if it fails to start)

Clone **your** copy (created via "Use this template"), open PowerShell in the repo folder, and run:

```powershell
# 1. Install dependencies (one-time; downloads CUDA-enabled PyTorch)
uv sync

# 2. Download the dataset and train the tokenizer (one-time)
uv run prepare.py

# 3. Fast end-to-end sanity check (~1 min)
uv run train.py --smoke-test

# 4. Your first real experiment (~8 min: 5 of training, then scoring)
uv run train.py
```

A successful run ends with a summary block whose first line is your score:

```
---
val_bpb:          0.520082
```

`val_bpb` is "validation bits per byte" — how surprised the model is by text it has never seen. **Lower is better.** An untrained model scores ~3.2 (that's what the smoke test prints, since it barely trains); after 5 minutes on a laptop RTX 4000 Ada it scores about 0.52. Two runs of the same code differ by about 0.003, so treat smaller differences as ties.

**Meet your model:**

```powershell
uv run chat.py
```

Open `http://localhost:8000` and type a prompt. The default dataset is [TinyStories](https://huggingface.co/datasets/karpathy/tinystories-gpt4-clean) (GPT-4-written children's stories), so your model will continue any prompt in bedtime-story style. It will be charmingly clumsy. What makes it less clumsy — the data, the tokens, the recipe — is what this kit lets you explore.

## Run the research loop

An AI agent runs this loop for you, all night:

```mermaid
flowchart TD
    A["Start (edit program.md to change direction)"] --> B["Read program.md, prepare.py, train.py"]
    B --> C["Modify train.py\narchitecture · hyperparams · optimizer"]
    C --> D["uv run train.py\n5-minute fixed training budget"]
    D --> E{Score improved?}
    E -->|keep| F["git commit the change\nappend keep row to results.tsv"]
    E -->|discard| G["revert train.py\nappend discard row to results.tsv"]
    E -->|crash| H["record crash in results.tsv\nrestore last working state"]
    F --> C
    G --> C
    H --> C
```

### Before you start

- **A coding agent and an account for it.** Claude Code needs a Claude Pro or Max plan or Anthropic API billing; Codex CLI needs a ChatGPT plan or OpenAI API billing. A night of experiments uses a lot of a plan's allowance, and hitting a usage limit ends the run early.
- **Node.js**, which the agents' installers (`npm install -g ...`) need: [nodejs.org](https://nodejs.org/).
- **A PC that stays awake.** Windows Settings → System → Power → set sleep to *Never* while plugged in, for the night.
- **Your dataset and tokenizer prepared** (`uv run prepare.py`, see [Swap the dataset or the tokenizer](#swap-the-dataset-or-the-tokenizer)). The agent never changes them.

### Start the agent

Any coding agent that can read files, edit code, and run terminal commands works. The starting prompt is always:

```
Read program.md, do setup checks, and start a new experiment loop. Log each result in results.tsv.
```

**A word about permissions, before you paste any command below.** For an unattended session the agent needs the ability to edit files and run shell commands *without asking you each time* — that's what "autonomous" means. Flags like `--dangerously-skip-permissions` and `danger-full-access` grant exactly that: the agent can run anything your user account can run, for the whole session. That is the tool doing its job, not a bug — but understand it before granting it. Run agents only in this repo's folder, on a machine whose contents you're comfortable with, and skim the log afterwards. If that trade is not one you want to make yet, use the interactive/selective modes and approve actions by hand.

**Claude Code** (Anthropic's CLI agent):

```powershell
# Install (one-time)
npm install -g @anthropic-ai/claude-code

# Interactive — watch it work, approve each action; Ctrl+C to stop
claude "Read program.md, do setup checks, and start a new experiment loop. Log each result in results.tsv."

# Unattended / overnight — no prompts, everything logged to agent.log
claude --dangerously-skip-permissions "Read program.md, do setup checks, and start a new experiment loop. Log each result in results.tsv." 2>&1 | Tee-Object -FilePath agent.log

# Middle ground — auto-approve file edits, still ask before shell commands
claude --permission-mode acceptEdits "Read program.md, do setup checks, and start a new experiment loop. Log each result in results.tsv."
```

**Codex CLI** (OpenAI's terminal agent):

```powershell
# Install (one-time)
npm install -g @openai/codex

# Unattended — full access, logged to agent.log
codex exec -s danger-full-access "Read program.md, do setup checks, and start a new experiment loop. Log each result in results.tsv." 2>&1 | Tee-Object -FilePath agent.log

# More cautious: -s workspace-write auto-approves edits but asks before shell commands
```

**To stop either:** press **Ctrl+C**. The agent commits after every experiment, so interrupting is always safe — `results.tsv` and git stay consistent. Expect about **6 experiments an hour** (each takes 8–11 minutes: 5 of training, then scoring), so an 8-hour night is about 50–60.

### In the morning

1. **`results.tsv`** — every experiment: what the agent tried, the score, keep or discard. Differences under about 0.003 are ties.
2. **`uv run chat.py`**, then `http://localhost:8000` — the score chart, and two of your models side by side on the same prompt. Ask: does the writing differ, and why?
3. **`runs/`** — one file per experiment with what the model wrote at 0, 10, 30, 60 and 120 seconds and at the end. Open one and watch it learn.
4. **`git log --oneline`** — the lab notebook. `git push` shares the whole night.

## Troubleshooting the real failure modes

**Smart App Control blocks Python (`DLL load failed ... Application Control policy`).**
Windows Smart App Control blocks uv's standalone Python builds because they are unsigned. Fix: install the signed interpreter from [python.org](https://www.python.org/downloads/) (match the version pinned in `.python-version`), then point the venv at it:
```powershell
uv venv --python "C:\Path\To\python.exe"
uv sync
```

**`CUDA not available` (or torch reports no GPU).**
Fix, in order: (1) update your NVIDIA driver and confirm `nvidia-smi` shows your GPU; (2) make sure PyTorch came from `uv sync` — this repo pins CUDA wheels via its own PyTorch index in `pyproject.toml`. If you ever `pip install torch` manually you'll get the CPU-only build; delete `.venv` and re-run `uv sync`.

**VRAM floor warning at startup.**
The script checks the floor (Turing 8 GB+, Ampere/Ada/Blackwell 10 GB+). Below floor, runs will likely crash with out-of-memory errors mid-training. The built-in autotuner already picks the largest batch size that fits — there's little headroom to recover by hand. Below-floor GPU? Rent one by the hour: see [HARDWARE.md](HARDWARE.md).

**"My scores are worse than the walkthrough's."**
Not a bug. Training runs for a fixed **5 minutes of wall-clock time**, so a slower GPU simply completes fewer steps and lands at a higher `val_bpb`. Correctness is unaffected, and comparisons *within your own machine's history* — the only comparisons the loop needs — are perfectly fair. Never compare absolute scores across different hardware.

**`results.tsv` looks broken / the analysis chokes on it.**
It is **tab**-separated, not comma-separated — descriptions contain commas, and commas as delimiters silently shred rows. Six columns, one row per run, header row intact, never rewrite past rows (the log is append-only, even for discards and crashes). If an agent mangled it, fix the delimiters before the next session; the agent reads this file at startup to know what's been tried.

## Swap out parts — make it yours

This is the heart of the kit. Everything above is the default configuration; none of it is sacred.

### Swap the dataset or the tokenizer

Two datasets and three tokenizers are built in. Choosing them is your decision, not the agent's:

```powershell
uv run prepare.py --dataset folktales                       # folk and myth tales instead of TinyStories
uv run prepare.py --dataset tinystories --tokenizer phi3    # Phi-3 / Llama 2 vocabulary (32,011 tokens)
uv run prepare.py --dataset tinystories --tokenizer gpt2    # GPT-2 vocabulary (50,257); needs about 10 GB of GPU memory
uv run prepare.py --dataset tinystories --tokenizer own     # back to the default: a vocabulary built from the data
```

The pair you prepare last is active for training, `generate.py` and `chat.py`, and every run file records it. Scores compare across tokenizers on the same dataset, never across datasets: start a fresh `results.tsv` when you switch dataset. Phi-3 scores about 0.1% low: it counts one extra byte per document for its word-boundary marker, so treat differences smaller than that as ties.

To add your own text (poetry, code, your own writing), add an entry to `DATASET_CONFIGS` and its name to `DATASET_CHOICES` in `prepare.py`.

### The headline swap: rewrite `program.md`

Here is the real secret of this project: **`program.md` IS the program.** The Python files are the lab equipment; the Markdown file is the research strategy — and it's the layer you're actually meant to iterate on. The default is a deliberately bare-bones greedy hill-climb: try a change, keep if better. You can rewrite the strategy itself:

- **Different metrics to log** — track `mfu_percent`, tokens/sec, or params alongside `val_bpb`; tell the agent to prefer improvements that don't inflate VRAM.
- **Different search policies** — "run every experiment twice and keep only if both improve" (noise control); "sweep one variable across 4 values before deciding" (mini grid search); "alternate one safe tweak with one wild idea" (explore/exploit).
- **Stopping criteria** — "stop after 10 consecutive discards and write a summary of what you believe and why."
- **Scope and risk** — "optimizer changes only tonight"; "no change may increase VRAM above 9 GB"; "prefer deletions."

Two students with identical hardware and different `program.md` files are running different research organizations. Comparing whose *strategy* finds better models faster is a far more interesting competition than comparing GPUs.

## How hosting works (and why not Ollama)

Your trained model ships with its own server — `chat.py` — instead of loading into Ollama or LM Studio. That's not a limitation to apologize for; it's the point. Those apps run **standardized** open-weights architectures packaged as GGUF files: someone else trained the model, llama.cpp knows its exact shape, you just download and run it. Your model is a **deliberately custom architecture** — value embeddings, windowed attention, a custom `rustbpe` tokenizer — that no standard runtime has ever heard of, because you (or your agent) invented this exact configuration last night. Custom architecture ⇒ custom server. Ollama runs other people's models; this kit trains *yours*.

**This isn't theoretical — it's the demo linked at the top.** [autoresearch-demo.fly.dev](https://autoresearch-demo.fly.dev/) is exactly this `chat.py`, in a container, on one small **CPU-only** machine. No GPU is involved in serving, and none is needed: these models are ~19M parameters, so an ordinary shared CPU streams them comfortably. That's the second half of the lesson — a model you can train in five minutes is a model you can host for pocket change. The recipe is public as well. The worked-example repo's [`deploy/`](https://github.com/aroughidea/autoresearch-win-rtx/tree/master/deploy) folder holds the Dockerfile and `fly.toml` behind that site: it builds the image from the repo root and serves the checkpoints committed alongside it, so putting *your* trained model on the internet the same way is mostly a matter of pointing the same recipe at your repo. (The public copy caps generation — max 500 tokens, `top_k` ≤ 200, prompts up to 2000 characters — and shows a banner linking to how those models were made. Everything else is identical to `uv run chat.py` on your own machine.)

**Going-further project (advanced, satisfying):** rewrite `train.py`'s architecture into a llama.cpp-supported one (e.g. a standard Llama-style transformer), train it, convert the checkpoint to GGUF, and genuinely serve your own model in Ollama. Then you'll have earned the standard.

## Going further

### Run the loop by hand (stretch goal)

The agent is the default, but `program.md` is a complete protocol you can follow by hand, which is a good way to see what the agent is deciding:

1. Run `uv run train.py` unchanged once to establish your **baseline** score. Log it in `results.tsv`.
2. Change **one thing** in `train.py` — a constant like `DEPTH`, a learning rate, `WINDOW_PATTERN`. One change per experiment, so you know what caused what.
3. Run `uv run train.py`. Compare `val_bpb` to your current best.
4. **Improved?** `git commit` the change and log a `keep` row. **Worse?** Revert (`git checkout -- train.py`) and log a `discard` row. Log crashes too — a crash you recorded is data; a crash you forgot is a repeat.
5. Go to 2.

Ten runs is an evening. Archive a kept model by hand (copy `checkpoint_pre_eval.pt` into `checkpoints/`) if you want to compare it in `chat.py` later.

### Hand-tuning: the seven knobs (stretch goal)

From the upstream author's guidance on tuning autoresearch for machines far smaller than an H100:

1. **Use a low-entropy dataset.** Narrow-scope text (like TinyStories) lets small models produce visibly reasonable samples. *Already the default in this kit — knob 1 is pre-turned for you.*
2. **Decrease `VOCAB_SIZE`** (in `prepare.py`; it sizes the `own` tokenizer only): 8192 → 4096, 2048, 1024. Delete that dataset's `tokenizer` folder in the cache and re-run `uv run prepare.py`, since the tokenizer must be retrained. For a standard vocabulary instead, use `--tokenizer`.
3. **Lower `MAX_SEQ_LEN`** (in `prepare.py`), even down to 256, and compensate with a slightly larger per-device batch size (this kit autotunes that per GPU — see the candidate lists in `train.py`).
4. **Decrease `EVAL_TOKENS`** (in `prepare.py`) so validation runs on less data and eats less of your run.
5. **`DEPTH`** (in `train.py`) is the single primary knob for model complexity — most other sizes derive from it. Try lowering it to 4.
6. **`WINDOW_PATTERN`** (in `train.py`): plain `"L"` (full attention everywhere) may beat the banded patterns like `"SSSL"` on small GPUs. Try it.
7. **Lower `TOTAL_BATCH_SIZE`** (in `train.py`) — a lot, but keep it a power of 2, e.g. down to `2**14`.

Knobs 2–4 live in `prepare.py`, which experiments must not touch — but *you*, between sessions, absolutely may. Changing them (or anything in `prepare.py`) resets the meaning of your scores: start a fresh `results.tsv` so the log stays coherent.

### More to read

- **What this demonstrates** — [TRAINING-DECISIONS.md](https://github.com/aroughidea/autoresearch-win-rtx/blob/master/TRAINING-DECISIONS.md) in the worked example: the learning goals, and what each decision changes, in plain language.
- **Worked example** — [aroughidea/autoresearch-win-rtx](https://github.com/aroughidea/autoresearch-win-rtx) is the live repo this template was extracted from: real `results.tsv` history, kept and discarded experiments, and a full session walkthrough in `WALKTHROUGH.md`.
- **Karpathy's own session** — branch [`exp/H100/mar8`](https://github.com/karpathy/autoresearch/tree/exp/H100/mar8) on karpathy/autoresearch: ~125 experiments run overnight on an H100. Read the log like a paper: what did the agent try, what stuck? His project announcement is [here](https://x.com/karpathy/status/2029701092347630069).
- **New to neural networks?** — karpathy's README points beginners at this ["Dummy's Guide"](https://x.com/hooeem/status/2030720614752039185) for the background this README assumes.
- **Different hardware?** — [HARDWARE.md](HARDWARE.md): macOS forks, and renting a GPU pod for ~$5/night.

### Credits

- [Andrej Karpathy](https://github.com/karpathy) — the original [autoresearch](https://github.com/karpathy/autoresearch) and [nanochat](https://github.com/karpathy/nanochat), which the training code simplifies.
- [jsegov](https://github.com/jsegov) — the [Windows/consumer-GPU port](https://github.com/jsegov/autoresearch-win-rtx) with tiered VRAM floors.
- [aroughidea](https://github.com/aroughidea) — `chat.py`, run capture, the dataset and tokenizer choices, and this starter packaging.

License: MIT — see [LICENSE](LICENSE).
