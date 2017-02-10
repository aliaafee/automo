import wx
import cStringIO
import base64

def BitmapFromBase64(str_base64):
    image = base64.b64decode(str_base64)
    stream = cStringIO.StringIO(image)

    return wx.BitmapFromImage(wx.ImageFromStream(stream))


icon_b64 = \
"""AAABAAEAEBAQAAEABAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAgAAAAKAB
AACgAQAAEAAAABAAAAAxMTEAMzMzAIqKigCwsLAA19fXANra2gDc3NwA5OTkAOXl
5QDm5uYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAqqqqqqqqqqqqoQAAAAAAqqqg
iIiIiICqqgAAAAAAgKqqBVVVVVCAqqoFIiIiUICqqgVVVVVQgKqqBSIiIlCAqqoF
VERFYICqqgUlJSWQgKqqBSJVkpCAqqoFJSUAAICqqgUiWQMwcKqqCZmZAwAAqqoA
AAAAqqqqqqqqqqqqqqr//wAA4AMAAOADAADAAwAAwAMAAMADAADAAwAAwAMAAMAD
AADAAwAAwAMAAMADAADAAwAAwAMAAMA/AAD//wAA"""


checked_16_b64 = \
"""Qk02AwAAAAAAADYAAAAoAAAAEAAAABAAAAABABgAAAAAAAADAAAAAAAAAAAAAAAA
AAAAAAAA////////////////////////////////////////////////////////
////////////////gVIdgVIdgVIdgVIdgVIdgVIdgVIdgVIdgVIdgVIdgVIdgVId
gVId////////////gVId8fPz8/X19vf3+Pn5+fr6+/z8/f39/v7+////////////
gVId////////////gVId7/Hx8fPz8/X19vf3+Pn5+fr6+/z8/f39/v7+////////
gVId////////////gVId7O/v7/Hx8fPz8/X1IqEi+Pn5+fr6+/z8/f39/v7+////
gVId////////////gVId6ezs7O/v7/HxIqEiIqEiIqEi+Pn5+fr6+/z8/f39/v7+
gVId////////////gVId5urq6ezsIqEiIqEiIqEiIqEiIqEi+Pn5+fr6+/z8/f39
gVId////////////gVId4+fn5urqIqEiIqEi7/HxIqEiIqEiIqEi+Pn5+fr6+/z8
gVId////////////gVId4eXl4+fnIqEi6ezs7O/v7/HxIqEiIqEiIqEi+Pn5+fr6
gVId////////////gVId3+Pj4eXl4+fn5urq6ezs7O/v7/HxIqEiIqEi9vf3+Pn5
gVId////////////gVId3eLi3+Pj4eXl4+fn5urq6ezs7O/v7/HxIqEi8/X19vf3
gVId////////////gVId3eLi3eLi3+Pj4eXl4+fn5urq6ezs7O/v7/Hx8fPz8/X1
gVId////////////gVId3eLi3eLi3eLi3+Pj4eXl4+fn5urq6ezs7O/v7/Hx8fPz
gVId////////////gVIdgVIdgVIdgVIdgVIdgVIdgVIdgVIdgVIdgVIdgVIdgVId
gVId////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////"""


