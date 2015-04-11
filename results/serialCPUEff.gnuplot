set terminal png notransparent medium nocrop enhanced size 1280,960 font arial 24
set output 'serialCPUEff.png'
set title "CPU Efficiency when data transferred from FNAL"
set title font "*,24"
set xlabel "CPU Efficiency"
set xlabel font "*,24"
set xlabel offset 0,-3.
set ylabel "number of jobs"
set ylabel font "*,24"
set ylabel offset -10.
#set origin -0.1,0
set xrange [0:100]
set yrange [0:15000]
#set xtics out border nomirror rotate by -45 offset character 0,-0.2,0
set xtics out border nomirror rotate by -45 offset character -0.2,0,0
set xtics font "*,24"
set ytics font "*,24"
set grid
set ytics out border nomirror
#set key at 60.,80000.
#set key font "*,20"
set key off
#set style fill solid 1.0
set style line 1 linetype 2 linecolor rgb "black"   linewidth 2.000 pointtype 3 pointsize 0.1
# green
set style line 2 linetype 2 linecolor rgb "#10ad1d"   linewidth 3.000 pointtype 3 pointsize 0.1
set style line 3 linetype 2 linecolor rgb "red"    linewidth 3.000 pointtype 3 pointsize 0.1
set style line 4 linetype 2 linecolor rgb "#3323ad"   linewidth 3.000 pointtype 3 pointsize 0.1
set style line 5 linetype 2 linecolor rgb "purple" linewidth 3.000 pointtype 3 pointsize 0.1
set style fill solid
binwidth=1
bin(x,width)=width*floor(x/width)
f(y) = mean_x
fit f(y) 'serialCPUEff.txt' u 5:5 via mean_x
set label 1 gprintf("Average: %2.1f%%", mean_x) at 40,10000 font "*,20"

plot \
'serialCPUEff.txt' using (bin($5,binwidth)):(1.0) smooth freq with boxes ls 4

