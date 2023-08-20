import subprocess, os

class AppsInstall ():

    def __init__(self):
        self.update()

    def update (self):
        process = subprocess.Popen(['pacman', '-Syu', '--noconfirm'], stdout=subprocess.PIPE, text=True)
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip())
            result = process.poll()
            if result is not None:
                self.search_pkg ("lightdm")
                break

    def install_pkg (self, pkg):
        process = os.system(f"pacman -S {pkg} --noconfirm")
        if process == 0:
            print("0")

    def search_pkg (self, pkg):
        if os.system(f"pacman -Ss {pkg} --noconfirm" ) == 0:
            print(f"The package {pkg} was found in official repository")
        else:
            print(f"The package was founded in AUR")
