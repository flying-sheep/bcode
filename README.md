bcoding
=======

yet another… but mine is fast as hell.

install
-------
```
pip install bcoding
```

use
---

```python
from bcoding import bencode, bdecode
```

### decoding:

```python
# decoding from binary files or streams:
with open('some.torrent', 'rb') as f:
	torrent = bdecode(f)
	print(torrent['announce'])

# decoding from (byte)strings:
one = bdecode(b'i1e')
two = bdecode('3:two')
```

### encoding (note that any iterable or mapping can be bencoded):

```python
# encoding into binary files or streams:
bencode({'a': 0}, sys.stdout.buffer) # ⇒ d1:ai0ee

# encoding to bytestrings:
assert bencode(('a', 0)) == b'l1:ai0ee'
```
