$(document).ready(function () {
    var _data = [];
    var _labels = [];
    var full_data = [];
    var getdata = $.ajax({
        url: "/get_pie_chart_data",
        dataType: "json",
        type: "GET",
        data: {vals: ''},
        dataSrc: "payload",
        contentType: "application/json",


        success: function (response) {
            full_data = response.payload;
            _data = full_data['data'];
            _labels = full_data['labels'];

            var color_list = [];

            var dynamicColors = function (i, total) {
                var b = 150 + i * 155 / total;
                var g = i * 255 / total + 20;
                var r = i * 255 / total - 20;
                return "rgb(" + r + "," + g + "," + b + ")";
            };
            for (let i in _data) {
                color_list.push(dynamicColors(i, _data.length));
            }

            var pieChart = new Chart(document.getElementById("pieChart"), {
                type: 'pie',
                data: {
                    labels: full_data.labels,
                    datasets: [
                        {
                            label: "Number of reclamation",
                            backgroundColor: color_list,
                            data: full_data.data,

                        }
                    ]
                },
                options: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Number of parts models reclamation in the last month'
                    }
                }
            });
        },
    });
});


