var tableMaxTextLength = 20;
function truncateText(text, maxLength=20){
   if (text.length > maxLength) {
      return text.substring(0, maxLength) + '...';
   }
   return text;
}

function makeDataTable(data, quality){
	// get data based on quality selected
	var dataSelected = data[quality];

	// i < 5 because we're looking at the top 5 songs
	for (let i = 0; i < 5; i++){
		dataSelected[i][quality] = parseFloat(dataSelected[i][quality]).toFixed(0); // round
	}

	function tabulate(data, columns) {
		var table = d3.select('#spotify-table-container')
					  .append('table')
					  .attr("id", "spotify-table");
		var thead = table.append('thead');
		var	tbody = table.append('tbody');

		// append the header row
		thead.append('tr')
		  .selectAll('th')
		  .data(columns).enter()
		  .append('th')
		    .text(function (column) { return column; });

		// create a row for each object in the data
		var rows = tbody.selectAll('tr')
		  .data(data)
		  .enter()
		  .append('tr')
		  .style('background-color', function(d,i){return i % 2 == 1 ? 'white' : '#F0F0F0'});

		// create a cell in each row for each column
		var cells = rows.selectAll('td')
		  .data(function (row) {
		    return columns.map(function (column) {
		      return {column: column, value: row[column]};
		    });
		  })
		  .enter()
		  .append('td')
		    .text(function (d) { return truncateText(d.value, tableMaxTextLength); })
		    .attr("data-tooltip", function(d){return d.value.length > tableMaxTextLength ? d.value : "";});
	  
	  return table;
	}

	// render the table(s)
	tabulate(dataSelected, ['rank', 'track', 'artist', quality]); // 2 column table

	$('#spotify-table').DataTable({searching: false, paging: false, info: false, ordering: false});
}

function updateDataTable(data, quality){
	// get data based on quality selected
	var dataSelected = data[quality];
	// i < 5 because we're looking at the top 5 songs
	for (let i = 0; i < 5; i++){
		dataSelected[i][quality] = parseFloat(dataSelected[i][quality]).toFixed(0); // round
	}

  var table = d3.select("#spotify-table");
  var thead = table.select("thead");
  var tbody = table.select("tbody");

  var columns = ['rank', 'track', 'artist', quality];

  // Note, the only header we need to update is the last column (quality)
  var lastColumn = $("#spotify-table th:last")[0]
  // color the last header (optional)
  lastColumn.innerHTML = quality;
  if (quality == "plays"){
  	$(lastColumn).css("background-color","#FFFFFF");
  } else {
  	$(lastColumn).css("background-color","#FEFFC3");
  }

  // update the table body
  tbody.selectAll("tr")
  .data(dataSelected)
  .selectAll("td")
  .data(function(row) {
    return columns.map(function(column) {
      return {
        column: column,
        value: row[column]
      };
    });
  })
  .text(function(d) {return truncateText(d.value, tableMaxTextLength);})
  .attr("data-tooltip", function(d){return d.value.length > tableMaxTextLength ? d.value : "";});
}

d3.json(spotifyTableDataPath, function(data){	
	makeDataTable(data,"plays");
	$(".legend").click(function(){
    	updateDataTable(data, $(this).text());
 	});
 	$(".reset").click(function(){
    	updateDataTable(data, "plays");
 	});
});

