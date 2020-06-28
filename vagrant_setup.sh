#!/usr/bin/env bash
set -euxo pipefail
echo "Starting provision."
echo "-----------------------------"
start_seconds="$(date +%s)"

apt_packages=(
    vim
    curl
    wget
    git

    # pyenv requirements from common build issues
    make
    build-essential
    libssl-dev
    zlib1g-dev
    libbz2-dev
    libreadline-dev
    libsqlite3-dev
    llvm
    libncurses5-dev
    libncursesw5-dev
    xz-utils
    tk-dev
    libffi-dev
    liblzma-dev
    python-openssl

    # project needed packages
    nginx
    ffmpeg
    libavcodec-extra
)

sudo apt-get update -y
# Force debconf frontend to noninteractive and set option to package manager to install new conf without prompt.
sudo DEBIAN_FRONTEND=noninteractive apt-get -o Dpkg::Options::="--force-confnew" -y upgrade

# Packages Installation
echo "Installing packages..."
sudo apt-get install -y ${apt_packages[@]}
sudo apt-get clean

# pyenv installation
if [ ! -d "$HOME/.pyenv" ]; then
    echo "Installing pyenv and virtualenv plugin"
    curl https://pyenv.run | bash
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"

    # add following lines to .bashrc
    echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> $HOME/.bashrc
    echo 'eval "$(pyenv init -)"' >> $HOME/.bashrc
    echo 'eval "$(pyenv virtualenv-init -)"' >> $HOME/.bashrc
else
    echo "Pyenv is already installed."
fi

# Check if we can run pyenv command
if command -v pyenv; then
    pyenv version
else
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
fi

# Install python 3.6.1 with pyenv, delete virtual env and recreate it.
pyenv install 3.6.1 --skip-existing

#  Check if project virtualenv exists or create it
if [ ! -d "$HOME/.pyenv/versions/3.6.1/envs/transcriber" ]; then
    pyenv virtualenv 3.6.1 transcriber
fi

# Preemptively accept Github's SSH fingerprint, but only
# if we previously haven't done so.
fingerprint="$(ssh-keyscan -H github.com)"
if ! grep -qs "$fingerprint" $HOME/.ssh/known_hosts; then
    echo "$fingerprint" >> $HOME/.ssh/known_hosts
    echo "Added github.com fingerprint"
fi

# Vagrant should've created /srv/www according to the Vagrantfile,
# but let's make sure it exists even if run directly.
if [[ ! -d "/srv/www" ]]; then
    echo "Creating /srv/www/"
    sudo mkdir "/srv/www"
    sudo chown vagrant:vagrant "/srv/www"
fi

# Check if repo directory exists, if not clone repo
if [[ ! -d "/srv/www/video-transcriber" ]]; then
    echo "Cloning repo, setting virtual environment and installing requirements."
    git clone git@github.com:KappaLambda/video-transcriber.git /srv/www/video-transcriber/
    cd /srv/www/video-transcriber/
    pyenv local transcriber
    # upgrade pip and setuptools to avoid google-gax and google-cloud-python installation errors
    # More info here: https://github.com/googleapis/google-cloud-python/issues/2990
    pip install --upgrade pip setuptools
    pip install -r requirements.txt
    cd /srv/www/video-transcriber/video_transcriber/
    python manage.py collectstatic --noinput
fi

# set nginx
if [ ! -h "/etc/nginx/sites-enabled/transcriber.liopetas.com.conf" ] && [[ -d "/srv/www/video-transcriber" ]]; then
    echo "Creating Nginx block symlink."
    sudo ln -s /srv/www/video-transcriber/nginx-blocks/transcriber.liopetas.com.conf /etc/nginx/sites-enabled/transcriber.liopetas.com.conf
    sudo nginx -t && sudo service nginx restart
fi

end_seconds="$(date +%s)"
echo "-----------------------------"
echo "Provision completed in "$(expr $end_seconds - $start_seconds)" seconds"
