#!/usr/bin/env python3.6
#
# This script queries GitHub for the latest list of packages in the
# `gap-packages` organization, and then uses git and mercurial to clone any
# of them which have not already been cloned


from __future__ import print_function

import sys
if sys.version_info < (2,7):
    print("Python 2.7 or newer is required", file=sys.stderr)
    exit(1)

import json
import requests
import os
from subprocess import call

# all known repositories
repos = dict()

# add some repos not in the gap-packages org
repos['aaa'] = "https://github.com/ffloresbrito/aaa.git"
repos['CaratInterface'] = "https://github.com/lbfm-rwth/CaratInterface.git"
repos['crisp'] = "https://github.com/bh11/crisp.git"
repos['decomp'] = "https://gitlab.com/kaashif/decomp.git"
repos['DeepThoughtPackage'] = "https://github.com/duskydolphin/DeepThoughtPackage.git"
repos['difsets'] = "https://github.com/dylanpeifer/difsets.git"
repos['EDIM'] = "https://github.com/frankluebeck/EDIM.git"
repos['fga'] = "https://github.com/chsievers/fga.git"
repos['fining'] = "https://bitbucket.org/jdebeule/fining.git"
repos['fsr'] = "https://github.com/nzidaric/fsr.git"
repos['irredsol'] = "https://github.com/bh11/irredsol.git"
repos['jupyterviz'] = "https://github.com/nathancarter/jupyterviz.git"
repos['MajoranaAlgebras'] = "https://github.com/MWhybrow92/MajoranaAlgebras.git"
repos['matgrp'] = "https://github.com/hulpke/matgrp.git"
repos['ModularGroup'] = "https://github.com/le-on/ModularGroup.git"
repos['NoCK'] = "https://github.com/pjastr/NoCK.git"
repos['Predicata'] = "https://github.com/FKlie/Predicata.git"
repos['QPA2'] = "https://github.com/oysteins/QPA2.git"
repos['simpcomp'] = "https://github.com/simpcomp-team/simpcomp.git"
repos['Thelma'] = "https://github.com/vlaver/Thelma.git"
repos['transgrp'] = "https://github.com/hulpke/transgrp.git"

#repos['ArangoDBInterface'] = "https://github.com/homalg-project/ArangoDBInterface"
#repos['CAP_project'] = "https://github.com/homalg-project/CAP_project"
#repos['homalg_project'] = "https://github.com/homalg-project/homalg_project"


# repos to skip in the gap-packages org
skip = frozenset([
    "francy",           # ??? should we perhaps include it?
    "gap-packages.github.io",   # not a package
    "gbnp",             # broken tests
    "itc",              # requires graphics, no point in testing
    "linboxing",        # retracted
    "pargap",           # retracted
    "PythonInterface",  # does not (yet?) do anything useful
    "rig",              # broken tests
    "ve",               # not a GAP 4 package
    "xgap",             # requires graphics, no point in testing
    ])

# TODO: skip more packages, based on the GAP branch we are targeting?

# TODO: make the GAP branch in the following customizable
sys.stdout.write("""language: c

branches:
  only:
    - master

env:
  global:
    - GAPCONTAINER="gapsystem/gap-docker-stable-4.10"

  matrix:
""")


print("Fetching repository list from GitHub...", file=sys.stderr)
url = 'https://api.github.com/orgs/gap-packages/repos?per_page=100'
while True:
    r = requests.get(url)
    j = r.json()
    # we ignore archived repositories
    new_repos = {item['name']: item['clone_url'] for item in j if not item['archived']}
    repos.update(new_repos)
    if "next" in r.links:
        print("Fetching more...", file=sys.stderr)
        url = r.links["next"]["url"]
    else:
        break

for pkg_name in sorted(repos, key=lambda s: s.lower()):
    if pkg_name in skip:
        continue
    print("    - REPO_URL=" + repos[pkg_name])
    #print("    - PKG_NAME=" + pkg_name + " REPO_URL=" + repos[pkg_name])

# Print .travis.yml footer
sys.stdout.write("""
services:
  - docker

before_install:
  - docker version
  - docker pull ${GAPCONTAINER}

script:
  - docker run -v $PWD:/home/gap/travis/ ${GAPCONTAINER} /bin/sh -c "REPO_URL=${REPO_URL} TERM=xterm LANG=en_GB.UTF-8 /home/gap/travis/ci.sh"
""")