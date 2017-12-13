import time
import sys

from interactive import InteractiveStrategy
from HydraQuoteManager import HydraQuoteManager
from HydraOrderManager import HydraOrderManager


args = sys.argv[1:]
es_port = 10000
is_port = 10001


if len(args) > 0:
    es_port = int(args[0])
if len(args) > 1:
    is_port = int(args[1])

print es_port, is_port
qm = HydraQuoteManager(is_port)
em = HydraOrderManager(es_port)

s = InteractiveStrategy(qm, em)

time.sleep(1)
s.start()

s.stop()

qm.close_socket()
em.close_socket()
print 'done'
