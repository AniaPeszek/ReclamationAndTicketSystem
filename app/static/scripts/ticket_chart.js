$(document).ready(function () {
    var _data = [];
    var _labels = [];
    var full_data = [];
    var getdata = $.ajax({
        url: "/get_tickets_chart_data",
        dataType: "json",
        type: "GET",
        data: {vals: ''},
        dataSrc: "payload",
        contentType: "application/json",


        success: function (response) {
            full_data = response.payload;
            _data = full_data['data'];
            _labels = full_data['labels'];

            var myChart = new Chart(document.getElementById("ticketChart"), {
                type: 'line',
                data: {
                    labels: full_data.labels,
                    datasets: [
                        {
                            label: "Number of tasks in month",
                            backgroundColor: '#0275d8',
                            data: full_data.data,

                            fill: true,
                            lineTension: 0.1,
                            borderColor: '#0275d8',
                            borderCapStyle: 'butt',
                            borderDash: [],
                            borderDashOffset: 0.0,
                            borderJoinStyle: 'miter',
                            pointBorderColor: "#0275d8",
                            pointBackgroundColor: "#fff",
                            pointBorderWidth: 1,
                            pointHoverRadius: 5,
                            pointHoverBackgroundColor: "rgba(75,192,192,1)",
                            pointHoverBorderColor: "rgba(220,220,220,1)",
                            pointHoverBorderWidth: 2,
                            pointRadius: 1,
                            pointHitRadius: 10,
                            spanGaps: false

                        }
                    ]
                },
                options: {
                    legend: {
                        display: false
                    }
                    ,
                    title: {
                        display: true,
                        text: 'Number of my tasks in the last 6 months '
                    },
                    scales:{
                        yAxes: [{
                            ticks:{
                                beginAtZero: true
                            }
                        }]
                    }
                }
            });
        },
    });
});


