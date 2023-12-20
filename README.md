#
'''
sudo apt install libasound2 libasound2-dev
sudo apt-get install libsndfile1-dev
'''

#
gcc -lsndfile -lm -lasound -pthread server.c -o server