const start_input = d3.select("#start")
const end_input = d3.select("#end")
const button = d3.select("#filter-btn")

const get_data = function() {
    let start = d3.select("#start").property("value")
    let end = d3.select("#end").property("value")
    
    let data_route = "get_data?"
    
    if (start) {data_route += "start=" + start}
    if (end) {data_route += "&end=" + end}

    window.location.href = data_route
}

button.on("click", get_data)

window.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        get_data()
    }
})
