$(document).ready(function () {
    var r_data = [];
    var r_labels = [];
    var r_full_data = [];
    var getdata = $.ajax({
        url: "/get_reclamations_chart_data",
        dataType: "json",
        type: "GET",
        data: {vals: ''},
        dataSrc: "payload",
        contentType: "application/json",


        success: function (response) {
            r_full_data = response.payload;
            r_data = r_full_data['data'];
            r_labels = r_full_data['labels'];
            // var updatedData = {
            //     labels: r_full_data.labels,
            //     datasets: [
            //         {
            //             label: "Population (millions)",
            //             backgroundColor: ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850"],
            //             data: full_data.data
            //         }
            //     ]
            // };
            // reclChart.data = updatedData;
            // reclChart.update();

            var reclChart = new Chart(document.getElementById("reclamationChart"), {
                type: 'bar',
                data: {
                    labels: r_full_data.labels,
                    datasets: [
                        {
                            label: "Reclamations in month",
                            backgroundColor: "#0275d8",
                            data: r_full_data.data
                        }
                    ]
                },
                options: {
                    legend: {display: false},
                    title: {
                        display: true,
                        text: 'Number of new reclamations in the last 6 months '
                    }
                }
            });
        },
    });
});


