@echo off
powershell -NoProfile -ExecutionPolicy Bypass -Command "$src = Resolve-Path 'faia_blender_tools/__init__.py'; $bak = '__init__.py.bak'; Copy-Item $src $bak; $c = [System.IO.File]::ReadAllText($src) -replace 'Production tools for game studios', 'Production tools for game studios (DEV)'; [System.IO.File]::WriteAllText($src, $c); Compress-Archive -Path 'faia_blender_tools' -DestinationPath 'faia_blender_tools.zip' -Force; Copy-Item $bak $src; Remove-Item $bak"
echo ZIP created: faia_blender_tools.zip
