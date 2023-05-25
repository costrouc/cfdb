# Efficiently Storing Conda-Forge Data

# Current Statistics

Done via `sqlite3_analyzer`.

I am achieving around 0.77 compression ratio on actual data.

```
INODEMETADATA..................................... 1707        45.6% 
BUILDARTIFACT..................................... 1136        30.4% 
INODE............................................. 793         21.2% 
BUILDARTIFACTINDEX................................ 30           0.80% 
ENVIRONMENTVARIABLE............................... 28           0.75% 
BUILDARTIFACT_CHANNEL............................. 19           0.51% 
BUILDARTIFACT_ENVIRONMENTVARIABLE................. 19           0.51% 
BUILDARTIFACT_MAINTAINER.......................... 2            0.053% 
CHANNEL........................................... 2            0.053% 
LICENSE........................................... 2            0.053% 
MAINTAINER........................................ 2            0.053% 
SQLITE_SCHEMA..................................... 1            0.027% 
```
