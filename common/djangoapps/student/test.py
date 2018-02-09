f = open("/static/popup_index/index.html", 'r')
while True:
    line = f.readline()
    if not line: break
    print(line)
f.close()