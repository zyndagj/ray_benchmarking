#!/usr/bin/env python

import sys, argparse, os
from glob import glob

def main():
	parser = argparse.ArgumentParser(description="Generates SLURM scripts for running throughput Ray runs.")
	parser.add_argument("--N", metavar="STR", help="Comma delimited string of node counts", type=str)
	parser.add_argument("-A", metavar="STR", help="Allocation", type=str)
	parser.add_argument("--ppn", metavar="INT", help="Processes per node", type=int)
	parser.add_argument("-k", metavar="STR", help="Comma delimited string of Ks to run simultaneously", type=str, default="31")
	parser.add_argument("-p", metavar="STR", help="scheduler queue", type=str, required=True)
	parser.add_argument("-r", metavar="INT", help="Replicates", type=int, default=3)
	parser.add_argument("-B", metavar="FILE", help="Ray binary to use", type=str, required=True)
	parser.add_argument("--mpi", metavar="STR", help="MPI spawnder (ibrun or aprun)", required=True)
	parser.add_argument("-D", metavar="TYPE", help="GAGE size (tiny, small..)", required=True)
	parser.add_argument("-s", help="Run replicates simultaneously", action='store_true')
	args = parser.parse_args()

	for N in map(int, args.N.split(',')):
		# Total number of cores
		n=args.ppn*N
		# Total number of cores per task
		kList = map(int, args.k.split(','))
		if args.s:
			nt=n/(len(kList)*args.r)
		else:
			nt=n/len(kList)
		# Print header
		jobName = "%s_%s_%ix%i"%(os.path.split(args.B)[1], args.D, N, args.ppn)
		OUT = open(jobName+'.slurm', 'w') 
		if args.p in set(('test1','normal','flat-quadrant','test2')):
			# SLURM
			OUT.write(slurmHeader.format(J=jobName, N=N, n=n, p=args.p, A=args.A)+'\n')
			OUT.write(retryIB+'\n')
			offset=0
			for r in range(1, args.r+1):
				for k in kList:
					OF="out-%s-%s-%s-n%i-k%i-r%i"%(args.p, args.D, os.path.split(args.B)[1], nt, k, r)
					config=confDir[args.D]+'/Ray.conf'
					OUT.write("retry %s %s %s %i %i %i &\n" %(OF, args.B, config, nt, k, offset))
					offset += nt
				if not args.s:
					OUT.write("wait\n")
					offset = 0
			if args.s:
				OUT.write("wait\n")
		else:
			# PBS
			OUT.write(pbsHeader.format(J=jobName, N=N, PPN=args.ppn)+'\n')
			OUT.write(retryAC+'\n')
			for r in range(1, args.r+1):
				for k in kList:
					OF="out-%s-%s-%s-n%i-k%i-r%i"%(args.p, args.D, os.path.split(args.B)[1], nt, k, r)
					config=confDir[args.D]+'/Ray.conf'
					OUT.write("retry %s %s %s %i %i &\n" %(OF, args.B, config, nt, k))
				if not args.s:
					OUT.write("wait\n")
			if args.s:
				OUT.write("wait\n")
		OUT.close()
			
confDir={'huge':'huge_b.impatiens', 'large':'large_h.sapiens', 'small':'small_r.sphaeroides', 'tiny':'tiny_s.aureus'}
pbsHeader='''#!/bin/bash
#PBS -l nodes={N}:ppn={PPN}:xe
#PBS -l walltime=4:00:00
#PBS -N {J}
### set the job stdout and stderr
#PBS -e {J}.$PBS_JOBID.e
#PBS -o {J}.$PBS_JOBID.o

cd $PBS_O_WORKDIR
'''
slurmHeader='''#!/bin/bash
#SBATCH -J {J}
#SBATCH -o {J}.%j.o
#SBATCH -e {J}.%j.e
#SBATCH -t 24:00:00
#SBATCH -N {N}
#SBATCH -n {n}
#SBATCH -p {p}
#SBATCH -A {A}
'''
retryIB = '''
function retry {
	OF=$1; RAY=$2; CONFIG=$3; NTASKS=$4; K=$5; OFFSET=$6
	for i in {1..3}; do
		[ -e ${OF} ] && rm -rf ${OF}*
		( echo "-o ${OF} -k ${K}" && cat ${CONFIG} ) > ${OF}.conf
		ibrun -n ${NTASKS} -o ${OFFSET} ${RAY} ${OF}.conf &> ${OF}.log && return 0 || sleep 2
	done
	return 1
}
export -f retry
'''
retryAC = '''
function retry {
	OF=$1; RAY=$2; CONFIG=$3; NTASKS=$4; K=$5
	for i in {1..3}; do
		[ -e ${OF} ] && rm -rf ${OF}*
		( echo "-o ${OF} -k ${K}" && cat ${CONFIG} ) > ${OF}.conf
		aprun -n ${NTASKS} ${RAY} ${OF}.conf &> ${OF}.log && return 0 || sleep 2
	done
	return 1
}
export -f retry
'''

if __name__ == "__main__":
	main()
