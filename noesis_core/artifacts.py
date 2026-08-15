"""Native artifact adapters. They execute only when a local source checkout is configured."""
from __future__ import annotations
from pathlib import Path
import json, os, subprocess
from .provenance import VerificationRecord

class ArtifactAdapter:
    def __init__(self, repo_root: str | None = None): self.root=Path(repo_root) if repo_root else None
    def exists(self, path): return bool(self.root and (self.root/path).exists())
    def run(self, argv, timeout=60):
        if not self.root: return {"ok":False,"error":"repository root not configured"}
        try:
            p=subprocess.run(argv,cwd=self.root,text=True,capture_output=True,timeout=timeout)
            return {"ok":p.returncode==0,"returncode":p.returncode,"stdout":p.stdout[-10000:],"stderr":p.stderr[-10000:]}
        except (OSError, subprocess.TimeoutExpired) as e: return {"ok":False,"error":str(e)}

class FrequencyEvidenceAdapter(ArtifactAdapter):
    def validate(self):
        target=self.root/"core"/"validate_mcp_network.py" if self.root else None
        if not target or not target.exists(): return {"ok":False,"error":"141hz validator not found"}
        return self.run([os.getenv("PYTHON","python"),str(target)])

class LeanAdapter(ArtifactAdapter):
    def build(self): return self.run(["lake","build"],timeout=300)
