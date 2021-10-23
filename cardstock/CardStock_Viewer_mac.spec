# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['viewer.py'],
             pathex=['.'],
             binaries=[],
             datas=[],
             hiddenimports=['serial'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['serial'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='CardStock_Viewer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='CardStock_Viewer')
app = BUNDLE(coll,
             name='CardStock_Viewer.app',
             icon=None,
             bundle_identifier=None,
             info_plist={
                'NSPrincipalClass': 'NSApplication',
                'NSAppleScriptEnabled': False,
                'CFBundleDocumentTypes': [
                    {
                        'CFBundleTypeName': 'CardStock Stack',
                        'CFBundleTypeRole': 'Viewer',
                        'CFBundleTypeExtensions': ['cds'],
                        'LSHandlerRank': 'Alternate'
                        }
                    ]
                },
            )
