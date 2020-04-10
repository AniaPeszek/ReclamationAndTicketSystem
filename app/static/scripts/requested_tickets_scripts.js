var $oTable;

function setupData() {
    $(document).ready(function () {
        // Setup - add a text input to each footer cell
        $('#ticket_table tfoot th').each(function () {
            if ($(this).index() == 0) {
                $(this).html('<input type="text" placeholder="Search" size="2"/>');
            } else {
                $(this).html('<input type="text" placeholder="Search" size="6"/>');
            }
        });

        //DataTable initialization
        $oTable = $('#ticket_table').DataTable({
            "ajax": {
                "url": "/requested_tickets_get_data",
                "dataType": "json",
                "dataSrc": "tickets",
                "contentType": "application/json"
            },
            "columns": [
                {"data": "id"},
                {
                    "data": "creation_date", render: function (data) {
                        return moment(data).format('L')
                    }
                },
                {
                    "data": "due_date", render: function (data) {
                        return moment(data).format('L')
                    }
                },
                {
                    "data": "finished_date", render: function (data) {
                        if (data) {
                            return moment(data).format('L')
                        } else {
                            return ""
                        }
                    }
                },
                {
                    "data": "status", render: function (data) {
                        if (data === 0) {
                            return "open"
                        } else {
                            return "closed"
                        }
                    }
                },
                {"data": "reclamation.reclamation_part_sn_id.part_sn"},
                {"data": "reclamation.reclamation_customer.name"},
                {"data": "reclamation_id"},
                {
                    "data": "ticket_assigned", render: function (data, type, row) {
                        return row.ticket_assigned.first_name + ' ' + row.ticket_assigned.last_name;
                    }
                },
                {
                    "data": "description_ticket", render: function (data, type) {
                        return type === 'display' && data.length > 50 ?
                            '<span title="' + data + '">' + data.substr(0, 49) + '...</span>' :
                            data;
                    }
                },
            ],
            lengthMenu: [
                [10, 25, 50, -1],
                ['10', '25', '50', 'Show all']
            ],
            "responsive": true,

        });

        //multi filter
        $oTable.columns().every(function () {
            var that = this;

            $('input', this.footer()).on('keyup change clear', function () {
                if (that.search() !== this.value) {
                    that
                        .search(this.value)
                        .draw();
                }
            });
        });

        $('.datepicker').datepicker();

        //for create_date
        $("#dateStart").keyup(function () {
            $oTable.draw();
        });
        $("#dateStart").change(function () {
            $oTable.draw();
        });
        $("#dateEnd").keyup(function () {
            $oTable.draw();
        });
        $("#dateEnd").change(function () {
            $oTable.draw();
        });

        //for due_date
        $("#dateStart1").keyup(function () {
            $oTable.draw();
        });
        $("#dateStart1").change(function () {
            $oTable.draw();
        });
        $("#dateEnd1").keyup(function () {
            $oTable.draw();
        });
        $("#dateEnd1").change(function () {
            $oTable.draw();
        });

        //for finished_date
        $("#dateStart2").keyup(function () {
            $oTable.draw();
        });
        $("#dateStart2").change(function () {
            $oTable.draw();
        });
        $("#dateEnd2").keyup(function () {
            $oTable.draw();
        });
        $("#dateEnd2").change(function () {
            $oTable.draw();
        });
    });
}

$(window).on("load", setupData);

//create links to tickets
$(document).ready(function () {
    $('#ticket_table').on('click', 'tbody tr', function (evt) {
        var $cell = $(evt.target).closest('td');
        if ($cell.index() > 0) {
            window.location = $oTable.row(this).data()._links.self
        }
    });
});


// The plugin function for adding a new filtering routine for creation_date
$.fn.dataTableExt.afnFiltering.push(
    function (oSettings, aData, iDataIndex) {
        var dateStart = parseDateValue($("#dateStart").val());
        var dateEnd = parseDateValue($("#dateEnd").val());
        var evalDate = parseDateValue(aData[1]);

        if (dateStart == null && dateEnd == null) {
            return true;
        }
        if (dateStart == null && evalDate <= dateEnd) {
            return true;
        }
        if (dateEnd == null && evalDate >= dateStart) {
            return true;
        }
        if (evalDate >= dateStart && evalDate <= dateEnd) {
            return true;
        }
        return false;

    });

// The plugin function for adding a new filtering routine for due_date
$.fn.dataTableExt.afnFiltering.push(
    function (oSettings, aData, iDataIndex1) {
        var dateStart1 = parseDateValue($("#dateStart1").val());
        var dateEnd1 = parseDateValue($("#dateEnd1").val());
        var evalDate1 = parseDateValue(aData[2]);

        if (dateStart1 == null && dateEnd1 == null) {
            return true;
        }
        if (dateStart1 == null && evalDate1 <= dateEnd1) {
            return true;
        }
        if (dateEnd1 == null && evalDate1 >= dateStart1) {
            return true;
        }
        if (evalDate1 >= dateStart1 && evalDate1 <= dateEnd1) {
            return true;
        }
        return false;

    });


// The plugin function for adding a new filtering routine for finished_date
$.fn.dataTableExt.afnFiltering.push(
    function (oSettings, aData, iDataIndex2) {
        var dateStart2 = parseDateValue($("#dateStart2").val());
        var dateEnd2 = parseDateValue($("#dateEnd2").val());
        var evalDate2 = parseDateValue(aData[3]);

        if (dateStart2 == null && dateEnd2 == null) {
            return true;
        }
        if (dateStart2 == null && evalDate2 <= dateEnd2) {
            return true;
        }
        if (dateEnd2 == null && evalDate2 >= dateStart2) {
            return true;
        }
        if (evalDate2 >= dateStart2 && evalDate2 <= dateEnd2) {
            return true;
        }
        return false;

    });

// Function for converting a mm/dd/yyyy date value into a numeric string for comparison (example 08/12/2010 becomes 20100812
function parseDateValue(rawDate) {
    if (rawDate == '') {
        return null
    }
    var dateArray = rawDate.split("/");
    var parsedDate = dateArray[2] + dateArray[0] + dateArray[1];
    return parsedDate;
}

$("#clear").click(function () {
    $('#dateStart').datepicker('setDate', null);
    $('#dateStart1').datepicker('setDate', null);
    $('#dateStart2').datepicker('setDate', null);
    $('#dateEnd').datepicker('setDate', null);
    $('#dateEnd1').datepicker('setDate', null);
    $('#dateEnd2').datepicker('setDate', null);
    $oTable.draw();
});
