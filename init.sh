sudo ln -s /home/ubuntu/app/etc/nginx.conf   /etc/nginx/sites-enabled/fish.conf
sudo ln -s /etc/nginx/sites-available/fish.conf /etc/nginx/sites-enabled
sudo systemctl reload nginx

sudo ln -s /home/ubuntu/app/etc/application.service /etc/systemd/system/fish.service
sudo systemctl start fish