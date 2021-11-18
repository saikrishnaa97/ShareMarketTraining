yum install wget unzip -y
cd opt/ShareMarketTraining/rest_client/
wget https://www.bseindia.com/downloads/Help/file/scrip.zip
unzip scrip.zip
mv SCRIP/SCRIP*.TXT ./SCRIP.TXT
rm -rf SCRIP.json
rm -rf scrip.zip SCRIP/
