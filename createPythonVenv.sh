source ./setenv.sh

# ***** Create Python Virtual environment
main()
{
    echo ${blu}"#########################################################"${end}
    echo ${blu}"########## Python Virtual Environment creation ##########"${end}
    echo ${blu}"#########################################################"${end}
    # Check if the directory exists
    echo Check if Python virtual environment ${blu}$PYTORCH_CLIENT_VIRTUAL_ENV${end} exists
    if [ -d "$PYTORCH_CLIENT_VIRTUAL_ENV" ]; then
        echo "Python virtual environment ${blu}$PYTORCH_CLIENT_VIRTUAL_ENV${end} exists, activating ..."
        echo
        activate $1
    else
        echo "${mag}Python virtual environment $PYTORCH_CLIENT_VIRTUAL_ENV does not exist, creating ..."${end}
        echo
        create
        echo
        activate $1
    fi
}

create()
{
    echo Creating Python Virtual Environment ...
    python3 -m venv $PYTORCH_CLIENT_VIRTUAL_ENV
    echo ${grn}Python Virtual Environment created${end}
}

activate()
{
    source ./activatePythonVenv.sh $1
}

# ***** MAIN EXECUTION
main $1