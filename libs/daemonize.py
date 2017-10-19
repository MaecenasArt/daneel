# -*- coding: utf-8 -*-
import sys
import os
import time
import  atexit
from signal import SIGTERM
import logging
# initialize log module which can be imported from parent module
log = logging.getLogger()


class Daemon:
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self,
            pidfile,
            stdin='/dev/null',
            stdout='/dev/null',
            stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (
                e.errno, e.strerror)
                )
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (
                e.errno, e.strerror)
                )
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        if os.path.isfile(self.pidfile):
            log.debug("Pidfile exists")
            try:
                pf = file(self.pidfile, 'r')
                pid = int(pf.read().strip())
                pf.close()
            except IOError:
                log.critical("Cannot read pid file")
                pid = None
        else:
            pid = None

        if pid:
            message = "Daemon already running on pid %s\n"
            sys.stderr.write(message % pid)
            log.critical("Daemon already running on pid %s" % pid)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()
        log.info("Daemon started")

    def stop(self):
        """
        Stop the daemon
        """
        # Try to fet the pid from the pidfile
        if os.path.isfile(self.pidfile):
            log.debug("Pidfile exists")
            try:
                pf = file(self.pidfile, 'r')
                pid = int(pf.read().strip())
                pf.close()
            except IOError:
                log.critical("Cannot read pid information")
                pid = None
        else:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            log.critical("pidfile %s does not exist. Daemon not running?" %
                self.pidfile)
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
                log.info("Daemon stopped correctly")
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                log.critical(str(err))
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been daemonized by start()
        or restart().
        """
        pass
