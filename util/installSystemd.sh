#!/bin/bash

echo "Input username: "
read user

echo "[Unit]
Description=$user's Markov Bot
After=multi-user.target

[Service]
Type=simple
WorkingDirectory=/home/ubuntu/markov/$user/
ExecStart=/usr/bin/python3 /home/ubuntu/markov/$user/markovChain.py
StandardInput=tty-force
User=ubuntu
Restart=always

[Install]
WantedBy=multi-user.target" > /lib/systemd/system/$user.service;


systemctl enable $user.service;
systemctl start $user.service;
