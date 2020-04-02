var oTable;

function setupData() {
    $(document).ready(function () {
        oTable = $('#ticket_table').DataTable({
            "ajax": {
                "url": "/tickets_get_data",
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
                {"data": "reclamation.reclamation_customer.name"},
                {"data": "reclamation_id"},
                {
                    "data": "ticket_assigned", render: function (data, type, row) {
                        return row.ticket_assigned.first_name + ' ' + row.ticket_assigned.last_name;
                    }
                },
                {
                    "data": "description_ticket", render: function (data, type) {
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
    $('#ticket_table').on('click', 'tbody tr', function (evt) {
        var $cell = $(evt.target).closest('td');
        if ($cell.index() > 0) {
            window.location = oTable.row(this).data()._links.self
        }
    });
});