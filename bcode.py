#!/usr/bin/env python

"""
bencode/decode library.

bencoding is used in bittorrent files

use the exposed functions to encode/deocde them.
"""

from io import BytesIO, SEEK_CUR
try: #py 3.3
	from collections.abc import Iterable, Mapping
except ImportError:
	from collections     import Iterable, Mapping

_TYPE_INT  = b'i'
_TYPE_LIST = b'l'
_TYPE_DICT = b'd'
_TYPE_END  = b'e'
_TYPE_SEP  = b':'
_TYPES_STR = b'0123456789'

TYPES = {
	_TYPE_INT:  int,
	_TYPE_LIST: list,
	_TYPE_DICT: dict,
	_TYPE_END:  None,
	#_TYPE_SEP only appears in strings, not here
}
for byte in _TYPES_STR:
	TYPES[bytes([byte])] = str #b'0': str, b'1': str, …

def _readuntil(f, end=_TYPE_END):
	"""Helper function to read bytes until a certain end byte is hit"""
	buf = bytearray()
	while True:
		byte = f.read(1)
		if byte != end:
			buf += byte
		else:
			break
	return buf

def _decode_int(f):
	"""
	Integer types are normal ascii integers
	Delimited at the start with 'i' and the end with 'e'
	"""
	assert f.read(1) == _TYPE_INT
	return int(_readuntil(f))

def _decode_buffer(f):
	"""
	String types are normal (byte)strings
	starting with an integer followed by ':'
	which designates the string’s length.
	Since there’s
	"""
	strlen = int(_readuntil(f, _TYPE_SEP))
	buf = f.read(strlen)
	try:
		return buf.decode()
	except UnicodeDecodeError:
		return buf

def _decode_list(f):
	assert f.read(1) == _TYPE_LIST
	ret = []
	while True:
		item = bdecode(f)
		if item is None:
			break
		else:
			ret.append(item)
	return ret

def _decode_dict(f):
	assert f.read(1) == _TYPE_DICT
	ret = {}
	while True:
		key = bdecode(f)
		if key is None:
			break
		else:
			assert isinstance(key, (str, bytes))
			ret[key] = bdecode(f)
	return ret

DECODERS = {
	int:  _decode_int,
	str:  _decode_buffer,
	list: _decode_list,
	dict: _decode_dict,
}

def bdecode(f):
	"""
	bdecodes data contained in a file f opened in bytes mode.
	works by looking up the type byte,
	and using it to look up the respective decoding function,
	which in turn is used to return the decoded object
	"""
	btype = TYPES[f.read(1)]
	if btype is not None:
		f.seek(-1, SEEK_CUR)
		return DECODERS[btype](f)
	else: #Used in dicts and lists to designate an end
		return None

def bdecode_buffer(data):
	"""Convenience wrapper around bdecode that accepts strings or bytes"""
	if isinstance(data, str):
		data = data.encode()
	with BytesIO(data) as f:
		return bdecode(f)

################
### Encoding ###
################

def _encode_int(integer, f):
	f.write(_TYPE_INT)
	f.write(str(integer).encode())
	f.write(_TYPE_END)

def _encode_buffer(string, f):
	"""Writes the bencoded form of the input string or bytes"""
	if isinstance(string, str):
		string = string.encode()
	f.write(str(len(string)).encode())
	f.write(_TYPE_SEP)
	f.write(string)

def _encode_iterable(iterable, f):
	f.write(_TYPE_LIST)
	for item in iterable:
		bencode(item, f)
	f.write(_TYPE_END)

def _encode_mapping(mapping, f):
	f.write(_TYPE_DICT)
	for key, value in mapping.items():
		_encode_buffer(key, f)
		bencode(value, f)
	f.write(_TYPE_END)

def bencode(data, f):
	"""
	Writes a serializable data piece to f
	The order of tests is nonarbitrary,
	as strings and mappings are iterable.
	"""
	if isinstance(data, int):
		_encode_int(data, f)
	elif isinstance(data, (str, bytes)):
		_encode_buffer(data, f)
	elif isinstance(data, Mapping):
		_encode_mapping(data, f)
	elif isinstance(data, Iterable):
		_encode_iterable(data, f)

def bencode_buffer(data):
	"""
	Convenience wrapper around bencode that returns a byte array
	of the serialized sata
	"""
	with BytesIO() as f:
		bencode(data, f)
		return f.getvalue()

def main():
	import sys, pprint
	from argparse import ArgumentParser, FileType
	parser = ArgumentParser(description='Decodes bencoded files to python objects.')
	parser.add_argument('infile',  nargs='?', type=FileType('rb'), default=sys.stdin.buffer,
		help='bencoded file (e.g. torrent) [Default: stdin]')
	parser.add_argument('outfile', nargs='?', type=FileType('w'), default=sys.stdout,
		help='python-syntax serialization [Default: stdout]')
	args = parser.parse_args()
	
	data = bdecode(args.infile)
	pprint.pprint(data, stream=args.outfile)

if __name__ == '__main__':
	main()