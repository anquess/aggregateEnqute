# -*- mode: python -*-

block_cipher = None


a = Analysis(['mainResult.py'],
             pathex=['C:\\Users\\higashiyama-k105r\\Documents\\�A���P�[�g���C�v���O����\\srcMakeResult'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='mainResult',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
