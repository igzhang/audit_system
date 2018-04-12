
def parse(file_path):
    """
    原生ssh日志分析
    :param file_path:
    :return:
    """
    result_list = []
    with open(file_path) as file_stream:
        tmp = []
        complete_flag = False
        for line in file_stream:
            pid,time,mode,cmd = line.split()[0:4]
            cmd = cmd.strip(",").strip('\"')
            if complete_flag:
                if mode.startswith("write(5"):
                    if not cmd.startswith("\\"):
                        tmp.append(cmd)
                    complete_flag = False
            if mode.startswith("read(4"):
                complete_flag = False
                if cmd == "\\r" or cmd == "\\n":
                    each_log = "执行命令".join([time,"".join(tmp)])
                    result_list.append(each_log)
                    tmp.clear()
                elif cmd == "\\t":
                    complete_flag = True
                else:
                    tmp.append(cmd)


    return result_list

if __name__ == '__main__':
    print(parse("..\\logs\\2.log"))