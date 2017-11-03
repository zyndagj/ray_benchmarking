ifeq ($(I_MPI_CC), icc)
	AR = xiar
	CXF = -Wall -std=c++98 -O3 -ipo
	EFA2 = -xCORE-AVX2
	EFN = -xHOST
	EFA2NV = -xCORE-AVX2 -no-vec -no-simd
	EFA5 = -xCOMMON-AVX512
else
	AR = gcc-ar
	CXF = -Wall -std=c++98 -O3 -flto -fwhole-program
	EFN = -march=native
	EFA2 = -march=broadwell -mtune=broadwell -ftree-vectorize
	EFA2NV = -march=broadwell -mtune=broadwell -fno-tree-vectorize
	EFA5 = -march=broadwell -mtune=skylake-avx512 -mavx512f -mavx512cd -ftree-vectorize
endif

VAR = PREFIX="$(PWD)" HAVE_LIBZ=y HAVE_LIBBZ2=y CLOCK_GETTIME=y MPI_IO=y
MT = clean showOptions Ray

all: Ray data

Ray: Ray-$(I_MPI_CC)-avx2 Ray-$(I_MPI_CC)-avx2-novec-nosimd Ray-$(I_MPI_CC)-common-avx512 Ray-$(I_MPI_CC)-native

Ray-cray: ray.tar.gz
	mkdir $@_dir && tar -xzf $^ -C $@_dir
	cd $@_dir && module swap PrgEnv-cray PrgEnv-gnu && $(MAKE) MPICXX=CC CXXFLAGS="-std=c++98 -O3 -march=native -fno-tree-vectorize" $(VAR) $(MT)
	strip $@_dir/Ray
	mv $@_dir/Ray $@
	rm -rf $@_dir/

data: huge_b.impatiens large_h.sapiens small_r.sphaeroides tiny_s.aureus 

ray.tar.gz:
	git clone https://github.com/sebhtml/ray.git
	rm ray/RayPlatform
	cd ray && git clone https://github.com/sebhtml/RayPlatform.git
	cd ray && tar -czf ../$@ *
	rm -rf ray

Ray-$(I_MPI_CC)-native: ray.tar.gz
	mkdir $@_dir && tar -xzf $^ -C $@_dir
	cd $@_dir && $(MAKE) AR=$(AR) CXXFLAGS="$(CXF) $(EFN)" $(VAR) $(MT)
	strip $@_dir/Ray
	mv $@_dir/Ray $@
	rm -rf $@_dir/

Ray-$(I_MPI_CC)-avx2: ray.tar.gz
	mkdir $@_dir && tar -xzf $^ -C $@_dir
	cd $@_dir && $(MAKE) AR=$(AR) CXXFLAGS="$(CXF) $(EFA2)" $(VAR) $(MT)
	strip $@_dir/Ray
	mv $@_dir/Ray $@
	rm -rf $@_dir/

Ray-$(I_MPI_CC)-avx2-novec-nosimd: ray.tar.gz
	mkdir $@_dir && tar -xzf $^ -C $@_dir
	cd $@_dir && $(MAKE) AR=$(AR) CXXFLAGS="$(CXF) $(EFA2NV)" $(VAR) $(MT)
	strip $@_dir/Ray
	mv $@_dir/Ray $@
	rm -rf $@_dir/

Ray-$(I_MPI_CC)-common-avx512: ray.tar.gz
	mkdir $@_dir && tar -xzf $^ -C $@_dir
	cd $@_dir && $(MAKE) AR=$(AR) CXXFLAGS="$(CXF) $(EFA5)" $(VAR) $(MT)
	strip $@_dir/Ray
	mv $@_dir/Ray $@
	rm -rf $@_dir/

TINY = http://gage.cbcb.umd.edu/data/Staphylococcus_aureus/Data.original/
SMALL = http://gage.cbcb.umd.edu/data/Rhodobacter_sphaeroides/Data.original/
LARGE = http://gage.cbcb.umd.edu/data/Hg_chr14/Data.original/
HUGE = http://gage.cbcb.umd.edu/data/Bombus_impatiens/Data.original/

tiny_s.aureus:
	mkdir $@ && cd $@ && \
	for url in `wget --no-cache --spider -r -nd -np $(TINY) 2>&1 | grep "^--" | awk '{ print $$3 }' | grep "gz$$"`; do \
		prefix=$$(basename $$url) && prefix=$${prefix%%.fastq.gz}_ && \
		curl -s $$url | zcat - | split -l 1000000 - $$prefix & \
	done && wait
	cd $@ && for f in *_[12]_??; do \
		mv $${f} $${f}.fastq; \
	done
	cd $@ && for f in *_1_??.fastq; do \
        	echo -e "-p\n\t$${PWD}/$${f}\n\t$${PWD}/$${f%_1_*}_2_$${f##*_1_}"; \
	done > Ray.conf

small_r.sphaeroides:
	mkdir $@ && cd $@ && \
	for url in `wget --no-cache --spider -r -nd -np $(SMALL) 2>&1 | grep "^--" | awk '{ print $$3 }' | grep "gz$$"`; do \
		prefix=$$(basename $$url) && prefix=$${prefix%%.fastq.gz}_ && \
		curl -s $$url | zcat - | split -l 1000000 - $$prefix & \
	done && wait
	cd $@ && for f in *_[12]_??; do \
		mv $${f} $${f}.fastq; \
	done
	cd $@ && for f in *_1_??.fastq; do \
        	echo -e "-p\n\t$${PWD}/$${f}\n\t$${PWD}/$${f%_1_*}_2_$${f##*_1_}"; \
	done > Ray.conf

large_h.sapiens:
	mkdir $@ && cd $@ && \
	for url in `wget --no-cache --spider -r -nd -np $(LARGE) 2>&1 | grep "^--" | awk '{ print $$3 }' | grep "gz$$"`; do \
		prefix=$$(basename $$url) && prefix=$${prefix%%.fastq.gz}_ && \
		curl -s $$url | zcat - | split -l 4000000 - $$prefix & \
	done && wait
	cd $@ && for f in *_[12]_??; do \
		mv $${f} $${f}.fastq; \
	done
	cd $@ && for f in *_1_??.fastq; do \
        	echo -e "-p\n\t$${PWD}/$${f}\n\t$${PWD}/$${f%_1_*}_2_$${f##*_1_}"; \
	done > Ray.conf

huge_b.impatiens:
	mkdir $@ && cd $@ && \
	for url in `wget --no-cache --spider -r -nd -np $(HUGE) 2>&1 | grep "^--" | awk '{ print $$3 }' | grep "gz$$"`; do \
		prefix=$$(basename $$url) && prefix=$${prefix%%.fastq.gz}_ && prefix=$${prefix%%sequence.txt.gz*} && \
		curl -s $$url | zcat - | split -l 10000000 - $$prefix & \
	done && wait
	cd $@ && for f in *_[12]_??; do \
		mv $${f} $${f}.fastq; \
	done
	cd $@ && for f in *_1_??.fastq; do \
        	echo -e "-p\n\t$${PWD}/$${f}\n\t$${PWD}/$${f%_1_*}_2_$${f##*_1_}"; \
	done > Ray.conf

clean:
	@rm -rf ray.tar.gz Ray-*-* huge_b.impatiens large_h.sapiens small_r.sphaeroides tiny_s.aureus
