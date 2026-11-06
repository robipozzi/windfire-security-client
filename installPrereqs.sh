source ./common.sh

# ***** Main function
main()
{
    echo "Installing Python prerequisites..."
    installPythonModules
    echo "Python prerequisites installation complete."
    echo ""
}

# ***** Install Python prerequisites
installPythonModules()
{
    pip3 install -r requirements.txt
}

# ***** MAIN EXECUTION
main $1