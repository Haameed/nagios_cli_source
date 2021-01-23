
import subprocess
import paramiko


def bash_execute(bashcommand):
    process = subprocess.Popen(bashcommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return {"output": output,"error":error}


def remote_bash_execute(remote_server, bashcommand):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(remote_server, port=22, username='root')
    stdin, stdout, stderr = ssh.exec_command(bashcommand)
    stdin.flush()
    return {"output": stdout.readlines(), "error": stderr.readlines()}
    ssh.close()




