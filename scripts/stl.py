"""Binary/ASCII STL reading and binary conversion for current CAD exports."""
import struct

def triangles(path):
 data=path.read_bytes()
 if len(data)>=84 and len(data)==84+50*struct.unpack_from('<I',data,80)[0]:
  for offset in range(84,len(data),50):yield [struct.unpack_from('<fff',data,offset+12+i*12) for i in range(3)]
 else:
  vs=[tuple(map(float,l.split()[1:])) for l in data.decode().splitlines() if l.strip().startswith('vertex ')]
  for i in range(0,len(vs),3):yield vs[i:i+3]
def binary_stl(path):
 tris=list(triangles(path));data=bytearray(b'Galia prototype STL'.ljust(80,b'\0'))
 data.extend(struct.pack('<I',len(tris)))
 for tri in tris:data.extend(struct.pack('<12fH',0,0,0,*tri[0],*tri[1],*tri[2],0))
 path.write_bytes(data)
