# Basic Launcher Native

![Untitled](https://github.com/user-attachments/assets/1ea31e29-d083-4e65-8300-c75442811e8c)

the new/alternative version of my [basic-launcher](https://github.com/ingobeans/basic-launcher)

it uses pygame rather than eel! 

## why pygame?

i switched from eel because i wanted to be able to compile to binary that doesn't rely on a browser / electron. also eel was quite slow at launching

pygame is easy to build, and has **native controller support**, which is and was one of the primary goals of basic-launcher. most UI libraries don't offer controller support.

## build

build with pyinstaller with: `python -m PyInstaller main.py --add-data assets;assets --onefile --noconsole -n basic-launcher.exe`