checked_32_b64 = \
"""Qk2KDAAAAAAAAIoAAAB8AAAAIAAAACAAAAABABgAAAAAAAAMAAAAAAAAAAAAAAAA
AAAAAAAAAAD/AAD/AAD/AAAAAAAA/0JHUnOAwvUoYLgeFSCF6wFAMzMTgGZmJkBm
ZgagmZkJPArXAyRcjzIAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAgVIdgFEc
f08ZfUwVfEsUfEsUfEsUfEsUfEsUfEsUfEsUfEsUfEsUfEsUfEsUfEsUfEsUfEsU
fEsUfEsUfEsUfEsUfEsUfEsUfEsUfEsUfEsTfEsTfEwVfk4YgFEcgVIdgFEcg1Qg
iFwqjmQ1j2c5j2c4j2Y4j2Y4kGc4kGc4kGc4kGc4kGc4kGc5kGc5kGc5kGc5kGc5
kGc5kGc5kWc5kWc5kWc5kWg5kWg5kWg5kWg6kWg6j2U2iV0rg1UhgFEcf08ZiFwq
nXpSs5p9u6WMu6WLuqSJu6SKvKWKvKWKvKWLvaaLvaaLvaaMvaaMvqeMvqeNv6eN
v6iNv6iNv6iNwKiOwKiOwKmOwKmOwKiOwaqQwquSuaCCoH1ViV0rfk4YfUwVjWQ1
s5p929TJ6ejk6Obh6OTf6eXg6ubg6+fh6+fi7Oji7Ojj7enj7enk7url7+vl8Ovm
8Ovm8ezm8ezn8ezn8u3n8u3o8u3o8u3o9PDr9vLu5t3TuqCCj2U2fEwVfEsUj2c4
uqWL6Ofj+P7/9/z+9/r8+Pv9+fz9+v3++/3//P7//v///////////////v//////
////////////////////////////////////////8u3owKiOkWg5fEsUfEsUj2Y4
uaOJ5uTf9vr99fj69Pb39ff49vj59/n6+Pr7+vv8/f39/v7//v7//P7+/P7+/f7/
/v///v//////////////////////////////////8u3owKiOkWg5fEsUfEsUj2Y3
uKGH4+Db8/b48vX28fPz8vT08/X19fb39vf48fXy5PDl3O3d5PHl8/f0+/v8+/z8
+/z8/Pz8/P39/f39/f7+/v7+/v7+////////////8u3owKiOkWg5fEsUfUsUjmY3
t6GG4uDa8vb38fT18PLy8fPz8vT0+Pf6/Pn+5vDnsNuxkM6Qrtuu5fLl//3///3/
+vv7+vv7/Pz8/P39/f39/v7+/v7+/v7+////////8u3owKmOkWg5fEsUfUsUjmY3
tqCG4d/Z8fX28PP07/Hx8PLy8fPz9PX28fTzy+XMecR6SLFJdcN1yebK9fj2+/v8
+fr6+vv7+/z8/Pz8/P39/f39/v7+/v7+////////8u3owKmOkWg5fEsUfUwUjmU3
tqCF4N7Y7/T17/Lz7/Hy9fT38vP03+zhvt/Aj82RT7NPK6UrS7JLjc2Ov+LA4/Hk
+vr7//3//Pz9+/z8+/z8/P39/f39/f7+////////8u3nwKiOkWc5fEsUfUwUjmU3
tZ+F393X7vP07fHy7/Dx9/T57vHwvN6+d8N4R7BHLaYtJaIlLKUsRa9FdcN2veG+
9Pj1//3/+/v8+vv7+/z8/Pz8/P39/f39////////8eznwKiOkWc5fEsUfUwUjmU3
tZ+E3tzW7vL07fHy6O3r4OvjyeLKj8uQR69HH6AfG54bIKAgG54bHp8eQ69Ejc2O
zefO6vPr9fj2+/v8/Pz9+/z8/Pz8/P39////////8eznv6iNkWc5fEsUfUwUjmU3
tJ6E3dvW7vL17vDz2ufdrtewfcR+U7RUL6YvG54bGJ0YG54bGJ0YGp4aLaYtUrVS
f8d/td626fPp//3///3/+vv7+vv7/Pz8/v//////8ezmv6iNkGc5fEsUfUwUjmU3
s56D3NrV7vH27/D0zuLQg8aFPqw+JKIkIqEiJKIkKKMoK6QrKKMoJKIkI6EjI6Ij
O6s7f8d/zefO9Pj1+vr7+fr6+vv7+/z8/v//////8Ovmv6iNkGc5fEsUfUwVjWU2
s52D29nU7vD17u/zyuDNd8F4K6QsEpsSGJ0XLKUsUbNRZ7xoU7RULqYuGZ4ZFJsU
I6IjUrVSjc2OveG+4/Hk+/v8//3/+/z8/f7/////8Ovmv6eNkGc5fEsUfUwVjWU2
sp2C2tjT7O/07e7yyeDNecJ7MKYwFZwUGZ4ZPaw9h8iItNq1jMqNQq1CHJ8cGZ4Z
I6EjLaYtQ69EdcN2v+LA9fj2//3/+/v8/P7+////7+vlvqeNkGc5fEsUfUwVjWQ2
spyC2dfS6+7y6+3xyN/Md8F5MacyJKIkOqo6aLxps9m13+vhudy7br9vQK1ALKUs
IqEiGZ0ZHZ8dRrBGj86Py+fM5/Lo8/j0/P3/////7urlvqeMkGc5fEsUfUwVjWQ2
sZyB2NfR6u3y6uzwxt3Jcb5yMKYwP6xAe8N8rdav1ubZ6u7s2unctNq1hciGTLFM
IaEhFJsUGp4aLqYuUbRRfMZ8s9yz5fLm/v7/////7enkvaaMkGc5fEsUfUwVjWQ2
sZuB19bQ6ezw6evuyN3LecF7Q61EZrpntNi34+rm7O7v6+7u7/Dx6e/rwd/CdcF2
N6k3I6EjI6EjIaEhIaEhPaw9iMuJ2u3b//7/////7enjvaaMkGc5fEsUfUwVjWQ2
sZuA1tXQ5uru5uns0eDVoM6jgMOCms6c0ePU7+7z8O/z7O7v8vH19fP43ergq9at
eMJ4TbJNK6QrF5wXEZoRLKUsfcZ+1+vY//7/////7OjjvaaLkGc4fEsUfUwVjWQ2
sJuA1tTP5Onr4+fp3OTgz9/SxtzJzuDS3+fj6evs6uzt6u3t7O7v7vDx6e7s3+vh
w+DEg8eEPqw+Gp4aFZwVMqcygMeB1+vY/v3/////7OjivaaLkGc4fEsUfUwVjWQ2
sJqA1dTO4ujq4ebn4eXl5Obo5ujq5unq5unq5urq5+vq6Ozs6e3s6+7u7/Dx9vP4
6O7qsdmybb5uP6w/JaIlMqgyfsZ+1urX/fz/////6+fivKWLkGc4fEsUfUwVjWQ2
r5qA1NPO4efp4ebm4eTl5Obo5ufq5ujq5ejp5eno5urp5+vr6Ozr6e3t7e7v8vH1
7fDw2Ojatdq3g8eEQ65DMacxd8N40+nV/Pv///7/6+fhvKWKkGc4fEsUfUwVjGQ2
r5p/1NPO4efp4OXm3+Pj4OTk4eXl4ubm4ubm4+fn5enp5urq5+vr6Ozs6u3t6+7u
6+/u8PHy6u/svN2+a75sSbBJgsiD1unX+/r+/f3/6ubgvKWKkGc4fEsUfUwVjGQ2
r5p/09PO4Ofo3+Xm3uPj3+Pj4OTk4eXl4ubm4ubm4+jo5enp5urq5+vr6Ozs6e3s
6+7u8/H29PP32ejbpNSljMqNrtiv4O3i+Pj7+vz/6eXgu6SKj2Y4fEsUfUwVjGQ2
r5p/1NPO4Ofo3+Tl3uLi3uPj3+Pj4OTk4eXl4ubm4ubm4+fn5enp5urq5+vr6Ozs
6u3t7O7v7e/w5+3p2unc1efW3uvg7PHu9ff49/r86OTfuqSJj2Y4fEsUfUwVjWQ2
sJuB1dXR4ens4Ofo3+Tl3+Xm4OXm4ebm4ebn4ufo4+jp5Onq5err5uvs5+zt6e3u
6u7v6+/w7PDx7/Lz8vT39fX59PX48/X29fj69/z+6Obhu6WLj2c4fEsUfUwVjWU2
sJyD1tfT4+zv4ens4Ofo4Ofo4efp4efp4ujq4+nq5Onr5ers5uvt5+zu6O3v6e7w
6vDx6/Dy7fHz7/P18vX59fb79Pf68/f59vr9+P7/6ejku6WMj2c5fEsUfk0Wi2Iz
qpN1y8a71tfT1dXR1NPO09PO1NPO1NPO1dTO1tTP1tXQ19bQ2NfR2dfS2tjT29nU
3NrV3dvW3tzW393X4N7Y4d/Z4uDa4+Db5uTf6Ofj29TJs5p9jmQ1fUwVf08Zh1sp
mHZOqpN1sJyDsJuBr5p/r5p/r5p/r5qAsJqAsJuAsZuAsZuBsZyBspyCsp2Cs52D
s56DtJ6EtZ+EtZ+FtqCFtqCGt6GGuKGHuaOJuqWLs5p9nXpSiFwqf08ZgVEcglQg
h1spi2IzjWU2jWQ2jGQ2jGQ2jGQ2jWQ2jWQ2jWQ2jWQ2jWQ2jWQ2jWQ2jWU2jWU2
jmU3jmU3jmU3jmU3jmU3jmY3jmY3j2Y3j2Y4j2c4jWQ1iFwqg1QggFEcgVIdgVEc
f08Zfk0WfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwV
fUwUfUwUfUwUfUwUfUwUfUsUfUsUfEsUfEsUfEsUfUwVf08ZgFEcgVId"""


