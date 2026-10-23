@echo off
powershell -Command "Compress-Archive -Path 'faia_blender_tools' -DestinationPath 'faia_blender_tools.zip' -Force"
echo ZIP created: faia_blender_tools.zip
