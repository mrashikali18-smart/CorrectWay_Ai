import pathlib
import zipfile
root = pathlib.Path(__file__).resolve().parent
archive = root / 'correctway_django.zip'
if archive.exists():
    archive.unlink()
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for p in sorted(root.rglob('*')):
        if p == archive or p.name == 'create_project_zip.py':
            continue
        if p.is_file():
            z.write(p, p.relative_to(root))
print('ZIP_CREATED', archive.name, archive.stat().st_size)
