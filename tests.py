import pexpect
import sys


VERBOSE = False
if len(sys.argv) > 1:
    if sys.argv[1] == "-v":
        VERBOSE = True


def start_shell():
    child = pexpect.spawn("python3 main.py")
    if VERBOSE:
        child.logfile = sys.stdout.buffer
    expect_prompt(child)
    return child


def exit_shell(child):
    child.sendline("exit")
    child.expect(pexpect.EOF)


def expect_prompt(child):
    res = child.expect(["(.*) > ", pexpect.TIMEOUT], timeout=1)
    if res != 0:
        print("Timeout")
        exit(1)


# Test if exit command works
def test_exit():
    child = start_shell()
    exit_shell(child)
    print("!!!!!!! start and exit passed !!!!!!!")


# Test if cd command works
child = start_shell()
child.sendline("mkdir x")
expect_prompt(child)
child.sendline("cd x")
expect_prompt(child)
exit_shell(child)
print("!!!!!!! mkdir and cd passed !!!!!!!")

# Test if pwd command works
child = start_shell()
# the prompt is the current working directory
prompt = child.match.group(1).decode()
child.sendline("pwd")
child.expect_exact([prompt, pexpect.TIMEOUT], timeout=1)
exit_shell(child)
print("!!!!!!! pwd changes prompt passed !!!!!!!")

# Test if entering just newlines works
child = start_shell()
for i in range(5):
    child.sendline("\n")
    expect_prompt(child)
exit_shell(child)
print("!!!!!!! blank commands passed !!!!!!!")

# Test if entering a command that is not in the PATH works
child = start_shell()
child.sendline("not_a_command")
child.expect_exact(["Command not found in the path", pexpect.TIMEOUT], timeout=1)
exit_shell(child)
print("!!!!!!! non-existent command passed !!!!!!!")

# Test if entering running mkdir works, and showing where it is found in the path
child = start_shell()
child.sendline("mkdir x")
expect_prompt(child)
child.sendline("which mkdir")
child.expect_exact(["/bin/mkdir", pexpect.TIMEOUT], timeout=1)
expect_prompt(child)
exit_shell(child)
print("!!!!!!! mkdir and which mkdir passed !!!!!!!")

# Test if the prompt changes when you cd to directory x
child = start_shell()
child.sendline("cd x")
expect_prompt(child)
new_prompt = child.match.group(1).decode()
if not new_prompt.endswith("/x"):
    print("Prompt did not change for cd command")
    exit(1)
exit_shell(child)
print("!!!!!!! prompt changes after cd passed !!!!!!!")

# Test if you see an error when trying to cd into a non-existent directory
child = start_shell()
child.sendline("cd adsf")
child.expect_exact("No such file or directory: 'adsf'")
expect_prompt(child)
exit_shell(child)
print("!!!!!!! error message shown when cd to non-existent directory passed !!!!!!!")


# Test if running the true command returns a zero exit code,
# and that the exit code information is printed
child = start_shell()
child.sendline("true")
res = child.expect_exact(["[Child pid: ", pexpect.TIMEOUT], timeout=1)
if res == 1:
    print("Timeout")
    exit(1)
res = child.expect_exact([" -> 0]", pexpect.TIMEOUT], timeout=1)
if res == 1:
    print("ERROR: Timeout")
    exit(1)
exit_shell(child)
print("!!!!!!! zero exit code shown passed !!!!!!!")

# Test if running the false command returns a non-zero exit code
child = start_shell()
child.sendline("false")
res = child.expect_exact(["[Child pid: ", pexpect.TIMEOUT], timeout=1)
if res == 1:
    print("Timeout")
    exit(1)
res = child.expect_exact([" -> 1]", pexpect.TIMEOUT], timeout=1)
if res == 1:
    print("Timeout")
    exit(1)
exit_shell(child)
print("!!!!!!! 1 exit code shown passed !!!!!!!")

# Test if putting sleep in the background executes
child = start_shell()
child.sendline("sleep 2 &")
expect_prompt(child)
exit_shell(child)
print("!!!!!!! background command passed !!!!!!!")

# Test if putting multiple & at the end fails
child = start_shell()
child.sendline("sleep 1 & &")
child.expect_exact("only one & allowed")
expect_prompt(child)
exit_shell(child)
print("!!!!!!! multiple & in command line passed !!!!!!!")

# Test if putting & before the end fails
child = start_shell()
child.sendline("& sleep 1 &")
child.expect_exact("only one & allowed")
expect_prompt(child)
exit_shell(child)
print("!!!!!!! & at beginning detected passed !!!!!!!")

# Test if putting & not at the end fails (even if there is only 1)
child = start_shell()
child.sendline("sleep & 1")
child.expect_exact("& must be last item on the command line", timeout=1)
expect_prompt(child)
exit_shell(child)
print("!!!!!!! & in the middle detected passed !!!!!!!")

# Test running command with full pathname (/bin/sleep) finishes
child = start_shell()
child.sendline("/bin/sleep 1")
# You should see the child pid info, then the prompt.
res = child.expect_exact(["[Child pid: ", pexpect.TIMEOUT], timeout=1)
if res == 1:
    assert False, "Timeout"
res = child.expect_exact([" -> 0]", pexpect.TIMEOUT], timeout=2)
if res == 1:
    assert False, "ERROR: Timeout"
exit_shell(child)
print("!!!!!!! running command with full pathname passed !!!!!!!")

# Test if putting command in background returns prompt before command finishes
child = start_shell()
child.sendline(
    "./sleepecho &"
)  # this command sleeps for 3 seconds and then displays "done sleeping"

# You should see the child pid info, then the prompt and then "done sleeping" output.
res = child.expect(["""(\[Child pid:) (.*) > """, pexpect.TIMEOUT], timeout=4)
if res == 1:
    print("Timeout")
    exit(1)
child.expect("done sleeping", timeout=5)
exit_shell(child)
print("!!!!!!! prompt shown immediately when command in bg passed !!!!!!!")
