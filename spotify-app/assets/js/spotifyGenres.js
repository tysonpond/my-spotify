d3.json(spotifyGenresDataPath, function(data){

	d3.select("#spotify-genres")
		.selectAll("div")
		.data(data["genres"])
		.enter()
		.append("div")
		.text(d => d)
		.style("margin", "3px 5px")
		.style("padding", "4px 10px")
		.style("border", "3px solid #333333")
		.style("border-radius", "2% 6% 5% 4% / 1% 1% 2% 4%")
   	 	.style("text-transform", "uppercase")
    	.style("letter-spacing", "0.3ch")
});

function updateGenres(selection){
	d3.json(spotifyGenresDataPath, function(data){
		d3.select("#spotify-genres")
			.selectAll("div")
			.data(data[selection])
			.text(d => d)
	});
}

$("input[type=radio][name=top-choice]").change(function(){
	updateGenres(this.value);
});