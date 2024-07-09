// $(document).ready(function(){
//     function drawGraph(url) {
//         $.getJSON(url, function(data){
//             var graphDiv = document.getElementById('graph');
//             Plotly.newPlot(graphDiv, JSON.parse(data).data, JSON.parse(data).layout);

//             graphDiv.on('plotly_click', function(data){
//                 var point = data.points[0];
//                 var category = point.x;

//                 // Show the back button
//                 $('#back-button').show();

//                 // Draw detailed graph
//                 $.getJSON(`/details/${category}`, function(detailData){
//                     Plotly.newPlot(graphDiv, JSON.parse(detailData).data, JSON.parse(detailData).layout);
//                 });
//             });
//         });
//     }

//     // Draw the initial graph
//     drawGraph('/initial');

//     // Handle the back button click
//     $('#back-button').on('click', function() {
//         // Draw the initial graph again
//         drawGraph('/initial');
//         // Hide the back button
//         $(this).hide();
//     });
// });
