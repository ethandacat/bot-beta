import re
import traceback
import sys
import io
import os
import subprocess
import multiprocessing

TIME_LIMIT = 10
CPP_COMPILE_TIME_LIMIT = 100
CPP_RUN_TIME_LIMIT =50

def extlangcode(text: str):
    parts = text.strip().split(None, 1)
    if not parts:
        return None, None
    language = parts[0].strip().lower()
    remainder = parts[1].strip() if len(parts) > 1 else ""
    remainder = re.sub(r'^`{1,3}', '', remainder).strip()
    if '\n' in remainder:
        first_line, rest = remainder.split('\n', 1)
        if re.match(r'^[a-zA-Z0-9+#]+$', first_line.strip()):
            code = rest.strip()
        else:
            code = remainder.strip()
    else:
        code = remainder.strip()
    code = re.sub(r'`{1,3}$', '', code).strip()
    return language, code


def run_code_python(code, queue):
    try:
        banned=[]
        ecode=re.sub(r'\s+', '', code.lower())
        ban = [
            "exec",                   # exec(...)
            "eval(",                  # eval(...)
            "compile(",               # compile(...)
            "__import__",             # __import__('os')
            "importlib",              # importlib.import_module(...)
            "builtins",               # builtins.open, getattr(builtins, ...)
            "__builtins__",           # __builtins__["open"], __builtins__.get(...)
            "getattr(",               # getattr(obj, "open"), or getattr(__builtins__, "open")
            "setattr(",               # setattr(obj, "__code__", ...)
            "globals(",               # globals()
            "locals(",                # locals()
            "__globals__",            # function.__globals__
            "__closure__",            # function.__closure__
            "__code__",               # function.__code__
            "__mro__",                # type.__mro__
            "__subclasses__",         # object.__subclasses__()
            "object.__getattribute__",# digging into internals
            "vars(",                  # vars(obj)
            "dir(",                   # dir(obj)
            "self.__dict__",          # accessing internal dicts
            "__dict__",               # any use of __dict__

            # Direct filesystem / OS access
            "open(",                  # open("/etc/passwd", ...)
            "os.",                    # os.system, os.popen, os.environ, os.remove, etc.
            "fromos",                 # from os import ...
            "importos",               # import os
            ",os",                    # ,os after removing whitespace
            "sys.",                   # sys.exit, sys.modules, sys.path, etc.
            "fromsys",                # from sys import ...
            "importsys",              # import sys
            ",sys",                   # ,sys (normalized)
            "os.environ",             # os.environ["SECRET"]
            "getenv(",                # os.getenv(...)

            # Subprocess / shell / process management
            "subprocess",             # import subprocess, subprocess.Popen
            "fromsubprocess",         # from subprocess import ...
            "importsubprocess",       # import subprocess
            ",subprocess",            # ,subprocess
            "popen(",                 # os.popen(...), subprocess.Popen(...)
            "system(",                # os.system("…")
            "fork(",                  # os.fork()
            "exec(",                  # exec(…)  (already banned, but catch stray)
            "spawn(",                 # os.spawn*, multiprocessing.spawn
            "multiprocessing",        # import multiprocessing
            "frommultiprocessing",    # from multiprocessing import ...
            "importmultiprocessing",  # import multiprocessing
            ",multiprocessing",       # ,multiprocessing
            "threading",              # import threading
            "fromthreading",          # from threading import ...
            "importthreading",        # import threading
            ",threading",             # ,threading
            "concurrent",             # import concurrent, concurrent.futures
            "fromconcurrent",         # from concurrent import ...
            "importconcurrent",       # import concurrent
            ",concurrent",            # ,concurrent
            "asyncio",                # import asyncio
            "fromasyncio",            # from asyncio import ...
            "importasyncio",          # import asyncio
            ",asyncio",               # ,asyncio
            "pty",                    # import pty (interactive channels)
            "frompty",                # from pty import ...
            "importpty",              # import pty
            ",pty",                   # ,pty
            "fork",                   # detected anywhere (normalized)

            # Networking / HTTP / FTP / RPC
            "socket",                 # import socket, socket.socket()
            "fromsocket",             # from socket import ...
            "importsocket",           # import socket
            ",socket",                # ,socket
            "http",                   # import http.server, http.client, etc.
            "fromhttp",               # from http import ...
            "importhttp",             # import http
            ",http",                  # ,http
            "urllib",                 # import urllib.*, urllib.request.urlopen
            "fromurllib",             # from urllib import …
            "importurllib",           # import urllib
            ",urllib",                # ,urllib
            "requests",               # import requests
            "fromrequests",           # from requests import ...
            "importrequests",         # import requests
            ",requests",              # ,requests
            "ftplib",                 # import ftplib.FTP
            "fromftplib",             # from ftplib import ...
            "importftplib",           # import ftplib
            ",ftplib",                # ,ftplib
            "telnetlib",              # import telnetlib
            "fromtelnetlib",          # from telnetlib import ...
            "importtelnetlib",        # import telnetlib
            ",telnetlib",             # ,telnetlib
            "xmlrpc",                 # import xmlrpc.client
            "fromxmlrpc",             # from xmlrpc import ...
            "importxmlrpc",           # import xmlrpc
            ",xmlrpc",                # ,xmlrpc
            "websockets",             # import websockets
            "fromwebsockets",         # from websockets import ...
            "importwebsockets",       # import websockets
            ",websockets",            # ,websockets

            # File compression / serialization (arbitrary code exec)
            "pickle",                 # import pickle
            "frompickle",             # from pickle import …
            "importpickle",           # import pickle
            ",pickle",                # ,pickle
            "marshal",                # import marshal
            "frommarshal",            # from marshal import …
            "importmarshal",          # import marshal
            ",marshal",               # ,marshal
            "shelve",                 # import shelve
            "fromshelve",             # from shelve import …
            "importshelve",           # import shelve
            ",shelve",                # ,shelve
            "zipfile",                # import zipfile
            "fromzipfile",            # from zipfile import …
            "importzipfile",          # import zipfile
            ",zipfile",               # ,zipfile
            "tarfile",                # import tarfile
            "fromtarfile",            # from tarfile import …
            "importtarfile",          # import tarfile
            ",tarfile",               # ,tarfile
            "gzip",                   # import gzip
            "fromgzip",               # from gzip import …
            "importgzip",             # import gzip
            ",gzip",                  # ,gzip

            # Code introspection / reflection
            "code",                   # import code (interactive interpreter)
            "fromcode",               # from code import ...
            "importcode",             # import code
            ",code",                  # ,code
            "types",                  # import types
            "fromtypes",              # from types import ...
            "importtypes",            # import types
            ",types",                 # ,types
            "inspect",                # import inspect
            "frominspect",            # from inspect import ...
            "importinspect",          # import inspect
            ",inspect",               # ,inspect
            "ast",                    # import ast
            "fromast",                # from ast import ...
            "importast",              # import ast
            ",ast",                   # ,ast

            # Low-level / C-type / extensions
            "ctypes",                 # import ctypes
            "fromctypes",             # from ctypes import ...
            "importctypes",           # import ctypes
            ",ctypes",                # ,ctypes
            "cffi",                   # import cffi
            "fromcffi",               # from cffi import ...
            "importcffi",             # import cffi
            ",cffi",                  # ,cffi
            "sysconfig",              # import sysconfig
            "fromsysconfig",          # from sysconfig import ...
            "importsysconfig",        # import sysconfig
            ",sysconfig",             # ,sysconfig
            "resource",               # import resource
            "fromresource",           # from resource import ...
            "importresource",         # import resource
            ",resource",              # ,resource
            "signal",                 # import signal
            "fromsignal",             # from signal import ...
            "importsignal",           # import signal
            ",signal",                # ,signal
            "readline",               # import readline
            "fromreadline",           # from readline import ...
            "importreadline",         # import readline
            ",readline",              # ,readline
            "pty",                    # import pty
            "frompty",                # from pty import ...
            "importpty",              # import pty
            ",pty",                   # ,pty
            "termios",                # import termios
            "fromtermios",            # from termios import ...
            "importtermios",          # import termios
            ",termios",               # ,termios
            "turtle",                 # import turtle
            "fromturtle",             # from turtle import ...
            "importturtle",           # import turtle
            ",turtle",                # ,turtle

            # Dangerous built-in names often used for staging
            "open",                   # open(…)
            "input(",                 # input(…)
            "=input",                 # var=input
            " input",                 # “ input” (normalized catches “ from input”)
            "getattr(",               # getattr(obj, …)
            "setattr(",               # setattr(obj, …)
            "exit(",                  # exit(…)  (alias for sys.exit)
            "quit(",                  # quit(…) 
            "help(",                  # help(…)  
            "memoryview(",            # memoryview(...) (can reflect on binary data)
            "buffer(",                # buffer(...) (Python 2 compatibility)
            "eval",                   # eval(…) 
            "exec",                   # exec statement/function
            "chr(",                   # chr(...) (used in string‐reconstruction tricks)
            "ord(",                   # ord(...) (used with chr in obfuscation)

            # Other “almost‐always dangerous” names
            "__class__",              # cls = obj.__class__
            "__bases__",              # <type>.__bases__
            "__subclasshook__",       # <type>.__subclasshook__
            "__getattribute__",       # obj.__getattribute__(...)
            "__setattr__",            # obj.__setattr__(...)
            "__delattr__",            # obj.__delattr__(...)
            "__dict__",               # obj.__dict__
            "__dir__",                # obj.__dir__()
            "__call__",               # obj.__call__()
            "__reduce__",             # for pickle exploit
            "__reduce_ex__",          # for pickle exploit
            "__getattribute__",       # repeated to be sure
        ]


        hasin = False
        cstrip = re.sub(r'\s+', '', ecode.lower())
        banned = [b for b in ban if b in cstrip]
        
        if banned:
            msg = f"### Error: Your code is potentially dangerous.\n\nBanned keywords found:\n`{banned}`"
            print("BANNEDDDDDD PYTHON",banned)
            if "input" in banned or "input(" in banned or "=input" in banned:
                msg += "\n\n*(input is not supported by `@bot run` currently.)*"
            queue.put(msg)
            return

        output = io.StringIO()
        sys.stdout = output
        try:
            exec(code, {})
        except BaseException:
            queue.put(f"### Error:\n```txt\n{traceback.format_exc()}```")
            return
        finally:
            sys.stdout = sys.__stdout__

        queue.put(
            f"### Execution completed successfully.\nLanguage: Python\n\n**Output:**\n```txt\n{output.getvalue()}```"
        )

    except BaseException:
        queue.put(f"### Critical error:\n```txt\n{traceback.format_exc()}```")


