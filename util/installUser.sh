#!/bin/bash
echo "Input username: "
read user

mkdir /home/ubuntu/markov/$user
cp ../conf.py /home/ubuntu/markov/$user
cp ../initializeDatabase.py /home/ubuntu/markov/$user

cd /home/ubuntu/markov/$user
ln ../code/* .;
ln -s ../code/markovify .;
