#!/bin/bash
source ./setenv.sh

# ***** Run Windfire Security client test application

# ===== MAIN FUNCTION =====
main()
{
    echo -e "${BLU}#########################################################################${RESET}"
    echo -e "${BLU}############### Windfire Security client test application ###############${RESET}"
    echo -e "${BLU}#########################################################################${RESET}"
    echo This script will run the following steps:
    echo    1. Create a Python Virtual Environment, if does not exist
    echo    2. Activate the Python Virtual Environment
    echo    3. Install Python prerequisites, if not already installed
    echo    4. Run the Windfire Security client test application
    echo 
    source ./createPythonVenv.sh
    run $1
}

# ===== Run Authentication client quick test =====
run()
{
    printSelectEnvironment $1
    getCredentials
    echo -e "${CYAN}Running authentication client in environment : $ENVIRONMENT${RESET}"
    ENVIRONMENT=$ENVIRONMENT \
    USERNAME=$USERNAME \
    PASSWORD=$PASSWORD \
    SERVICE=$AUTH_SERVICE_TEST \
    python3 testAuth.py
}

# ===== EXECUTION =====
main $1