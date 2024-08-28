# SmartRockClimbing

## Description
SmartRockClimbing is a desktop application that offers AI assistance for rock climbing enthusiasts.

## Features
- Suggests climbing routes
- Analyzes climbing techniques
- Provides real-time feedback

## Installation
1. Clone the repository.
2. Follow the setup instructions below.
3. Launch the application on your desktop.

## Usage
- Input your climbing goals.
- Receive personalized AI guidance.

---

## How to Create .exe Files

- Create Install_SmartRockClimbing.exe file

```shell
cd ./Installation
pyinstaller --debug=all --windowed --onefile --add-data ".\Data;.\Data" .\Install_SmartRockClimbing.py
(Run Install_SmartRockClimbing.exe inside /Installation/dist)
```

- Create SmartRockClimbing.exe file

```shell
cd ..
pyinstaller --debug=all --windowed --onefile .\SmartRockClimbing.py
(copy the below text to SmartRockClimbing.spec)
pyinstaller .\SmartRockClimbing.spec
(Run SmartRockClimbing.exe inside /dist)
```

_SmartRockClimbing.spec_

```plaintext
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

def get_mediapipe_path():
    import mediapipe
    mediapipe_path = mediapipe.__path__[0]
    return mediapipe_path

a = Analysis(
    ['SmartRockClimbing.py'],
    pathex=[],
    binaries=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

mediapipe_tree = Tree(get_mediapipe_path(), prefix='mediapipe', excludes=["*.pyc"])
a.datas += mediapipe_tree
a.binaries = filter(lambda x: 'mediapipe' not in x[0], a.binaries)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [('v', None, 'OPTION')],
    name='RockClimbing',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```
