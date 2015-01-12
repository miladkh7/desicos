def print_run_file(study_dir, model_names, tmpf):
    tmpf.write("import time\n")
    tmpf.write("import os\n")
    tmpf.write("import sys\n")
    tmpf.write("import inspect\n")
    tmpf.write("from subprocess import Popen\n")
    tmpf.write("abspath = os.path.abspath(inspect.getfile(inspect.currentframe()))\n")
    tmpf.write("CURDIR = os.path.dirname(abspath)\n")
    tmpf.write("output_dir = os.path.join(r'" + study_dir + "','outputs')\n")
    tmpf.write("os.chdir(output_dir)\n")
    tmpf.write("class Logger(object):\n")
    tmpf.write("    def __init__(self):\n")
    tmpf.write("        self.terminal = sys.stdout\n")
    tmpf.write("        self.log_path = os.path.join(CURDIR,'run_log.txt')\n")
    tmpf.write("        log = open(self.log_path, 'w')\n")
    tmpf.write(r"        log.write('RUN LOG FILE\n\n')" + "\n")
    tmpf.write("        log.close()\n")
    tmpf.write("\n")
    tmpf.write("    def write(self, message):\n")
    tmpf.write("        self.terminal.write(message)\n")
    tmpf.write("        log = open(self.log_path, 'a')\n")
    tmpf.write("        log.write(message)\n")
    tmpf.write("        log.close()\n")
    tmpf.write("sys.stdout = Logger()\n")
    tmpf.write("use_stopper=False\n")
    tmpf.write("if 'use_stopper' in sys.argv:\n")
    tmpf.write("    use_stopper=True\n")
    tmpf.write("    sys.argv.pop(sys.argv.index('use_stopper'))\n")
    tmpf.write("if 'gui' in sys.argv:\n")
    tmpf.write("    sys.argv.pop(sys.argv.index('gui'))\n")
    tmpf.write("else:\n")
    tmpf.write("    os.system('title Running ABAQUS jobs in {0}'.format(sys.argv[0]))\n")
    tmpf.write("\n")
    tmpf.write("model_names = [\\\n")
    for model_name in model_names:
        tmpf.write("            '" + model_name + "'" + ",\n")
    tmpf.write("           ]\n")
    tmpf.write("total = len(model_names)\n")
    tmpf.write("job_counter = 0\n")
    tmpf.write("for model_name in model_names:\n")
    tmpf.write("    job_counter += 1\n")
    tmpf.write("    #checking if job input file exists\n")
    tmpf.write("    tmp = os.path.join(output_dir, model_name + '.inp')\n")
    tmpf.write("    if not os.path.isfile(tmp):\n")
    tmpf.write("        print('Not found .inp  for: {0} at {1}'.format(model_name, time.ctime()))\n")
    tmpf.write("        continue\n")
    tmpf.write("    #checking if job is already finished\n")
    tmpf.write("    tmp = os.path.join(output_dir, model_name + '.log')\n")
    tmpf.write("    if os.path.isfile(tmp):\n")
    tmpf.write("        msgfile = open(tmp, 'r')\n")
    tmpf.write("        lines = msgfile.readlines()\n")
    tmpf.write("        msgfile.close()\n")
    tmpf.write("        if len(lines) > 1:\n")
    tmpf.write("            if lines[-2].find('End Abaqus/Standard Analysis') > -1:\n")
    tmpf.write("                print('Skipping: {0} at {1}'.format(model_name, time.ctime()))\n")
    tmpf.write("                continue\n")
    tmpf.write("            elif lines[-1].find('Abaqus/Analysis exited with errors') > -1:\n")
    tmpf.write("                print('Skipping (with ERRORS): {0} at {1}'.format(model_name, time.ctime()))\n")
    tmpf.write("                continue\n")
    tmpf.write("    if os.path.isfile('{0}.lck'.format(model_name)):\n")
    tmpf.write("        os.system('del {0}.lck'.format(model_name))\n")
    tmpf.write("    input_file = os.path.join(output_dir, model_name + '.inp')\n")
    tmpf.write("    command = 'abaqus job={0} input={1}'.format(model_name, input_file)\n")
    tmpf.write("    if len(sys.argv) > 1:\n")
    tmpf.write("        for i in range(1, len(sys.argv)):\n")
    tmpf.write("            command += ' '\n")
    tmpf.write("            command += sys.argv[ i ]\n")
    tmpf.write("    os.system(command)\n")
    tmpf.write("    print  '____________________'\n")
    tmpf.write("    print  ''\n")
    tmpf.write("    print('Counter: job {0:05d} out of {1:05d}'.format(job_counter, total))\n")
    tmpf.write("    print('Started  ABAQUS for: {0} at {1}'.format(model_name, time.ctime()))\n")
    tmpf.write("    stopper = 'not created yet'\n")
    tmpf.write("    while True:\n")
    tmpf.write("        if os.path.isfile(tmp):\n")
    tmpf.write("            msgfile = open(tmp, 'r')\n")
    tmpf.write("            lines = msgfile.readlines()\n")
    tmpf.write("            msgfile.close()\n")
    tmpf.write("            if len(lines) > 1:\n")
    tmpf.write("                if lines[-2].find('End Abaqus/Standard Analysis') > -1:\n")
    tmpf.write("                    print('Finished: {0} at {1}'.format(model_name, time.ctime()))\n")
    tmpf.write("                    break\n")
    tmpf.write("                elif lines[-1].find('Abaqus/Analysis exited with errors') > -1:\n")
    tmpf.write("                    print('Finished with ERRORS: {0} at {1}'.format(model_name, time.ctime()))\n")
    tmpf.write("                    break\n")
    tmpf.write("        else:\n")
    tmpf.write("            time.sleep(3)\n")
    tmpf.write("        time.sleep(5)\n")
    tmpf.write("        if not use_stopper:\n")
    tmpf.write("            continue\n")
    tmpf.write("        if os.name == 'nt':\n")
    tmpf.write("            if stopper == 'not created yet':\n")
    tmpf.write("                stopper = Popen(r'python ..\\job_stopper.py {0} {1}'.format(output_dir, model_name))\n")
    tmpf.write("            else:\n")
    tmpf.write("                if stopper.poll() == 0:\n")
    tmpf.write("                    stopper = Popen(r'python ..\\job_stopper.py {0} {1}'.format(output_dir, model_name))\n")
    tmpf.write("        else:\n")
    tmpf.write("            if stopper == 'not created yet':\n")
    tmpf.write("                stopper = Popen('python ../job_stopper.py {0} {1}'.format(output_dir, model_name))\n")
    tmpf.write("            else:\n")
    tmpf.write("                if stopper.poll() == 0:\n")
    tmpf.write("                    stopper = Popen('python ../job_stopper.py {0} {1}'.format(output_dir, model_name))\n")
    tmpf.write("print  '____________________'\n")
    tmpf.write("print  ''\n")
    tmpf.write("os.system('title Completed ABAQUS jobs in {0}'.format(sys.argv[0]))\n")
    tmpf.write("\n")
