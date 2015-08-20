---
post_title:     Interactive visualization of insertion sort
post_author:    Markus Hsi-Yang Fritz
post_date:      2014-09-22 22:01
post_tags:      [D3.js, JavaScript, Visualization, Algorithm]
post_slug:      interactive-insertion-sort
post_summary:   In this post we'll take a look at an interactive, animated D3.js visualization of the insertion sort algorithm.
is_public:      true
---

Interactive visualization of insertion sort
===========================================

When it comes to visualizing algorithms, sorting is probably
the class of algorithms people have thought about the most.
The [Wikipedia page of insertion sort](http://en.wikipedia.org/wiki/Insertion_sort), 
for example, includes three different visualizations
at the time of writing: a
[static vis](http://en.wikipedia.org/wiki/File:Insertionsort-edited.png) 
and two animated GIFs, using
[boxes](http://en.wikipedia.org/wiki/File:Insertion-sort-example-300px.gif)
and [bars](http://en.wikipedia.org/wiki/File:Insertion_sort.gif).

In general, I think that none of these are perfect
and that they complement each other, at least to some degree.
A static vis, for example, can be helpful to illustrate higher level
features of an algorithm. For insertion sort one such feature
is that as the algorithm progresses sequentially
through the array, the subarray to the left of the active element is guaranteed to be sorted.
Animations, on the other hand, are arguably more fun and engaging
and as the algorithm unfolds in front of one's eyes in real-time,
it can aid
understanding the individual, low level steps and thus make
implementing the algorithm easier. 

Due to the nature of insertion sort (sequential, in-place swap operations),
I think an animated bar chart is actually quite appropriate. However,
I have several issues with the Wikipedia animation, in particular:

* there are too many elements being displayed (30 at the time of writing)
* the animation is too quick
* it is not obvious which element is the active one

Additionally, from an educational perspective, it would be
great to make the visualization customizable.
What I mean by this is the possibility to set
up a specific starting constellation.
One particularly useful aspect of this is the
exploration of common and
[edge cases](http://en.wikipedia.org/wiki/Edge_case).
For sorting algorithms an important common real world case to consider
is a pre-sorted array. For insertion sort, a pre-sorted array
leads to best case execution time and a reverse sorted
array to worst case behavior.

Coming back to Wikipedia's animation, of course 
there is a technical limitation due to the GIFs being used.
It would actually be pretty amazing if one could include small, embedded,
interactive JavaScript applications on Wikipedia pages.
I do hope that this will be possible in the near future.

Anyhow, so I thought that an interactive, customizable
app would be neat that would mitigate the issues outlined above. 
In addition, this would also allow parameterizing
the speed of the animation which is quite important as well.
Below is such an app I put together with the help of
[D3.js](http://d3js.org/).
The only non-obvious thing to point out is that you can
drag the bars around, arranging them as you see fit. Have fun!

<div class="vis"></div>

There certainly is room for improvement. I'll probably
add some sort of indicator of the loop variables to bring
out the aspect of the double nested `for` loop better.
It would actually be awesome to show the pseudo code as well
and to visually highlight the lines that are being executed.

Also, I'll probably
extend this post soon or write a separate, follow-up post explaining the 
D3.js implementation. For the time being though, let's leave things
at this and if you're interested, grab the code in its current form from
[github](https://github.com/mhyfritz/interactive-insertion-sort). TTFN!

<script src="http://code.jquery.com/jquery-1.11.0.min.js"></script>
<script src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script>
<script src="insertion-sort-d3.js"></script>
