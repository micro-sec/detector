async function startMonitoring() {
    const {value: file} = await Swal.fire({
        title: "Provide a valid JSON file",
        input: "file",
        inputAttributes: {
            "accept": "application/json",
        },
        showCancelButton: true,
        confirmButtonText: "Continue",
        reverseButtons: true
    });

    if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
            Swal.fire({
                title: 'Do you wish to submit this configuration?',
                html: "<pre style=\"text-align: left;\">" + JSON.stringify(JSON.parse(e.target.result), null, 2) + "</pre>",
                confirmButtonText: "Start Monitoring",
                showLoaderOnConfirm: true,
                showCancelButton: true,
                reverseButtons: true,
                preConfirm: () => {
                    return axios({
                        method: "post",
                        url: "/api/monitoring/start",
                        data: JSON.parse(e.target.result)
                    }).then(response => {
                        Swal.fire({
                            title: "Success!",
                            text: response.data,
                            icon: "success"
                        }).then(function(){
                            //location.reload();
                            window.location.href = "/"
                        });
                    }, error => {
                        Swal.fire({
                            title: "Error!",
                            text: error,
                            icon: "error"
                        }).then(function(){
                            //location.reload();
                            window.location.href = "/"
                        });
                    });
                },
                backdrop: true,
                allowOutsideClick: () => !Swal.isLoading()
            });
        }
        reader.readAsText(file);
    }
}

function stopMonitoring() {
    Swal.fire({
        title: "Are you sure you want to stop monitoring?",
        confirmButtonText: "Stop Monitoring",
        showLoaderOnConfirm: true,
        showCancelButton: true,
        reverseButtons: true,
        preConfirm: () => {
            return axios({
                method: "post",
                url: "/api/monitoring/stop",
                data: {}
            }).then(response => {
                Swal.fire({
                    title: "Success!",
                    text: response.data,
                    icon: "success"
                }).then(function(){
                    //location.reload();
                    window.location.href = "/"
                });
            }, error => {
                Swal.fire({
                    title: "Error!",
                    text: error,
                    icon: "error"
                }).then(function(){
                    //location.reload();
                    window.location.href = "/"
                });
            });
        },
        backdrop: true,
        allowOutsideClick: () => !Swal.isLoading()
    })
}

async function startInspecting() {
    const {value: file} = await Swal.fire({
        title: "Provide a valid JSON file",
        input: "file",
        inputAttributes: {
            "accept": "application/json",
        },
        showCancelButton: true,
        confirmButtonText: "Continue",
        reverseButtons: true
    });

    if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
            Swal.fire({
                title: 'Do you wish to submit this configuration?',
                html: "<pre style=\"text-align: left;\">" + JSON.stringify(JSON.parse(e.target.result), null, 2) + "</pre>",
                confirmButtonText: "Start Inspecting system calls",
                showLoaderOnConfirm: true,
                showCancelButton: true,
                reverseButtons: true,
                preConfirm: () => {
                    return axios({
                        method: "post",
                        url: "/api/inspecting/start",
                        data: JSON.parse(e.target.result)
                    }).then(response => {
                        Swal.fire({
                            title: "Success!",
                            text: response.data,
                            icon: "success"
                        }).then(function(){
                            //location.reload();
                            window.location.href = "/"
                        });
                    }, error => {
                        Swal.fire({
                            title: "Error!",
                            text: error,
                            icon: "error"
                        }).then(function(){
                            //location.reload();
                            window.location.href = "/"
                        });
                    });
                },
                backdrop: true,
                allowOutsideClick: () => !Swal.isLoading()
            });
        }
        reader.readAsText(file);
    }
}


function stopInspecting(identifier){
    let url = "/api/inspecting/stop"
    if(identifier){
        url = "/api/inspecting/stop?id=" + identifier;
    }
    Swal.fire({
        title: "Are you sure you want to stop inspecting the system calls?",
        confirmButtonText: "Stop Inspecting",
        showLoaderOnConfirm: true,
        showCancelButton: true,
        reverseButtons: true,
        preConfirm: () => {
            return axios({
                method: "post",
                url: url,
                data: {}
            }).then(response => {
                Swal.fire({
                    title: "Success!",
                    text: response.data,
                    icon: "success"
                }).then(function(){
                    //location.reload();
                    window.location.href = "/"
                });
            }, error => {
                Swal.fire({
                    title: "Error!",
                    text: error,
                    icon: "error"
                }).then(function(){
                    //location.reload();
                    window.location.href = "/"
                });
            });
        },
        backdrop: true,
        allowOutsideClick: () => !Swal.isLoading()
    })
}


function exportAlarms() {
    return axios({
        method: "get",
        url: "/api/alarms",
        responseType: 'arraybuffer',
    }).then (response => {
        const type = response.headers['content-type']
        const blob = new Blob([response.data], { type: type, encoding: 'UTF-8' })
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = 'alarms.json'
        link.click()
    })
}

function deleteAlarms() {
    return axios({
        method: "delete",
        url: "/api/alarms"
    }).then (response => {
        $('#table').bootstrapTable('refresh')
    })
}
