python3 main.py events
psql -U ntyrreuir -d timetable -c 'COPY (select * from "Event") TO STDOUT WITH (FORMAT CSV, HEADER)' -o 'CSV/Event.csv'
psql -U ntyrreuir -d timetable -c 'COPY (select * from "GroupToEvent") TO STDOUT WITH (FORMAT CSV, HEADER)' -o 'CSV/GroupToEvent.csv'
psql -U ntyrreuir -d timetable -c 'COPY (select * from "UserToEvent") TO STDOUT WITH (FORMAT CSV, HEADER)' -o 'CSV/UserToEvent.csv'
git add CSV
git commit -m "Change tables"
git push origin first-branch
