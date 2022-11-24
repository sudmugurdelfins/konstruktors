#!/bin/bash
secret="/my_secret_files"

echo "Automization script start"
#PAŅEMTS NO PIEMĒRA
echo "Checking if config file exists"
echo "==============================================="
echo "===============================================" 
if test -f "config.ini"; then
    echo "exists"
else
	echo "Copying config file from secure secret storage"
	cp $HOME$secret/config.ini .
	if [ $? -eq 0 ]; then echo "OK"; else echo "Problem copying config.ini file"; exit 1; fi
fi
echo "==============================================="
echo "==============================================="

echo "Getting python3 executable loc"
echo "==============================================="
echo "==============================================="
python_exec_loc=$(which python3)
if [ $? -eq 0 ]; then echo "OK"; else echo "Problem getting python3 exec location"; exit 1; fi
echo "$python_exec_loc"
echo "==============================================="
echo "==============================================="

echo "Running twitter test"
echo "==============================================="
echo "==============================================="
$python_exec_loc test_secret.py
if [ $? -eq 0 ]; then echo "OK"; else echo "Configuration test FAILED"; exit 1; fi
echo "==============================================="
echo "==============================================="

echo "Checking if tweeting file exists"
echo "==============================================="
echo "==============================================="
if test -f "tweet_apocalypse.py"; then
    echo "Exists"
else
	echo "Copying tweet file from dev map"
	cp dev/tweet_apocalypse.py.dev tweet_apocalypse.py
	if [ $? -eq 0 ]; then echo "OK"; else echo "Problem copying tweet_apocalypse.py file"; exit 1; fi
fi
echo "==============================================="
echo "==============================================="



echo "Making a tweet"
echo "==============================================="
echo "==============================================="
$python_exec_loc tweet_apocalypse.py
if [ $? -eq 0 ]; then echo "OK"; else echo "Tweet failed"; exit 1; fi
echo "==============================================="
echo "==============================================="




