#/bin/bash
. ./chia-blockchain/activate
chia init -c ca
chia start harvester
mkdir "/root/.chia/mainnet/log"
touch "/root/.chia/mainnet/log/debug.log"
deactivate
python -u watcher.py