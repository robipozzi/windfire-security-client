source ./common.sh

# ***** Main function
main()
{
    echo "Installing Python prerequisites..."
    installPythonModules
    echo "Python prerequisites installation complete."
    echo ""
}

# ***** Install Python prerequisites for Google Calendar API
installPythonModules()
{
    pip3 install -r requirements.txt
}

# ***** MAIN EXECUTION
main $1