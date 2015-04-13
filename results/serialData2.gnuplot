set terminal png notransparent medium nocrop enhanced size 1280,960 font arial 24
set output 'serialData2.png'
set lmargin 25
set rmargin 10
set tmargin 6
set bmargin 8
set title "Network out of FNAL when data transferred from FNAL"
set title font "*,24"
set xlabel "hours"
set xlabel font "*,24"
set xlabel offset 0,-3.
set ylabel "Bandwidth (MB/s)"
set ylabel font "*,24"
set ylabel offset -10.
#set origin -0.1,0
set xrange [0:100]
set yrange [0:40000]
#set xtics out border nomirror rotate by -45 offset character 0,-0.2,0
set xtics out border nomirror rotate by -45 offset character -0.2,0,0
set xtics font "*,24"
set ytics font "*,24"
set grid
set ytics out border nomirror
#set key at 40.,40000.
set key font "*,20"
#set style fill solid 1.0
set style line 1 linetype 2 linecolor rgb "black"   linewidth 2.000 pointtype 3 pointsize 0.1
# green
set style line 2 linetype 2 linecolor rgb "#10ad1d"   linewidth 3.000 pointtype 3 pointsize 0.1
set style line 3 linetype 2 linecolor rgb "red"    linewidth 3.000 pointtype 3 pointsize 0.1
set style line 4 linetype 2 linecolor rgb "#3323ad"   linewidth 3.000 pointtype 3 pointsize 0.1
set style line 5 linetype 2 linecolor rgb "purple" linewidth 3.000 pointtype 3 pointsize 0.1
set style line 6 linetype 2 linecolor rgb "green" linewidth 3.000 pointtype 3 pointsize 0.1
set style line 7 linetype 2 linecolor rgb "blue" linewidth 3.000 pointtype 3 pointsize 0.1
set style line 8 linetype 2 linecolor rgb "orange" linewidth 3.000 pointtype 3 pointsize 0.1
set style fill solid
#set label 1 at 60,1000 "Florida,MIT,UCSD,Wiscosin" font "*,15"
#set label 2 at 50,10000 "Caltech,Nebraska,\nPurdue,Vanderbilt" font "*,15"
plot \
'serialData.txt' using 1:($18) with linespoints ls 8 title 'Wisconsin', \
'serialData.txt' using 1:($17) with linespoints ls 7 title 'Vanderbilt', \
'serialData.txt' using 1:($16) with linespoints ls 6 title 'Purdue', \
'serialData.txt' using 1:($15) with linespoints ls 5 title 'Florida', \
'serialData.txt' using 1:($14) with linespoints ls 1 title 'MIT', \
'serialData.txt' using 1:($13) with linespoints ls 2 title 'Nebraska', \
'serialData.txt' using 1:($12) with linespoints ls 3 title 'UCSD', \
'serialData.txt' using 1:11 with linespoints ls 4 title 'Caltech'

