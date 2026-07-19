(function () {
    function currentTheme() {
        return document.documentElement.getAttribute("data-theme") || "light";
    }

    function setTheme(t) {
        document.documentElement.setAttribute("data-theme", t);
        localStorage.setItem("whatstext-theme", t);
    }

    var toggle = document.getElementById("theme-toggle");
    if (toggle) {
        toggle.addEventListener("click", function () {
            setTheme(currentTheme() === "dark" ? "light" : "dark");
        });
    }

    var dropzone = document.getElementById("dropzone");
    if (!dropzone) return;

    var fileInput = document.getElementById("file-input");
    var progressWrap = document.getElementById("progress-wrap");
    var progressFill = document.getElementById("progress-fill");
    var statusText = document.getElementById("status-text");
    var errorText = document.getElementById("error-text");

    function showError(message) {
        errorText.textContent = message;
        errorText.hidden = false;
        progressWrap.hidden = true;
        dropzone.hidden = false;
    }

    var WARN_BYTES = 2 * 1024 * 1024 * 1024; // 2GB

    function upload(file) {
        if (!file) return;
        if (!file.name.toLowerCase().endsWith(".zip")) {
            showError("Please choose the WhatsApp export .zip file.");
            return;
        }

        if (file.size > WARN_BYTES) {
            var gb = (file.size / (1024 * 1024 * 1024)).toFixed(1);
            var proceed = confirm(
                gb + " GB is a large export — processing could take a while " +
                "and use a similar amount of disk space temporarily. Continue?"
            );
            if (!proceed) return;
        }

        errorText.hidden = true;
        dropzone.hidden = true;
        progressWrap.hidden = false;
        statusText.textContent = "Uploading " + file.name + "…";
        progressFill.style.width = "0%";

        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/upload", true);
        xhr.setRequestHeader("X-Filename", encodeURIComponent(file.name));

        xhr.upload.addEventListener("progress", function (e) {
            if (e.lengthComputable) {
                var pct = Math.round((e.loaded / e.total) * 100);
                progressFill.style.width = pct + "%";
                if (pct >= 100) {
                    statusText.textContent = "Extracting and parsing…";
                }
            }
        });

        xhr.onload = function () {
            if (xhr.status >= 200 && xhr.status < 400) {
                window.location.href = xhr.responseURL || "/";
            } else {
                showError(xhr.responseText || ("Upload failed (status " + xhr.status + ")"));
            }
        };

        xhr.onerror = function () {
            showError("Upload failed — is the local server still running?");
        };

        xhr.send(file);
    }

    dropzone.addEventListener("click", function () {
        fileInput.click();
    });

    fileInput.addEventListener("change", function () {
        upload(fileInput.files[0]);
    });

    ["dragenter", "dragover"].forEach(function (evt) {
        dropzone.addEventListener(evt, function (e) {
            e.preventDefault();
            dropzone.classList.add("drag-over");
        });
    });

    ["dragleave", "drop"].forEach(function (evt) {
        dropzone.addEventListener(evt, function (e) {
            e.preventDefault();
            dropzone.classList.remove("drag-over");
        });
    });

    dropzone.addEventListener("drop", function (e) {
        upload(e.dataTransfer.files[0]);
    });
})();
