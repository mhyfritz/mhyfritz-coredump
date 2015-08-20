---
post_title:     A line delimited JSON format for genomic data
post_author:    Markus Hsi-Yang Fritz
post_date:      2014-10-02 18:40
post_tags:      [Genomics, Science]
post_slug:      genomic-ldjson
post_summary:   A proposal for a small, flexible JSON format for positional genome data and some ideas about a tool ecosystem around it. 
is_public:      false
---

A line delimited JSON format for genomic data
=============================================

Genomic data formats are a mess.
Idiosyncratic flat files that need custom tooling and are a pain
to parse.
As a result a lot of my time gets wasted writing
dedicated parsers, reading specs to figure out what data types
are encoded, converting format *X* to format *Y*.

To give file formats some common denominator and make
them easy to slice and dice on the command line, many
programs spit out tab delimited data.
The problem I have with these files though is that, at the same time,
they are too strict and too loose: too strict as they force a
common, pre-defined layout of records, too loose as they
don't provide a standardized way to encode data types.

* data types
* "schema-free" (records can be heterogenous)
* line-base (command-line friendly)

As a web dev hobbyist, I have used the JSON format
for quite some time and I really love it.
It's both lightweight and flexible, and as
an incredidbly popular format there already exists
a huge tooling ecosystem around it.
We want "atomic" records that we stream
and manipulate, e.g. via pipes on a
command line. This is were line-delimited
JSON (LDJSON) comes in: we simply encode
every record as one independent JSON object
per line. 

Another important consideration is indexing. Genomic data
often comes in positional form and we want to
facilitate random access into them.
The good news for TSV files is that a neat, generic
indexer exist: `tabix`. You tell `tabix` which column
numbers hold the chromosome, start and end and
it will build an index of your file.

The index itself, however, doesn't care of the actual
layout of the file, it essentially holds offsets to lines.
So by swapping the TSV parser by a JSON parser, we should
be able to use the `tabix` index for `GOON`.
Chromosome and position key.

So our full `GOON` specification boils down to this:

* line-delimited JSON
* every line encodes one datum of type *Object* with following mandatory keys/values:
    * a sequence name key and an associated string value
    * one or two position keys (start/end) with assocaiated integer values

Simple. Here are few examples of records that fulfill the spec:

~~~
{"chrom": "chr1", "start": 1, "end": 10, "id": "foo"}

{"name": "chr1", "pos": 20, "scores": [5,2,7]}
~~~


* tabix
* compression ratio ens/enc; index time tabix/goon
* I am addicted to the *nix shells and tools --> jq
* goonsort
* mongodb

![my caption](/home/mhyf/code/c/gnx/test/real-world/goon.rel.file.size.png)

Thanks to Joachim Weischenfeldt and Tobias Rausch for initiating
a discussion about variant call file formats which ultimately
lead me to think about all of the above.

OK, test data. Let's head to https://genome.ucsc.edu/ and grab some
via the *Table Browser*. We'll use the *hg19 GENCODE Genes V19*
and *hg19 ENCODE TFBS V3* data sets and save them to `gzip` compressed
files `hg19.ucsc.gencode.v19.txt.gz` and `hg19.ucsc.encode.tfbs.v3.txt.gz`
respectively. With a little helper script, we can convert the
tab-delimited files to LDJSON. One thing to note is that we
need to look at the table schema what datatypes are used where.
Technically one could think of automating this, but the problem
are list columns which have SQL type *longblob* and can
contain integers, floats, strings...

~~~bash
ucsc_to_ldj.py --file hg19.ucsc.gencode.v19.txt.gz \
               --intcols bin txStart txEnd cdsStart cdsEnd \
                         exonCount score \
               --intlistcols exonStarts exonEnds exonFrames \
    | gzip \
    > hg19.ucsc.gencode.v19.ldj.gz

ucsc_to_ldj.py --file hg19.ucsc.encode.tfbs.v3.txt.gz \
               --intcols bin chromStart chromEnd score expCount \
               --intlistcols expNums expScores \
    | gzip \
    > hg19.ucsc.encode.tfbs.v3.ldj.gz
~~~

For indexing, we need to sort the files. We could have sorted the
table files first, but obviously we need also a way to sort *GOON*
files directly. 

~~~bash
zcat hg19.ucsc.gencode.v19.ldj.gz \
    | goontools sort -s chrom -b txStart \
    | bgzip \
    > hg19.ucsc.gencode.v19.srt.ldj.gz

zcat hg19.ucsc.encode.tfbs.v3.ldj.gz \
    | goontools sort -s chrom -b chromStart \
    | bgzip \
    > hg19.ucsc.encode.tfbs.v3.srt.ldj.gz
~~~

Before continuing with the `GOON` files, let's also prep
the table files for `tabix` so we can compare file sizes
and execution times. Analogously, we sort and bgzip.

~~~bash
zcat hg19.ucsc.gencode.v19.txt.gz | head -1 > hg19.ucsc.gencode.v19.srt.txt
zcat hg19.ucsc.gencode.v19.txt.gz \
    | sed 1d | sort -s -k3,3 -k5,5n \
    >> hg19.ucsc.gencode.v19.srt.txt
bgzip hg19.ucsc.gencode.v19.srt.txt

zcat hg19.ucsc.encode.tfbs.v3.txt.gz | head -1 > hg19.ucsc.encode.tfbs.v3.srt.txt
zcat hg19.ucsc.encode.tfbs.v3.txt.gz \
    | sed 1d | sort -s -k2,2 -k3,3n \
    >> hg19.ucsc.encode.tfbs.v3.srt.txt
bgzip hg19.ucsc.encode.tfbs.v3.srt.txt
~~~

Now that we have sorted, bgzip compressed files,
we can index those. 

~~~bash
tabix -s 3 -b 5 -e 6 -0 hg19.ucsc.gencode.v19.srt.txt.gz
tabix -s 2 -b 3 -e 4 -0 hg19.ucsc.encode.tfbs.v3.srt.txt.gz

goontools index -s chrom -b txStart -0 -r hg19.ucsc.gencode.v19.srt.ldj.gz
goontools index -s chrom -b chromStart -e chromEnd -0 -r hg19.ucsc.encode.tfbs.v3.srt.ldj.gz
~~~

~~~bash
# for retrival, tabix uses 1-based, closed coordinates
tabix hg19.ucsc.gencode.v19.srt.txt.gz chr1:11869-11869

goontools view hg19.ucsc.gencode.v19.srt.ldj.gz chr1:11868-11869
goontools view -1 -c hg19.ucsc.gencode.v19.srt.ldj.gz chr1:11869-11869
~~~


As mentioned before, JSON is a bloated format as every record stores all
key names. Compression obviously helps here, and as shown in the figure below,
the increase in file sizes isn't too bad.


