#!/bin/bash

ssh -i /home/ubuntu/engg_533/lab_2.pem -t -t  -T ubuntu@54.69.236.149 <<EOF
#cd /home/ubuntu/engg_533
sudo /home/ubuntu/engg_533/setmysql.sh&
sudo /home/ubuntu/engg_533/collectlcpu.sh&
sudo /home/ubuntu/engg_533/sar.sh&
sudo taskset 0x001 sudo service apache2 start
exit
EOF

echo "STARTING HTTPERF"
httperf --server 54.69.236.149 --port 80 --wsesslog 1000,0,input.txt --period e0.035 --dead=35 --rfile=/home/ubuntu/engg_533/responsetimes/rfile.txt > /home/ubuntu/engg_533/responsetimes/output.txt

ssh -i /home/ubuntu/engg_533/lab_2.pem -t -t  -T ubuntu@54.69.236.149  <<EOF
sudo killall collectl
sudo killall sar
sudo taskset 0x001 sudo service apache2 stop
exit
EOF