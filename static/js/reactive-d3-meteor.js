$(function () {
  
  var svg, width = 500, height = 75, x,
    data = [5, 8, 11, 14, 17, 20];

  svg = d3.selectAll('.vis').append('svg')
    .attr('width', width)
    .attr('height', height);

  x = d3.scale.ordinal()
    .domain(d3.range(data.length))
    .rangePoints([0, width], 1);

  drawCircles(false);

  setInterval(function () {
    d3.shuffle(data);
    drawCircles(true);
  }, 2000);

  function drawCircles(update) {
    var circles = svg.selectAll('circle').data(data);
    if (!update) {
      circles = circles.enter().append('circle')
        .attr('cx', function (d, i) { return x(i); })
        .attr('cy', height / 2)
        .attr('fill', '#663399');
    } else {
      circles = circles.transition().duration(1000);
    }
    circles.attr('r', function (d) { return d; });
  }
});
