@echo off
powershell -Command " ^
  $src = 'faia_blender_tools/__init__.py'; ^
  $bak = 'faia_blender_tools/__init__.py.bak'; ^
  Copy-Item $src $bak; ^
  (Get-Content $src) -replace 'Production tools for game studios', 'Production tools for game studios (DEV)' | Set-Content $src -Encoding UTF8; ^
  Compress-Archive -Path 'faia_blender_tools' -DestinationPath 'faia_blender_tools.zip' -Force; ^
  Copy-Item $bak $src; ^
  Remove-Item $bak ^
"
echo ZIP created: faia_blender_tools.zip
