# !/usr/bin/python3
import os
import fnmatch
import re
import sys
import tempfile
import codecs
import time

from subprocess import Popen, PIPE

import neovim

@neovim.plugin
class Gitch(object):

    def __init__(self, nvim):
        self.nvim = nvim;
        self.init = False;

    @neovim.autocmd('VimEnter', pattern='*', eval='&filetype', sync=True)
    def on_vim(self, filetype):
        # self.nvim.command("GitchLoading")
        # self.nvim.async_call(lambda:[self.entrance(filetype)]);
        self.entrance(filetype)

    @neovim.autocmd('VimLeave', pattern='*', sync=True)
    def on_vim_l(self):
        if self.init:
            self.git.die()

    @neovim.autocmd('CursorMoved', pattern='*', eval="getline('.')", sync=True)
    def on_move(self, arg):
        x = self.git.branch(arg)
        if x != "":
            self.nvim.command("echohl diffAdded")
            self.nvim.command("echom '{}'".format(x))
            self.nvim.command("echohl NONE")

    @neovim.function("GitStatus", sync=True)
    def gitstatus(self, args):
        if len(args) == 1:
            # TODO refine
            x = self.git.temp_status(args[0])
            if x != "":
                self.nvim.command('10sp {}'.format(x))
                # FIXME
                time.sleep(.1)
                self.nvim.command('e')
                time.sleep(.1)
                self.nvim.command('set syntax={}'.format('gitcommit'))
        else:
            return '';

    def entrance(self, filetype):
        self.git = git();
        self.init = True;

        for x in self.git.project_list():
            self.nvim.out_write("{}\n".format(x));

        self.nvim.command("call gitch#gitList({})".format(self.git.project_list()));
        self.nvim.command("Gitch")

    # @neovim.autocmd('BufEnter', pattern='*.py', eval='expand("<afile>")', sync=True)
    # def on_bufenter(self, filename):
    #     self.nvim.out_write("testplugin is in " + filename + "\n")

class git():
    def die(self):
        for x in self.temps:
            os.remove(x)

    def __init__(self):
        # TODO setup user vars
        self.bases = ['C:\\Users\\bcoffman'];

        # TODO dont look inside of .git folders...
        self.excludes = ['AppData', '.local', '.fzf', '.cargo', '.nuget', 'node_modules', 'bin', '.hyper_plugins', '.multirust', '.rustup', '.vscode']

        self.gitRepos = [];
        self.get_repos();
        self.dirs = []
        self.temps = []

    def get_repos(self):
        for b in self.bases:
            for root, dirs, files in os.walk(b):
                dirs[:] = [d for d in dirs if not d in self.excludes];
                for d in dirs:
                    if d == ".git":
                        self.gitRepos.append(Repo(root));

    def project_list(self):
        out = [];
        for r in self.gitRepos:
            out.append(r.root)
        return out;

    def _get_rep(self,rep):
        rep = codecs.decode(rep, 'unicode_escape')
        self.temp = tempfile.NamedTemporaryFile('w+',delete=False)
        for x in self.gitRepos:
            if x.root == rep:
                return x;

    def branch(self,rep):
        x = self._get_rep(rep)
        if x:
            return x.get_command_branch()
        else:
            return "";

    def temp_status(self,rep):
        x = self._get_rep(rep)
        if x:
            x.run_command(['git', 'status'], self.temp);
            self.temp.close()
            self.temps.append(self.temp.name)
            return self.temp.name;
        else:
            return "";


class Repo():
    def __init__(self, d):
        self.root = d;
        self.branch = '';

    def get_command_branch(self):
        orig = os.getcwd();
        os.chdir(self.root);

        if self.branch == '':
            with Popen(['git', 'branch', '--no-color'], stdout=PIPE, stderr=PIPE, universal_newlines=True) as process:
                for line in process.stdout:
                    if line[0] == '*':
                        self.branch = line.strip();
                        break

        os.chdir(orig);
        return self.branch

    def run_command(self, cmd, temp):
        cmd.insert(1, "color.status=never")
        cmd.insert(1, "-c")

        orig = os.getcwd();
        os.chdir(self.root);

        with Popen(cmd, stdout=PIPE, universal_newlines=True) as process:
            for line in process.stdout:
                if len(line.strip()) > 0:
                    temp.write('# ' + line)
                else:
                    temp.write('#\n')

        os.chdir(orig);


#    def clean(self, wet = False):
#        if not wet:
#            x.run_command(['git', 'clean', '-fd', '--dry-run'])
#        else:
#            x.run_command(['git', 'clean', '-fd'])
#
#    def build_clean(self, wet = False):
#        if not wet:
#            x.run_command(['git', 'clean', '-Xfd', '--dry-run'])
#        else:
#            x.run_command(['git', 'clean', '-Xfd'])
#
#    def fetch(self, wet = False):
#        if not wet:
#            x.run_command(['git', 'fetch', '-a', '--dry-run'])
#        else:
#            x.run_command(['git', 'fetch', '-a'])
#
#    def status(self):
#        x.run_command(['git', 'status', '--porcelain'])
#
#    def diff(self):
#        x.run_command(['git', 'diff', '--stat'])
