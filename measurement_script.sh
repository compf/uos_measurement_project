#env/bash
ts=$(date +%s)
sudo python3 measurement_tool.py $ts
scp -r "project_archive/"$ts".json" compf@37.221.197.246:project/project_archive