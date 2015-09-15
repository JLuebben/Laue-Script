# -*- mode: python -*-
a = Analysis(['bin/LSInvCif'],
             pathex=['/home/jens/Laue-Script/projects/LSInvCif'],
             hiddenimports=[],
             hookspath=['lsinvcif'],
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='LSInvCif',
          debug=False,
          strip=None,
          upx=True,
          console=True )
