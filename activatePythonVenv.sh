source ./setenv.sh

# ***** Activate Python Virtual environment
main()
{
    echo ${blu}"###########################################################"${end}
    echo ${blu}"########## Python Virtual Environment activation ##########"${end}
    echo ${blu}"###########################################################"${end}
    # Ensure the environment variable is set
    if [ -z "$PYTORCH_CLIENT_VIRTUAL_ENV" ]; then
        echo "${mag}PYTORCH_CLIENT_VIRTUAL_ENV${end} is not set"
        exit 1
    fi

    # Verify $PYTORCH_CLIENT_VIRTUAL_ENV directory exists (check parent and current dir)
    if [ -d $PYTORCH_CLIENT_VIRTUAL_ENV ]; then
        echo "${blu}Found $PYTORCH_CLIENT_VIRTUAL_ENV at${end} ${blu}$PYTORCH_CLIENT_VIRTUAL_ENV${end}"
        # Activate the virtual environment
        echo "${blu}PYTORCH_CLIENT_VIRTUAL_ENV${end} is set to ${blu}$PYTORCH_CLIENT_VIRTUAL_ENV${end}, proceeding to activate ..."
        echo Activating Python Virtual Environment with command ${blu}source $PYTORCH_CLIENT_VIRTUAL_ENV/bin/activate${end}...
        source "$PYTORCH_CLIENT_VIRTUAL_ENV/bin/activate"
        echo ${grn}Python Virtual Environment activated${end}
        echo 
        source ./installPrereqs.sh $1
    else
        echo "${mag}Directory specified by PYTORCH_CLIENT_VIRTUAL_ENV not found:${end} ${mag}$PYTORCH_CLIENT_VIRTUAL_ENV${end}"
        echo "${mag}Exiting ...${end}"
        exit 1
    fi
}

# ***** MAIN EXECUTION
main $1