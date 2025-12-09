#!/bin/bash
# run-QTranslator.sh

# some colores for making text bueaty 
BLACK='\033[0;30m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
NC='\033[0m'

function colored(){
    echo -e "${2}${1}${NC}"
}

# Exit when error accored
set e


# check venv is exist
if ! [ -d "venv/" ]; then
    colored "venv file not exist" "$RED"
    colored "creating env file.." "$YELLOW"
    python3 -m venv venv
    if [ "$?" != "0" ];then
        colored "failed to create venv." "$RED"
        exit 1
    else
        colored "virtual environment created." "$GREEN"
    fi
fi


# activate virtual environment
if [ -f "venv/bin/activate" ]; then
  source "venv/bin/activate"
else
  colored "activation file not found." "$RED"
  exit 1
fi

# installing dependencies
python -c "import deep_translator,arabic_reshaper,bidi,gtts,pygame,pynput,pyperclip,termcolor" &> /dev/null
if [ "$?" != "0" ]; then
    colored "dependencies need to download..." "$YELLOW"
    pip install deep-translator arabic-reshaper python-bidi gtts pygame pynput pyperclip termcolor  
fi
clear
colored "dependencies are ready!" "$GREEN"

# Strating QTranslator
exec python QTranslator.py
