---
author: Markus Hsi-Yang Fritz
title: Reactive data visualization with D3.js and Meteor
slug: reactive-d3-meteor
date: 2014-08-16T11:34:00+01:00
summary: A tutorial in which we'll use the Meteor framework and D3.js library to create a reactive SVG chart that automatically updates when the underlying data changes.
tags: [D3.js, Meteor, JavaScript, Visualization]
draft: false
---

A while back I wrote a web dashboard for my group at work that displays
stats on disk and compute cluster usage. I did not bake in any
kind of automatic update functionality, the browser page refresh 
button was a crucial [UI](http://en.wikipedia.org/wiki/User_interface) 
component. Groundbreaking user experience, I know. 
So when I started playing around with [`Meteor`](https://www.meteor.com/) 
a few weeks ago, one of my first thoughts was reimplementing 
that dashboard and making it
[reactive](http://en.wikipedia.org/wiki/Reactive_programming).

In this post we'll take a look at how one can
combine [`D3.js`](http://d3js.org/) and `Meteor` 
to create a reactive 
[SVG](http://en.wikipedia.org/wiki/Scalable_Vector_Graphics) chart. 
In particular, our server will store a collection of values 
and update them in regular intervals. Wiring together some of `Meteor`'s 
[reactivity components](http://docs.meteor.com/#reactivity)
to `D3.js` calls, those value updates will automatically get reflected
in the SVG chart.

Before diving into the code, let's take a look at the toy chart we'll create.
In a nutshell, a sequence of integers gets visually mapped to SVG circles, the
sequence gets shuffled every few seconds, the chart updates accordingly.

<div class="vis"></div>

So now that you are all pumped up by those pulsating circles, let's step
through the code. Assuming that you have 
[`Meteor` installed](http://docs.meteor.com/#quickstart), 
let's create a new `Meteor` project (BTW, you can also grab the code from
[github](https://github.com/mhyfritz/reactive-d3-meteor)).

```bash
$ meteor create reactive-d3-meteor
$ cd reactive-d3-meteor
$ ls -1
reactive-d3-meteor.css
reactive-d3-meteor.html
reactive-d3-meteor.js
```

As already mentioned, we'll be using `D3.js`. It's an officially supported
third party [package](http://docs.meteor.com/#packages), 
so we can install it as follows:

```bash
$ meteor add d3
```

We'll also be using [`Underscore.js`](http://underscorejs.org/).
At the time of writing (`Meteor` version 0.8.3),
this library is automatically included in all projects. However,
as per official recommendation, we'll still explicitly add it as the
default `Underscore.js` will be removed at some point in the future.

```bash
$ meteor add underscore
```

For starters, let's create a simple HTML file. Open `reactive-d3-meteor.html`
and edit it as follows:

```html
<head>
  <title>reactive-d3-meteor</title>
</head>

<body>
  {{> vis}}
</body>

<template name="vis">
  <div id="circles"></div>
</template>
```

Not much going on here. The only part worth pointing out is the
[`Spacebars`](https://github.com/meteor/meteor/blob/devel/packages/spacebars/README.md)
template called *vis*. This template simply holds an empty `div` with 
`id` *circles*
into which we'll inject an SVG tag later on. That being said, let's check out
`reactive-d3-meteor.js`. I am pasting its entire content below in case you
want to run or read it right away. Otherwise, you might want to skip it for now
and read the explanation of the individual parts that follows.

```javascript
var Circles = new Meteor.Collection('circles');

if (Meteor.isServer) {
  Meteor.startup(function () {
    if (Circles.find().count() === 0) {
      Circles.insert({data: [5, 8, 11, 14, 17, 20]});
    }
  });

  Meteor.setInterval(function () {
    var newData = _.shuffle(Circles.findOne().data);
    Circles.update({}, {data: newData});
  }, 2000);
}

if (Meteor.isClient) {
  Template.vis.rendered = function () {
    var svg, width = 500, height = 75, x;

    svg = d3.select('#circles').append('svg')
      .attr('width', width)
      .attr('height', height);

    var drawCircles = function (update) {
      var data = Circles.findOne().data;
      var circles = svg.selectAll('circle').data(data);
      if (!update) {
        circles = circles.enter().append('circle')
          .attr('cx', function (d, i) { return x(i); })
          .attr('cy', height / 2);
      } else {
        circles = circles.transition().duration(1000);
      }
      circles.attr('r', function (d) { return d; });
    };

    Circles.find().observe({
      added: function () {
        x = d3.scale.ordinal()
          .domain(d3.range(Circles.findOne().data.length))
          .rangePoints([0, width], 1);
        drawCircles(false);
      },
      changed: _.partial(drawCircles, true)
    });
  };
}
```

Before breaking things down, a few words on file structure. 
We only use a single JavaScript file, i.e. we dump 
both the client- and server-side code into one `.js` file. 
This is how `meteor create`
sets things up. For small projects, in particular toy projects
like this one, this is fine. For larger projects though you probably
want to create a *server* and *client* directory,
where everything in *server* runs on the server and the server only
and everything in *client* runs on the client and the client only.
It's important to understand that in the shared file setup,
even though the server-side code does *not run* on the client
it still *gets sent* to it. Keep that in mind when
storing sensitive data. On a related note,  make sure to 
[read up](http://docs.meteor.com/#dataandsecurity)
on the `autopublish` and `insecure` packages which I won't 
get into. I'm digressing. Let's move on.

```javascript
var Circles = new Meteor.Collection('circles');
```

We declare a collection with name *circles* 
and assign it to a variable *Circles*.
This collection will hold the data points for the chart.
Next up, server-side code:

```javascript
if (Meteor.isServer) {
  Meteor.startup(function () {
    if (Circles.find().count() === 0) {
      Circles.insert({data: [5, 8, 11, 14, 17, 20]});
    }
  });

  Meteor.setInterval(function () {
    var newData = _.shuffle(Circles.findOne().data);
    Circles.update({}, {data: newData});
  }, 2000);
}
```

As mentioned, we use a single file for both server- and client-side
code. For this setup, `Meteor` provides the flags
`Meteor.isClient` and `Meteor.isServer` to define what will
run only on the client and only on the server respectively.

The `Meteor.startup` code runs when the server starts.
We check whether the collection is empty and, if so, insert a single
document `{data: [5, 8, 11, 14, 17, 20]}` that holds the values
for the chart.

Finally, we set up a timer: every 2 seconds we randomly
permute the values using `Underscore`'s `shuffle` function
and update the collection. 

On to the client side. Analogous to the server code, we wrap
the client logic in a `Meteor.isClient` block. Also, before
we can interact with the template code, we have to wait
till it's rendered. For this we use `Template.vis.rendered`.

```javascript
if (Meteor.isClient) {
  Template.vis.rendered = function () {
    ...
  };
}
```

We then declare a couple of variables:
`svg` will reference the SVG container,
`width` and `height` define its dimensions and 
`x` is a scale function we'll use for spatially
arranging the circles inside the container.

```javascript
var svg, width = 500, height = 75, x;
```

Next, we inject an SVG element into `<div id="circles">` and set
its dimensions using `D3`.

```javascript
svg = d3.select('#circles').append('svg')
  .attr('width', width)
  .attr('height', height);
```

Let's leave the SVG drawing code for later and skip to the last
bit of code in the file:

```javascript
Circles.find().observe({
  added: function () {
    x = d3.scale.ordinal()
      .domain(d3.range(Circles.findOne().data.length))
      .rangePoints([0, width], 1);
    drawCircles(false);
  },
  changed: _.partial(drawCircles, true)
});
```

This really is the most important part: hooking up
`Meteor`'s reactivity to `D3` calls.
First we get a [cursor](http://en.wikipedia.org/wiki/Database_cursor)
to our collection using `find`. Instead of
using that cursor to fetch documents, we utilize its
[`observe`](http://docs.meteor.com/#observe) method which will 
execute callbacks when the collection changes.
We use the `added` callback to initialize the chart and
`changed` to update it.

For initialization we call `drawCircles` (more on that in a bit)
and set its argument `update` to `false` as we're setting things
up not updating them. Additionally we define `x`, a `D3` scale function.
In particular we're using an 
[ordinal](http://en.wikipedia.org/wiki/Ordinal_scale#Ordinal_scale) 
scale of type 
[`rangePoints`](https://github.com/mbostock/d3/wiki/Ordinal-Scales#ordinal_rangePoints)
which is handy for positioning evenly spaced points, pretty much
what we want to achieve with our chart. The second argument
to `rangePoints` is a padding parameter that prevents the first
and last circle to overflow the SVG container and to be cut in half.

The only thing we need to do when the collection changes
is to call `drawCircles` passing `update=true`. To create
a version of `drawCircles` that has its argument bound to
`true`, we're using `Underscore`'s [`partial`](http://underscorejs.org/#partial)
function.

Let's now take a look at `drawCircles`. 

```javascript
var drawCircles = function (update) {
  var data = Circles.findOne().data;
  var circles = svg.selectAll('circle').data(data);
  if (!update) {
    circles = circles.enter().append('circle')
      .attr('cx', function (d, i) { return x(i); })
      .attr('cy', height / 2);
  } else {
    circles = circles.transition().duration(1000);
  }
  circles.attr('r', function (d) { return d; });
};
```

In a bit more detail. First off, we grab the current sequence
of data points from the collection, select all SVG circles
and bind the data to them. If `drawCircles` is called for the
first time (with `update=false`), this will be an empty
selection and we use `enter` to create the
actual circle elements. In addition we position the circles
horizontally using the `x` scale function and set the height
of the circles' center to half the SVG container height.
If we update the chart (`update=true`), 
we instead create a transition to create a nice visual resize effect. 
In both cases we set the circles' radius to the
according data point.

Almost done... At this point, the CSS file `reactive-d3-meteor.css` is empty and we 
could very well delete it.  Instead though, let's add a rule to change the 
color of the circles, and let's make that color
[*rebeccapurple*](http://meyerweb.com/eric/thoughts/2014/06/19/rebeccapurple/).

```css
svg circle {
  fill: #663399;
}
```

Done and dusted. Start a `Meteor` server (`$ meteor`),
open a web browser and point it to `localhost:3000`.
In fact, you might want to open multiple browser windows and
see how the chart is synchronized everywhere.
And here's our final chart again in all its glory:

<div class="vis"></div>

Hope you learned a thing or two.
Later.

<script src="http://code.jquery.com/jquery-1.11.0.min.js"></script>
<script src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script>
<script src="/js/reactive-d3-meteor.js"></script>
