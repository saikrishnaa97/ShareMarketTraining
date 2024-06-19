yum install -y httpd
systemctl enable httpd
systemctl restart httpd
firewall-cmd --add-service=http --permanent
firewall-cmd --add-service=https --permanent
firewall-cmd --reload


yum -y install gcc-c++ python3-devel python3-pip python3 python3-setuptools
