pid = 12858
pid2 = "12858"

dic = {
    "12858": True
}

if __name__ == '__main__':
    print(dic.keys())
    for key in dic.keys():
        if key == str(pid):
            print(True)
            print(dic[str(pid)])