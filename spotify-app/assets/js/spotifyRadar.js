/* Radar chart design created by Nadieh Bremer - VisualCinnamon.com */

d3.json(spotifyRadarDataPath, function(data){
	////////////////////////////////////////////////////////////// 
	//////////////////////// Set-Up ////////////////////////////// 
	////////////////////////////////////////////////////////////// 

	// var margin = {top: 40, right: 100, bottom: 40, left: 100};
	// var width = window.innerWidth;
	// width = width > 992 ? width*0.833*0.45 : width*0.85;
	// var height = Math.min(width, window.innerHeight/2);
	// width = width - margin.left - margin.right;
	// height = height - margin.top - margin.bottom;
	
	var margin = {top: 100, right: 100, bottom: 100, left: 100},
		width = Math.min(500, window.innerWidth - 10) - margin.left - margin.right,
		height = Math.min(width, window.innerHeight - margin.top - margin.bottom - 20);

	var color = d3.scaleOrdinal().range(["#41ae76", "#006d2c"]);

	var radarChartOptions = {
	  w: width,
	  h: height,
	  margin: margin,
	  maxValue: 100,
	  levels: 5,
	  roundStrokes: true,
	  color: color,
	  tooltipTextColor: "#007bff",
	  legendBackgroundColor: "#FEFFC3"
	};

	////////////////////////////////////////////////////////////// 
	//////////////////// Draw the Chart ////////////////////////// 
	////////////////////////////////////////////////////////////// 

	// The usage of '[data]' is because radarChart.js expects multiple radar chart
	// groups. Since we're only plotting 1 we need to wrap it in a list.
	RadarChart("#spotify-radar", [data], radarChartOptions);	
});