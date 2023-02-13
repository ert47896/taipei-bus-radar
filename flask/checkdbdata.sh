#!/bin/sh
#check_result=$(docker exec -i web sh -c "test -f /workspace/flask/app/cache.txt && echo 'Success!'")
#while [ ! $(docker exec -i web sh -c "test -f /workspace/flask/app/checkpoint.txt && echo 'Success!'") ];
while [ $(docker top web | grep 'python ./module/MOTCdata_init.py' | awk '{print $2}') ]
do
	echo "Wait insert TDX data into MySQL"
	#echo $(docker exec -i web sh -c "cd /workspace/flask/app && ls -la")
	sleep 5
done
#[ $(docker exec -i web sh -c "test -f /workspace/flask/app/checkpoint.txt && echo 'Existed'") ] && docker exec -i web sh -c "rm -f /workspace/flask/app/checkpoint.txt"
docker exec -i web sh -c "cd /workspace/flask/app && python -m pytest -v"

