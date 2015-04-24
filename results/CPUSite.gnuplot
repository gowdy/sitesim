set terminal png notransparent medium nocrop enhanced size 1280,960 font arial 24
set output basename.'CPUSite.png'
set lmargin 25
set rmargin 10
set tmargin 6
set bmargin 8
if (basename[0:2] eq 'T_') \
	set title "Job running at sites with preplaced data"; \
else \
	if (basename[0:2] eq'F_') \
		set title "Job running with data read from FNAL"; \
	else \
		if (basename[0:2] eq 'S_') \
			set title "Job running with data transferred"; \
		else \
			print "Unexpected basename: ",basename; \
			exit

set title font "*,24"
set xlabel "hours"
set xlabel font "*,24"
set xlabel offset 0,-3.
set ylabel "number of jobs"
set ylabel font "*,24"
set ylabel offset -10.
#set origin -0.1,0
set xrange [0:100]
set yrange [0:21000]
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
set style line 9 linetype 2 linecolor rgb "violet" linewidth 3.000 pointtype 3 pointsize 0.1
set style fill solid
plot \
basename.'CPUSite.txt' using 1:($11+$12+$13+$14+$15+$16+$17+$18+$19) with filledcurves x1 ls 9 title 'FNAL', \
basename.'CPUSite.txt' using 1:($11+$12+$13+$14+$15+$16+$17+$18) with filledcurves x1 ls 8 title 'MIT', \
basename.'CPUSite.txt' using 1:($11+$12+$13+$14+$15+$16+$17) with filledcurves x1 ls 7 title 'UCSD', \
basename.'CPUSite.txt' using 1:($11+$12+$13+$14+$15+$16) with filledcurves x1 ls 6 title 'Nebraska', \
basename.'CPUSite.txt' using 1:($11+$12+$13+$14+$15) with filledcurves x1 ls 5 title 'Caltech', \
basename.'CPUSite.txt' using 1:($11+$12+$13+$14) with filledcurves x1 ls 1 title 'Florida', \
basename.'CPUSite.txt' using 1:($11+$12+$13) with filledcurves x1 ls 2 title 'Caltech', \
basename.'CPUSite.txt' using 1:($11+$12) with filledcurves x1 ls 3 title 'Vanderbilt', \
basename.'CPUSite.txt' using 1:11 with filledcurves x1 ls 4 title 'Purdue'

