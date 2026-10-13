"""Repository files that the experiment record depends on."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _ignored(path):
    return subprocess.run(["git", "check-ignore", "-q", "--no-index", path], cwd=ROOT).returncode == 0


def _tracked(path):
    out = subprocess.run(["git", "ls-files", "--", path], cwd=ROOT, capture_output=True, text=True).stdout
    return bool(out.strip())


def test_the_record_and_the_models_stay_on_this_machine():
    assert _ignored("sessions/s1/runs/r.json")
    assert _ignored("checkpoint_pre_eval.pt") and _ignored("checkpoints/r.pt")
    assert _ignored("runs/r.json")            # runs outside a session: quick tests


def test_there_is_no_top_level_scoreboard_to_edit():
    """Each session's scoreboard is sessions/<name>/results.tsv, written by lab.py; a top-level one
    would invite the agent to edit the wrong file."""
    assert not _tracked("results.tsv")
