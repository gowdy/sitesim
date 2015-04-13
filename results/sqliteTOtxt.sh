sqlite3 today.sqlite "select (time-1423531206)/3600.,SUM(BandwidthUsed),group_concat(s.name),group_concat(BandwidthUsed)
from Transfers t
left join Links l on (t.[LinkId] == l.[Id])
left join Sites s on (s.[Id] == l.[ToSite])
left join Sites f on (f.Id == l.[FromSite] )
where FromSite==(select id from sites where name='T1_US_FNAL') group by time;
" | sed 's/|/ /g;s/,/ /g' > todayData.txt

sqlite3 today.sqlite "select (time-1423531206)/3600.,SUM(BandwidthUsed),group_concat(s.name),group_concat(BandwidthUsed)
from Transfers t
left join Links l on (t.[LinkId] == l.[Id])
left join Sites s on (s.[Id] == l.[ToSite])
left join Sites f on (f.Id == l.[FromSite] )
where f.[Name]!='T1_US_FNAL' and s.[Name]!='T1_US_FNAL' group by time;
" | sed 's/|/ /g' > todayDataT2.txt

sqlite3 today.sqlite "select (start-1423531206)/3600.,start,end,cpu,(cpu/(end-start))*100 from Jobs;" | sed 's/|/ /g' > todayCPUEff.txt

sqlite3 today.sqlite "select (time-1423531206)/3600.,SUM(QUEUED),SUM(RUNNING),SUM(DONE) from SitesBatch group by time;" | sed 's/|/ /g' > todayCPU.txt

sqlite3 today.sqlite "select (time-1423531206)/3600.,group_concat(SITE),group_concat(RUNNING) from SitesBatch group by time;" | sed 's/|/ /g;s/,/ /g' > todayCPUSite.txt 

# changed first one to use actually done transfers instead

sqlite3 today100.sqlite "select (time-1423531206)/3600.,SUM(DoneData/100),group_concat(s.name),group_concat(DoneData/100)
from Transfers t
left join Links l on (t.[LinkId] == l.[Id])
left join Sites s on (s.[Id] == l.[ToSite])
left join Sites f on (f.Id == l.[FromSite] )
where FromSite==(select id from sites where name='T1_US_FNAL') group by time;
" | sed 's/|/ /g;s/,/ /g' > todayData.txt

sqlite3 today100.sqlite "select (time-1423531206)/3600.,SUM(DoneData/100),group_concat(s.name),group_concat(DoneData/100)
from Transfers t
left join Links l on (t.[LinkId] == l.[Id])
left join Sites s on (s.[Id] == l.[ToSite])
left join Sites f on (f.Id == l.[FromSite] )
where f.[Name]!='T1_US_FNAL' and s.[Name]!='T1_US_FNAL' group by time;
" | sed 's/|/ /g' > todayDataT2.txt
