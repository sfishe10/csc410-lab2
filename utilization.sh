#!/bin/bash

file=$1
#line= `tail +6 $file|head -n 1`
lines=`cat $1 | wc -l`
count=0
sum=0
for ((  num = 9 ;  num <= $lines;  num = num + 12  ))
do
line=`sed -n ${num}p $file`
idle=`echo $line | cut -d " " -f  9`
num1=`expr 100 - $idle`
#echo $num1
sum=`expr $sum + $num1`
count=`expr $count + 1`
done

#echo "Sum is: "
#echo "$sum"
#echo "Count is: "
#echo $count
#num=`expr $num1 + $num2 + $num3 + $num4 + $num5 + $num6 + $num7 + $num8 + $num9 + $num10 + $num11`
echo "Utilization of core 0 is: "
echo "scale=2; $sum / $count " | bc
count=0
sum=0
for ((  num = 10 ;  num <= $lines;  num = num + 12  ))
do
line=`sed -n ${num}p $file`
idle=`echo $line | cut -d " " -f  9`
num1=`expr 100 - $idle`
#echo $num1
sum=`expr $sum + $num1`
count=`expr $count + 1`
done

#echo "Sum is: "
#echo "$sum"
#echo "Count is: "
#echo $count
#num=`expr $num1 + $num2 + $num3 + $num4 + $num5 + $num6 + $num7 + $num8 + $num9 + $num10 + $num11`
echo "Utilization of core 1 is: "
echo "scale=2; $sum / $count " | bc