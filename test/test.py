import os
# from qqwry import updateQQwry
# from qqwry import QQwry
import requests
import binascii

from lxml import etree
import base64
import re
# import execjs
# js=execjs.eval('''function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('$(10).Z(Y(){$(\'.X\').0(11);$(\'.12\').0(15);$(\'.14\').0(13);$(\'.W\').0(V);$(\'.O\').0(N);$(\'.M\').0(L);$(\'.P\').0(Q);$(\'.U\').0(T);$(\'.S\').0(R);$(\'.16\').0(17);$(\'.1m\').0(1l);$(\'.1k\').0(1j);$(\'.1n\').0(1o);$(\'.1r\').0(1q);$(\'.1p\').0(1i);$(\'.1h\').0(1b);$(\'.1a\').0(19);$(\'.18\').0(1c);$(\'.1d\').0(1g);$(\'.1f\').0(1e);$(\'.K\').0(D);$(\'.g\').0(f);$(\'.e\').0(d);$(\'.h\').0(i);$(\'.l\').0(k);$(\'.j\').0(c);$(\'.a\').0(3);$(\'.5\').0(2);$(\'.1\').0(4);$(\'.b\').0(6);$(\'.9\').0(8);$(\'.7\').0(m);$(\'.J\').0(n);$(\'.C\').0(B);$(\'.A\').0(E);$(\'.F\').0(I);$(\'.H\').0(G);$(\'.z\').0(y);$(\'.r\').0(q);$(\'.p\').0(o);$(\'.s\').0(t);$(\'.x\').0(w);$(\'.v\').0(u);$(\'.1s\').0(2V);$(\'.1t\').0(2s);$(\'.2r\').0(2q);$(\'.2u\').0(2v);$(\'.2y\').0(2x);$(\'.2w\').0(2p);$(\'.2o\').0(2h);$(\'.2g\').0(2f);$(\'.2e\').0(2i);$(\'.2j\').0(2n);$(\'.2m\').0(2l);$(\'.2k\').0(2z);$(\'.2A\').0(2P);$(\'.2O\').0(2N);$(\'.2M\').0(2Q);$(\'.2R\').0(2U);$(\'.2T\').0(2S);$(\'.2L\').0(2K);$(\'.2E\').0(2D);$(\'.2C\').0(2B);$(\'.2F\').0(2G);$(\'.2J\').0(2I);$(\'.2H\').0(2d);$(\'.2c\').0(1J);$(\'.1I\').0(1H);$(\'.1G\').0(1K);$(\'.1L\').0(1O);$(\'.1N\').0(1M);$(\'.1F\').0(1E);$(\'.1x\').0(1w);$(\'.1v\').0(1u);$(\'.1y\').0(1z);$(\'.1D\').0(1C);$(\'.1B\').0(1A);$(\'.1P\').0(1Q);$(\'.26\').0(25);$(\'.24\').0(23);$(\'.27\').0(28);$(\'.2b\').0(2a);$(\'.29\').0(22);$(\'.21\').0(1U);$(\'.1T\').0(1S);$(\'.1R\').0(1V);$(\'.1W\').0(20);$(\'.1Z\').0(1Y);$(\'.1X\').0(2t)});',62,182,'html|r54a3|34403|9999|39371|r9531|35746|r5286|34273|raa9a|r7ca5|r6039|8908|38091|rdaf5|45521|r82ec|r87a8|39533|r0e4a|33948|r5b05|43036|52479|31870|r4efe|8041|r915c|r7749|51489|8197|r175d|61279|r007e|42119|rc747|r96f8|58573|r7ae4|23500|38525|r529c|3888|rc4bb|1081|r74b0|rbb2d|999|rd532|51200|r1cd6|rf509|8081|8000|r9c00|80|r243e|3128|r2e40|r26b7|function|ready|document|8080|r0fd5|53281|rb01e|32108|reda7|21231|rfd21|57797|r6b02|60020|33630|rb4d1|35816|r34ca|65205|r29d8|61047|42956|r1479|55443|r49dc|r83db|60604|r019d|35709|re93f|r0953|ra3e0|8118|rc5f0|36739|r45e9|rdedc|34454|57149|r3cbc|41868|rddef|37979|r325c|rb5b4|3129|r5e31|53731|38898|r668f|50782|r5d83|50330|r23e1|45476|re6fe|41714|r4629|44590|10030|r4f7a|r3cb5|43496|re474|54159|rcb4e|34638|3153|r086a|46944|re441|ra6e3|1981|r8dd4|3140|r30be|r9f46|47548|re299|32052|r820f|1080|30716|r622a|r5076|8090|rfa0f|53758|r6e69|47324|9090|rc376|8181|8089|rd522|5000|rd50b|5836|r1db9|48458|r6de0|39330|ra08b|54555|r18f3|rb0a4|42033|raa98|31120|r8e74|9991|r3c05|r633d|56167|r848c|48515|46669|re8eb|45578|r4153|47615|8082'.split('|'),0,{})''')
# result=js
# print(result)
# exit(-1)

# print("1.1.1.1:123".split(':'))
# if False == os.path.isfile("qqwry.dat"):
#     ret = updateQQwry("qqwry.dat")
#     print(ret)

# q = QQwry()
# q.load_file('qqwry.dat')
# area = q.lookup('182.150.123.72')
# print(" ".join(area))
print(['https://hidemy.name/en/proxy-list/?start=%s' % i for i in (range(0, 577, 64))])
exit(-1)
# import urllib.parse
# s='%3c%61%20%68%72%65%66%3d%22%68%74%74%70%3a%2f%2f%77%77%77%2e%66%72%65%65%70%72%6f%78%79%6c%69%73%74%73%2e%6e%65%74%2f%7a%68%2f%31%38%35%2e%34%2e%31%33%35%2e%37%37%2e%68%74%6d%6c%22%3e%31%38%35%2e%34%2e%31%33%35%2e%37%37%3c%2f%61%3e'
# s=urllib.parse.unquote(s)
# print(s)
# exit(-1)
proxies = {
    "http": "http://127.0.0.1:54321",
    "https": "http://127.0.0.1:54321"
    }
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
               'Accept': '*/*',
               'Connection': 'keep-alive',
               'Accept-Language': 'zh-CN,zh;q=0.8'
               }
r = requests.get("http://www.us-proxy.org/", headers=headers, proxies=proxies, timeout=5)
print(r.status_code)
print(r.headers)
print(r.cookies.get_dict())