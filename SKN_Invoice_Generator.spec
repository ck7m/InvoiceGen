from PyInstaller.utils.hooks import collect_all

datas = [('src/rendering/template.html', 'src/rendering')]
binaries = []
hiddenimports = [
    'flet_desktop',
    'flet_desktop.version',
]

for package_name in ['flet', 'flet_desktop', 'weasyprint', 'jinja2', 'xhtml2pdf', 'reportlab']:
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(package_name)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

a = Analysis(
    ['src/main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SKN_Invoice_Generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SKN_Invoice_Generator',
)
import sys

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='SKN_Invoice_Generator.app',
        icon=None,
        bundle_identifier=None,
    )

