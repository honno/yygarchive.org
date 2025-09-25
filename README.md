# YoYo Games Archive

A searchable archive of the old YoYo Games Sandbox.

It's a very simple a [Flask](https://flask.palletsprojects.com/) project. For development I run it like so:

```bash
pip install -e .
flask --app app run --debug
```

## Deployment guide

These are my notes for deploying on a Ubuntu machine.

### Update and prepare system

```sh
sudo apt update
sudo apt upgrade -y
sudo apt install -y software-properties-common git ufw gunicorn nginx snapd
```

### Setup Python

Can use pyenv:

```sh
sudo apt install -y build-essential libssl-dev zlib1g-dev libreadline-dev libsqlite3-dev libncurses-dev ca-certificates
curl -fsSL https://pyenv.run | bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init - bash)"' >> ~/.bash_profile
exec bash
pyenv install 3.13.3
```

Or for Ubuntu specifically can use the deadsnakes ppa:

```sh
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev
```

### Clone repo

```sh
git clone https://github.com/honno/yygarchive.org yygarchive.org
cd yygarchive.org
```

### Set up Python environment
```sh
python -m venv venv  # python13.3 if installed with deadsnakes
source venv/bin/activate
pip install --upgrade pip
pip install -e .[deploy]
```

### Test Gunicorn locally
```sh
gunicorn --bind 0.0.0.0:5000 app.wsgi:app
```

Open in your browser at `http://localhost:5000`.

If SSHing can tunnel to your own machine to say port `9090`:
```sh
ssh -L 9090:localhost:5000 user@IP
```

### Configure firewall
```sh
sudo ufw allow OpenSSH
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
sudo ufw status
```

### Create systemd service for Gunicorn
Create the service file:
```sh
sudo vim /etc/systemd/system/yygarchive.service
```

Paste this inside:
```ini
[Unit]
Description=Gunicorn instance for yygarchive
After=network.target

[Service]
User=USER
Group=www-data
WorkingDirectory=/home/USER/yygarchive.org
Environment="PATH=/home/USER/yygarchive.org/venv/bin"
ExecStart=/home/USER/yygarchive.org/venv/bin/gunicorn --workers 3 --bind unix:/home/USER/yygarchive.org/yygarchive.sock app.wsgi:app
ExecStartPre=/bin/chown USER:www-data /home/USER/yygarchive.org
UMask=007

[Install]
WantedBy=multi-user.target
```

Reload `systemd` and start the service:
```sh
sudo systemctl daemon-reload
sudo systemctl start yygarchive
sudo systemctl enable yygarchive
sudo systemctl status yygarchive
```

### Install and configure Nginx
```sh
sudo vim /etc/nginx/sites-available/yygarchive.org
```

Paste this inside (we'll modify this later):
```javascript
server {
    listen 80;
    server_name yygarchive.org www.yygarchive.org;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/USER/yygarchive.org/yygarchive.sock;
    }
}
```

Enable site and reload Nginx:
```sh
sudo ln -s /etc/nginx/sites-available/yygarchive.org /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Enable HTTPS with Certbot
```sh
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

sudo certbot --nginx -d yygarchive.org -d www.yygarchive.org
sudo certbot renew --dry-run
```

### Enable www redirect to naked domain

Replace the contents of your nginx again at `/etc/nginx/sites-available/yygarchive.org` with:

```javascript
# Redirect ALL www.yygarchive.org (HTTP + HTTPS) → https://yygarchive.org
server {
    listen 80;
    listen 443 ssl;

    server_name www.yygarchive.org;

    # Reuse your certs so HTTPS works long enough to redirect
    ssl_certificate /etc/letsencrypt/live/yygarchive.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yygarchive.org/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    return 301 https://yygarchive.org$request_uri;
}

# Redirect all naked-domain HTTP → HTTPS
server {
    listen 80;
    server_name yygarchive.org;
    return 301 https://yygarchive.org$request_uri;
}

# Main site block, HTTPS only, naked domain
server {
    listen 443 ssl;
    server_name yygarchive.org;

    ssl_certificate /etc/letsencrypt/live/yygarchive.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yygarchive.org/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/USER/yygarchive.org/yygarchive.sock;
    }
}
```

### Troubleshoot ownership

What I've needed to do to make sure internal permissions are fine:

```sh
sudo chown -R USER:www-data /home/USER/yygarchive.org
sudo chmod 750 /home/USER/yygarchive.org
sudo chown USER:www-data /home/USER/yygarchive.org/yygarchive.sock
sudo chmod 660 /home/USER/yygarchive.org/yygarchive.sock
```

### Deploy updates

Code changes just need
```sh
sudo systemctl restart yygarchive
```

If requirements change make sure to install them!
```sh
cd ~/yygarchive.org
git pull
source venv/bin/activate
pip install -e .   # if deps changed
```
