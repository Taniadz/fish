sudo ln -s /home/tania/PycharmProjects/fish/etc/nginx.conf   /etc/nginx/sites-enabled/fish.conf
sudo ln -s /etc/nginx/sites-available/fish.conf /etc/nginx/sites-enabled
sudo systemctl reload nginx

sudo ln -s /home/tania/Pycd nginxcharmProjects/fish/etc/application.service /etc/systemd/system/fish.service
sudo systemctl start fish