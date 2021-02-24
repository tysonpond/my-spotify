
function getRecentSunday(date, sunday=1) {
  // Get most recent sunday. If 'date' is a Sunday, then this returns back 'date'.
  // to get the most recent Monday, set sunday=1
  // to get the most recent Tuesday, set sunday=2 ...
  var t = new Date(date); // note, setDate will *modify* dt unless we make a copy 
  var day = (t.getDay()+(7-sunday)) % 7,
      diff = t.getDate() - day;
  return new Date(t.setDate(diff));
}

function formatY(d){
      var day = d.date.getDay();
      return ["Mon", "Tu", "Wed", "Th", "Fri", "Sat","Sun"][(day + 6) % 7];
}

//Read the data
d3.csv(spotifyHeatmapDataPath,
  
  function(d){
    d.date = d3.timeParse("%Y-%m-%d")(d.date);
    d.plays = parseFloat(d.plays);
    return d
  },

  function(data) {

    // set the dimensions and margins of the graph
    var margin = {top: 20, right: 70, bottom: 20, left: 70},
    width = Math.min(500, window.innerWidth - 10) - margin.left - margin.right,
    height = Math.min(200, window.innerHeight - margin.top - margin.bottom - 20),
    squareSize = 24;

    // append the svg object to the body of the page
    var svg = d3.select("#spotify-heatmap")
      .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("id","plot")
        .attr("transform",
              "translate(" + margin.left + "," + margin.top + ")");

    // x-axis (scale and axis)

    // Using scalePoint -- the code below gives us the appropriate domain
    // get all unique x values from data into a list and then sort
    var uniqueX = data.map(d => getRecentSunday(d.date).getTime()); // first get recent sunday and convert to timestamp so they can be compared in next line
    uniqueX = uniqueX.filter((x, i, a) => a.indexOf(x) === i); // get unique timestamps
    uniqueX = uniqueX.sort(); // sort in ascending order
    uniqueX = uniqueX.map(d => new Date(d)); // convert timestamps back to dates

    var x = d3.scalePoint()
      .domain(uniqueX)
      .range([ 0, width ]);
    svg.append("g")
      .attr("id","xAxis")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x)
      	      .tickFormat(d3.timeFormat("%b %-d"))
      	      .ticks(2)
      	      .tickSizeOuter(0));

    // y-axis (scale and axis)
    var y = d3.scalePoint()
    .domain(["Mon", "Tu", "Wed", "Th", "Fri", "Sat","Sun", ""])
    .range([0,height]); 
    svg.append("g")
      .attr("id","yAxis")
      .attr("transform", "translate(" + (-squareSize) + ", 0)") // this prevents first column from overlapping with y-axis
      .call(d3.axisLeft(y));

    // color scale
    var colorFn = d3.scaleSequential(d3.interpolateBuGn)
      .domain(d3.extent(data, d => d.plays));

    // add rectangles
    svg.selectAll("rect")
      .data(data)
      .enter()
      .append("rect")
      .attr("class", "data")
      .attr("index", function(d,i) {return i;})
      .attr("x", d => x(getRecentSunday(d.date)) - squareSize/2)
      .attr("y", d => y(formatY(d)) - squareSize/2)
      .attr("rx",4)
      .attr("ry",4)
      .attr("height", squareSize)
      .attr("width", squareSize)
      .style("fill", d => colorFn(d.plays))
      .style("pointer-events", "none");

  var tooltip = svg.append("text")
    .attr("class", "tooltip")
    .style("opacity", 0)
    .style("pointer-events", "none");

  svg.selectAll("rect").each(function(d,i){
    rect = d3.select(this);
    svg.insert('rect', ':first-child')
       .attr("class","overlay")
       .attr("index",i)
       .attr("x", rect.attr("x")-2)
       .attr("y", rect.attr("y")-2)
       .attr("rx",4)
       .attr("ry",4)
       .attr("height", parseFloat(rect.attr("height"))+4)
       .attr("width", parseFloat(rect.attr("width"))+4)
       .style("fill","black")
       .style("opacity",0)
       .on("mouseover", function(){
          overlay = d3.select(this);
          overlay.style("opacity",1);
          newX =  parseFloat(overlay.attr('x'));
          newY =  parseFloat(overlay.attr('y'));
          newX = Math.min(width - squareSize - 60, newX);
          newY = Math.max(squareSize/2, newY); // make sure tooltip doesn't go above the plot

          tooltip
            .attr('x', newX)
            .attr('y', newY)
            .text('plays' + ": " + (d.plays).toFixed(0))
            .style("fill", "#007bff")
            .style("font-size", 0.75*squareSize + "px")
            .style('opacity', 1);
        })
       .on("mouseout", function(){
          d3.select(this).style("opacity",0);
          tooltip.style("opacity", 0);
        });
  });

  function updatePlot(selectedValue) {
    colorFn = d3.scaleSequential(d3.interpolateBuGn)
      .domain([0,100]);
    // could also use .domain(d3.extent(data, d => d[selectedValue]));
    // but I think it's better if the scale is constant

    // tooltip: need special formatting for null values
    function textFormat(data, i, selectedValue){
      var selectedData = data[i][selectedValue];
      if (selectedValue == "plays"){
        return "plays: " +  parseFloat(selectedData).toFixed(0);
      } else {
        return selectedValue + ": " + (selectedData !== "" ? parseFloat(selectedData).toFixed(2) : "NA");
      }
    }

    svg.selectAll(".data")
       .transition().duration(500)
       .style("fill", d => colorFn(d[selectedValue]))
       .each(function(){
          var i = d3.select(this).attr("index");
          var overlay = d3.select(".overlay[index='" + i + "']");
          overlay.on("mouseover", function(){
          overlay.style("opacity",1);
          newX =  parseFloat(overlay.attr('x'));
          newY =  parseFloat(overlay.attr('y'));
          newX = Math.min(width - squareSize - 60, newX);
          newY = Math.max(squareSize/2, newY); // make sure tooltip doesn't go above the plot

          tooltip
            .attr('x', newX)
            .attr('y', newY)
            .text(textFormat(data, i, selectedValue))
            .style("fill", "#007bff")
            .style("font-size", 0.75*squareSize + "px")
            .style('opacity', 1);
        })
       .on("mouseout", function(){
          overlay.style("opacity",0);
          tooltip.style("opacity", 0);
        });
  });
  }
  $(".legend").click(function(){
    updatePlot($(this).text());
  });
  $(".reset").click(function(){
    updatePlot("plays");
  })
});