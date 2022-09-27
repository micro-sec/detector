const alarmsChartDom = document.getElementById("alarmsChart");
const syscallsChartDom = document.getElementById("syscallsChart");
const resizeMainContainer = function () {
    //alarmsChartDom.style.width = window.innerWidth + "px";
    //alarmsChartDom.style.height = 300 + "px";
    syscallsChartDom.style.width = window.innerWidth + "px";
    syscallsChartDom.style.height = 300 + "px";
};
resizeMainContainer();

//const alarmsChart = echarts.init(alarmsChartDom);
const syscallsChart = echarts.init(syscallsChartDom);
const syscallsWindowSize = 3600;
syscallsChart.showLoading();

let syscalls_data = [];

window.onresize = function() {
    syscallsChart.resize();
}

const syscallsOption = {
    title: {
        text: "System calls collected over time",
        textStyle : {
            fontWeight: "bold",
            fontSize: 14
        }
    },
    toolbox: {
        feature: {
            dataView: { show: true, readOnly: false },
            restore: { show: true },
            saveAsImage: { name: "syscallsChart", title: "Save", show: true }
        }
    },
    tooltip: {
        trigger: "axis",
        formatter: function (params) {
            params = params[0];
            const date = new Date(params.value[0]);
            const year = date.getFullYear();
            const month = date.getMonth();
            const day = date.getDate();
            const hour = date.getHours();
            const min = date.getMinutes();
            const sec = date.getSeconds();
            return "x: " + hour + ":" + min + ":" + sec + "\ny: " + params.value[1];
        },
        axisPointer: {
            animation: false
        }
    },
    xAxis: {
        type: "time",
        splitLine: {
            show: false
        }
    },
    yAxis: {
        type: "value",
        boundaryGap: [0, "100%"],
        splitLine: {
            show: true
        }
    },
    series: [
        {
            name: "Syscalls",
            type: "line",
            showSymbol: false,
            data: syscalls_data
        }
    ]
};

setInterval(function () {
    axios.get("/api/stats")
        .then( (response) => {
            // Handle syscalls data
            if(syscalls_data.length >= syscallsWindowSize) syscalls_data.shift();
            syscalls_data.push(
                { name: "syscalls",
                    value: [response.data.syscalls.x, response.data.syscalls.y]
                }
            );

            // Handle general statistics
            $('#totalAlarms').text(response.data.alarms.total);
            $('#totalSyscalls').text(response.data.monitoring.total_syscalls);
            $('#totalSize').text(response.data.monitoring.total_size);
            $('#totalBatches').text(response.data.monitoring.total_batches);

            // Handle Monitoring Configs
            let monitoringElapsedTime = Math.round((Date.now() / 1000) - Math.round($('#monitoringStartTimeTimestamp').text()));
            $('#monitoringElapsedTime').text(new Date(monitoringElapsedTime * 1000).toISOString().substr(11, 8));

            // Handle Inspecting Configs
            let allDetections = $('#allDetections').text().split(",").slice(0,-1);
            for (let i = 0; i < allDetections.length; i++) {
                let inspectingStartTimeTimestamp = $('#inspectingStartTimeTimestamp_' + allDetections[i])
                let inspectingStartTime = Math.round(inspectingStartTimeTimestamp.text());
                let inspectingElapsedTime = Math.round((Date.now() / 1000) - inspectingStartTime);
                $('#inspectingElapsedTime_' + allDetections[i]).text(new Date(inspectingElapsedTime * 1000).toISOString().substr(11, 8));

                // Refresh page if inspecting duration ends and ask to save data
                let inspectingDuration = $('#inspectingDuration_' + allDetections[i]).text()
                if (inspectingDuration > 0 && inspectingStartTime !== 0 && inspectingElapsedTime > inspectingDuration) {
                    inspectingStartTimeTimestamp.text(0);
                    location.reload();
                    /*Swal.fire({
                        title: 'Inspecting finished successfully',
                        text: 'Do you wish to save the alarms?',
                        showDenyButton: true,
                        confirmButtonText: 'Save',
                        denyButtonText: "Don't save",
                        backdrop: "filter: blur(10px);",
                        reverseButtons: true,
                    }).then((result) => {
                        if (result.isConfirmed) {
                            exportAlarms()
                            location.reload()
                        } else if (result.isDenied) {
                            location.reload()
                        }
                    })*/
                }
            }
        });


    syscallsChart.hideLoading();
    syscallsChart.setOption({
        series: [
            {
                data: syscalls_data
            }
        ]
    });
}, 1000);

syscallsOption && syscallsChart.setOption(syscallsOption);
