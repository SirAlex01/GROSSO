import os
from file_info import File, getDisassembly, getStrings
from utils import shouldCollect, isExecutableFile

def readDirectoryRecursively(root_dir, max_size_bytes):
    all_files = []
    layout_lines = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        level = dirpath.replace(root_dir, '').count(os.sep)
        indent = '│   ' * level
        layout_lines.append(f"{indent}├── {os.path.basename(dirpath)}/")

        subindent = '│   ' * (level + 1)
        for filename in filenames:
            file_full_path = os.path.join(dirpath, filename)
            layout_lines.append(f"{subindent}├── {filename}")

            if os.path.isfile(file_full_path) and not os.path.islink(file_full_path):
                f = File(file_full_path, root_dir)
                if shouldCollect(f, max_size_bytes):
                    all_files.append(f)

    layout_text = "\n".join(layout_lines)
    return all_files, layout_text

def collectFileContents(files):
    file_dict = {}

    for f in files:
        try:
            if f.kind == "text":
                with open(f.path, "r", encoding="utf-8", errors="replace") as fp:
                    content = fp.read()
            elif f.kind == "binary" and isExecutableFile(f):
                disassembly = getDisassembly(f.path)
                strings = getStrings(f.path)
                content = f"--- Disassembly ---\n{disassembly}\n\n--- Strings ---\n{strings}"
            else:
                content = "[Binary file without disassembly]"
        except Exception as e:
            content = f"[Error reading file: {e}]"

        file_dict[f] = content

    return file_dict

