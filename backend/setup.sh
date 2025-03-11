#!/bin/bash
# Setup script for the chatbot template backend

echo "Setting up the project..."

# Create virtual environment
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment"
    exit 1
fi
echo "Virtual environment created."

# Activate virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment"
    exit 1
fi
echo "Virtual environment activated."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

# Configure environment
echo "Copying environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from .env.example"
else
    echo ".env file already exists"
fi

# Create an activation script that can be sourced
cat > activate_env.sh << 'EOL'
#!/bin/bash
source "$(dirname "$0")/venv/bin/activate"
echo "Virtual environment activated. You can now run: make run"
EOL
chmod +x activate_env.sh

echo "Setup complete!"

# Attempt to activate in the current shell if this script is sourced
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    source venv/bin/activate
    echo "Virtual environment has been activated in your current shell."
    echo "You can now run the application with: make run"
else
    echo "NOTE: The setup is complete, but the virtual environment is not yet activated."
    echo "To activate the virtual environment, either:"
    echo "  - Run this script with source: source ./setup.sh"
    echo "  - Or use the activation script: source activate_env.sh"
    echo "After activation, you can run the application with: make run"
fi