unchecked_16_b64 = \
"""Qk02AwAAAAAAADYAAAAoAAAAEAAAABAAAAABABgAAAAAAAADAAAAAAAAAAAAAAAA
AAAAAAAA////////////////////////////////////////////////////////
////////////////gVIdgVIdgVIdgVIdgVIdgVIdgVIdgVIdgVIdgVIdgVIdgVId
gVId////////////gVId4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
gVId////////////gVId4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
gVId////////////gVId4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
gVId////////////gVId4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
gVId////////////gVId4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
gVId////////////gVId4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
gVId////////////gVId4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
gVId////////////gVId4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
gVId////////////gVId4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
gVId////////////gVId4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
gVId////////////gVId4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
gVId////////////gVIdgVIdgVIdgVIdgVIdgVIdgVIdgVIdgVIdgVIdgVIdgVId
gVId////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////"""


unchecked_32_b64 = \
"""Qk2KDAAAAAAAAIoAAAB8AAAAIAAAACAAAAABABgAAAAAAAAMAAAAAAAAAAAAAAAA
AAAAAAAAAAD/AAD/AAD/AAAAAAAA/0JHUnOAwvUoYLgeFSCF6wFAMzMTgGZmJkBm
ZgagmZkJPArXAyRcjzIAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAgVIdgFEc
f08ZfUwVfUwUfUwUfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwV
fUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwUfUwUfUwVf08ZgFEcgVIdgFEcg1Qg
h1sqjGM0jmU3jWU3jWU2jWU2jWU2jWU2jWU2jWU2jWU2jWU2jWU2jWU2jWU2jWU2
jWU2jWU2jWU2jWU2jWU2jWU2jWU2jWU2jWU3jmU3jGM0h1sqg1QggFEcf08Zh1sq
mXdPrZV4tJ+Fs56EspyCspyCspyCspyCspyCspyCspyCspyCspyCspyCspyCspyC
spyCspyCspyCspyCspyCspyCspyCspyCs56EtJ+FrZV4mXdPh1sqf08ZfUwVjGM0
rZV40MrA3NzY2trV2djS2djS2djS2djS2djS2djS2djS2djS2djS2djS2djS2djS
2djS2djS2djS2djS2djS2djS2djS2djS2trV3NzY0MrArZV4jGM0fUwVfUwUjmU3
tJ+F3NzY6fH06O7x5uzu5uzu5uzu5uzu5uzu5uzu5uzu5uzu5uzu5uzu5uzu5uzu
5uzu5uzu5uzu5uzu5uzu5uzu5uzu5uzu6O7x6fH03NzYtJ+FjmU3fUwUfUwUjWU3
s56E2trV6O7x5uzu5enq5enq5enq5enq5enq5enq5enq5enq5enq5enq5enq5enq
5enq5enq5enq5enq5enq5enq5enq5enq5uzu6O7x2trVs56EjWU3fUwUfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwVjWU2
spyC2djS5uzu5enq4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn
4+fn4+fn4+fn4+fn4+fn4+fn4+fn4+fn5enq5uzu2djSspyCjWU2fUwVfUwUjWU3
s56E2trV6O7x5uzu5enq5enq5enq5enq5enq5enq5enq5enq5enq5enq5enq5enq
5enq5enq5enq5enq5enq5enq5enq5enq5uzu6O7x2trVs56EjWU3fUwUfUwUjmU3
tJ+F3NzY6fH06O7x5uzu5uzu5uzu5uzu5uzu5uzu5uzu5uzu5uzu5uzu5uzu5uzu
5uzu5uzu5uzu5uzu5uzu5uzu5uzu5uzu6O7x6fH03NzYtJ+FjmU3fUwUfUwVjGM0
rZV40MrA3NzY2trV2djS2djS2djS2djS2djS2djS2djS2djS2djS2djS2djS2djS
2djS2djS2djS2djS2djS2djS2djS2djS2trV3NzY0MrArZV4jGM0fUwVf08Zh1sq
mXdPrZV4tJ+Fs56EspyCspyCspyCspyCspyCspyCspyCspyCspyCspyCspyCspyC
spyCspyCspyCspyCspyCspyCspyCspyCs56EtJ+FrZV4mXdPh1sqf08ZgFEcg1Qg
h1sqjGM0jmU3jWU3jWU2jWU2jWU2jWU2jWU2jWU2jWU2jWU2jWU2jWU2jWU2jWU2
jWU2jWU2jWU2jWU2jWU2jWU2jWU2jWU2jWU3jmU3jGM0h1sqg1QggFEcgVIdgFEc
f08ZfUwVfUwUfUwUfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwV
fUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwVfUwUfUwUfUwVf08ZgFEcgVId"""


