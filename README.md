# YouTube video transcriber

YouTube video transcriber that performs on-the-fly text-to-speech conversion of any provided Youtube video URL, leveraging the Google Speech API.

## Table of Contents

- [Requirements](#requirements)
- [Setup - Install](#setup---install)
- [Automated Setup](#automated-setup)
- [Run](#run)
- [Supported YouTube URLs](#supported-youtube-urls)
- [Demo](#demo)
- [License](#license)

## Requirements

- Ubuntu 16.04
- Python 3.6.1
- pyenv
- pyenv/virtualenv plugin
- Nginx
- Gunicorn
- ffmpeg

## Setup

```bash
sudo apt-get update
# Install application requirements
sudo apt-get install -y nginx ffmpeg libavcodec-extra
# Install pyenv requirements
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl
# Install pyenv and pyenv-virtualenv with pyenv-installer
# https://github.com/pyenv/pyenv-installer
curl https://pyenv.run | bash
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> $HOME/.bashrc
echo 'eval "$(pyenv init -)"' >> $HOME/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> $HOME/.bashrc
exec "$SHELL"
pyenv install 3.6.1 --skip-existing
pyenv virtualenv 3.6.1 transcriber
git clone https://github.com/KappaLambda/video-transcriber.git /srv/www/video-transcriber
cd /srv/www/video-transcriber/
pyenv local transcriber

# To avoid google-gax and google-cloud installation errors upgrade pip and setuptools.
# read more here https://github.com/googleapis/google-cloud-python/issues/2990
pip install --upgrade pip setuptools

pip install -r requirements.txt
sudo ln -s /srv/www/video-transcriber/nginx-blocks/transcriber.liopetas.com.conf /etc/nginx/sites-enabled/transcriber.liopetas.com.conf
sudo nginx -t && sudo service nginx restart
```

## Automated Setup

### Requirements for automated setup

- [Vagrant](https://www.vagrantup.com/)
- [Virtualbox](https://www.virtualbox.org/)

Install latest versions of Vagrant and VirtualBox.

Inside repo's root directory there is a `Vagrantfile` that can be used to bring up a virtual machine.

There is also a provision script, `vagrant_setup.sh` that installs all prerequisites and requirements, installs pyenv and virtualenv, clones the repo, creates symlink for nginx block, etc.

In this case, the above [setup - install](#setup---install) procedure is not needed.

Clone repo or copy the important files (`Vagrantfile`, `vagrant_setup.sh`) and then just run the following command to bring up the VM:

```bash
vagrant up
```

## Run

First edit your `hosts` file to point transcriber.liopetas.com to localhost or to the VM's IP address.

Before running the gunicorn script you have to create a project on Google Cloud Platform and enable Google Speech-to-Text API for your project and get the file with the key and credentials in json format. Rename the json file to `google-application-credentials.json` and place it in the root directory of the repo. Find more info [here](https://cloud.google.com/speech-to-text/docs/quickstart-protocol).

Then run the gunicorn script.

```bash
bash gunicorn.sh
```

## Supported YouTube URLs

- http(s)://www.youtube.com/watch?v=youtube_id
- http(s)://youtu.be/youtube_id
- http(s)://www.youtube.com/embed/youtube_id
- http(s)://m.youtube.com/watch?v=youtube_id

## Demo

You can see a demo [here](http://transcriber.liopetas.com).

## License

[The MIT License](LICENSE.md)
