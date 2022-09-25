# -*- coding: utf-8 -*-
# from https://gist.github.com/jpmens/6248478

__all__ = ("get_git_version")

from subprocess import Popen, PIPE
import time

def get_current_git_head(abbrev):
    try:
        p = Popen(['git', 'rev-parse', 'HEAD'],
                  stdout=PIPE, stderr=PIPE)
        p.stderr.close()
        line = p.stdout.readlines()[0].decode("utf-8")
        return line.strip()

    except:
        return None


def is_dirty():
    try:
        p = Popen(["git", "diff", "--stat"],
                  stdout=PIPE, stderr=PIPE)
        p.stderr.close()
        lines = p.stdout.readlines()
        return len(lines) > 0
    except:
        return False


def read_release_version():
    try:
        f = open("RELEASE-VERSION", "r")

        try:
            version = f.readlines()[0]
            return version.strip()

        finally:
            f.close()

    except:
        return None


def get_git_version(abbrev=7):
    # Read in the version that's currently in RELEASE-VERSION.

    version = read_release_version()

    # try to get the current git head

    version += '+' + get_current_git_head(abbrev)
    if is_dirty():
        version += ".dirty" + str(int(time.time()))


    return version


if __name__ == "__main__":
    print(get_git_version())
