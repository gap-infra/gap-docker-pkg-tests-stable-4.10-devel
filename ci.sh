#!/usr/bin/env bash

set -e

SRCDIR=${SRCDIR:-$PWD}
# `-f5` relies on format https://provider.com/username/packagename
PKG_NAME="$(cut -d'/' -f5 <<< ${REPO_URL})"

echo SRCDIR   : $SRCDIR
echo REPO_URL : $REPO_URL
echo PKG_NAME : $PKG_NAME

git clone ${REPO_URL}

cd ${PKG_NAME}

###############################################################################
#

if [[ -f prerequisites.sh ]]
then
  ./prerequisites.sh
fi

# The next block is borrowed from 
# https://github.com/gap-system/gap/blob/master/bin/BuildPackages.sh
#
# build this package, if necessary
#
# We want to know if this is an autoconf configure script
# or not, without actually executing it!
if [[ -f autogen.sh && ! -f configure ]]
then
  ./autogen.sh
fi
if [[ -f "configure" ]]
then
  if grep Autoconf ./configure > /dev/null
  then
    ./configure --with-gaproot=/home/gap/inst/${GAPDIRNAME}
  else
    ./configure /home/gap/inst/${GAPDIRNAME}
  fi
  make
else
  echo "No building required for $PKG"
fi

# set up a custom GAP root containing only this package, so that
# we can force GAP to load the correct version of this package
mkdir -p gaproot/pkg/
ln -s $PWD gaproot/pkg/

###############################################################################

# start GAP with custom GAP root, to ensure correct package version is loaded
GAP="/home/gap/inst/${GAPDIRNAME}/bin/gap.sh -l $PWD/gaproot; --quitonbreak -q"

# Run package test
$GAP <<GAPInput
Read("/home/gap/travis/ci.g");
if TestOnePackage(LowercaseString(GetNameFromPackageInfo("PackageInfo.g"))) <> true then
    FORCE_QUIT_GAP(1);
fi;
QUIT_GAP(0);
GAPInput
