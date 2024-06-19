yum install -y httpd
systemctl enable httpd
systemctl restart httpd
firewall-cmd --add-service=http --permanent
firewall-cmd --add-service=https --permanent
firewall-cmd --reload
