#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mercurial import demandimport; demandimport.enable()
from mercurial.dispatch import dispatch
from shlex import split

import sys, os

def _serve(repo_root, args):
    
    # get repo path
    repo_path = None
    for i in range(len(args)):
        if args[i] == '-R':
            repo_path = args[i+1]
    
    # validate repo path
    if repo_path is None:
        raise RuntimeError('Invalid repository path')
    
    # get full repo path
    full_repo_path = os.path.join(repo_root, repo_path)
    
    # replace old repo path
    for i in range(len(args)):
        if args[i] == repo_path:
            args[i] = full_repo_path
    
    return dispatch(args)


def _init(repo_root, args):
    
    # get repo path
    repo_path = None
    for i in range(len(args)):
        if args[i] == 'init':
            repo_path = args[i+1]

    # validate repo path
    if repo_path is None:
        raise RuntimeError('Invalid repository path')
    
    # get full repo path
    full_repo_path = os.path.join(repo_root, repo_path)
    
    # replace old repo path
    for i in range(len(args)):
        if args[i] == repo_path:
            args[i] = full_repo_path
    
    if dispatch(args) is None:
        with open(os.path.join(full_repo_path, '.hg', 'hgrc'), 'w') as fp:
            fp.write('''\
[web]
contact = undefined
description = %(path)s
''' % dict(path = repo_path))
        print >> sys.stderr, 'Created: %r' % full_repo_path
        
    else:
        raise RuntimeError('Failed to create: %r' % full_repo_path)
    

ALLOWED_ACTIONS = {
    'serve': _serve,
    'init': _init,
}


def hg_ssh():
    
    if len(sys.argv) != 2:
        raise RuntimeError('You should provide the repositories root.')
    
    repo_root = sys.argv[1]
    
    pieces = split(os.getenv('SSH_ORIGINAL_COMMAND', '?'))
    
    # validate command
    if pieces[0].split('/')[-1] != 'hg':
        raise RuntimeError('Invalid command: %r' % pieces[0])
    
    # get mercurial action
    action = None
    for _action in ALLOWED_ACTIONS:
        for piece in pieces[1:]:
            if piece == _action:
                action = _action
    
    # validate mercurial action
    if action is None:
        raise RuntimeError('Invalid hg action: %r' % action)
    
    # run mercurial action
    return ALLOWED_ACTIONS[action](repo_root, pieces[1:])


if __name__ == '__main__':
    sys.exit(hg_ssh())

