var getColorArray = function(data) {
	col_array = [];
	for (var i=0; i<data.length; i++) {
		col = '#D50000';
		if(data[i].value >= 0){
			col = '#1B5E20';
		}
		col_array.push(col);
	}
	console.log(col_array);
	return col_array;
}

var clearChart = function() {
	svg = d3.select('#chart svg');
	svg.selectAll("*").remove();
}

var BarChart = function() {
	nv.addGraph(function() {
	  var chart = nv.models.discreteBarChart()
	    .x(function(d) { return d.label })
	    .y(function(d) { return d.value })
	    .staggerLabels(true)
	    .showValues(true)
	    .color(getColorArray(chartData[0]['values']))
	    chart.tooltip.enabled(true);
	  d3.select('#chart svg')
	    .datum(chartData)
	    .transition().duration(500)
	    .call(chart)
	    ;

	  nv.utils.windowResize(chart.update);

	  return chart;
	});
};


var LineChart = function() {
	nv.addGraph(function() {
	  var chart = nv.models.lineChart()
	    .useInteractiveGuideline(true);

	  chart.xAxis
	    .axisLabel('Time (ms)')
	    .tickFormat(d3.format(',r'));

	  chart.yAxis
	    .axisLabel('Voltage (v)')
	    .tickFormat(d3.format('.02f'));

	  d3.select('#chart svg')
	    .datum(lineData)
	    .transition().duration(500)
	    .call(chart);

	  nv.utils.windowResize(chart.update);

	  return chart;
	});
};

$(function() {
	refreshChartData();
	$("#btnLoadChart").click(function(){
		console.log("Loading the graph.");	
		BarChart();
	});
	$("#btnClearChart").click(function(){
		console.log("Clearing the graph.");	
		clearChart();
		$('.heading123').empty();
		$('.heading123').append('NDV3 heading');
	});
		$("#refreshChartData").click(function(){
		console.log("Refreshing the graph data.");	
		refreshChartData();
	});
});
$('#charts').change(function(){
  
    if ($(this).val() == 'Bar') {
    	refreshChartData();
    	clearChart();
    	BarChart();
    }
    else {
    	if ($(this).val() == 'Line')
    		clearChart();
    		LineChart();
    }

});