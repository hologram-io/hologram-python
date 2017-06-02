#!/bin/bash
set -euo pipefail

# This script will install the Hologram SDK and the necessary software dependencies
# for it to work.

required_programs=('python' 'pip' 'ps' 'kill')
OS=''

# Check OS.
if [ "$(uname)" == "Darwin" ]; then

    echo 'Darwin system detected'
    OS='DARWIN'

elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then

    echo 'Linux system detected'
    OS='LINUX'
    required_programs+=('ip' 'pppd')

elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]; then

    echo 'Windows 32-bit system detected'
    OS='WINDOWS'

elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then

    echo 'Windows 64-bit system detected'
    OS='WINDOWS'
fi

function pause() {
    read -p "$*"
}

function install_software() {
    if [ "$OS" == 'LINUX' ]; then
        sudo apt-get install "$*"
    elif [ "$OS" == 'DARWIN' ]; then
        brew install "$*"
        echo 'TODO: macOS should go here'
    elif [ "$OS" == 'WINDOWS' ]; then
        echo 'TODO: windows should go here'
    fi
}

function check_if_installed() {
    if command -v "$*" >/dev/null 2>&1; then
        echo "$* is already installed."
    else
        pause "Installing $*. Press [Enter] key to continue...";
        install_software "$*"
    fi
}

# Check all software to see if they are installed
for program in ${required_programs[*]}
do
    check_if_installed $program
done

# Check for conflicts

# Install SDK itself.
sudo pip install hologram-python
