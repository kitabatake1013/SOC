# -*- coding: utf-8 -*-
#app build tool
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import os
import sys
import subprocess
import shutil
import distutils.dir_util
import PyInstaller
def runcmd(cmd):
	proc=subprocess.Popen(cmd.split(), shell=True, stdout=1, stderr=2)
	proc.communicate()

appveyor=False

if len(sys.argv)==2 and sys.argv[1]=="--appveyor":
	appveyor=True

print("Starting build (appveyor mode=%s)" % appveyor)
build_filename=os.environ['APPVEYOR_REPO_TAG_NAME'] if 'APPVEYOR_REPO_TAG_NAME' in os.environ else 'snapshot'
print("Will be built as %s" % build_filename)

pyinstaller_path="pyinstaller.exe" if appveyor is False else "%PYTHON%\\Scripts\\pyinstaller.exe"
hooks_path = os.path.join(PyInstaller.__path__[0], "hooks/")
print("hooks_path is %s" % (hooks_path))
print("pyinstaller_path=%s" % pyinstaller_path)
if not os.path.exists("locale"):
	print("Error: no locale folder found. Your working directory must be the root of the project. You shouldn't cd to tools and run this script.")

if os.path.isdir("dist\\soc"):
	print("Clearling previous build...")
	shutil.rmtree("dist\\")
	shutil.rmtree("build\\")

print("Building...")
shutil.copy("tools/hook-googleapiclient.py", hooks_path)
runcmd("pyinstaller soc.py --windowed --log-level=ERROR")
runcmd("%s --windowed --log-level=ERROR soc.py" % pyinstaller_path)

shutil.copytree("tesseract-ocr\\", "dist\\SOC\\tesseract-ocr")
shutil.copytree("poppler\\", "dist\\SOC\\poppler")
shutil.copytree("locale\\","dist\\SOC\\locale", ignore=shutil.ignore_patterns("*.po", "*.pot", "*.po~"))
print("Compressing into package...")
shutil.make_archive("SOC-%s" % (build_filename),'zip','dist')
print("Done!")