def run_code_cpp(code, queue):
    try:
        banned = []
        ecode = re.sub(r'/\*.*?\*/|//.*?$','', code, flags=re.DOTALL|re.MULTILINE)
        ecode = re.sub(r'\s+', '', ecode.lower())
        ecode=ecode.replace('%:%:', '##').replace('%:', '#')
        ban = [
            # — Disallow macros or token‐pasting tricks —
            "%:",       # digraph for #
            "%:%:",     # digraph for ##
            "<:",
            ":>",
            "<%",
            "%>",
            "%>"
            "##",       # traditional token pasting
            "#define",  # macro definition
            "define",   # macro definition (even if disguised)
            "cat(",     # token pasting macro name (catch-all)
            "sys%:%:tem",  # reconstructed 'system'
            "ext%:%:ern",  # reconstructed 'extern'
            "a1(",         # user alias for system()
            "echo${",

            # — Dangerous headers (file I/O, processes, threads, sockets, dynamic loading)
            "<unistd.h>",       # POSIX: fork, exec, open, etc.
            "<sys/types.h>",
            "<sys/stat.h>",
            "<fcntl.h>",
            "<dirent.h>",

            "<sys/socket.h>",   # low‐level sockets
            "<netinet/in.h>",
            "<arpa/inet.h>",
            "<netdb.h>",

            "<sys/ipc.h>",      # IPC: shm, sem, msg
            "<sys/msg.h>",
            "<sys/shm.h>",
            "<sys/sem.h>",

            "<pthread.h>",      # POSIX threads
            "<thread>",         # std::thread (ban user threads)
            "<future>",         # std::future / promise
            "<mutex>",          # std::mutex
            "<condition_variable>",

            "<fstream>",        # file streams (ifstream/ofstream)
            "<fstream.h>",

            "<stdio.h>",        # C stdio (fopen, fread, fwrite, etc.)
            "<cstdio>",

            "<cstdlib>",        # C stdlib (system, getenv, malloc, free)
            "<stdlib.h>",       # redundant but safe to keep

            "<signal.h>",       # signals, raise, etc.
            "<sys/time.h>",
            "<sys/resource.h>",

            "<windows.h>",      # WinAPI (CreateProcess, file, registry, etc.)
            "<winbase.h>",

            "<setjmp.h>",       # non‐local jumps
            "<longjmp.h>",

            "<dlfcn.h>",        # dynamic loading (dlopen, dlsym)

            "<sys/mman.h>",     # mmap/munmap
            "<sys/ioctl.h>",    # ioctl
            "<sys/ptrace.h>",   # ptrace
            "<sys/types.h>",    # repeated guard

            "<filesystem>",     # C++17 filesystem
            "<experimental/filesystem>",
            "<boost/filesystem",# any Boost.FILESYSTEM include

            "<netinet/in.h>",   # repeated
            "<winsock2.h>",     # Windows sockets
            "<ws2tcpip.h>",     # Windows sockets

            # — Dangerous function calls / identifiers —
            "system(",          # system("…")
            "popen(",           # popen("…")
            "fork(",            # fork()
            "exec(",            # exec* family
            "execve(", "execl(", "execlp(", "execle(", "execv(", "execvp(", "execvpe(",
            "kill(",            # kill(pid,…)
            "wait(",            # wait()
            "exit(",            # exit() or std::exit()
            "raise(",           # raise(signal)
            "signal(",          # signal(SIG… , …)

            "socket(",          # socket(...)
            "bind(",            # bind(...)
            "listen(",          # listen(...)
            "accept(",          # accept(...)
            "connect(",         # connect(...)

            "dlopen(",          # dlopen("…")
            "dlsym(",           # dlsym(...)
            "loadlibrary(",     # Windows LoadLibrary
            "getprocaddress(",  # Windows GetProcAddress

            "mmap(",            # mmap(...)
            "munmap(",          # munmap(...)

            "ptrace(",          # ptrace(...)
            "setuid(",          # setuid(...)
            "setgid(",          # setgid(...)
            "seteuid(",         # seteuid(...)
            "setegid(",         # setegid(...)

            "getenv(",          # getenv("…")
            "putenv(",          # putenv(...)
            "setenv(",          # setenv(...)
            "unsetenv(",        # unsetenv(...)

            "fopen(",           # fopen(...)
            "fclose(",          # fclose(...)
            "fread(",           # fread(...)
            "fwrite(",          # fwrite(...)
            "remove(",          # remove("…")
            "rename(",          # rename("…")

            "ifstream",         # std::ifstream
            "ofstream",         # std::ofstream

            "freopen(",         # freopen(...)
            "fgets(",           # fgets(...)
            "fgetc(",           # fgetc(...)

            # — Ban any direct “cin” or input from standard input —
            "cin",              # std::cin  (no input allowed)
            "std::cin",         # fully qualified
            "scanf(",           # scanf(...)
            "fscanf(",          # fscanf(...)
            "gets(",            # gets(...)
            "getchar(",         # getchar(...)
            "getc(",            # getc(...)
            "getchar_unlocked(",# getchar_unlocked(...)
            "read(",            # POSIX read(...)
            "getline(",         # std::getline or C getline
            "std::getline(",    # fully qualified

            # — Macros / token‐pasting pessimizations —
            "(void*)system",    # cast‐based “system” invocation
            "(void*)popen",
            "(void*)exec",
            "(void*)fork",
            "(*system)",        # function‐pointer style
            "(*popen)",
            "(*exec)",

            "decltype(system)", # type‐trap
            "decltype(popen)",
            "decltype(exec)",

            # — Inline assembly / compiler extensions —
            "__asm",            # inline assembly
            "__asm__",          # GCC/Clang‐style inline asm
            "__attribute__",    # arbitrary attributes
            "__declspec",       # MSVC extensions
            "#pragma",           # e.g. #pragma comment(linker,…)

            # — Comments might hide dangerous code—you strip those first, but re‐check here —
            "//system",         # “system” inside a comment
            "/*system",         # inside a block comment
            "\"system\"",       # literal string containing “system”
            "'system'",

            # — Generic catch‐alls for substrings “system ”, “exec ” to prevent edge cases —
            "system ",          
            "exec ",            
            "popen ",
            "fork ",

            # — Prevent user threads / concurrency —
            "thread",           # catches std::thread
            "std::thread",
            "pthread",          # catches pthread_create, etc.
            "mutex",            # std::mutex
            "std::mutex",
            "condition_variable",  # std::condition_variable
            "std::condition_variable",
            "future",           # std::future
            "std::future",
            "atomic",           # std::atomic
            "std::atomic",

            # — Low‐level I/O redirection / file descriptor tricks —
            "dup2(",            # dup2(...)
            "dup(",             # dup(...)
            "open(",            # open(...)  (POSIX)
            "open64(",          # open64(...)
            "close(",           # close(...) (could close stdout)

            # — Any remaining dangerous includes not yet covered —
            "<boost",           # any Boost header
            "<sys/",            # any <sys/...> include (covers shm, sem, etc.)
            "<windows.h>",      # repeated; ensures worst‐case
            "<winbase.h>",      # repeated

            # — Prevent attempts to read from /proc or /sys —
            "/proc/",           # reading procfs
            "/sys/",            # reading sysfs

            # — Additional catch‐alls in case normalization missed something —
            "extern\"c\"",      # extern "C" declarations
            "extern'c'",        # variations
            "extern",           # (optionally block all extern)
            "nullptr",          # (unlikely to be misused alone, but catches tricks)

            # — Finally, ensure they cannot pretend iostream types are functions —
            "cout(",            # invalid function‐style call
            "cerr(",            # invalid
            "endl(",            # invalid manipulator call
        ]



        cleanedcode = re.sub(r'\s+', '', ecode.lower())
        input_tokens = {
            "cin", "scanf(", "fscanf(", "gets(", "getchar(",
            "getc(", "getchar_unlocked(", "read(", "getline(",
            "std::getline(", "std::cin"
        }

        hasin = False
        for i in ban:
            if i in cleanedcode:
                if i in input_tokens:
                    print("DA I IS", i)
                    hasin = True
                banned.append(i)
        

        if banned:
            if hasin:
                queue.put(
                    f"### Error: Your code is potentially dangerous.\n\n Banned keywords found:\n`{banned}`\n\n*(input is not supported by `@bot run` currently.)*"
                )
            else:
                queue.put(
                    f"### Error: Your code is potentially dangerous.\n\n Banned keywords found:\n`{banned}`"
                )
            return

        with open("temp.cpp", "w") as f:
            f.write(code)
        include_path = "/nix/store/fwh4fxd747m0py3ib3s5abamia9nrf90-glibc-2.39-52-dev/include"
        #sysroot_path = "/nix/store/9bv7dcvmfcjnmg5mnqwqlq2wxfn8d7yi-gcc-wrapper-13.2.0"
        sysroot_path = "/tmp/glibc-sysroot"
        # Verify include path and stdlib.h
        if not os.path.exists(os.path.join(include_path, "stdlib.h")):
            queue.put(f"### Error: stdlib.h not found in {include_path}")
            return
        gcc_path="/nix/store/14c6s4xzhy14i2b05s00rjns2j93gzz4-gcc-13.2.0"
        glibc_path = "/nix/store/fwh4fxd747m0py3ib3s5abamia9nrf90-glibc-2.39-52-dev"
        # Compile with sysroot
        try:
            assert os.path.exists(f"{glibc_path}/include/stdlib.h")
            assert os.path.exists(f"{gcc_path}/include/c++/13.2.0/iostream")
        except AssertionError:
            queue.put("There was an assertion error")
        compile_process = subprocess.run(
            [
                "g++",
                "temp.cpp",
                "-o", "temp.out",
                "--sysroot=/tmp/glibc-sysroot",
                "-I", f"{gcc_path}/include/c++/13.2.0",
                "-I", f"{gcc_path}/include/c++/13.2.0/x86_64-unknown-linux-gnu",
                "-Wno-nonnull"  # optional: suppress some glibc warnings
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=CPP_COMPILE_TIME_LIMIT
        )

        if compile_process.returncode != 0:
            queue.put(f"### Error: Compilation failed.\n```txt\n{compile_process.stderr}```\n### thing\n```txt\n{os.listdir('/nix/store/fwh4fxd747m0py3ib3s5abamia9nrf90-glibc-2.39-52-dev/include')}```")
            return

        # Execute
        execution_process = subprocess.Popen(
            "./temp.out",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            stdout, stderr = execution_process.communicate(timeout=CPP_RUN_TIME_LIMIT)
        except subprocess.TimeoutExpired:
            execution_process.kill()
            queue.put(f"### Error: Execution timed out after {CPP_RUN_TIME_LIMIT} seconds")
            return

        if stderr:
            queue.put(f"### Error: Runtime error\n```txt\n{stderr}```")
            return

        if execution_process.returncode != 0:
            queue.put(f"### Error: Program exited with code {execution_process.returncode}\n```txt\n{stdout}```")
            return

        queue.put(f"### Execution completed successfully.\nLanguage: C++\n\n**Output:**\n```txt\n{stdout}\n```")
    except subprocess.TimeoutExpired:
        queue.put(
            "### Error: C++ compilation or execution timed out!\nThe time limit is 15 seconds (compile + runtime) for C++."
        )
    except BaseException:
        queue.put(f"### Error:\n```txt\n{traceback.format_exc()}```")


def run_code(code, lang):
    if lang.lower() in ["py3", "py", "python", "python3", "snake"]:
        queue = multiprocessing.Queue()
        p = multiprocessing.Process(target=run_code_python, args=(code, queue))
        p.start()
        p.join(timeout=TIME_LIMIT)

        if p.is_alive():
            p.terminate()
            p.join()
            return "### Error: Python code execution timed out!\nThe runtime limit for Python is 10 seconds."

        if not queue.empty():
            return queue.get()
        return "### Error: No output returned from code execution."

    elif lang.lower() in ["cpp", "c++", "gcc", "g++"]:
        return "### Due to a bug, C++ is currently not functioning. Sorry!"
        # queue = multiprocessing.Queue()
        # p = multiprocessing.Process(target=run_code_cpp, args=(code, queue))
        # p.start()
        # p.join(timeout=CPP_RUN_TIME_LIMIT)

        # if p.is_alive():
        #     p.terminate()
        #     p.join()
        #     return "### Error: C++ code execution timed out!\nThe runtime limit (compiling+running) for C++ is 10 seconds."

        # if not queue.empty():
        #     return queue.get()
        # return "### Error: No output returned from C++ execution."

    else:
        return "### Error: Not a valid language.\n `@bot run` only supports Python and C++ currently."