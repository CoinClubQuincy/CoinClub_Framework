echo "Start Dependancies"

apt update
apt install python3
apt install python3-pip

pip3 install requests


# /etc/init.d/dbus start
#Rippled
sudo apt-get install systemd
sudo apt -y update
sudo apt -y install rippled
systemctl status rippled.service
sudo systemctl start rippled.service
sudo systemctl enable rippled.service
/opt/ripple/bin/rippled server_info


#stellar
git clone https://github.com/StellarCN/py-stellar-base.git
cd py-stellar-base
git checkout 3.1.4
pip3 install .

pip3 install stellar-sdk==3.2.0
pip3 install pipdeptree



#sync:         rippled --rpc_ip 34.201.59.230:51234 server_info | grep seq
#count_code:   find . -name '*.py' | xargs wc -l
