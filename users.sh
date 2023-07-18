python3 main.py users
psql -U ntyrreuir -d timetable -c 'COPY (select * from "User") TO STDOUT WITH (FORMAT CSV, HEADER)' -o 'CSV/User.csv'
psql -U ntyrreuir -d timetable -c 'COPY (select * from "Group") TO STDOUT WITH (FORMAT CSV, HEADER)' -o 'CSV/Group.csv'
psql -U ntyrreuir -d timetable -c 'COPY (select * from "Field") TO STDOUT WITH (FORMAT CSV, HEADER)' -o 'CSV/Field.csv'
git add CSV
git commit -m "Change tables"
git push origin main
