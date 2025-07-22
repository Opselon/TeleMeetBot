$(document).ready(function() {
    let logInterval;

    $("#save-token-form").submit(function(event) {
        event.preventDefault();
        $.ajax({
            url: "/save_token",
            type: "POST",
            data: $(this).serialize(),
            success: function(data) {
                alert("Token saved successfully. Please restart the application for the changes to take effect.");
            },
            error: function() {
                alert("Failed to save token.");
            }
        });
    });

    $("#run-automation-form").submit(function(event) {
        event.preventDefault();
        $.ajax({
            url: "/run_automation",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                meet_link: $("#meet_link").val(),
                youtube_link: $("#youtube_link").val()
            }),
            success: function(data) {
                location.reload();
            },
            error: function() {
                alert("Failed to start automation.");
            }
        });
    });

    $(".stop-automation-btn").click(function() {
        var automationId = $(this).data("automation-id");
        $.ajax({
            url: "/stop_automation",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                automation_id: automationId
            }),
            success: function(data) {
                location.reload();
            },
            error: function() {
                alert("Failed to stop automation.");
            }
        });
    });

    $(".view-logs-btn").click(function() {
        var automationId = $(this).data("automation-id");
        $("#logs-container").html("Loading logs for automation " + automationId + "...");

        if (logInterval) {
            clearInterval(logInterval);
        }

        function fetchLogs() {
            $.get("/automations/" + automationId + "/logs", function(logs) {
                var logsHtml = "<table class='table table-striped'><thead><tr><th>Timestamp</th><th>Level</th><th>Message</th></tr></thead><tbody>";
                logs.forEach(function(log) {
                    logsHtml += "<tr><td>" + new Date(log.timestamp).toLocaleString() + "</td><td>" + log.level + "</td><td>" + log.message + "</td></tr>";
                });
                logsHtml += "</tbody></table>";
                $("#logs-container").html(logsHtml);
            }).fail(function() {
                $("#logs-container").html("Failed to load logs for automation " + automationId);
                clearInterval(logInterval);
            });
        }

        fetchLogs();
        logInterval = setInterval(fetchLogs, 5000); // Refresh logs every 5 seconds
    });

    $(".mute-btn").click(function() {
        $.ajax({
            url: "/mute",
            type: "POST",
            success: function(data) {
                alert("Microphone muted successfully.");
            },
            error: function() {
                alert("Failed to mute microphone.");
            }
        });
    });

    $(".unmute-btn").click(function() {
        $.ajax({
            url: "/unmute",
            type: "POST",
            success: function(data) {
                alert("Microphone unmuted successfully.");
            },
            error: function() {
                alert("Failed to unmute microphone.");
            }
        });
    });
});
