"""Verify public archive and select training/validation only using upstream split."""
import hashlib
import json
from pathlib import PurePosixPath
import sys
import tarfile
from common import ROOT, WORK, REPORTS, sha256, write_json
sys.path.insert(0, str(ROOT / "external/src/keyword-transformer"))
from kws_streaming.data.input_data import which_set

WORDS = "yes,no,up,down,left,right,on,off,stop,go".split(",")


def main():
    archive = ROOT / "external/cache/speech_commands_v0.02.tar.gz"
    if archive.stat().st_size != 2428923189:
        raise RuntimeError("Dataset archive is incomplete")
    h = hashlib.md5()
    with archive.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    if h.hexdigest() != "6b74f3901214cb2c2934e98196829835":
        raise RuntimeError("Dataset checksum differs from Google storage x-goog-hash")
    destination = WORK / "speech_subset"
    destination.mkdir(parents=True, exist_ok=True)
    buckets = {(split, label): [] for split in ("training", "validation") for label in WORDS + ["_unknown_"]}
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        for member in members:
            path = PurePosixPath(member.name)
            if not member.isfile() or path.suffix != ".wav" or len(path.parts) != 2 or path.parts[0].startswith("_"):
                continue
            split = which_set(path.name, 10, 10)
            label = path.parts[0] if path.parts[0] in WORDS else "_unknown_"
            if split in ("training", "validation"):
                buckets[split, label].append(member)
        chosen = []
        for (split, label), candidates in buckets.items():
            # Stable hash ordering independent of filesystem and TF RNG versions.
            candidates.sort(key=lambda p: hashlib.sha256(p.name.encode()).hexdigest())
            count = 8 if split == "training" else 4
            if len(candidates) < count:
                raise RuntimeError(f"Insufficient {split}/{label}")
            for member in candidates[:count]:
                target = destination / member.name
                if not target.resolve().is_relative_to(destination.resolve()):
                    raise RuntimeError("Unsafe dataset path")
                chosen.append({"split": split, "label": label, "archive_path": member.name,
                    "path": str(target.relative_to(ROOT)).replace("\\", "/")})
    by_name = {sample["archive_path"]: sample for sample in chosen}
    # One sequential extraction pass avoids repeated random seeks through gzip.
    with tarfile.open(archive, mode="r|gz") as tar:
        for member in tar:
            if member.name in by_name:
                sample = by_name[member.name]
                target = ROOT / sample["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(tar.extractfile(member).read())
                sample["sha256"] = sha256(target)
    # Silence is exactly 16000 zero samples, as required by the guide.
    chosen.extend({"split": s, "label": "_silence_", "path": None, "generated": "16000_float32_zeros"}
                  for s in ("training", "validation"))
    output = {"dataset": "speech_commands_v0.02", "source": "https://storage.googleapis.com/download.tensorflow.org/data/speech_commands_v0.02.tar.gz",
        "archive_sha256": sha256(archive), "archive_md5": h.hexdigest(), "samples": chosen,
        "split_implementation": "upstream input_data.which_set(filename,10,10)",
        "scope": "89 calibration and 45 validation samples; no testing data selected; not official 600 samples"}
    write_json(REPORTS / "model/dataset_manifest.json", output)
    print(output["scope"])


if __name__ == "__main__":
    main()
