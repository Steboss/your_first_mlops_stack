#!/bin/bash

# Function to install Conda for macOS
install_conda_mac() {
    echo "Installing Conda on macOS..."
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O ~/miniconda.sh
    bash ~/miniconda.sh -b -p $HOME/miniconda
    source "$HOME/miniconda/etc/profile.d/conda.sh"
    conda init
}

# Function to install Conda for Ubuntu
install_conda_ubuntu() {
    echo "Installing Conda on Ubuntu..."
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
    bash ~/miniconda.sh -b -p $HOME/miniconda
    source "$HOME/miniconda/etc/profile.d/conda.sh"
    conda init bash
}

# Check for Conda and install if not exists
if ! command -v conda &> /dev/null
then
    echo "Conda could not be found, installing..."
    # Detect the platform (similar to $OSTYPE)
    OS="`uname`"
    case $OS in
      'Linux')
        install_conda_ubuntu
        ;;
      'Darwin')
        install_conda_mac
        ;;
      *)
        echo "Operating system $OS not supported."
        exit 1
        ;;
    esac
else
    echo "Conda is already installed."
fi

# Create and activate Conda environment
echo "Creating and activating the Conda environment..."
conda create --name beam_pipeline python=3.11 -y
conda activate beam_pipeline

# Install requirements
echo "Installing requirements from requirements.txt..."
pip install -r requirements.txt

echo "Setup complete."
echo "To deactivate the conda environment use `conda deactivate beam_pipeline`";
