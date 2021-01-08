window.expandReportList = function (element, numberOfReports){
    var currentRow = element.parentElement.parentElement
    var nextTableRow = currentRow.nextElementSibling;

    var tipIcon = element.getElementsByClassName("rotated-tip")[0];
    var verticalLineIcon = element.getElementsByClassName("report-list-vl")[0];

    while (nextTableRow.className !== "tr-next-day-separator"){
        nextTableRow.classList.toggle("visible-hidden-report")
        nextTableRow = nextTableRow.nextElementSibling;
    }
    var allReportsHeight = calculateReportListHeight(currentRow, numberOfReports);

    var verticalLineIconHeight = allReportsHeight - 25;

    if (currentRow.offsetHeight < allReportsHeight) {
        verticalLineIcon.style.height = verticalLineIconHeight + "px";
        verticalLineIcon.style.transition = "0.2s";
    }
    else {
        verticalLineIcon.style.height = "0px";
        verticalLineIcon.style.transition = "0.2s";
    }
    tipIcon.classList.toggle("roll-reports-icon");
};

function calculateReportListHeight(currentRow, numberOfReports) {
    let reportListHeight = currentRow.offsetHeight;
    let nextRow = currentRow.nextElementSibling;

    for (var reportNumber=1; reportNumber < numberOfReports; reportNumber++) {
        reportListHeight = reportListHeight + nextRow.offsetHeight;
        nextRow = nextRow.nextElementSibling;

    }

    return reportListHeight;
}
