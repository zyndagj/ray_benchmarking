# ray_benchmarking
Repository to build and benchmark the Ray assembler

## Quickstart

```
ml intel
make -j 16 all
ml gcc
make -j 16 Ray
```

## Build Ray for intel

```
ml intel
make -j 16 Ray
```

## Build Ray for GCC

```
ml gcc
make -j 16 Ray
```

## Download GAGE data

```
make -j 16 data
```

Downloads the

* Staphylococcus aureus
* Rhodobacter sphaeroides
* Human Chromosome 14
* Bombus impatiens (bumblebee)

from the GAGE [website](http://gage.cbcb.umd.edu/data/index.html) and parititions the files for Ray.
