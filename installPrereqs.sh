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
    pip3 install --upgrade \
                google-auth-oauthlib==1.1.0 \
                google-auth-httplib2==0.2.0 \
                google-api-python-client==2.108.0 \
                colorama==0.4.6 \
                fastapi==0.104.1 \
                uvicorn[standard]==0.24.0 \
                PyJWT==2.8.0 \
                pydantic==2.5.0 \
                python-dateutil==2.9.0.post0 \
                cryptography==41.0.0
}

# ***** MAIN EXECUTION
main $1