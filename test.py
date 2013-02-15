from bcoding import *
from pytest import main, raises

#basic en/decoding

def test_stream_decoding():
	with BytesIO(b'd2:hii1ee') as f:
		mapping = bdecode(f)
	assert mapping['hi'] == 1

def test_buffer_decoding():
	assert bdecode(b'3:one') == 'one'
	assert bdecode('3:two') == 'two'

def test_stream_encoding():
	with BytesIO() as stream:
		bencode({'a': 0}, stream)
		assert stream.getvalue() == b'd1:ai0ee'

def test_buffer_encoding():
	assert bencode(('a', 0)) == b'l1:ai0ee'

#decode incomplete stuff

def test_decode_incomplete_int():
	with raises(ValueError):
		print(bdecode('i1'))

def test_decode_incomplete_buffer():
	with raises(ValueError):
		bdecode('1:')

def test_decode_incomplete_list():
	with raises(TypeError):
		print(bdecode('l'))

def test_decode_incomplete_dict():
	with raises(TypeError):
		print(bdecode('d1:k'))

if __name__ == '__main__':
	main(__file__)