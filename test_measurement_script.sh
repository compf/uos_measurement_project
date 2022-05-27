#!env/bash
git fetch && git pull
ts=$(date +%s)
ts=$(($ts-$(($ts%60)))) # resetting to removing effect of possible additional seconds
#cd /home/pi/project
python3 measurement_tool.py --time $ts --conf $1
#scp -r "project_archive/"$ts".json" compf@37.221.197.246:project/project_archive
