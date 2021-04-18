import subprocess

class colors:
    HEADER = '\033[95m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    END = '\033[0m'


print(colors.HEADER + "Testing in Env without Vim, but with Emacs" + colors.END)
out = subprocess.run('bash -c "source /projects/team-1/devops/anaconda3/etc/profile.d/conda.sh; conda activate test_1; /bin/bash check_for_emacs.sh; /bin/bash check_for_vim.sh"', shell=True)
print(out)

print(colors.HEADER + "Testing in Env without Emacs, but with Vim" + colors.END)
out = subprocess.run('bash -c "source /projects/team-1/devops/anaconda3/etc/profile.d/conda.sh; conda activate test_2; /bin/bash check_for_emacs.sh; /bin/bash check_for_vim.sh"', shell=True)
print(out)

