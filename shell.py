"""
shell.py

This program implements a shell.
It repeatedly reads and executes user commands from a keyboard.

Using Python 3.10.9

Name: Emma Wang (ejw38)
Date: Sat. 2-4-23

"""

import os

_runInBackground = False

class GetPath:
    '''This class looks through directories for a given cmd.'''

    # This function returns where the cmd is found.
    def find(self, cmd):

        # get value of the PATH
        key = 'PATH'
        value = os.getenv(key)

        # split PATH into array of directories
        directs = value.split(":")
        #directs = value.split(";")	# Windows uses ;
        #directs.remove('')		# only in Windows
    
        # search path directories for cmd
        # return the directory found or empty string
        for d in directs:
            try:
            	scnned = os.scandir(d)
            except:
            	print("Error: Can't find directory: ", d)
            for thing in scnned:
                if thing.name==cmd:
                    return d
            scnned.close()
        return ""


class Parser:
    '''This class separates the given string into words.'''
    
    # constructor
    def __init__(self, string):
        self.string = string
    
    # separates string into list of words
    def parse(self, string):
    
        # handle newline
        if string == "\n":
            string = "nothing"
        
        parsed = string.split()
        
        if parsed[-1] == "&":
            global _runInBackground
            _runInBackground = True
            parsed.remove("&")
            
        return parsed

def main():

    while(True):
        
        # reset global variable
        _runInBackground == False
        
        # get current working directory
        cwd = os.getcwd()
        stri = input(cwd + "$ ")
        
        # call the CommandLine class, Parser, to read and parse
        x = Parser(stri)
        xlist = x.parse(stri)
        
        # implement exit and pwd and newline commands
        if stri=="exit":
            break
        elif stri == "nothing":
            pass
        elif stri=="pwd":
            print(cwd)

        # call cd function
        elif xlist[0] == "cd":
            CD(xlist)
        
        # implement non-built-in commands
        
        # if a full pathname was given
        elif os.path.isabs(xlist[0]):
            # check if program exists and is executable
            #xlist[0] += ".exe"
            if os.access(xlist[0], os.F_OK) and os.access(xlist[0], os.X_OK):
                # call execute
                execute(xlist)
            # or else print error
            else:
                print("Error: path doesn't exist or is inexecutable: ", xlist[0])
        
        # otherwise find location of cmd in path using GetPath()
        else:
            #xlist[0] += ".exe"		# only on Windows?
            y = GetPath()
            path = y.find(xlist[0])
            # if not found print error
            if path == "":
                print("Error: command not found: ", xlist[0])
            # build the fully-specified string
            else:
                #path = path + "\\" + xlist[0]		# for run on Windows add \
                path += xlist[0]
                # call execute
                execute(xlist)

def CD(xlist):
    '''This function implements the cd command. '''
    
    # handle when there's a space in a directory name
    xlist.remove("cd")
    if len(xlist) > 1:
        xlist[0] = ' '.join(xlist)
    try:
        os.chdir(xlist[0])
    except:
        print("Error: path not found: ", xlist[0])
    
def execute(xlist):
    '''This function executes the command in a child process.'''
    
    pid = os.fork()
    if pid == 0:		# the child
        try:
            print("\n[Child pid: ", os.getpid(), "]")
            os.execvp(xlist[0], xlist)
        except:
            print("Error: can't execute command: ", xlist[0])
    elif pid > 0:		# the parent
        if _runInBackground == False:
            ret = os.waitpid(pid, 0)
            print("[", ret[0], " -> ", ret[1], "]")

if __name__ == "__main__":
    main()