toolbar_add_b64 = \
"""iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhk
iAAAAAlwSFlzAAADPwAAAz8BdDktJAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3Nj
YXBlLm9yZ5vuPBoAAAF+SURBVFiF7Za/S8NAFMdfEmvuyhVKCEZQSv+DYKEgdujk
UP8eJ+0m4uIf49bBraAUlGK3ji06mCWUpvZdDGkdJBATvNT4ow732e7du+/78vLu
CIBEIlkzSt6DlmW1CSF7AACc877jOOd/ZoBS2mg2m9eVSoUCAIzH43m32z1ExNuv
aql5DGiatsMYo9G6VCoVNU3bzaOVy8BPIg1sZCVQSg90Xd+Kx4IgqCfzlstlvVwu
v8Zjvu8/I2JPpC+8BZZltW3bPokPXIRhGKCq7w1cLBbgum7q/Gw2w8FgcOY4zsVn
NYQdIITY1Wo1VTyJqqpgmmYqbpomHQ6HNeHZLPHfRtgBzvnDaDQ6YowVk3srfoK5
7/t9UY3Ml5BSuq/r+nY8FgRBo9VqHRuGAQAArutCp9O5LBQKN/G8VYYw8xYgYg8R
P8QYY5vJPEVR7iaTyVWWXpK1z4A0kMtAGIZPnufNo/V0On0Jw/Axj9Z3fkhOCSE1
AADO+b3otZNIJP+aN00ug/bCc8o2AAAAAElFTkSuQmCC"""

