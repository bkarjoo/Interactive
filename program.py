import time
from interactive import InteractiveStrategy
from HydraQuoteManager import HydraQuoteManager
from HydraOrderManager import HydraOrderManager

qm = HydraQuoteManager()
em = HydraOrderManager()

s = InteractiveStrategy(qm, em)

time.sleep(1)
s.start()

s.stop()

qm.close_socket()
em.close_socket()
print 'done'
