"""Package only observable local evidence and our generated implementation data."""
import json
import subprocess
import zipfile
from common import ROOT, WORK, REPORTS, sha256, write_json


def main():
    output=WORK/"delivery"
    output.mkdir(parents=True,exist_ok=True)
    candidates=list((WORK/"logs").glob("*.log"))+list((WORK/"logs").glob("*.json"))
    candidates += list((WORK/"vectors").glob("layer*/*.hex"))
    candidates += [WORK/"synthesis/linear_engine_netlist.v",WORK/"activity/core_edges.vcd"]
    candidates += [WORK/"accelerator_soc"/name for name in ("driver.elf","driver.bin","driver.hex","driver.dump","driver.map")]
    files=sorted({p for p in candidates if p.is_file()})
    records=[{"path":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":sha256(p),"bytes":p.stat().st_size} for p in files]
    manifest={"project_id":"E203-KWT-Accelerator","active_version":"v1",
        "source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "evidence_class":"ALTERNATIVE_VALIDATION","official_acceptance":"REVISE",
        "includes_failed_attempts":True,"files":records,
        "excluded":"Official PDF/PDK/macros/licenses, audio, dependency binaries, full conversation and all hidden reasoning",
        "vector_scope":"Training/validation-derived local regression tasks, not official evaluation answers. Firmware never contains expected output vectors."}
    write_json(output/"evidence_manifest.json",manifest)
    archive_path=output/"E203-KWT-Accelerator-v1-local-evidence.zip"
    with zipfile.ZipFile(archive_path,"w",zipfile.ZIP_DEFLATED) as archive:
        archive.write(output/"evidence_manifest.json","evidence_manifest.json")
        for record,p in zip(records,files): archive.write(p,record["path"])
    with zipfile.ZipFile(archive_path) as archive:
        if archive.testzip() is not None: raise RuntimeError("Evidence archive CRC verification failed")
    write_json(output/"delivery_checksums.json",{"evidence_archive":{"name":archive_path.name,"sha256":sha256(archive_path),"bytes":archive_path.stat().st_size},
        "source_archive":{"name":"E203-KWT-Accelerator-v1-source.zip","sha256":sha256(output/"E203-KWT-Accelerator-v1-source.zip")}})
    print(json.dumps({"archive":str(archive_path),"files":len(files),"sha256":sha256(archive_path)}))


if __name__=="__main__":
    main()
