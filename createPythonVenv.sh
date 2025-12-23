source ./common.sh

# ***** Create Python Virtual environment
main()
{
    echo -e "${BLU}#########################################################${RESET}"
    echo -e "${BLU}########## Python Virtual Environment creation ##########${RESET}"
    echo -e "${BLU}#########################################################${RESET}"
    # Check if the directory exists
    echo -e "Check if Python virtual environment ${BLU}$PYTHON_CLIENT_VIRTUAL_ENV${RESET} exists"
    if [ -d "$PYTHON_CLIENT_VIRTUAL_ENV" ]; then
        echo -e "Python virtual environment ${BLU}$PYTHON_CLIENT_VIRTUAL_ENV${RESET} exists, activating ..."
        echo
        activate $1
    else
        echo -e "${MAGENTA}Python virtual environment $PYTHON_CLIENT_VIRTUAL_ENV does not exist, creating ...${RESET}"
        echo
        create
        echo
        activate $1
    fi
}

create()
{
    echo Creating Python Virtual Environment ...
    python3 -m venv $PYTHON_CLIENT_VIRTUAL_ENV
    echo -e "${GREEN}Python Virtual Environment created${RESET}"
}

activate()
{
    source ./activatePythonVenv.sh $1
}

# ***** MAIN EXECUTION
main $1