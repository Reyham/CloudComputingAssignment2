
j = JSON.parse(document.getElementById("data").innerHTML)
data = j["data"];
question = j["question"];


switch(question) {
  case "1":
    xoff = 0.45
    yoff = 5
    xlabel = "Gini coefficient"
    ylabel = "Number of COVID-19 Tweets"
    break;
  case "2":
    xoff = 0
    yoff = 0
    xlabel = "2019 Coaltion Two-Party Preferred Support"
    ylabel = "Mean Neighbourhood Tweet Sentiment"
    break;
  case "3":
    xoff = 0
    yoff = 5
    xlabel = "Percentage of polled residents with low trust"
    ylabel = "Number of COVID-19 Tweets"
    break;
  case "4":
    xoff = 0
    yoff = 5
    xlabel = "Migration rate"
    ylabel = "Number of Non-english tweets"
    break;
  default:
    xoff = 10
    yoff = 10
    xlabel = ""
    ylabel = ""
}
if (question == "2") {
  minydom = -1
} else {
  minydom = 0
}

/*
 * Code based on
 * https://www.d3-graph-gallery.com/graph/interactivity_zoom.html
 * https://www.d3-graph-gallery.com/graph/scatter_basic.html
 * An interactive D3js map
 *
 * Axis labels: https://stackoverflow.com/questions/11189284/d3-axis-labeling
 */


// set the dimensions and margins of the graph
var margin = {top: 10, right: 30, bottom: 30, left: 60},
    width = 460 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select("#graph")
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");


  // Add X axis
  var x = d3.scaleLinear()
    .domain([0, d3.max(data, function (d) { return d.x + xoff})])
    .range([0, width]);

  var xAxis = svg.append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x));

  // Add Y axis
  var y = d3.scaleLinear()
    .domain([minydom, d3.max(data, function (d) { return d.y + yoff; })])
    .range([height, 0]);

  var yAxis = svg.append("g")
    .call(d3.axisLeft(y));

  // X and Y axis labels
  svg.append("text")
    .attr("transform",
          "translate(" + (width/2) + " ," +
                         (height + margin.top + 20) + ")")
    .style("text-anchor", "middle")
    .text(xlabel);

  svg.append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", 0 - margin.left)
    .attr("x",0 - (height / 2))
    .attr("dy", "1em")
    .style("text-anchor", "middle")
    .text(ylabel);

  // clip path for zoom
  var clip = svg.append("defs").append("SVG:clipPath")
    .attr("id", "clip")
    .append("SVG:rect")
    .attr("width", width )
    .attr("height", height )
    .attr("x", 0)
    .attr("y", 0);

  var scatter = svg.append('g')
  .attr("clip-path", "url(#clip)")

  // Add dots
  scatter
    .selectAll("dot")
    .data(data)
    .enter()
    .append("circle")
      .attr("cx", function (d) { return x(d.x); } )
      .attr("cy", function (d) {return y(d.y); } )
      .attr("r", 4.5)
      .style("fill", "#69b3a2")

  var zoom = d3.zoom()
    .scaleExtent([.5, 20])  // This control how much you can unzoom (x0.5) and zoom (x20)
    .extent([[0, 0], [width, height]])
    .on("zoom", updateChart);

    // This add an invisible rect on top of the chart area. This rect can recover pointer events: necessary to understand when the user zoom
   svg.append("rect")
       .attr("width", width)
       .attr("height", height)
       .style("fill", "none")
       .style("pointer-events", "all")
       .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
       .call(zoom);
   // now the user can zoom and it will trigger the function called updateChart

function updateChart() {

// recover the new scale
var newX = d3.event.transform.rescaleX(x);
var newY = d3.event.transform.rescaleY(y);

// update axes with these new boundaries
xAxis.call(d3.axisBottom(newX))
yAxis.call(d3.axisLeft(newY))

// update circle position
scatter
 .selectAll("circle")
 .attr('cx', function(d) {return newX(d.x)})
 .attr('cy', function(d) {return newY(d.y)});
}
