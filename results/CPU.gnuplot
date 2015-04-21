if (!exists("basename")) print "basename not set"; exit
set terminal pngcairo dashed notransparent nocrop enhanced size 1280,960
outFile=basename.'CPU.png'
inFile=basename.'CPU.txt'
set output outFile
set lmargin 25
set rmargin 10
set tmargin 6
set bmargin 8
set title "Job States"
set title font "*,24"
set xlabel "hours"
set xlabel font "*,24"
set xlabel offset 0,-3.
set ylabel "number of jobs"
set ylabel font "*,24"
set ylabel offset -10.
#set origin -0.1,0
set xrange [0:100]
set yrange [0:120000]
#set xtics out border nomirror rotate by -45 offset character 0,-0.2,0
set xtics out border nomirror rotate by -45 offset character -0.2,0,0
set xtics font "*,24"
set ytics font "*,24"
set grid
set ytics out border nomirror
set key at 90.,80000.
set key font "*,20"
#set style fill solid 1.0
#set for [i=1:8] linetype i dashtype i
set style line 1 linetype 2 linecolor rgb "#10ad1d"   linewidth 3.000 pointtype 3 pointsize 0.1 dashtype 1
set style line 2 linetype 2 linecolor rgb "red"    linewidth 3.000 pointtype 3 pointsize 0.1 dashtype 1
set style line 3 linetype 2 linecolor rgb "#3323ad"   linewidth 3.000 pointtype 3 pointsize 0.1 dashtype 1
set style line 4 linetype 2 linecolor rgb "#10ad1d"   linewidth 3.000 pointtype 3 pointsize 0.1 dashtype 2
set style line 5 linetype 2 linecolor rgb "red"    linewidth 3.000 pointtype 3 pointsize 0.1 dashtype 2
set style line 6 linetype 2 linecolor rgb "#3323ad"   linewidth 3.000 pointtype 3 pointsize 0.1 dashtype 2
set style line 7 linetype 2 linecolor rgb "#10ad1d"   linewidth 3.000 pointtype 3 pointsize 0.1 dashtype 3
set style line 8 linetype 2 linecolor rgb "red"    linewidth 3.000 pointtype 3 pointsize 0.1 dashtype 3
set style line 9 linetype 2 linecolor rgb "#3323ad"   linewidth 3.000 pointtype 3 pointsize 0.1 dashtype 3
#set style fill solid
plot \
'T_'.inFile using 1:2 with lines ls 3 title 'Queued (preplaced)', \
'T_'.inFile using 1:3 with lines ls 2 title 'Running (preplaced)', \
'T_'.inFile using 1:4 with lines ls 1 title 'Done (preplaced)', \
'S_'.inFile using 1:2 with lines ls 6 title 'Queued (copied)', \
'S_'.inFile using 1:3 with lines ls 5 title 'Running (copied)', \
'S_'.inFile using 1:4 with lines ls 4 title 'Done (copied)', \
'F_'.inFile using 1:2 with lines ls 9 title 'Queued (remote)', \
'F_'.inFile using 1:3 with lines ls 8 title 'Running (remote)', \
'F_'.inFile using 1:4 with lines ls 7 title 'Done (remote)'
