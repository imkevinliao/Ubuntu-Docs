import os
import platform
import re
import subprocess

ERROR = -1


def run(cmds):
    """
    cmds：
    传入参数类型 list 视为多条命令
    传入参数类型 str 视为一条命令
    """

    # 函数内定义函数原因：减少缩进层级
    def core(cmd):
        completed = subprocess.run(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        ret = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
        print(f"Execute Command:{cmd}\nExecute status code: {ret}\n")
        if ret == 0:
            if stdout:
                print(f"Output:{stdout}\n")
        else:
            print(f"Error:{stderr}\n")

    if isinstance(cmds, list):
        for _ in cmds:
            core(_)
    elif isinstance(cmds, str):
        core(cmds)
    else:
        raise Exception("Input parameter is incorrect.")


def popen(cmds):
    def core(cmd):
        process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        for info in iter(process.stdout.readline()):
            print(info)
        stdout, stderr = process.communicate()
        ret = process.returncode
        print(f"Execute Command:{cmd}\nExecute status code: {ret}\n")
        if ret == 0:
            if stdout:
                print(f"Output:{stdout}\n")
        else:
            print(f"Error:{stderr}\n")
        process.kill()

    if isinstance(cmds, list):
        for _ in cmds:
            core(_)
    elif isinstance(cmds, str):
        core(cmds)
    else:
        raise Exception("Input parameter is incorrect.")


def config_python():
    """
    linux 下配置 sudo 免密，或者在 root 用户下执行
    <这些命令在我测试时候，被提示这些命令建议在终端交互下执行，不建议以脚本的方式执行>
    """
    config_source = ["sudo add-apt-repository ppa:deadsnakes/ppa -y",
                     "sudo apt update -y",
                     "sudo apt install python3.10 -y"]
    run(config_source)
    check_version = ["python3 --version", "python --version", "py3 --version"]
    python_version = None
    for i in check_version:
        completed = subprocess.run(i, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if completed.returncode == 0:
            _ = completed.stdout
            regex = r"3.\d+"
            match_result = re.search(regex, str(_))
            if match_result:
                python_version = match_result.group()
    config_version = ["sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1"]
    if python_version:
        config_version.append(
            f"sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python{python_version} 0")
    else:
        print(f"没有获取到系统当前的python3版本")
    run(config_version)


def config_git():
    # 个人偏爱
    git_log_a = """git config --global alias.lg "log --no-merges --color --graph --date=format:'%Y-%m-%d %H:%M:%S'
    --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Cblue %s %Cgreen(%cd) %C(bold blue)<%an>%Creset' --abbrev-commit" """
    # 更详细
    git_log_b = """git config --global alias.lg "log --no-merges --color --stat --graph --date=format:'%Y-%m-%d
    %H:%M:%S' --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Cblue %s %Cgreen(%cd) %C(bold blue)<%an>%Creset'
    --abbrev-commit" """
    # 网上通常是这个
    git_log_c = """git config --global alias.lg --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset
    %s %Cgreen(%cd) %C(bold blue)<%an>%Creset' --abbrev-commit -- """

    config_alias = ['git config --global alias.gp pull',
                    'git config --global alias.br branch',
                    'git config --global alias.co checkout',
                    'git config --global alias.ci commit',
                    'git config --global alias.st status', git_log_a]
    config_user = ['git config --global user.name "imkevinliao"',
                   'git config --global user.email "imkevinliao@gmail.com"']
    config_editor = ['git config --global core.editor vim']
    cmds = []
    cmds.extend(config_alias)
    cmds.extend(config_user)
    cmds.extend(config_editor)
    popen(cmds)
    print(f"config git finished，please use command：<cat ~/.gitconfig> to check.")


def git_dirs(path):
    all_dirs = []
    for root, dirs, files in os.walk(path):
        for dirname in dirs:
            all_dirs.append(os.path.join(root, dirname))
    g_dirs = []
    for _ in all_dirs:
        filepath, fullname = os.path.split(_)
        if ".git" == fullname:
            g_dirs.append(filepath)
    return g_dirs


def git_update(base_path=None):
    """
    linux 下默认查找当前用户目录下
    windows 默认查找当前脚本执行路径下
    """
    def get_base_path():
        if platform.system().lower() == "linux":
            _cmd = ["cd ~ && pwd"]
            completed = subprocess.run(_cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            if completed.returncode == 0:
                _base_path = completed.stdout.decode("utf-8").strip()
            else:
                _base_path = os.path.dirname(__file__)
        elif platform.system().lower() == "windows":
            _cmd = ["chdir"]
            completed = subprocess.run(_cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            _base_path = completed.stdout.decode("utf-8").strip()
        else:
            return ERROR
    if not base_path:
        base_path = get_base_path()
    git_paths = git_dirs(base_path)
    cmds = []
    for git_path in git_paths:
        cmd = f"cd {git_path} && git pull"
        cmds.append(cmd)
    run(cmds)


if __name__ == '__main__':
    git_update(base_path=r"D:\github")
