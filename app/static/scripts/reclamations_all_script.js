var oTable;

function setupData() {
    $(document).ready(function () {
        oTable = $('#reclamation_table').DataTable({
            "ajax": {
                "url": "/reclamation_get_data",
                "dataType": "json",
                "dataSrc": "reclamations",
                "contentType": "application/json"
            },
            "columns": [
                {"data": "id"},
                {
                    "data": "informed_date", render: function (data) {
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
                {"data": "reclamation_customer.name"},
                {"data": "reclamation_part_sn_id.part_sn"},
                {
                    "data": "description_reclamation", render: function (data, type) {
                        return type === 'display' && data.length > 40 ?
                            '<span title="' + data + '">' + data.substr(0, 38) + '...</span>' :
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
    });
}

$(window).on("load", setupData);

$(document).ready(function () {
    $('#reclamation_table').on('click', 'tbody tr', function (evt) {
        var $cell = $(evt.target).closest('td');
        if ($cell.index() > 0) {
            window.location = oTable.row(this).data()._links.self
        }
    });
});