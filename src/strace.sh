for i in $(seq 1 30)
do
    process_id=`ps -ef|grep "$2"|grep -v grep|grep -v sshpass|awk '{print $2}'`
    if [ ! -z "$process_id" ];then  
        echo "start trace"
        strace -fp "$process_id" -t -o "$1"
        break
    fi;
    sleep 1
done
