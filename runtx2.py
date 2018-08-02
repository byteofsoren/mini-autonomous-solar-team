#!/usr/bin/env python
import rosgraph
import time
import os
import subprocess
import signal

pidfile = "/tmp/mast.pid"
rosruns = list()

class ros_process():
    def __init__(self, module, program):
        ''' ros_process creates inteface to the ros system
        module:= i.e distance_sens
        program:= i.e main.py
        '''
        self.module = module
        self.program = program

    def start(self):
        args = ['rosrun', str(self.module), str(self.program)]
        print("Starting {module}".format(module=self.module))
        print(args)
        self.proc = subprocess.Popen(args, shell=True)
        self.pid = self.proc.pid

    def kill(self):
        self.proc.terminate();

class roscore(object):

    """A class for starting the roscore"""

    def __init__(self, param=0):
        """no parameters  """
        self.module = roscore
        self.param = param

    def start(self):
        if self.param == 0:
            args = ['roscore', str(self.param)]
        else:
            args = ['roscore']

        try:
            self.pid = rosgraph.Master('/rostopic').getPid()
            self.proc = subprocess.Popen(['roscore'], shell=True)
            self.pid = self.proc.pid
        except socket.error:
            print("roscore is running did not start a other one")
                #raise ROSTopicIOException("Unable to communicate with master!")

    def kill(self):
        self.proc.kill()



def Exit_gracefully(signal, frame):
    #... log exiting information ...
    #... close any open files ...
    # Open the pid file
    for item in rosruns:
        item.kill()
    sys.exit(0)




if __name__ == "__main__":
    signal.signal(signal.SIGINT, Exit_gracefully)
    rosruns.append(roscore())
    rosruns.append(ros_process('distance_sensor', 'main.py'))
    rosruns.append(ros_process('ros_labview', 'main.py'))
    rosruns.append(ros_process('ros_labview', 'to_controll.py'))
    rosruns.append(ros_process('ros_labview', 'emstop.py'))


    for item in rosruns:
        item.start()
        time.sleep(4)



