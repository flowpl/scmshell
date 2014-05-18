#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, re, sys, subprocess, getpass, socket


class Color:
    RED = '\x1b[31m'
    BLUE = '\x1b[34m'
    GREEN = '\x1b[32m'
    YELLOW = '\x1b[33m'
    WHITE = '\x1b[37m'
    MAGENTA = '\x1b[35m'
    CYAN = '\x1b[36m'
    RESET = '\x1b[37m'


class Style:
    BRIGHT = '\x1b[1m'
    DIM = '\x1b[2m'
    NORMAL = '\x1b[0m'



class InfoFactory:

    def __init__(self):
        self._classes = (HgInfo(), GitInfo())


    def getInfoClass(self):
        for cls in self._classes:
            if cls.isCorrect():
                return cls
        return None



class AbstractInfo:
    def _command(self, comm, err = True):
        """runs a console command and returns the output from both stdin and stderr"""
        try:
            if err:
                return subprocess.check_output(comm, stderr=subprocess.STDOUT)
            else:
                fnull = open(os.devnull, "w")
                if fnull:
                    return subprocess.check_output(comm, stderr=fnull)
                    fnull.close()
                else:
                    return subprocess.check_output(comm)
        except subprocess.CalledProcessError as e:
            return e.output

    def _char(self, char):
        """decodes a utf-8 character into console encoding"""
        return char.decode(sys.stdout.encoding)


class AbstractDistributedInfo(AbstractInfo):
    def getSCMInfo(self):
        """parses scm info into a string for output"""
        retVal = ""
        retVal = "%s(%s:%s" % (Color.YELLOW, self.getName(), self.getCurrentBranch())
        changes = self.getChanges()
        if changes:
            if "behind" in changes:
                retVal += Style.DIM + ",origin" + self._char('►') + str(changes["behind"]["count"])
            if "ahead" in changes:
                retVal += Style.DIM + ",origin" + self._char('◄') + str(changes["ahead"]["count"])
            if "untracked" in changes:
                retVal += Style.DIM + ",untracked:" + str(changes["untracked"]["count"])
            if "unstaged" in changes:
                retVal += Style.DIM + ",unstaged:" + str(changes["unstaged"]["count"])
            if "uncommitted" in changes:
                retVal += Style.DIM + ",uncommitted:" + str(changes["uncommitted"]["count"])

        retVal += Style.BRIGHT + ")"
        return retVal



class HgInfo(AbstractDistributedInfo):

    def isCorrect(self):
        output = self._command(["hg", "status"])
        return len(output) <= 0 or output[:5] != 'abort'

    def getName(self):
        return 'hg'

    def getCurrentBranch(self):
        return self._command(['hg', 'branch'], False).strip()

    def getChanges(self):
        output = self._command(['hg', 'status'])
        result = {}
        for line in output.split("\n"):
            if len(line) > 0:
                if line[0] == '?':
                    if 'untracked' not in result:
                        result['untracked'] = {'count': 0}
                    result['untracked']['count'] += 1
                if line[0] == 'M':
                    if 'uncommitted' not in result:
                        result['uncommitted'] = {'count': 0}
                    result['uncommitted']['count'] += 1

        return result



class GitInfo(AbstractDistributedInfo):

    def isCorrect(self):
        """tests whether this class should be used for the cwd"""
        output = self._command(["git", "status"])
        return len(output) > 0 and output[:5] != 'fatal'

    def getName(self):
        """returns the current SCM name"""
        return 'git'

    def getCurrentBranch(self):
        """returns the current branch name"""
        output = self._command(["git", "branch"])
        if len(output) > 0:
            matches = re.search(r"(\*) (.*)", output)
            if matches is not None:
                return matches.groups()[1]

    def getChanges(self):
        """parses 'git status' into a dictionary containing info about untracked, unstaged and uncommitted files 
           and whether the local copy is ahead of or behind origin"""
        output = self._command(["git", "status"])
        mode = "none"
        result = {}
        for line in output.split("\n"):
            line = line.strip("# ")
            if line.find("Untracked files:") > -1:
                mode = "untracked"
                result[mode] = {"count": 0}
                continue
            elif line.find("Changes not staged for commit:") > -1:
                mode = "unstaged"
                result[mode] = {"count": 0}
                continue
            elif line.find("Changes to be committed:") > -1:
                mode = "uncommitted"
                result[mode] = {"count": 0}
                continue
            elif re.match(r'^[A_Z]', line):
                mode = "none"
                continue

            if len(line) > 0 and line.find("(use \"git") == -1 and mode != "none":
                result[mode]["count"] += 1

        behind = re.search(r"Your branch is behind 'origin/[a-zA-Z0-9]+' by ([0-9]+) commits?", output)
        if behind:
            groups = behind.groups()
            result["behind"] = {"count": groups[0]}

        ahead = re.search(r"Your branch is ahead of 'origin/[a-zA-Z0-9]+' by ([0-9]+) commits?", output)
        if ahead:
            groups = ahead.groups()
            result["ahead"] = {"count": groups[0]}
        return result





def getSCMInfo():
    scmFac = InfoFactory()
    scm = scmFac.getInfoClass()
    if scm:
        return scm.getSCMInfo()
    else:
        return ''


def getDirectoryInfo():
    return "%s%s" % (Color.BLUE, os.getcwd())


def getUserInfo():
    user = getpass.getuser()
    color = Color.GREEN
    if user == 'root':
        color = Color.RED

    return "%s%s%s" % (Style.BRIGHT, color, user)


def getHostInfo():
    return socket.gethostname()


if __name__ == '__main__':

    scmInfo = getSCMInfo()
    print " "
    if len(scmInfo) > 0:
        print "%s%s@%s:%s%s%s%s" % (getUserInfo(), Style.DIM, getHostInfo(), Style.BRIGHT, getDirectoryInfo(), Style.NORMAL, Color.RESET)
        print "%s%s%s%s" % (Style.BRIGHT, getSCMInfo(), Style.NORMAL, Color.RESET)
    else:
        print "%s%s@%s:%s%s%s%s" % (getUserInfo(), Style.DIM, getHostInfo(), Style.BRIGHT, getDirectoryInfo(), Style.NORMAL, Color.RESET)
