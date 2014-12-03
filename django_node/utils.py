import os
import subprocess
import tempfile
from .settings import NPM_INSTALL_COMMAND
from .environment import npm_installed


def npm_install(target_dir):
    """
    cd into `target_dir`,
    call settings.NPM_INSTALL_COMMAND, and then
    cd back to the previous directory
    """

    origin_dir = os.getcwd()

    if not npm_installed:
        raise Exception(
            'Cannot run {command}: NPM cannot be found.'.format(
                command=NPM_INSTALL_COMMAND
            )
        )

    os.chdir(target_dir)

    with tempfile.TemporaryFile() as std_out_file, tempfile.TemporaryFile() as std_err_file:
        popen = subprocess.Popen(NPM_INSTALL_COMMAND, stdout=std_out_file, stderr=std_err_file)
        popen.wait()

        std_err_file.seek(0)
        std_err = std_err_file.read()
        if std_err:
            for line in std_err.splitlines():
                if line.lower().startswith('npm warn'):
                    print(line)
                else:
                    raise Exception(std_err)

        std_out_file.seek(0)
        std_out = std_out_file.read()
        if std_out:
            print('-' * 80)
            print(
                'Output from `{command}` in {target_dir}'.format(
                    command=' '.join(NPM_INSTALL_COMMAND),
                    target_dir=target_dir,
                )
            )
            print('-' * 80)
            print(std_out.strip())
            print('-' * 80)

    os.chdir(origin_dir)