#!/bin/sh

# Installation script for toolchain / serene.

# toolchain.sh should be donwloaded in HOME folder
# document how to download the script from github on the confluence page (only the script)
# with the script, install the project with pip and add the environment variables if they don't exist
# check the command line tools thingy, as well as adapt for windows users

# check if there is a .local/bin direcotry, create it otherwise, add it to the PATH permanently

# check if xcode / command tools is installed if on Mac
# when commands are not install then install them

# check the operating system > https://stackoverflow.com/questions/3466166/how-to-check-if-running-in-cygwin-mac-or-linux

PROFILE="$HOME/.profile"

if ! [ -x "$(command -v grep)" ]; then
  printf "[error] grep is not installed." >&2
  exit 1
fi

if ! [ -x "$(command -v curl)" ]; then
  printf "[error] curl is not installed." >&2
  exit 1
fi

if [ -d "$PROFILE" ] && [ grep -E "SEMRUSHKEY|VALUESERPKEY" "$PROFILE" ]; then
  printf "[info] Environment varibles already set."
fi

if [ ! -f "$PROFILE" ]; then
  touch "$PROFILE" && 
    printf "[info] $PROFILE file created."
fi
