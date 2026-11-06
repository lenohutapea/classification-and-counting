import re, sys
p = sys.argv[1]
s = open(p).read()
pola = re.compile(
    r'^([ \t]*)p3 = \[\s*\(\s*float\(a\)\s*,\s*float\(b\)\s*\)\s*for a, b, _ in re\.findall\(\s*pat3\s*,\s*ob\.findtext\(\s*"vertex3d"\s*\)\s*\)\s*\]',
    re.M,
)
def ganti(m):
    t = m.group(1)
    return (f'{t}nums = [float(v) for v in re.findall(NUM, ob.findtext("vertex3d"))]\n'
            f'{t}p3 = [(nums[i], nums[i + 1]) for i in range(0, len(nums) - 2, 3)] if len(nums) == 24 else []')
baru, n = pola.subn(ganti, s)
print("blok yang diganti:", n)
if n == 1:
    open(p, "w").write(baru)
    print("selesai")
else:
    print("TIDAK diubah. Baris terkait di file:")
    for i, b in enumerate(s.splitlines(), 1):
        if "p3" in b or "pat3" in b or "vertex3d" in b:
            print(f"  {i}: {b}")
