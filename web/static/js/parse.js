function parseAnnualData(data){
	graph = Object();
	console.log("graph object created")
	graph.labels = data.members;
	console.log("graph lables set")
	graph.udata = {};
	graph.ticks = []
	graph.labels.forEach(function(label){
		graph.udata[label]=[]
		console.log(graph.udata)
	});
	data.annualdata.forEach(function(data, index){
		data.userdata.forEach(function(userdata){
			graph.udata[userdata["name"]][index]=userdata["liststat"]
		});
		graph.ticks.push(data.year)
	});
	graph.plotdata = []
	graph.labels.forEach(function(label){
		graph.plotdata.push(graph.udata[label])
	});
	return graph;
}

