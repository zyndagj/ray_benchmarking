# ray_benchmarking
Repository to build and benchmark the Ray assembler

## Quickstart

```
# Compile the binaries and download data
ml intel
make -j 16 all
ml gcc
make -j 16 Ray

# Generate SLURM scripts
for bin in Ray-gcc*; do
	python generate_sbatch.py --N 4,8,16 -A allocation --ppn 68 -k 31,27 -r 3 -B ${bin} --mpi ibrun -D small -p normal
done
ml intel
for bin in Ray-icc*; do
	python generate_sbatch.py --N 4,8,16 -A allocation --ppn 68 -k 31,27 -r 3 -B ${bin} --mpi ibrun -D small -p normal
done

# Submit scripts
ls *slurm | xargs -n 1 sbatch

# Print runtime in seconds
python parse_runtime.py
```

## Compiling Ray

### Build Ray for intel

```
ml intel
make -j 16 Ray
```

### Build Ray for GCC

```
ml gcc
make -j 16 Ray
```

## Downloading data

```
make -j 16 data
```

Downloads the

* Staphylococcus aureus
* Rhodobacter sphaeroides
* Human Chromosome 14
* Bombus impatiens (bumblebee)

from the GAGE [website](http://gage.cbcb.umd.edu/data/index.html) and parititions the files for Ray.

## Generating slurm scripts

```
usage: generate_sbatch.py [-h] [--N STR] [-A STR] [--ppn INT]
	[-k STR] -p STR [-r INT] -B FILE --mpi STR -D TYPE [-s]
```

| Arg | Example | Description |
|:-:|:-----:|:---|
| `--N` | `--N 2,4,8` | Comma delimited string of node counts |
| `-A` | `-A allocation` | Scheduler allocation |
| `--ppn` | `--ppn 68` | MPI processes per node |
| `-k` | `-k 31,29,27` | Comma delimited string of k-mer sizes to run simultaneously \(throughput\) | 
| `-p` | `-p normal` | Scheduler queue |
| `-r` | `-r 3` | Number of times runs are repeated |
| `-B` | `-B Ray-gcc-avx2` | Binary to use |
| `-D` | `-D small` | Dataset to use \(tiny, small, large, huge\)|
| `-s` | `-s` | Run replicates simultaneously |

## Compiling runtime

Looks for `out*-r[0-9]` folders in the the current working directory and parses `ElapsedTime.txt` file for total runtime after confirming that Ray completed.
