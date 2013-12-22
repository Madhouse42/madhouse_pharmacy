# encoding: utf-8
from pickle import dumps, loads
import uuid
from struct import pack, unpack
import time
from decimal import Decimal, getcontext
from misc import create_counter


getcontext().prec = 2
init_balance = Decimal('100000.00')
pickle_init_balance = dumps(init_balance, -1)

show, inc = create_counter(32)

spec = {'manufacture': ((show(), inc(8)),
                        lambda: 'goodman',
                        lambda buf: buf.value),
        'uid': ((show(), inc(16)),
                lambda: uuid.uuid4().bytes,
                lambda buf: uuid.UUID(bytes=buf.value).hex),
        'creation time': ((show(), inc(4)),
                          lambda: pack('!I', int(time.time())),
                          lambda buf: unpack('!I', buf)[0]),
        'expire time': ((show(), inc(4)),
                        lambda: pack('!I', int(time.mktime(time.strptime('2020 1 1', '%Y %m %d')))),
                        lambda buf: unpack('!I', buf)[0]),
        'last used time': ((show(), inc(4)),
                           lambda: pack('!I', int(time.time())),
                           lambda buf: unpack('!I', buf)[0]),
        'used time': ((show(), inc(4)),
                      lambda: pack('!I', 0),
                      lambda buf: unpack('!I', buf)[0]),
        'last transaction complete': ((show(), inc(1)),
                                      lambda: pack('!B', 1),
                                      lambda buf: bool(unpack('!I', buf)[0])),
        'length of balance': ((show(), inc(4)),
                              lambda: pack('!I', len(pickle_init_balance)),
                              lambda buf: unpack('!I', buf)[0]),
        'balance': ((show(), inc(len(pickle_init_balance))),
                    lambda: pickle_init_balance,
                    lambda buf: loads(buf)),
        # hash: 32 bytes sha-256
        # backup: compressed backup data
}

next_offset = show()

spec = sorted(spec.iteritems(), key=lambda (_, ((offset, __), ___, ____)): offset)

