#system to manage massive runs of the molecular mixer to aid in Quinoline Analysis


for i in {1..12}
do
	#run molecule mixer for specifed amount of times with specifed settings
	python moleculeMixer.py -mxd 4 -c bq.xyz -c2 baseQuinoline.xyz -i 2 -m water.xyz -f xyz

	#mv over new coord file to numbered configuration file
	mv newbaseQuinoline.xyz q$i.xyz

	echo "ajsdflkajsdlkfjalsjdfkljsa"
	echo $i
done