toolbar_remove_b64 = \
"""iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhk
iAAAAAlwSFlzAAADPwAAAz8BdDktJAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3Nj
YXBlLm9yZ5vuPBoAAACnSURBVFiFY2AYBaNgFIyCUTAKBhgwElLAy8lpxcvCIkaO
4e///Hnx/fv3E2Q7QFlYuMZHXb1KiJOTkxwHvPv+/fvWmzdb7rx924ZLDQs+A3jZ
2PSNpKTIspyBgYFBQVCQ8+D9+4b41DCRazi1AN4Q+Pzr14WzT596CXNxcZFj+Ntv
3759+fXrHD41BBMhJyenhSALiwQ5DiAmEY6CUTAKRsEoGAUDDgBrcy4OPZfbBAAA
AABJRU5ErkJggg=="""

toolbar_save_b64 = \
"""iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhk
iAAAAAlwSFlzAAADPwAAAz8BdDktJAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3Nj
YXBlLm9yZ5vuPBoAAAHzSURBVFiF7ZZNaxNRFIafTHuT1jBpnJCkHRWxgoaqi1bF
DwoiuhDc6cKFLhVKwb+gfyC4d6W4cVtBgxsRhYqbgpWiqaJYLK2dpGG0TNN8zB03
KhSd5k4YUHDe5T3vOe9zhzPDQKRIf1mxLWo6ieQJPZU6HBc9qaCD3bZs2fX1Gdbs
V8CCn6/X53yQvQeeUDhSKEhbm7h2NWg+9+7e4ZmXBuvzCh/mblJdvq0OkB26zvFz
I4gEfY0Y+w8eCgwwkMtDeztkBvNUVy75AWh/7PbIIBKBQ32laX2+pfBSulME8O8D
bDRbXQ2uN9T6/L4Dv1RuCYrFIkfHRonF1B7Y2/kyszUHsiEArBkmU06TqdIL8Dwl
AJIpyO5RsnYEAEDEwcirhQeUGgCQW3hNGrejry0ln/L7kNv0EAHqDqd2Zjg7frKj
VUrJjfsPqAyPhQggXeKil4fPp5lfqqDhcfnMOLns71umaRo9SkN/+AN4mVuq8m73
KOWhEWbelIO0hgOwSYovRHcA0n1PzWqEE9ENQM26xcvHj9hwNt1TuC1Y/YKoLGIM
qG15J/ktoYe1eIXp0lNOXzz283Dywnksy0IIgWma6inN9a9+pa3+CaG/fxeZHSWS
enJYa5ppw1DK+2itOnZcrwHgfKtiL09g27PqxJEi/U/6DgmjkMigHweKAAAAAElF
TkSuQmCC"""

