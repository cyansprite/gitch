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

class Gitch(object):

    def __init__(self, nvim):
        self.nvim = nvim;
        self.init = False;
        self.filetype = ''

    @neovim.autocmd('BufEnter', pattern='*', sync=False)
    def on_vim(self):
        self.entrance()

    @neovim.autocmd('VimLeave', pattern='*', sync=True)
    def on_vim_l(self):
        if self.init:
            self.git.die()

    @neovim.autocmd('CursorMoved', pattern='*', eval="getline('.')", sync=True)
    def on_move(self, arg):
        if self.filetype == 'gitch':
            x = self.git.branch(arg)
            if x != "":
                self.nvim.command("echohl diffAdded")
                self.nvim.command("echom '{}'".format(x))
                self.nvim.command("echohl NONE")

    @neovim.autocmd('FileType', pattern='*', eval="&filetype", sync=True)
    def on_type(self, arg):
        self.filetype = arg;

    @neovim.autocmd('Syntax', pattern='*', eval="&syntax", sync=True)
    def on_syn(self, typ):
        self.syntax = typ;

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

    def entrance(self):
        if not self.init:
            self.git = git();
            self.init = True;
            self.nvim.out_write("Bitch\n")
            self.nvim.command("call gitch#gitList({})".format(self.git.project_list()));
            self.nvim.command("let g:gitchReady = 1")

    @neovim.command("TestCommand", range='', nargs='*')
    def testcommand(self, args, range):
        self.nvim.out_write("{}\n".format(self.git.roots))

    @neovim.function("GetSub", sync=True)
    def gitstatus(self, args):
        if len(args) == 1:
            if args[0] in self.git.roots:
                return self.git.roots[args[0]];
            return [];
        else:
            return [];

class git():
    def die(self):
        for x in self.temps:
            os.remove(x)

    def __init__(self):
        # TODO setup user vars
        self.bases = ['C:\\Users\\bcoffman'];
        # self.bases.append('C:\\Users\\bcoffman\\.local\\share\\nvim\\plugged');

        # TODO dont look inside of .git folders...
        self.excludes = ['AppData', '.local', '.fzf', '.cargo', '.nuget', 'node_modules', 'bin', '.hyper_plugins', '.multirust', '.rustup', '.vscode']

        self.gitRepos = []
        self.others = {}
        self.files = {}
        self.roots = {}
        self.dirs = []
        self.temps = []

        self.get_repos();

    def get_repos(self):
        for b in self.bases:
            for root, dirs, files in os.walk(b):
                dirs[:] = [d for d in dirs if not d in self.excludes];
                dirs[:] = [d for d in dirs if not d.startswith('.')];

                for d in dirs:
                    if d == ".git":
                        self.gitRepos.append(Repo(root));
                    elif root == b:
                        if b in self.others:
                            self.others[b].append(d)
                        else:
                            self.others[b] = [d]
                    else:
                        if root in self.roots:
                            self.roots[root].append(d)
                        else:
                            self.roots[root] = [d]

                for f in files:
                    if root == b:
                        if b in self.files:
                            self.files[b].append(f)
                        else:
                            self.files[b] = [f]


    def project_list(self):
        out = [];
        for r in self.gitRepos:
            out.append(r.root)
        return self.files;

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
