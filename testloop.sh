
#!/bin/zsh

while true; do
    clear
    # pytest -x -vv $subdir
    # pytest -vv -x tests # ${subdir}
    pytest  json2csv
    fswatch **/*.py -1
done