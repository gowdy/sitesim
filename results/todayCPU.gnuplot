set terminal png notransparent medium nocrop enhanced size 1280,960 font arial 24
set output 'todayCPU.png'
set title "Job States when data preplaced at Sites"
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
set key at 60.,80000.
set key font "*,20"
#set style fill solid 1.0
set style line 1 linetype 2 linecolor rgb "black"   linewidth 2.000 pointtype 3 pointsize 0.1
# green
set style line 2 linetype 2 linecolor rgb "#10ad1d"   linewidth 3.000 pointtype 3 pointsize 0.1
set style line 3 linetype 2 linecolor rgb "red"    linewidth 3.000 pointtype 3 pointsize 0.1
set style line 4 linetype 2 linecolor rgb "#3323ad"   linewidth 3.000 pointtype 3 pointsize 0.1
set style line 5 linetype 2 linecolor rgb "purple" linewidth 3.000 pointtype 3 pointsize 0.1
set style fill solid
plot \
'todayCPU.txt' using 1:2 with linespoints ls 4 title 'Queued', \
'todayCPU.txt' using 1:3 with linespoints ls 3 title 'Running', \
'todayCPU.txt' using 1:4 with linespoints ls 2 title 'Done'
