python3 main.py events
psql -U ntyrreuir -d tt -c 'COPY (select * from "Event") TO STDOUT WITH (FORMAT CSV, HEADER)' -o 'CSV/Event.csv'
psql -U ntyrreuir -d tt -c 'COPY (select * from "GroupToEvent") TO STDOUT WITH (FORMAT CSV, HEADER)' -o 'CSV/GroupToEvent.csv'
psql -U ntyrreuir -d tt -c 'COPY (select * from "UserToEvent") TO STDOUT WITH (FORMAT CSV, HEADER)' -o 'CSV/UserToEvent.csv'
psql -U ntyrreuir -d tt -c 'COPY (select * from CommonUserAndGroupsEventsInfo) TO STDOUT WITH (FORMAT CSV, HEADER)' -o 'CSV/SpecialEvents.csv'
git add CSV
git commit -m "Change tables"
git push origin main
