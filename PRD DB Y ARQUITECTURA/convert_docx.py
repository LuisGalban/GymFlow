import zipfile
import xml.etree.ElementTree as ET
import os

def read_docx(file_path):
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }
    texts = []
    try:
        with zipfile.ZipFile(file_path) as docx:
            tree = ET.fromstring(docx.read('word/document.xml'))
            for paragraph in tree.iter(f'{{{namespaces["w"]}}}p'):
                p_text = []
                for run in paragraph.iter(f'{{{namespaces["w"]}}}r'):
                    for text in run.iter(f'{{{namespaces["w"]}}}t'):
                        if text.text:
                            p_text.append(text.text)
                # Join runs and append to text list
                texts.append(''.join(p_text))
        return '\n'.join(texts)
    except Exception as e:
        return f"Error reading docx: {e}"

# Read PRD.docx and EstructuraDeLaBD.docx
workspace_dir = r"c:\Users\qwerty\Documents\GitHub\GymFlow\PRD DB Y ARQUITECTURA"
prd_path = os.path.join(workspace_dir, "PRD.docx")
db_path = os.path.join(workspace_dir, "EstructuraDeLaBD.docx")

prd_text = read_docx(prd_path)
db_text = read_docx(db_path)

with open(os.path.join(workspace_dir, "PRD.md"), "w", encoding="utf-8") as f:
    f.write(prd_text)

with open(os.path.join(workspace_dir, "EstructuraDeLaBD.md"), "w", encoding="utf-8") as f:
    f.write(db_text)

print("Extraction completed successfully.")
