##### Terminal Colors - START
# ===== COLOR CODES =====
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED=$'\e[1;31m'
MAGENTA=$'\e[1;35m'
BLU=$'\e[1;34m'
CYAN=$'\e[1;36m'
RESET='\033[0m'
BOLD='\033[1m'
# ===== EMOJI =====
coffee=$'\xE2\x98\x95'
coffee3="${coffee} ${coffee} ${coffee}"
##### Terminal Colors - END

###### Variable section - START
PYTHON_CLIENT_VIRTUAL_ENV=windfire-security-client
ENVIRONMENT=
DEFAULT_USERNAME=windfire
DEFAULT_AUTH_SERVICE_TEST=windfire-calendar-srv
VERIFY_SSL_CERTS=false
###### Variable section - END

###### Function section - START
# Function to select and set programs run environment
printSelectEnvironment()
{
    ENVIRONMENT_SELECTION=$1
    if [[ -n "${ENVIRONMENT_SELECTION}" ]]; then
        echo 
    else
        echo -e "${BLU}Select environment : ${RESET}"
        echo -e "${BLU}1. Development${RESET}"
        echo -e "${BLU}2. Test${RESET}"
        echo -e "${BLU}3. Production${RESET}"
        read ENVIRONMENT_SELECTION
    fi
	setEnvironment
}

setEnvironment()
{
	case $ENVIRONMENT_SELECTION in
		1)  ENVIRONMENT=dev
			;;
		2)  ENVIRONMENT=test
			;;
        3)  ENVIRONMENT=prod
            ;;
		*) 	printf "\n${RED}No valid option selected${RESET}\n"
			printSelectEnvironment
			;;
	esac
}

# Function to securely input credentials
getCredentials() {
    while true; do
        read -r -p "Enter username [${DEFAULT_USERNAME}]: " INPUT_USER
        if [[ -z "$INPUT_USER" ]]; then
            USERNAME="$DEFAULT_USERNAME"
        else
            USERNAME="$INPUT_USER"
        fi

        read -s -r -p "Enter password: " PASSWORD
        echo
        if [[ -z "$PASSWORD" ]]; then
            echo -e "${RED}Error: Password cannot be empty.${RESET}"
            continue
        fi

        read -r -p "Enter service [${DEFAULT_AUTH_SERVICE_TEST}]: " INPUT_SERVICE
        if [[ -z "$INPUT_SERVICE" ]]; then
            AUTH_SERVICE_TEST="$DEFAULT_AUTH_SERVICE_TEST"
        else
            AUTH_SERVICE_TEST="$INPUT_SERVICE"
        fi

        export USERNAME PASSWORD AUTH_SERVICE_TEST
        break
    done
}
###### Function section - END