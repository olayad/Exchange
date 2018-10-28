#!/bin/bash

liquid-cli importprivkey L3rby7pAZRvS7pJFeX8jPGxymukXZvHcwukVjeHGUPFgzHsenh3M
NEWBLOCK=$(liquid-cli getnewblockhex)
BLOCKSIG=$(liquid-cli signblock $NEWBLOCK)
SIGNED=$(liquid-cli combineblocksigs $NEWBLOCK \[\"$BLOCKSIG\"\] | jq -r '.hex')
liquid-cli submitblock $SIGNED
echo New block count:
echo $(liquid-cli getblockcount)
