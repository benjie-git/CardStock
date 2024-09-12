# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['designer.py'],
             pathex=['.'],
             binaries=[],
             datas=[('dist/containerDir', '.')],
             hiddenimports=['serial'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['PyInstaller', 'serial'],
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
          name='CardStock',
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
               name='CardStock')
app = BUNDLE(coll,
             name='CardStock.app',
             icon=None,
             bundle_identifier=None,
             info_plist={
                'NSPrincipalClass': 'NSApplication',
                'NSAppleScriptEnabled': False,
                'NSRequiresAquaSystemAppearance': True,
                'CFBundleDocumentTypes': [
                    {
                        'CFBundleTypeName': 'CardStock Stack',
                        'CFBundleTypeRole': 'Editor',
                        'CFBundleTypeExtensions': ['cds'],
                        'LSHandlerRank': 'Owner'
                        }
                    ]
                },
             )
