
service httpd start
firewall-cmd --help
firewall-cmd --list-ports
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --list-ports
firewall-cmd --reload
firewall-cmd --list-ports
systemctl enable httpd
systemctl restart httpd
firewall-cmd --reload
setsebool -P httpd_can_network_connect on
systemctl restart httpd
firewall-cmd --reload
