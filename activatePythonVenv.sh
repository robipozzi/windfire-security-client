source ./setenv.sh

# ***** Activate Python Virtual environment
main()
{
    echo -e "${BLU}###########################################################${RESET}"
    echo -e "${BLU}########## Python Virtual Environment activation ##########${RESET}"
    echo -e "${BLU}###########################################################${RESET}"
    # Ensure the environment variable is set
    if [ -z "$PYTORCH_CLIENT_VIRTUAL_ENV" ]; then
        echo -e "${MAGENTA}PYTORCH_CLIENT_VIRTUAL_ENV${RESET} is not set"
        exit 1
    fi

    # Verify $PYTORCH_CLIENT_VIRTUAL_ENV directory exists (check parent and current dir)
    if [ -d $PYTORCH_CLIENT_VIRTUAL_ENV ]; then
        echo -e "Found Python Virtual environment at ${BLU}$PYTORCH_CLIENT_VIRTUAL_ENV${RESET}"
        # Activate the virtual environment
        echo -e "${BLU}PYTORCH_CLIENT_VIRTUAL_ENV${RESET} is set to ${BLU}$PYTORCH_CLIENT_VIRTUAL_ENV${RESET}, proceeding to activate ..."
        echo -e "Activating Python Virtual Environment with command ${BLU}source $PYTORCH_CLIENT_VIRTUAL_ENV/bin/activate${RESET}..."
        source "$PYTORCH_CLIENT_VIRTUAL_ENV/bin/activate"
        echo -e "${GREEN}Python Virtual Environment activated${RESET}"
        echo 
        source ./installPrereqs.sh $1
    else
        echo -e "${MAGENTA}Directory specified by PYTORCH_CLIENT_VIRTUAL_ENV not found:${RESET} ${MAGENTA}$PYTORCH_CLIENT_VIRTUAL_ENV${RESET}"
        echo -e "${MAGENTA}Exiting ...${RESET}"
        exit 1
    fi
}

# ***** MAIN EXECUTION
main $1