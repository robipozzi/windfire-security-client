source ./common.sh

# ***** Activate Python Virtual environment
main()
{
    echo -e "${BLU}###########################################################${RESET}"
    echo -e "${BLU}########## Python Virtual Environment activation ##########${RESET}"
    echo -e "${BLU}###########################################################${RESET}"
    # Ensure the environment variable is set
    if [ -z "$PYTHON_CLIENT_VIRTUAL_ENV" ]; then
        echo -e "${MAGENTA}PYTHON_CLIENT_VIRTUAL_ENV${RESET} is not set"
        exit 1
    fi

    # Verify $PYTHON_CLIENT_VIRTUAL_ENV directory exists (check parent and current dir)
    if [ -d $PYTHON_CLIENT_VIRTUAL_ENV ]; then
        echo -e "Found Python Virtual environment at ${BLU}$PYTHON_CLIENT_VIRTUAL_ENV${RESET}"
        # Activate the virtual environment
        echo -e "${BLU}PYTHON_CLIENT_VIRTUAL_ENV${RESET} is set to ${BLU}$PYTHON_CLIENT_VIRTUAL_ENV${RESET}, proceeding to activate ..."
        echo -e "Activating Python Virtual Environment with command ${BLU}source $PYTHON_CLIENT_VIRTUAL_ENV/bin/activate${RESET}..."
        source "$PYTHON_CLIENT_VIRTUAL_ENV/bin/activate"
        echo -e "${GREEN}Python Virtual Environment activated${RESET}"
        echo 
        source ./installPrereqs.sh $1
    else
        echo -e "${MAGENTA}Directory specified by PYTHON_CLIENT_VIRTUAL_ENV not found:${RESET} ${MAGENTA}$PYTHON_CLIENT_VIRTUAL_ENV${RESET}"
        echo -e "${MAGENTA}Exiting ...${RESET}"
        exit 1
    fi
}

# ***** MAIN EXECUTION
main $1