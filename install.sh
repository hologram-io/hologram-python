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
        sudo apt-get -y install "$*"
    elif [ "$OS" == 'DARWIN' ]; then
        brew install "$*"
        echo 'TODO: macOS should go here'
    elif [ "$OS" == 'WINDOWS' ]; then
        echo 'TODO: windows should go here'
    fi
}

# EFECTS: Returns true if the specified program is installed, false otherwise.
function check_if_installed() {
    if command -v "$*" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Iterate over all programs to see if they are installed
# Installs them if necessary
for program in ${required_programs[*]}
do
    if [ "$program" == 'pppd' ]; then
        if ! check_if_installed "$program"; then
            pause "Installing $program. Press [Enter] key to continue...";
            install_software 'ppp'
        fi
    elif [ "$program" == 'pip' ]; then
        if ! check_if_installed "$program"; then
            pause "Installing $program. Press [Enter] key to continue...";
            install_software 'python-pip'
        fi
    elif check_if_installed "$program"; then
        echo "$program is already installed."
    else
        pause "Installing $program. Press [Enter] key to continue...";
        install_software "$program"
    fi
done

# Install SDK itself.
sudo pip install hologram-python
