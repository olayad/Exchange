#!/bin/bash

ADDR=CTEmARncQDR55oMA5pnYBVkpZtFUuh7W5zFrKvqTMmnGwKQzrxALf3nmK9Hgk2jwTiJnwWeUVS7dvhgD
PUBKEY=0267454a3d4c7657f30e513211fddfed9e0880f3007922efc0fcf1a9a53b40eacf
PRIVKEY=L3rby7pAZRvS7pJFeX8jPGxymukXZvHcwukVjeHGUPFgzHsenh3M
SIGNBLOCKSCRIPT=51210267454a3d4c7657f30e513211fddfed9e0880f3007922efc0fcf1a9a53b40eacf51ae
alias lid1="liquidd -signblockscript=$SIGNBLOCKSCRIPT"
alias lid2="liquidd -datadir=./liquidregtest2/ -signblockscript=$SIGNBLOCKSCRIPT"
alias lic1="liquid-cli"
alias lic2="liquid-cli -datadir=./liquidregtest2/"
