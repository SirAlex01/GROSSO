import os
import subprocess

class File:
    def __init__(self, path, root_dir):
        self.path = path
        self.name = os.path.join(os.path.basename(root_dir), os.path.relpath(path, root_dir))
        self.size = os.path.getsize(path)
        self.type = self._get_mime_type()
        self.kind = self._get_file_kind()

    def _get_mime_type(self):
        try:
            result = subprocess.run(['file', '--mime-type', '-b', self.path],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL,
                                    text=True,
                                    timeout=1)
            return result.stdout.strip()
        except Exception:
            return 'unknown'

    def _get_file_kind(self):
        try:
            result = subprocess.run(['file', '-b', self.path],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL,
                                    text=True,
                                    timeout=1)
            desc = result.stdout.lower()
            if 'text' in desc:
                return 'text'
            elif 'directory' in desc:
                return 'directory'
            else:
                return 'binary'
        except Exception:
            return 'unknown'

    def __repr__(self):
        return f"<File name={self.name}, size={self.size}B, type={self.type}, kind={self.kind}>"

def getDisassembly(path):
    try:
        result = subprocess.run(
            ['objdump', '-M', 'intel', '-d', path],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5
        )
        return result.stdout
    except Exception as e:
        return f"Disassembly failed: {e}"

def getStrings(path):
    try:
        result = subprocess.run(
            ['strings', path],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3
        )
        return result.stdout
    except Exception as e:
        return f"Strings failed: {e}"