toolbar_print_b64 = \
"""iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhk
iAAAAAlwSFlzAAADPwAAAz8BdDktJAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3Nj
YXBlLm9yZ5vuPBoAAAGmSURBVFiF7ZY9a8JQFIZfL+Zeg7EmCK2IUGKGDmJdC10M
7VLo2q0/p7+kS4f+hQpuXYoOgltF/CpFKDGC9SvaoRUkRL3GWyzFZ8w5vOfh3nAS
YM+eHRNY15DP5+8opSd+wieTydA0zdtVPcF1IZTSc8Mwcn4EGo3G67qetQJzut0u
arWaZy2TyYAQwm/mRyAajSKbzfoasgp/2gIRcgVukskkYrGYWIHfugJuAdu20Wq1
uHrj8Tg0TRMroCgKDMPgCw1yx/ILEEJAKeUOFi6wi5fwFMBhoVDQ2u02V9icSqUC
AGg2mzKASwA9ACUAI3ev57cgkUg8pNPp60gkomw0eQnD4XBcLpdf6vX6BYDPxZrX
CRzpum7qui5k+A9SOBw+syzrxrbt+8WC1yZUZVmWBQ4HADDGApIkJdzP//Yq7vV6
mM1mWw1gjIExtrnAdDpFp9PZajjwvcI3FbAHg8GAEHKQSqW2FpgzGo3gOM47j8Bb
tVp9VlX1SlEUIatvPB5Pi8ViybKsR3dt2T9hIBQK5SRJOhYh4DjOR7/ffwLQF5G3
Z8//4gur7nqiXV2K4gAAAABJRU5ErkJggg=="""
