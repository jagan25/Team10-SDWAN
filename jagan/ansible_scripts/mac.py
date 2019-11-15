#!/usr/bin/python
import random
print(':'.join('%02x'%random.randrange(256) for _ in range(6)))
                                                                
