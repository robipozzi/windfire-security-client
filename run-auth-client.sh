source ./setenv.sh
source ./commons.sh

# ***** Main function to run Windfire Security client test application
main()
{
    echo ${blu}"#########################################################################"${end}
    echo ${blu}"############### Windfire Security client test application ###############"${end}
    echo ${blu}"#########################################################################"${end}
    echo This script will run the following steps:
    echo    1. Create a Python Virtual Environment, if does not exist
    echo    2. Activate the Python Virtual Environment
    echo    3. Install Python prerequisites, if not already installed
    echo    4. Run the Windfire Security client test application
    echo 
    source ./createPythonVenv.sh
    run $1
}

# ***** Run Authentication client quick test
run()
{
    printSelectEnvironment $1
    getCredentials
    echo ${cyn}Running authentication client in environment : $ENVIRONMENT${end}
    ENVIRONMENT=$ENVIRONMENT \
    USERNAME=$USERNAME \
    PASSWORD=$PASSWORD \
    SERVICE=$AUTH_SERVICE_TEST \
    python3 testAuth.py
}

# ***** MAIN EXECUTION
main $1